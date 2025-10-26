# Blood on the Clocktower - Automated Email Game# AutomatedEmailBOTC



An automated email-based implementation of the social deduction game **Blood on the Clocktower**. This system manages game flow, role assignment, player communication, and game state through email interactions.Small collection of simple email utilities for testing with a Gmail account (or other SMTP/IMAP servers).



## OverviewOverview

- email_sender.py — small, tidy utility that exposes a sendemail(to, subject, message) function and a minimal CLI. Reads credentials from a `.env` file or prompts for them. Uses SMTP to send plain-text messages.

This system automates a Blood on the Clocktower game where:- email_listener.py — simple IMAP listener that polls the inbox and prints new messages (sender, subject, body). Reads credentials from the same `.env`.

- Players interact via email

- The system manages game phases (nights and days)Quick start

- Roles are automatically assigned with proper distribution1. Install requirements:

- Actions (kills, poisons, etc.) are processed and announced   ```bash

- Complete game state is tracked in JSON format   pip install -r requirements.txt

   ```

## Quick Start

2. Create a `.env` file in this directory with at least:

### Prerequisites   ```

   EMAIL_ADDRESS=you@example.com

- Python 3.7+   EMAIL_PASSWORD=<app-password>

- Gmail account with IMAP/SMTP access enabled   ```

- App-specific password for Gmail (recommended)

   Optional variables:

### Installation   ```

   DEFAULT_TO (DEFAULT_TEST_TO) — default recipient used by the sender CLI

1. Clone the repository   SMTP_HOST (default: smtp.gmail.com)

2. Install dependencies:   SMTP_PORT (default: 587)

```bash   IMAP_POLL_SECONDS (default: 10)

pip install -r requirements.txt   ```

```

Notes for Gmail

3. Create a `.env` file with your credentials:- Use an app password (Google account -> Security -> App passwords) for EMAIL_PASSWORD.

```- Ensure IMAP access is enabled for the account.

EMAIL=your-email@gmail.com

PASSWORD=your-app-passwordUsage

```

- Send an email (CLI):

### Running a Game  ```bash

  python email_sender.py

```bash  ```

python main.py  The CLI will prompt for a recipient (press Enter to accept DEFAULT_TO), subject and a message body (end with a line containing only `.`).

```

- Send programmatically:

The system will:  ```python

1. Collect player registrations via email  from email_sender import sendemail

2. Assign roles based on player count  sendemail("recipient@example.com", "Subject", "Message body")

3. Run through alternating night and day phases  ```

4. Process player actions and announce results

5. Save complete game state to `gamestate.json`- Listen for incoming mail (CLI):

  ```bash

## Game Flow  python email_listener.py

  ```

### Phase Sequence  The listener will poll the inbox and print each new message as it arrives.



1. **REGISTRATION**: Players send emails to joinSecurity

2. **NIGHT0** (First Night): Players receive role information and take first night actions- Do not commit your `.env` with real credentials to version control.

3. **DAY1**: Players discuss and vote on executions- Keep app passwords secret.

4. **NIGHT1**: Night phase - certain roles take actions

5. **DAY2**: Day phase continues...Troubleshooting

6. Pattern continues until game ends (max 10 phases by default)- Authentication errors usually mean wrong credentials or missing app password.

- For Gmail, make sure IMAP is enabled and you're using an app password if 2FA is enabled.

### Actions Between Phases



Actions from one phase are applied at the start of the next phase:

- Night kills are announced at the start of the day

- Day executions take effect before the next night

- Poisoner and other special abilities process accordingly# BOTC roles

## Townsfolk

## ArchitectureWasherwoman

	Washerwoman	You start knowing that 1 of 2 players is a particular Townsfolk.

### Module StructureLibrarian

	Librarian	You start knowing that 1 of 2 players is a particular Outsider. (Or that zero are in play.)

```Investigator

├── main.py                 # Entry point - initializes and starts game	Investigator	You start knowing that 1 of 2 players is a particular Minion.

