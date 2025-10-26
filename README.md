# AutomatedEmailBOTC

Small collection of simple email utilities for testing with a Gmail account (or other SMTP/IMAP servers).

Overview
- email_sender.py — small, tidy utility that exposes a sendemail(to, subject, message) function and a minimal CLI. Reads credentials from a `.env` file or prompts for them. Uses SMTP to send plain-text messages.
- email_listener.py — simple IMAP listener that polls the inbox and prints new messages (sender, subject, body). Reads credentials from the same `.env`.

Quick start
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in this directory with at least:
   ```
   EMAIL_ADDRESS=you@example.com
   EMAIL_PASSWORD=<app-password>
   ```

   Optional variables:
   ```
   DEFAULT_TO (DEFAULT_TEST_TO) — default recipient used by the sender CLI
   SMTP_HOST (default: smtp.gmail.com)
   SMTP_PORT (default: 587)
   IMAP_POLL_SECONDS (default: 10)
   ```

Notes for Gmail
- Use an app password (Google account -> Security -> App passwords) for EMAIL_PASSWORD.
- Ensure IMAP access is enabled for the account.

Usage

- Send an email (CLI):
  ```bash
  python email_sender.py
  ```
  The CLI will prompt for a recipient (press Enter to accept DEFAULT_TO), subject and a message body (end with a line containing only `.`).

- Send programmatically:
  ```python
  from email_sender import sendemail
  sendemail("recipient@example.com", "Subject", "Message body")
  ```

- Listen for incoming mail (CLI):
  ```bash
  python email_listener.py
  ```
  The listener will poll the inbox and print each new message as it arrives.

Security
- Do not commit your `.env` with real credentials to version control.
- Keep app passwords secret.

Troubleshooting
- Authentication errors usually mean wrong credentials or missing app password.
- For Gmail, make sure IMAP is enabled and you're using an app password if 2FA is enabled.





# BOTC roles
## Townsfolk
Washerwoman
	Washerwoman	You start knowing that 1 of 2 players is a particular Townsfolk.
Librarian
	Librarian	You start knowing that 1 of 2 players is a particular Outsider. (Or that zero are in play.)
Investigator
	Investigator	You start knowing that 1 of 2 players is a particular Minion.
Chef
	Chef	You start knowing how many pairs of evil players there are.
Empath
	Empath	Each night, you learn how many of your 2 alive neighbors are evil.
Fortune Teller
	Fortune Teller	Each night, choose 2 players: you learn if either is a Demon. There is a good player that registers as a Demon to you.
Undertaker
	Undertaker	Each night*, you learn which character died by execution today.
Monk
	Monk	Each night*, choose a player (not yourself): they are safe from the Demon tonight.
Ravenkeeper
	Ravenkeeper	If you die at night, you are woken to choose a player: you learn their character.
Virgin
	Virgin	The 1st time you are nominated, if the nominator is a Townsfolk, they are executed immediately.
Slayer
	Slayer	Once per game, during the day, publicly choose a player: if they are the Demon, they die.
Soldier
	Soldier	You are safe from the Demon.
Mayor
	Mayor	If only 3 players live & no execution occurs, your team wins. If you die at night, another player might die instead.
## 	OUTSIDERS	
Butler
	Butler	Each night, choose a player (not yourself): tomorrow, you may only vote if they are voting too.
Drunk
	Drunk	You do not know you are the Drunk. You think you are a Townsfolk character, but you are not.
Recluse
	Recluse	You might register as evil & as a Minion or Demon, even if dead.
Saint
	Saint	If you die by execution, your team loses.
##	MINIONS	
Poisoner
	Poisoner	Each night, choose a player: they are poisoned tonight and tomorrow day.
Spy
	Spy	Each night, you see the Grimoire. You might register as good & as a Townsfolk or Outsider, even if dead.
Scarlet Woman
	Scarlet Woman	If there are 5 or more players alive & the Demon dies, you become the Demon. (Travellers don't count.)
Baron
	Baron	There are extra Outsiders in play. [+2 Outsiders]
##	DEMONS	
Imp
	Imp	Each night*, choose a player: they die. If you kill yourself this way, a Minion becomes the Imp.


## Number of each role 
number of players; number of townsfolk, number of outsiders, number of minions, number of demons 
- 5; 3,0,1,1
- 6; 3,1,1,1
- 7; 5,0,1,1
- 8; 5,1,1,1
- 9; 5,2,1,1
- 10; 7,0,2,1
- 11; 7,1,2,1
- 12; 7,2,2,1
- 13; 9,0,3,1
- 14; 9,1,3,1
- 15; 9,2,3,1