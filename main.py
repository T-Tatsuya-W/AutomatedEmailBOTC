#!/usr/bin/env python3
"""CLI for setting up a game and emailing players."""

from config import DATA_FILE
from models import GameStateManager
from player_setup import PlayerSetup
from role_manager import RoleManager
from phase_handlers import RegistrationHandler
from game_flow import GameOrchestrator


def main():
    """Main entry point for the Blood on the Clocktower game setup."""
    print("Blood on the Clocktower Game Setup")
    print("=" * 50)
    
    # Initialize game state
    state_manager = GameStateManager(DATA_FILE)
    state_manager.reset()
    
    # Setup players
    print("\nPlayer Setup")
    print("-" * 50)
    count = PlayerSetup.prompt_player_count()
    players = PlayerSetup.build_players(count)
    
    # Assign roles
    print("\nAssigning roles...")
    RoleManager.assign_roles(players)
    state_manager.set_players(players)
    print(f"Saved player data to {DATA_FILE.name}.")
    
    # Registration phase
    registration_handler = RegistrationHandler(state_manager)
    registration_handler.run(players)
    
    # Run game phases
    orchestrator = GameOrchestrator(state_manager)
    orchestrator.run_game_phases()


if __name__ == "__main__":
    main()
