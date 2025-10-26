#!/usr/bin/env python3
"""CLI for setting up a game and emailing players."""
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from email_sender import DEFAULT_TEST_TO, sendemail


load_dotenv()


DATA_FILE = Path(__file__).with_name("gamestate.json")
DEFAULT_PLAYER_EMAIL = (
    os.getenv("DEFAULT_PLAYER_EMAIL")
    or os.getenv("DEFAULT_TO")
    or os.getenv("TO_EMAIL_ADDRESS")
    or os.getenv("EMAIL_ADDRESS")
    or DEFAULT_TEST_TO
)
DEFAULT_ROLE_NAME = os.getenv("DEFAULT_ROLE_PLACEHOLDER", "Villager")
INITIAL_PHASE = "DAY0"
MAX_PHASES = 10


@dataclass
class Player:
    number: int
    name: str
    email: str
    alive: bool = True
    hasGhostVote: bool = True
    role: str = DEFAULT_ROLE_NAME

    def to_dict(self) -> dict:
        return asdict(self)


class GameStateManager:
    """Manage the on-disk representation of the game state."""

    def __init__(self, path: Path):
        self._path = path
        self._state = {"phase": INITIAL_PHASE, "players": []}

    @property
    def phase(self) -> str:
        return self._state["phase"]

    def reset(self) -> None:
        """Reset the stored game state to an empty roster and initial phase."""
        self._state = {"phase": INITIAL_PHASE, "players": []}
        self._write()

    def set_players(self, players: List[Player]) -> None:
        """Persist the list of players while keeping the current phase."""
        self._state["players"] = [player.to_dict() for player in players]
        self._write()

    def update_phase(self, new_phase: str) -> None:
        """Update the phase in memory and on disk."""
        self._state["phase"] = new_phase
        self._write()

    def _write(self) -> None:
        self._path.write_text(json.dumps(self._state, indent=2))


def prompt_player_count():
    """Prompt for and return a positive integer number of players."""
    while True:
        try:
            raw = input("How many players? ").strip()
            count = int(raw)
            if count <= 0:
                raise ValueError
            return count
        except ValueError:
            print("Please enter a positive integer for the number of players.")


def build_players(count: int) -> List[Player]:
    """Create players with default values derived from configuration."""
    players = []
    for idx in range(1, count + 1):
        player = Player(
            number=idx,
            name=f"player{idx}",
            email=DEFAULT_PLAYER_EMAIL,
        )
        players.append(player)
    return players


def save_players(state_manager: GameStateManager, players: List[Player]):
    """Persist player data to a JSON file."""
    state_manager.set_players(players)
    print(f"\nSaved player data to {DATA_FILE.name}.")


def notify_players(players: List[Player], phase: str) -> None:
    """Send an email to each player announcing the current phase."""
    subject = f"Game phase {phase}"
    body = (
        "Blood on the Clocktower is starting!\n"
        f"Current game phase: {phase}.\n"
        "Stay tuned for further updates."
    )
    for player in players:
        try:
            sendemail(player.email, subject, body)
            print(f"Sent email to {player.name} at {player.email}.")
        except Exception as exc:
            print(f"Failed to send email to {player.name} ({player.email}): {exc}")


def run_game_phases(state_manager: GameStateManager, max_phases: int = MAX_PHASES) -> None:
    """Iterate through placeholder phases for testing purposes."""
    for idx in range(1, max_phases + 1):
        phase_name = f"PHASE{idx}"
        state_manager.update_phase(phase_name)
        print(f"Now game phase {idx}")


def main():
    print("Blood on the Clocktower Game Setup")
    state_manager = GameStateManager(DATA_FILE)
    state_manager.reset()
    count = prompt_player_count()
    players = build_players(count)
    save_players(state_manager, players)
    print("\nSending emails...")
    notify_players(players, state_manager.phase)
    run_game_phases(state_manager)


if __name__ == "__main__":
    main()
