"""Data models for game entities."""
from dataclasses import dataclass, asdict
from typing import List, Optional
import json
from pathlib import Path
from datetime import datetime

from config import DEFAULT_ROLE_NAME, INITIAL_PHASE


@dataclass
class Player:
    """Represents a player in the game."""
    number: int
    name: str
    email: str
    alive: bool = True
    hasGhostVote: bool = True
    drunk: bool = False
    poisoned: bool = False
    roleClass: str = "townsfolk"
    roleName: str = DEFAULT_ROLE_NAME

    def to_dict(self) -> dict:
        """Convert player to dictionary."""
        return asdict(self)


class GameStateManager:
    """Manage the on-disk representation of the game state."""

    def __init__(self, path: Path):
        self._path = path
        self._state = {
            "phase": INITIAL_PHASE,
            "players": [],
            "phase_updates": {},
            "metadata": {
                "created_at": None,
                "last_updated": None,
                "version": "1.0"
            }
        }

    @property
    def phase(self) -> str:
        """Get current phase."""
        return self._state["phase"]

    @property
    def players(self) -> List[Player]:
        """Get list of players as Player objects."""
        return [
            Player(**p) if isinstance(p, dict) else p
            for p in self._state.get("players", [])
        ]

    def reset(self) -> None:
        """Reset the stored game state to an empty roster and initial phase."""
        self._state = {
            "phase": INITIAL_PHASE,
            "players": [],
            "phase_updates": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        self._write()

    def set_players(self, players: List[Player]) -> None:
        """Persist the list of players while keeping the current phase."""
        self._state["players"] = [player.to_dict() for player in players]
        self._write()

    def update_phase(self, new_phase: str, sent_body: Optional[str] = None) -> None:
        """Update the phase in memory and on disk and create phase_updates entry."""
        self._state["phase"] = new_phase
        phase_updates = self._state.setdefault("phase_updates", {})
        
        if new_phase not in phase_updates:
            phase_updates[new_phase] = {
                "sent": sent_body,
                "responses": {},
                "actions": [],
                "announcements": ""
            }
        elif sent_body is not None:
            phase_updates[new_phase]["sent"] = sent_body
        
        self._write()

    def record_response(
        self, phase: str, player_number: int, 
        response_text: str, sender_email: str
    ) -> None:
        """Record a player's response for a given phase. Do not overwrite existing response."""
        phase_updates = self._state.setdefault("phase_updates", {})
        phase_entry = phase_updates.setdefault(phase, {
            "sent": None,
            "responses": {},
            "actions": [],
            "announcements": ""
        })
        responses = phase_entry.setdefault("responses", {})
        
        key = str(player_number)
        if key in responses:
            return  # Already have a response from this player
        
        responses[key] = {
            "from": sender_email,
            "text": response_text
        }
        self._write()

    def has_response(self, phase: str, player_number: int) -> bool:
        """Check if a player has already responded for a phase."""
        responses = (
            self._state.get("phase_updates", {})
            .get(phase, {})
            .get("responses", {})
        )
        return str(player_number) in responses

    def record_action(self, phase: str, action_type: str, details: dict) -> None:
        """Record an action (e.g. kill) taken during a phase."""
        phase_updates = self._state.setdefault("phase_updates", {})
        phase_entry = phase_updates.setdefault(phase, {
            "sent": None,
            "responses": {},
            "actions": [],
            "announcements": ""
        })
        actions = phase_entry.setdefault("actions", [])
        
        action = {
            "type": action_type,
            "details": details,
            "applied": False
        }
        actions.append(action)
        self._write()

    def get_actions(self, phase: str) -> list:
        """Return list of actions recorded for a phase (may be empty)."""
        return (
            self._state.get("phase_updates", {})
            .get(phase, {})
            .get("actions", [])
        )

    def set_announcements(self, phase: str, announcements: str) -> None:
        """Set the announcements for a phase."""
        phase_updates = self._state.setdefault("phase_updates", {})
        phase_entry = phase_updates.setdefault(phase, {
            "sent": None,
            "responses": {},
            "actions": [],
            "announcements": ""
        })
        phase_entry["announcements"] = announcements
        self._write()

    def get_announcements(self, phase: str) -> str:
        """Get the announcements for a phase."""
        return (
            self._state.get("phase_updates", {})
            .get(phase, {})
            .get("announcements", "")
        )

    def apply_actions(self, phase: str, players: List[Player]) -> list:
        """
        Apply any un-applied actions from 'phase' to the players list.
        Returns a list of human-readable results for announcements.
        """
        results = []
        phase_updates = self._state.setdefault("phase_updates", {})
        phase_entry = phase_updates.setdefault(phase, {
            "sent": None,
            "responses": {},
            "actions": [],
            "announcements": ""
        })
        actions = phase_entry.setdefault("actions", [])
        
        for action in actions:
            if action.get("applied"):
                continue
            
            action_type = action.get("type")
            print(f"    Processing action: {action_type}")
            
            if action_type == "kill":
                result = self._apply_kill_action(action, players)
                if result:
                    results.append(result)
                    print(f"      → {result}")
            elif action_type == "poison":
                result = self._apply_poison_action(action, players)
                if result:
                    results.append(result)
                    print(f"      → {result}")
            elif action_type == "butler_choice":
                # Butler choices don't generate announcements
                action["applied"] = True
                action["result"] = {"status": "recorded"}
                print(f"      → Butler choice recorded")
            else:
                # Mark unknown actions as applied without effect
                action["applied"] = True
                action["result"] = {"status": "unhandled_action_type"}
                print(f"      → Unknown action type, skipped")
        
        # Persist updated players and actions
        self._state["phase_updates"][phase] = phase_entry
        self._state["players"] = [p.to_dict() for p in players]
        self._write()
        
        return results

    def _apply_kill_action(self, action: dict, players: List[Player]) -> Optional[str]:
        """Apply a kill action to a player. Returns announcement text if successful."""
        details = action.get("details", {})
        target_num = details.get("target")
        by_num = details.get("by")
        
        print(f"      DEBUG: Kill action - by: {by_num}, target: {target_num}")
        print(f"      DEBUG: Players in list: {[p.number for p in players]}")
        
        target = next((p for p in players if p.number == target_num), None)
        
        print(f"      DEBUG: Target found: {target.name if target else 'None'}")
        print(f"      DEBUG: Target alive: {target.alive if target else 'N/A'}")
        
        if target and target.alive:
            target.alive = False
            action["applied"] = True
            action["result"] = {
                "target": target_num,
                "target_name": target.name
            }
            print(f"      DEBUG: Target {target.name} killed successfully")
            return f"{target.name} was killed"
        else:
            action["applied"] = True
            action["result"] = {
                "target": target_num,
                "status": "invalid_or_already_dead"
            }
            print(f"      DEBUG: Kill failed - target invalid or dead")
            return f"Kill action by player {by_num} failed (target {target_num} invalid)."

    def _apply_poison_action(self, action: dict, players: List[Player]) -> Optional[str]:
        """Apply a poison action to a player. Returns None (no public announcement)."""
        details = action.get("details", {})
        target_num = details.get("target")
        by_num = details.get("by")
        
        target = next((p for p in players if p.number == target_num), None)
        
        if target and target.alive:
            target.poisoned = True
            action["applied"] = True
            action["result"] = {
                "target": target_num,
                "target_name": target.name,
                "status": "poisoned"
            }
            # Poison is secret, no public announcement
            return None
        else:
            action["applied"] = True
            action["result"] = {
                "target": target_num,
                "status": "invalid_or_already_dead"
            }
            return None

    def _write(self) -> None:
        """Write the in-memory state to the configured JSON file."""
        # Update metadata timestamp
        if "metadata" not in self._state:
            self._state["metadata"] = {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
        else:
            self._state["metadata"]["last_updated"] = datetime.now().isoformat()
        
        self._path.write_text(json.dumps(self._state, indent=2))
