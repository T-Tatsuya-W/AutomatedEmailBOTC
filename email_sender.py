#!/usr/bin/env python3
"""Small email sender utility.

Provides:
- sendemail(to, subject, message): sends an email using credentials from .env
- CLI for quick manual use
"""
import os
import sys
import getpass
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
DEFAULT_SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
# Add a default test recipient: read DEFAULT_TO from .env or fall back to the sender address (if set)
DEFAULT_TEST_TO = os.getenv("DEFAULT_TO") or os.getenv("TO_EMAIL_ADDRESS") or "tobytw312@gmail.com"

def _get_credentials():
    """Return (email_address, password) from env or prompt the user."""
    addr = os.getenv("EMAIL_ADDRESS")
    pwd = os.getenv("EMAIL_PASSWORD")
    if not addr:
        addr = input("Email address (FROM): ").strip()
    if not pwd:
        pwd = getpass.getpass("Email password (app password): ").strip()
    return addr, pwd

def sendemail(to, subject, message, from_addr=None, password=None,
              smtp_host=DEFAULT_SMTP_HOST, smtp_port=DEFAULT_SMTP_PORT, timeout=30):
    """
    Send a plain-text email.
    - to: recipient email address (string)
    - subject: email subject (string)
    - message: email body (string)
    Optional: from_addr/password to override .env values.
    Raises smtplib.SMTPException on failure.
    """
    if not from_addr or not password:
        from_addr, password = _get_credentials()

    msg = MIMEText(message or "", _subtype="plain", _charset="utf-8")
    msg["From"] = from_addr
    msg["To"] = to
    msg["Subject"] = subject or ""

    with smtplib.SMTP(smtp_host, smtp_port, timeout=timeout) as smtp:
        smtp.ehlo()
        # use STARTTLS if port indicates it (587) or user configured
        try:
            smtp.starttls()
            smtp.ehlo()
        except Exception:
            # if server doesn't support STARTTLS, proceed (will likely fail auth on modern servers)
            pass
        smtp.login(from_addr, password)
        smtp.send_message(msg)

    return True

def _cli():
    from_addr_env = os.getenv("EMAIL_ADDRESS")
    print("Simple email sender")
    # show default and allow Enter to accept it
    to_prompt = f"Send to (email address) [{DEFAULT_TEST_TO}]: "
    to = input(to_prompt).strip() or DEFAULT_TEST_TO
    subject = input("Subject: ").strip()
    print("Enter message body. End with a line containing only '.'")
    lines = []
    while True:
        line = sys.stdin.readline()
        if not line or line.rstrip("\n") == ".":
            break
        lines.append(line)
    body = "".join(lines).rstrip("\n")
    try:
        sendemail(to, subject, body)
        print("Email sent.")
    except Exception as e:
        print("Failed to send email:", e)

if __name__ == "__main__":
    _cli()

