"""Email services for IMAP and SMTP operations."""
import os
import imaplib
import email
import time
import re
from typing import List, Dict, Optional
from email.header import decode_header
from email.utils import parseaddr

from email_sender import sendemail
from config import IMAP_POLL_INTERVAL


class IMAPService:
    """Service for handling IMAP email operations."""

    def __init__(self):
        self.connection = None

    def connect(self) -> imaplib.IMAP4_SSL:
        """Connect to IMAP using env vars. Raises SystemExit if not configured."""
        host = os.getenv("IMAP_HOST") or os.getenv("IMAP_SERVER")
        user = (
            os.getenv("IMAP_USER")
            or os.getenv("IMAP_USERNAME")
            or os.getenv("IMAP_EMAIL")
            or os.getenv("EMAIL_ADDRESS")
        )
        password = (
            os.getenv("IMAP_PASS")
            or os.getenv("IMAP_PASSWORD")
            or os.getenv("IMAP_PWD")
            or os.getenv("EMAIL_PASSWORD")
        )
        port = int(os.getenv("IMAP_PORT") or os.getenv("IMAP_SSL_PORT") or "993")

        if not (host and user and password):
            raise SystemExit(
                "IMAP configuration missing. Set IMAP_SERVER (or IMAP_HOST), "
                "and provide credentials via IMAP_USER/IMAP_PASS or "
                "EMAIL_ADDRESS/EMAIL_PASSWORD environment variables."
            )

        try:
            imap = imaplib.IMAP4_SSL(host, port)
            imap.login(user, password)
            self.connection = imap
            return imap
        except Exception as exc:
            raise SystemExit(f"IMAP connection failed: {exc}")

    def fetch_unseen_messages(self, imap: imaplib.IMAP4_SSL) -> List[Dict]:
        """
        Return list of dicts: {'uid', 'from', 'subject', 'body'} 
        for unseen messages using UID-based operations.
        """
        msgs = []
        try:
            imap.select("INBOX")
            status, data = imap.uid('search', None, 'UNSEEN')
            
            if status != "OK" or not data or not data[0]:
                return msgs

            for uid_bytes in data[0].split():
                uid = uid_bytes.decode() if isinstance(uid_bytes, bytes) else str(uid_bytes)
                status, fetch_data = imap.uid('fetch', uid, '(RFC822)')
                
                if status != "OK" or not fetch_data:
                    continue

                raw = fetch_data[0][1]
                if not raw:
                    continue

                msg = email.message_from_bytes(raw)
                from_addr = parseaddr(self._decode_header(msg.get("From")))[1]
                subject = self._decode_header(msg.get("Subject"))
                body = self._extract_body(msg)

                msgs.append({
                    "uid": uid,
                    "from": from_addr,
                    "subject": subject,
                    "body": body
                })
        except Exception as exc:
            print(f"Error fetching messages: {exc}")

        return msgs

    def mark_seen(self, imap: imaplib.IMAP4_SSL, uid: str) -> None:
        """Mark a message as seen by UID."""
        try:
            imap.uid('store', uid, '+FLAGS', '(\\Seen)')
        except Exception:
            pass

    def close(self, imap: Optional[imaplib.IMAP4_SSL] = None) -> None:
        """Close IMAP connection."""
        connection = imap or self.connection
        if connection:
            try:
                connection.logout()
            except Exception:
                pass

    @staticmethod
    def _decode_header(value: Optional[str]) -> str:
        """Decode a possibly MIME-encoded header value to a unicode string."""
        if value is None:
            return ""

        parts = decode_header(value)
        decoded = ""
        for part, enc in parts:
            if isinstance(part, bytes):
                decoded += part.decode(enc or "utf-8", errors="replace")
            else:
                decoded += part
        return decoded

    @staticmethod
    def _extract_body(msg: email.message.Message) -> str:
        """Extract plain text body from email message."""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = str(part.get("Content-Disposition") or "")
                
                if ctype == "text/plain" and "attachment" not in disp:
                    payload = part.get_payload(decode=True)
                    if payload is None:
                        continue
                    
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        body = payload.decode(charset, errors="replace")
                    except Exception:
                        body = payload.decode("utf-8", errors="replace")
                    break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                try:
                    body = payload.decode(charset, errors="replace")
                except Exception:
                    body = payload.decode("utf-8", errors="replace")

        return body

    @staticmethod
    def normalize_subject(subject: Optional[str]) -> str:
        """Normalize subject by stripping common reply/forward prefixes."""
        if not subject:
            return ""
        
        s = subject.strip()
        prefix_re = re.compile(r'^(?:\s*(?:re|fw|fwd)\s*[:\-]\s*)+', flags=re.IGNORECASE)
        s = prefix_re.sub("", s).strip()
        return s.lower()


class EmailComposer:
    """Service for composing and sending emails."""

    @staticmethod
    def send_email(to_email: str, subject: str, body: str) -> None:
        """Send an email using the configured SMTP service."""
        sendemail(to_email, subject, body)

    @staticmethod
    def build_player_list(players: List) -> str:
        """Build a formatted string of players with their status."""
        return "\n".join(
            f"{p.number}: {p.name}{' (dead)' if not p.alive else ''}"
            for p in players
        )

    @staticmethod
    def get_first_non_empty_line(text: str) -> str:
        """Extract the first non-empty line from text."""
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                return stripped
        return ""


class ResponseCollector:
    """Service for collecting player responses via email."""

    def __init__(self, imap_service: IMAPService):
        self.imap_service = imap_service

    def wait_for_responses(
        self,
        imap: imaplib.IMAP4_SSL,
        expected_subjects: Dict[str, str],
        waiting_players: set,
        callback
    ) -> None:
        """
        Wait for responses from players.
        
        Args:
            imap: IMAP connection
            expected_subjects: Map of player_id -> expected subject
            waiting_players: Set of player IDs still waiting for response
            callback: Function to call for each message, signature:
                     callback(player_id, player, message, uid) -> bool
                     Return True to remove from waiting list
        """
        expected_map = {
            self.imap_service.normalize_subject(s): pid
            for pid, s in expected_subjects.items()
        }
        
        last_waiting_count = None

        while waiting_players:
            if last_waiting_count != len(waiting_players):
                print(f"Waiting for {len(waiting_players)} responses.")
                last_waiting_count = len(waiting_players)

            msgs = self.imap_service.fetch_unseen_messages(imap)
            if not msgs:
                time.sleep(IMAP_POLL_INTERVAL)
                continue

            for m in msgs:
                uid = m["uid"]
                from_addr = (m["from"] or "").strip()
                subj = m["subject"] or ""
                body = m["body"] or ""

                player_key = expected_map.get(self.imap_service.normalize_subject(subj))
                if not player_key:
                    self.imap_service.mark_seen(imap, uid)
                    continue

                # Call the callback with the message data
                should_remove = callback(player_key, from_addr, body, subj, uid)
                
                if should_remove:
                    waiting_players.discard(player_key)

                self.imap_service.mark_seen(imap, uid)
