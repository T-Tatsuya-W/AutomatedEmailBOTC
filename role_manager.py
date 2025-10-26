"""Role management and assignment logic."""
import random
from typing import List

from config import (
    TOWNSFOLK_ROLES,
    OUTSIDER_ROLES,
    MINION_ROLES,
    DEMON_ROLES,
    ROLE_DISTRIBUTION,
    DEFAULT_ROLE_NAME
)
from models import Player


class RoleManager:
    """Manages role assignment and distribution."""

    @staticmethod
    def get_role_counts(player_count: int) -> dict:
        """
        Return dict with counts for each class based on player count.
        
        Returns:
            dict: {"townsfolk": int, "outsider": int, "minion": int, "demon": int}
        """
        if player_count < 2:
            raise ValueError("player count must be >= 2")

        # Clamp to 15 if higher (use 15 rules)
        if player_count > 15:
            player_count = 15

        townsfolk, outsiders, minions, demons = ROLE_DISTRIBUTION.get(
            player_count,
            ROLE_DISTRIBUTION[15]
        )

        return {
            "townsfolk": townsfolk,
            "outsider": outsiders,
            "minion": minions,
            "demon": demons
        }

    @staticmethod
    def assign_roles(players: List[Player]) -> None:
        """
        Assign roleClass and roleName to each player randomly based on count rules.
        Modifies players in-place.
        """
        count = len(players)
        counts = RoleManager.get_role_counts(count)

        # Build a pool of classes to assign
        pool = []
        pool += ["townsfolk"] * counts["townsfolk"]
        pool += ["outsider"] * counts["outsider"]
        pool += ["minion"] * counts["minion"]
        pool += ["demon"] * counts["demon"]

        # If pool length differs from player count (shouldn't), fill with townsfolk
        if len(pool) < count:
            pool += ["townsfolk"] * (count - len(pool))

        # Shuffle pool and assign to players in random order
        random.shuffle(pool)
        random_players = random.sample(players, len(players))

        for cls, player in zip(pool, random_players):
            player.roleClass = cls
            player.roleName = RoleManager._get_role_name_for_class(cls)

    @staticmethod
    def _get_role_name_for_class(role_class: str) -> str:
        """Get a random role name for a given role class."""
        role_lists = {
            "townsfolk": TOWNSFOLK_ROLES,
            "outsider": OUTSIDER_ROLES,
            "minion": MINION_ROLES,
            "demon": DEMON_ROLES
        }

        role_list = role_lists.get(role_class)
        if role_list:
            return random.choice(role_list)
        return DEFAULT_ROLE_NAME

    @staticmethod
    def is_demon(player: Player) -> bool:
        """Check if a player has the demon role."""
        return player.roleClass.lower() == "demon"
