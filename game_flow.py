"""Game flow orchestration and phase management."""
from typing import List

from models import Player, GameStateManager
from phase_handlers import DayPhaseHandler, NightPhaseHandler, FirstNightHandler
from config import MAX_PHASES


def phase_sort_key(phase_name: str) -> tuple:
    """
    Return a sortable key for phase names to ensure chronological ordering.
    
    Order: REGISTRATION (0) -> NIGHT0 (1) -> DAY1 (2) -> NIGHT1 (3) -> DAY2 (4) -> ...
    """
    if phase_name == "REGISTRATION":
        return (0, 0)
    elif phase_name.startswith("NIGHT"):
        night_num = int(phase_name.replace("NIGHT", ""))
        return (1 + night_num * 2, night_num)
    elif phase_name.startswith("DAY"):
        day_num = int(phase_name.replace("DAY", ""))
        return (2 + (day_num - 1) * 2, day_num)
    return (999, 0)  # Unknown phases go last


class GameOrchestrator:
    """Orchestrates the game flow through phases."""

    def __init__(self, state_manager: GameStateManager):
        self.state_manager = state_manager
        self.first_night_handler = FirstNightHandler(state_manager)
        self.day_handler = DayPhaseHandler(state_manager)
        self.night_handler = NightPhaseHandler(state_manager)

    def run_game_phases(self, max_phases: int = MAX_PHASES) -> None:
        """Run the game through alternating day and night phases."""
        print("\nBeginning Game Loop...")

        night_counter = 0
        day_counter = 0

        for idx in range(1, max_phases + 1):
            # Determine phase type and name
            if idx == 1:
                phase_name = "NIGHT0"
                phase_type = "first_night"
                night_counter = 0
            elif idx % 2 == 0:
                # Even phases are day
                day_counter += 1
                phase_name = f"DAY{day_counter}"
                phase_type = "day"
            else:
                # Odd phases (after first) are night
                night_counter += 1
                phase_name = f"NIGHT{night_counter}"
                phase_type = "night"

            print(f"\n{'='*50}")
            print(f"Starting {phase_name}")
            print(f"{'='*50}")

            # Apply actions from previous phase and announce results
            if idx > 1:
                self._apply_previous_phase_actions(phase_name)

            # Get updated player list AFTER applying actions
            players = self.state_manager.players

            # Save current game state before phase starts
            self._save_phase_snapshot(phase_name, phase_type, players)

            # Run appropriate phase
            if phase_type == "first_night":
                self.first_night_handler.run(players, phase_name)
            elif phase_type == "night":
                self.night_handler.run(players, phase_name)
            else:  # day
                self.day_handler.run(players, phase_name)

            # Get updated player list after phase completes
            players = self.state_manager.players

            # Save final state after phase completes
            self._save_phase_snapshot(phase_name, phase_type, players, completed=True)

    def _apply_previous_phase_actions(self, current_phase: str) -> None:
        """Apply actions from previous phase and set announcements."""
        # Get all phases and sort them chronologically
        all_phases = list(self.state_manager._state.get("phase_updates", {}).keys())
        all_phases = sorted(all_phases, key=phase_sort_key)
        
        if not all_phases:
            return
        
        # Find current phase index and get previous
        try:
            current_idx = all_phases.index(current_phase)
            if current_idx == 0:
                return  # No previous phase
            prev_phase = all_phases[current_idx - 1]
        except ValueError:
            # Current phase not in list yet, use last phase
            prev_phase = all_phases[-1]

        print(f"\nApplying actions from {prev_phase} to {current_phase}:")
        
        # Check if there are any actions to apply
        actions = self.state_manager.get_actions(prev_phase)
        if not actions:
            print("  No actions to apply.")
            return
        
        unapplied_actions = [a for a in actions if not a.get("applied")]
        if not unapplied_actions:
            print(f"  All {len(actions)} action(s) already applied.")
            return
        
        print(f"  Found {len(unapplied_actions)} unapplied action(s) to process...")

        players = self.state_manager.players
        announcement_lines = self.state_manager.apply_actions(prev_phase, players)

        if announcement_lines:
            announcements = "\n".join(announcement_lines)
            self.state_manager.set_announcements(current_phase, announcements)
            print(f"\nAnnouncements for {current_phase}:")
            for line in announcement_lines:
                print(f"  ✓ {line}")
        else:
            print("  No announcements generated from actions.")

    def _save_phase_snapshot(
        self,
        phase_name: str,
        phase_type: str,
        players: List[Player],
        completed: bool = False
    ) -> None:
        """Save a snapshot of the game state for this phase."""
        # Update phase-specific metadata
        phase_updates = self.state_manager._state.setdefault("phase_updates", {})
        phase_entry = phase_updates.setdefault(phase_name, {
            "sent": None,
            "responses": {},
            "actions": [],
            "announcements": ""
        })
        
        # Add phase metadata
        phase_entry["phase_type"] = phase_type
        phase_entry["completed"] = completed
        
        # Add player snapshot
        phase_entry["player_snapshot"] = {
            "alive_count": sum(1 for p in players if p.alive),
            "dead_count": sum(1 for p in players if not p.alive),
            "players": [
                {
                    "number": p.number,
                    "name": p.name,
                    "alive": p.alive,
                    "roleClass": p.roleClass,
                    "roleName": p.roleName
                }
                for p in players
            ]
        }
        
        # Save to disk
        self.state_manager._write()
        
        status = "completed" if completed else "starting"
        print(f"Game state snapshot saved for {phase_name} ({status})")
