"""Player setup and initialization."""
from typing import List

from models import Player
from config import DEFAULT_PLAYER_EMAIL


class PlayerSetup:
    """Handles player creation and setup."""

    @staticmethod
    def prompt_player_count() -> int:
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

    @staticmethod
    def build_players(count: int) -> List[Player]:
        """
        Create players by prompting for name and email, using defaults when blank.
        
        Args:
            count: Number of players to create
            
        Returns:
            List of Player objects
        """
        players = []
        for idx in range(1, count + 1):
            default_name = f"player{idx}"
            name_prompt = f"Name for player {idx} [{default_name}]: "
            email_prompt = f"Email for player {idx} [{DEFAULT_PLAYER_EMAIL}]: "

            raw_name = input(name_prompt).strip()
            name = raw_name if raw_name else default_name

            raw_email = input(email_prompt).strip()
            email = raw_email if raw_email else DEFAULT_PLAYER_EMAIL

            player = Player(
                number=idx,
                name=name,
                email=email,
            )
            players.append(player)

        return players
