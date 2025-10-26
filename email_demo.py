#!/usr/bin/env python3
"""
Simple Email Demo Script
This script demonstrates sending and receiving emails using Python.
It logs email contents and sender addresses.
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import sys
import time


class EmailDemo:
    """A simple class to demonstrate sending and receiving emails."""
    
    def __init__(self, email_address, password, smtp_server, smtp_port, imap_server):
        """
        Initialize the email demo with credentials and server settings.
        
        Args:
            email_address: Email address for sending/receiving
            password: Email password or app-specific password
            smtp_server: SMTP server address (e.g., smtp.gmail.com)
            smtp_port: SMTP port (usually 587 for TLS)
            imap_server: IMAP server address (e.g., imap.gmail.com)
        """
        self.email_address = email_address
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        
    def send_email(self, to_address, subject, body):
        """
        Send an email to the specified address.
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            body: Email body text
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_address
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server and send email
            print(f"[{datetime.now()}] Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable TLS encryption
            
            print(f"[{datetime.now()}] Logging in as {self.email_address}")
            server.login(self.email_address, self.password)
            
            print(f"[{datetime.now()}] Sending email to {to_address}")
            text = msg.as_string()
            server.sendmail(self.email_address, to_address, text)
            server.quit()
            
            print(f"[{datetime.now()}] ✓ Email sent successfully!")
            print(f"  From: {self.email_address}")
            print(f"  To: {to_address}")
            print(f"  Subject: {subject}")
            print(f"  Body: {body[:100]}..." if len(body) > 100 else f"  Body: {body}")
            print("-" * 80)
            
            return True
            
        except Exception as e:
            print(f"[{datetime.now()}] ✗ Error sending email: {str(e)}")
            return False
    
    def receive_emails(self, mailbox='INBOX', max_emails=10, mark_as_read=False):
        """
        Receive and log emails from the specified mailbox.
        
        Args:
            mailbox: Mailbox to check (default: 'INBOX')
            max_emails: Maximum number of emails to retrieve
            mark_as_read: Whether to mark emails as read
            
        Returns:
            list: List of email data dictionaries
        """
        emails_data = []
        
        try:
            # Connect to IMAP server
            print(f"[{datetime.now()}] Connecting to IMAP server: {self.imap_server}")
            mail = imaplib.IMAP4_SSL(self.imap_server)
            
            print(f"[{datetime.now()}] Logging in as {self.email_address}")
            mail.login(self.email_address, self.password)
            
            # Select mailbox
            print(f"[{datetime.now()}] Selecting mailbox: {mailbox}")
            mail.select(mailbox)
            
            # Search for emails (get all unseen emails)
            status, message_ids = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                print(f"[{datetime.now()}] No emails found or error searching mailbox")
                mail.logout()
                return emails_data
            
            # Get list of email IDs
            email_ids = message_ids[0].split()
            
            if not email_ids:
                print(f"[{datetime.now()}] No new (unseen) emails found in {mailbox}")
                mail.logout()
                return emails_data
            
            print(f"[{datetime.now()}] Found {len(email_ids)} new email(s)")
            print("=" * 80)
            
            # Fetch emails (limit to max_emails)
            for i, email_id in enumerate(email_ids[-max_emails:], 1):
                try:
                    # Fetch email data
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        print(f"[{datetime.now()}] Error fetching email {email_id}")
                        continue
                    
                    # Parse email
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            # Extract email details
                            from_address = msg.get('From', 'Unknown')
                            subject = msg.get('Subject', 'No Subject')
                            date = msg.get('Date', 'Unknown Date')
                            
                            # Get email body
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        try:
                                            body = part.get_payload(decode=True).decode()
                                            break
                                        except:
                                            pass
                            else:
                                try:
                                    body = msg.get_payload(decode=True).decode()
                                except:
                                    body = msg.get_payload()
                            
                            # Log email details
                            print(f"\n[{datetime.now()}] Email #{i}")
                            print(f"  From: {from_address}")
                            print(f"  Subject: {subject}")
                            print(f"  Date: {date}")
                            print(f"  Body Preview: {body[:200]}..." if len(body) > 200 else f"  Body: {body}")
                            print("-" * 80)
                            
                            # Store email data
                            email_data = {
                                'from': from_address,
                                'subject': subject,
                                'date': date,
                                'body': body
                            }
                            emails_data.append(email_data)
                            
                except Exception as e:
                    print(f"[{datetime.now()}] Error processing email {email_id}: {str(e)}")
            
            # Close connection
            mail.logout()
            print(f"[{datetime.now()}] ✓ Retrieved {len(emails_data)} email(s) successfully")
            print("=" * 80)
            
        except Exception as e:
            print(f"[{datetime.now()}] ✗ Error receiving emails: {str(e)}")
        
        return emails_data


def demo_mode():
    """
    Run a demonstration mode that shows how to use the EmailDemo class.
    This mode doesn't require actual credentials.
    """
    print("=" * 80)
    print("EMAIL DEMO - DEMONSTRATION MODE")
    print("=" * 80)
    print("\nThis is a demonstration of the email functionality.")
    print("To use this script with real emails, you need to:")
    print("1. Create a .env file with your email credentials")
    print("2. Use environment variables or pass credentials directly")
    print("\nExample usage:")
    print("-" * 80)
    print("""
# Create an EmailDemo instance
demo = EmailDemo(
    email_address='your_email@example.com',
    password='your_password_or_app_password',
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    imap_server='imap.gmail.com'
)

# Send an email
demo.send_email(
    to_address='recipient@example.com',
    subject='Test Email',
    body='This is a test email from the Python email demo!'
)

# Receive emails
emails = demo.receive_emails(max_emails=5)
for email_data in emails:
    print(f"From: {email_data['from']}")
    print(f"Subject: {email_data['subject']}")
    print(f"Body: {email_data['body']}")
""")
    print("-" * 80)
    print("\n✓ Demo completed!")
    print("=" * 80)


def main():
    """Main function to run the email demo."""
    print("=" * 80)
    print("PYTHON EMAIL DEMO SCRIPT")
    print("=" * 80)
    print()
    
    # Check if credentials are provided via environment variables
    email_address = os.environ.get('EMAIL_ADDRESS')
    email_password = os.environ.get('EMAIL_PASSWORD')
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    imap_server = os.environ.get('IMAP_SERVER', 'imap.gmail.com')
    
    if not email_address or not email_password:
        print("⚠ No credentials found in environment variables.")
        print("Running in demonstration mode...\n")
        demo_mode()
        return
    
    # Create EmailDemo instance
    demo = EmailDemo(
        email_address=email_address,
        password=email_password,
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        imap_server=imap_server
    )
    
    # Interactive menu
    while True:
        print("\nWhat would you like to do?")
        print("1. Send an email")
        print("2. Receive emails")
        print("3. Send and receive (demo full workflow)")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            to_address = input("Enter recipient email address: ").strip()
            subject = input("Enter email subject: ").strip()
            body = input("Enter email body: ").strip()
            demo.send_email(to_address, subject, body)
            
        elif choice == '2':
            max_emails = input("Enter max number of emails to retrieve (default 10): ").strip()
            max_emails = int(max_emails) if max_emails else 10
            emails = demo.receive_emails(max_emails=max_emails)
            print(f"\nRetrieved {len(emails)} email(s)")
            
        elif choice == '3':
            print("\n--- FULL WORKFLOW DEMO ---")
            # Send a test email to self
            print("\n1. Sending test email to self...")
            demo.send_email(
                to_address=email_address,
                subject=f"Test Email - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                body="This is a test email sent by the Python email demo script!"
            )
            
            # Wait a bit for the email to arrive
            print("\n2. Waiting 5 seconds for email to arrive...")
            time.sleep(5)
            
            # Receive emails
            print("\n3. Checking for new emails...")
            emails = demo.receive_emails(max_emails=5)
            print(f"\n✓ Full workflow completed! Retrieved {len(emails)} email(s)")
            
        elif choice == '4':
            print("\nExiting email demo. Goodbye!")
            break
            
        else:
            print("\n⚠ Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()