├── config.py              # Configuration constants and role definitionsChef

├── models.py              # Core data models (Player, GameStateManager)	Chef	You start knowing how many pairs of evil players there are.

├── email_service.py       # Email I/O (IMAP/SMTP handling)Empath

├── role_manager.py        # Role assignment logic	Empath	Each night, you learn how many of your 2 alive neighbors are evil.

├── phase_handlers.py      # Phase-specific game logicFortune Teller

├── game_flow.py          # Game orchestration and phase management	Fortune Teller	Each night, choose 2 players: you learn if either is a Demon. There is a good player that registers as a Demon to you.

├── player_setup.py       # Player creation utilitiesUndertaker

└── gamestate.json        # Persistent game state (auto-generated)	Undertaker	Each night*, you learn which character died by execution today.

```Monk

	Monk	Each night*, choose a player (not yourself): they are safe from the Demon tonight.

### Key ClassesRavenkeeper

	Ravenkeeper	If you die at night, you are woken to choose a player: you learn their character.

- **GameStateManager**: Manages game state, applies actions, tracks player statusVirgin

- **GameOrchestrator**: Controls phase flow and action application	Virgin	The 1st time you are nominated, if the nominator is a Townsfolk, they are executed immediately.

- **PhaseHandler** (base class): Abstract handler for phase logicSlayer

  - **RegistrationHandler**: Collects players	Slayer	Once per game, during the day, publicly choose a player: if they are the Demon, they die.

  - **FirstNightHandler**: Sends role info and handles first nightSoldier

  - **DayPhaseHandler**: Manages voting and executions	Soldier	You are safe from the Demon.

  - **NightPhaseHandler**: Processes night actionsMayor

- **EmailComposer**: Constructs phase-specific emails	Mayor	If only 3 players live & no execution occurs, your team wins. If you die at night, another player might die instead.

- **IMAPService**: Fetches and processes incoming emails

- **ResponseCollector**: Waits for and collects player responses## 	OUTSIDERS	

Butler

### State Management	Butler	Each night, choose a player (not yourself): tomorrow, you may only vote if they are voting too.

Drunk

All game state is saved to `gamestate.json` with:	Drunk	You do not know you are the Drunk. You think you are a Townsfolk character, but you are not.

- Player list (name, email, role, alive status)Recluse

- Phase history with timestamps	Recluse	You might register as evil & as a Minion or Demon, even if dead.

- Recorded actions (kills, votes, etc.)Saint

- Announcements for each phase	Saint	If you die by execution, your team loses.

- Snapshots before and after each phase

##	MINIONS	

## RolesPoisoner

	Poisoner	Each night, choose a player: they are poisoned tonight and tomorrow day.

### Townsfolk (Blue Team)Spy

- **Washerwoman**: Learns 2 players and 1 of their roles (one is correct)	Spy	Each night, you see the Grimoire. You might register as good & as a Townsfolk or Outsider, even if dead.

- **Librarian**: Learns 2 players and an outsider role (one might be)Scarlet Woman

- **Investigator**: Learns 2 players and a minion role (one might be)	Scarlet Woman	If there are 5 or more players alive & the Demon dies, you become the Demon. (Travellers don't count.)

- **Chef**: Learns how many pairs of evil players sit adjacentBaron

- **Empath**: Learns how many living neighbors are evil	Baron	There are extra Outsiders in play. [+2 Outsiders]

- **Fortune Teller**: Each night, choose 2 players - learn if either is the demon

- **Undertaker**: Each night, learn which role died by execution today##	DEMONS	

- **Monk**: Each night, protect a player from the demonImp

- **Ravenkeeper**: If you die at night, choose a player and learn their role	Imp	Each night*, choose a player: they die. If you kill yourself this way, a Minion becomes the Imp.

- **Virgin**: First time you are nominated, if nominator is townsfolk, they are executed

- **Slayer**: Once per game, choose a player in day - if demon, they die

- **Soldier**: You are immune to demon kills## Number of each role 

- **Mayor**: If only 3 players alive and no execution, your team winsnumber of players; number of townsfolk, number of outsiders, number of minions, number of demons 

- 2; 1,0,0,1

### Outsiders (Blue Team)- 3; 2,0,0,1

- **Butler**: Each night, choose a player - you can only vote if they vote- 4; 3,0,0,1

- **Drunk**: You think you are a townsfolk, but you're not (learn wrong info)- 5; 3,0,1,1

- **Recluse**: You might register as evil or as minion/demon- 6; 3,1,1,1

- **Saint**: If you die by execution, your team loses- 7; 5,0,1,1

- 8; 5,1,1,1

### Minions (Red Team)- 9; 5,2,1,1

- **Poisoner**: Each night, poison a player (their ability malfunctions)- 10; 7,0,2,1

- **Spy**: Each night, see grimoire. Might register as good or townsfolk/outsider- 11; 7,1,2,1

- **Scarlet Woman**: If demon dies, you become demon (unless 5+ players alive)- 12; 7,2,2,1

- **Baron**: There are extra outsiders in play (modifies setup)- 13; 9,0,3,1

- 14; 9,1,3,1

### Demons (Red Team)- 15; 9,2,3,1
- **Imp**: Each night, kill a player. If you kill yourself, minion becomes Imp

## Email Protocol

### Player Registration
Send email with subject: `BOTC-REGISTRATION`

### Player Responses
- **First Night**: Players respond with actions (e.g., "I choose Alice")
- **Day Phase**: Players submit nominations/votes (e.g., "I nominate Bob" or "Yes")
- **Night Phase**: Active roles submit their night actions

All responses should reply to the phase email or use the phase name in the subject.

## Configuration

### Environment Variables (`.env`)
```
EMAIL=your-storyteller-email@gmail.com
PASSWORD=your-app-specific-password
```

### Constants (`config.py`)
- `MAX_PHASES`: Maximum number of phases (default: 10)
- `WAIT_TIME_SECONDS`: How long to wait for responses (default: 300)
- Role lists: Customize available roles for your game

### Role Distribution
Roles are assigned based on player count following standard BOTC rules:
- 5 players: 3 Townsfolk, 0 Outsiders, 1 Minion, 1 Demon
- 6 players: 3 Townsfolk, 1 Outsider, 1 Minion, 1 Demon
- 7 players: 5 Townsfolk, 0 Outsiders, 1 Minion, 1 Demon
- And so on...

## Development

### Adding New Roles
1. Add role to appropriate list in `config.py`
2. Add role description in `FirstNightHandler` if it has first night info
3. Add action handling in appropriate phase handler
4. Update role distribution in `ROLE_DISTRIBUTION` dict

### Adding New Phases
1. Create a new handler class inheriting from `PhaseHandler`
2. Implement the `run()` method
3. Add phase logic to `GameOrchestrator.run_game_phases()`

### Debug Mode
The system includes console logging for tracking phase transitions and action processing. Check terminal output for detailed flow information.

## Troubleshooting

### Common Issues

**Players not receiving emails:**
- Check SMTP settings and credentials
- Verify Gmail allows less secure apps or use app-specific password
- Check spam folders

**Actions not applying:**
- Verify phase names follow NIGHT0/DAY1/NIGHT1/DAY2 pattern
- Check `gamestate.json` for recorded actions
- Review console output for action processing logs

**Role assignment errors:**
- Ensure enough players for configured roles
- Check `ROLE_DISTRIBUTION` mapping in `config.py`

## Files Generated

- `gamestate.json`: Complete game state, saved after each phase
- `.env`: Your email credentials (not tracked in git)

## Security Notes

- Never commit `.env` file
- Use app-specific passwords for email
- Consider rate limits on email sending
- Review Gmail security settings

## Credits

Based on the social deduction game **Blood on the Clocktower** by The Pandemonium Institute.

## License

This is a personal automation tool for running BOTC games. Game rules and roles are property of The Pandemonium Institute.
