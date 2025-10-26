"""Configuration constants and environment variable loading."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# File paths
DATA_FILE = Path(__file__).with_name("gamestate.json")

# Email configuration
DEFAULT_TEST_TO = os.getenv("DEFAULT_TEST_TO", "test@example.com")
DEFAULT_PLAYER_EMAIL = (
    os.getenv("DEFAULT_PLAYER_EMAIL")
    or os.getenv("DEFAULT_TO")
    or os.getenv("TO_EMAIL_ADDRESS")
    or os.getenv("EMAIL_ADDRESS")
    or DEFAULT_TEST_TO
)

# Game constants
DEFAULT_ROLE_NAME = "Villager"
INITIAL_PHASE = "REGISTRATION"
MAX_PHASES = 10
IMAP_POLL_INTERVAL = int(os.getenv("IMAP_POLL_INTERVAL", "5"))

# Email subject templates
REGISTRATION_SUBJECT_TEMPLATE = "testGames Registration - Player {num}"
PHASE_SUBJECT_TEMPLATE = "testGames {phase} - Player {num}"

# Role lists
TOWNSFOLK_ROLES = [
    "Washerwoman", "Librarian", "Investigator", "Chef", "Empath",
    "Fortune Teller", "Undertaker", "Monk", "Ravenkeeper", "Virgin",
    "Slayer", "Soldier", "Mayor"
]
OUTSIDER_ROLES = ["Butler", "Drunk", "Recluse", "Saint"]
MINION_ROLES = ["Poisoner", "Spy", "Scarlet Woman", "Baron"]
DEMON_ROLES = ["Imp"]

# Player count to role distribution mapping
ROLE_DISTRIBUTION = {
    2: (1, 0, 0, 1),
    3: (2, 0, 0, 1),
    4: (3, 0, 0, 1),
    5: (3, 0, 1, 1),
    6: (3, 1, 1, 1),
    7: (5, 0, 1, 1),
    8: (5, 1, 1, 1),
    9: (5, 2, 1, 1),
    10: (7, 0, 2, 1),
    11: (7, 1, 2, 1),
    12: (7, 2, 2, 1),
    13: (9, 0, 3, 1),
    14: (9, 1, 3, 1),
    15: (9, 2, 3, 1),
}
