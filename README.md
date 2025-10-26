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