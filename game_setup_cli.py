#!/usr/bin/env python3
"""CLI for setting up a game and emailing players."""
import json
from pathlib import Path

from email_sender import sendemail


DATA_FILE = Path(__file__).with_name("players.json")


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


def prompt_players(count):
    """Prompt for player details and return a list of player dictionaries."""
    players = []
    for idx in range(1, count + 1):
        print(f"\nPlayer {idx}")
        name = input("  Name: ").strip()
        while not name:
            print("    Name cannot be empty. Please enter a name.")
            name = input("  Name: ").strip()
        email = input("  Email: ").strip()
        while not email:
            print("    Email cannot be empty. Please enter an email address.")
            email = input("  Email: ").strip()
        players.append({
            "number": idx,
            "name": name,
            "email": email,
        })
    return players


def save_players(players):
    """Persist player data to a JSON file."""
    DATA_FILE.write_text(json.dumps(players, indent=2))
    print(f"\nSaved player data to {DATA_FILE.name}.")


def notify_players(players):
    """Send an email to each player."""
    for player in players:
        subject = f"GAME0 Player {player['number']} [{player['name']}]"
        try:
            sendemail(player["email"], subject, "test email content")
            print(f"Sent email to {player['name']} at {player['email']}.")
        except Exception as exc:
            print(f"Failed to send email to {player['name']} ({player['email']}): {exc}")


def main():
    print("Blood on the Clocktower Game Setup")
    count = prompt_player_count()
    players = prompt_players(count)
    save_players(players)
    print("\nSending emails...")
    notify_players(players)


if __name__ == "__main__":
    main()
