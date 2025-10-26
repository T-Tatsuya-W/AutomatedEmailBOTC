import os
import time
import sys
import getpass
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
DEFAULT_POLL_SECONDS = int(os.getenv("IMAP_POLL_SECONDS") or 10)

def prompt_for_missing_credentials():
    global EMAIL_ADDRESS, EMAIL_PASSWORD
    if not EMAIL_ADDRESS:
        EMAIL_ADDRESS = input("Email address (IMAP user): ").strip()
    if not EMAIL_PASSWORD:
        EMAIL_PASSWORD = getpass.getpass("Email password (app password): ").strip()

def _decode_subject(raw_subject):
    parts = decode_header(raw_subject or "")
    out = []
    for s, enc in parts:
        if isinstance(s, bytes):
            out.append(s.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(s)
    return "".join(out)

def get_text_from_msg(msg):
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get("Content-Disposition") or "")
            if ctype == "text/plain" and "attachment" not in cdispo:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
        return ""
    else:
        payload = msg.get_payload(decode=True)
        return payload.decode(msg.get_content_charset() or "utf-8", errors="replace") if payload else ""

def listen_for_emails(imap_user, imap_password, poll_interval=DEFAULT_POLL_SECONDS):
    def _connect():
        imap_conn = imaplib.IMAP4_SSL("imap.gmail.com")
        imap_conn.login(imap_user, imap_password)
        imap_conn.select("INBOX")
        return imap_conn

    imap = None
    try:
        imap = _connect()
        print(f"Listening for new mail as {imap_user} (poll every {poll_interval}s). Ctrl+C to stop.")
        while True:
            # keep connection alive / refresh server state
            try:
                imap.noop()
            except Exception:
                # try to reconnect if noop fails
                try:
                    if imap is not None:
                        imap.logout()
                except Exception:
                    pass
                try:
                    imap = _connect()
                except Exception as e:
                    print("Reconnect failed:", e)
                    time.sleep(poll_interval)
                    continue

            # use UID search for stability
            try:
                typ, data = imap.uid('search', None, 'UNSEEN')
            except Exception as e:
                print("IMAP search error, attempting reconnect:", e)
                try:
                    imap.logout()
                except Exception:
                    pass
                try:
                    imap = _connect()
                except Exception as e2:
                    print("Reconnect failed:", e2)
                    time.sleep(poll_interval)
                    continue
                time.sleep(poll_interval)
                continue

            if typ == "OK" and data and data[0]:
                uids = data[0].split()
                for uid in uids:
                    try:
                        typ, msg_data = imap.uid('fetch', uid, '(RFC822)')
                    except Exception as e:
                        print("Fetch failed for UID", uid, ":", e)
                        continue
                    if typ != "OK" or not msg_data:
                        continue
                    raw = msg_data[0][1]
                    if not raw:
                        continue
                    msg = email.message_from_bytes(raw)
                    sender = email.utils.parseaddr(msg.get("From"))[1]
                    subject = _decode_subject(msg.get("Subject"))
                    body = get_text_from_msg(msg)
                    print("="*60)
                    print("From:   ", sender)
                    print("Subject:", subject)
                    print("Body:\n" + (body or "(empty)"))
                    print("="*60)
                    # mark seen via UID
                    try:
                        imap.uid('store', uid, '+FLAGS', '(\\Seen)')
                    except Exception:
                        pass
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("\nStopping listener (keyboard interrupt).")
    except imaplib.IMAP4.error as e:
        print("IMAP error:", e)
    except Exception as e:
        print("Listener error:", e)
    finally:
        try:
            if imap is not None:
                imap.logout()
        except Exception:
            pass

def main():
    prompt_for_missing_credentials()
    listen_for_emails(EMAIL_ADDRESS, EMAIL_PASSWORD, DEFAULT_POLL_SECONDS)

if __name__ == "__main__":
    main()
