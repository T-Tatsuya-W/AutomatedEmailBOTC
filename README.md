# AutomatedEmailBOTC

A simple Python demonstration script for sending and receiving emails. This project showcases how to use Python's built-in email libraries to interact with email servers via SMTP and IMAP protocols.

## Features

- **Send Emails**: Send emails using SMTP (Simple Mail Transfer Protocol)
- **Receive Emails**: Retrieve and read emails using IMAP (Internet Message Access Protocol)
- **Logging**: Automatically logs email contents, sender addresses, subjects, and timestamps
- **Interactive Mode**: User-friendly menu for testing email operations
- **Demo Mode**: Run without credentials to see example code and usage
- **Full Workflow Demo**: Send an email to yourself and immediately receive it

## Requirements

- Python 3.6 or higher
- An email account (Gmail recommended for testing)
- No external dependencies required (uses Python's standard library)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/T-Tatsuya-W/AutomatedEmailBOTC.git
cd AutomatedEmailBOTC
```

### 2. Configure Email Credentials (Optional)

If you want to test with real emails:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your email credentials:
   ```
   EMAIL_ADDRESS=your_email@gmail.com
   EMAIL_PASSWORD=your_app_specific_password
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   IMAP_SERVER=imap.gmail.com
   ```

### 3. For Gmail Users

To use Gmail with this script:

1. Enable 2-factor authentication on your Google account
2. Generate an app-specific password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Copy the generated password
3. Use this app-specific password in your `.env` file

**Important**: Never commit your `.env` file to version control!

## Usage

### Demo Mode (No Credentials Required)

Run the script without credentials to see example code and documentation:

```bash
python3 email_demo.py
```

This will display:
- How to use the EmailDemo class
- Example code for sending and receiving emails
- Configuration instructions

### Interactive Mode (With Credentials)

If you have configured your `.env` file, load the environment variables and run:

```bash
# On Linux/Mac
export $(cat .env | xargs) && python3 email_demo.py

# On Windows (PowerShell)
Get-Content .env | ForEach-Object { $var = $_.Split('='); [Environment]::SetEnvironmentVariable($var[0], $var[1]) }
python3 email_demo.py
```

The interactive menu offers:
1. **Send an email** - Send a custom email to any address
2. **Receive emails** - Check inbox and display new emails
3. **Send and receive (demo full workflow)** - Send yourself a test email and retrieve it
4. **Exit** - Close the application

### Programmatic Usage

You can also import and use the `EmailDemo` class in your own scripts:

```python
from email_demo import EmailDemo

# Create an instance
demo = EmailDemo(
    email_address='your_email@gmail.com',
    password='your_app_password',
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    imap_server='imap.gmail.com'
)

# Send an email
demo.send_email(
    to_address='recipient@example.com',
    subject='Hello from Python!',
    body='This is a test email.'
)

# Receive emails
emails = demo.receive_emails(max_emails=10)
for email_data in emails:
    print(f"From: {email_data['from']}")
    print(f"Subject: {email_data['subject']}")
    print(f"Body: {email_data['body']}")
```

## Features Demonstrated

### Email Sending (SMTP)
- Connects to SMTP server with TLS encryption
- Authenticates with email credentials
- Sends formatted emails with subject and body
- Logs all operations with timestamps

### Email Receiving (IMAP)
- Connects to IMAP server with SSL
- Retrieves unread emails from inbox
- Parses email metadata (from, subject, date)
- Extracts plain text body content
- Logs email details with sender information

### Security Features
- Uses TLS/SSL for encrypted connections
- Supports app-specific passwords
- Credentials stored in environment variables (not hardcoded)
- `.gitignore` configured to prevent credential commits

## Example Output

```
================================================================================
PYTHON EMAIL DEMO SCRIPT
================================================================================

What would you like to do?
1. Send an email
2. Receive emails
3. Send and receive (demo full workflow)
4. Exit

Enter your choice (1-4): 3

--- FULL WORKFLOW DEMO ---

1. Sending test email to self...
[2025-10-26 14:59:42.345678] Connecting to SMTP server: smtp.gmail.com:587
[2025-10-26 14:59:42.567890] Logging in as your_email@gmail.com
[2025-10-26 14:59:42.789012] Sending email to your_email@gmail.com
[2025-10-26 14:59:43.012345] ✓ Email sent successfully!
  From: your_email@gmail.com
  To: your_email@gmail.com
  Subject: Test Email - 2025-10-26 14:59:42
  Body: This is a test email sent by the Python email demo script!
--------------------------------------------------------------------------------

2. Waiting 5 seconds for email to arrive...

3. Checking for new emails...
[2025-10-26 14:59:48.234567] Connecting to IMAP server: imap.gmail.com
[2025-10-26 14:59:48.456789] Logging in as your_email@gmail.com
[2025-10-26 14:59:48.678901] Selecting mailbox: INBOX
[2025-10-26 14:59:48.890123] Found 1 new email(s)
================================================================================

[2025-10-26 14:59:49.012345] Email #1
  From: your_email@gmail.com
  Subject: Test Email - 2025-10-26 14:59:42
  Date: Sun, 26 Oct 2025 14:59:43 +0000
  Body: This is a test email sent by the Python email demo script!
--------------------------------------------------------------------------------
[2025-10-26 14:59:49.234567] ✓ Retrieved 1 email(s) successfully
================================================================================

✓ Full workflow completed! Retrieved 1 email(s)
```

## Troubleshooting

### Gmail Authentication Errors
- Make sure 2-factor authentication is enabled
- Use an app-specific password, not your regular password
- Check that "Less secure app access" is not required (it's deprecated)

### Connection Errors
- Verify your SMTP and IMAP server addresses
- Check that your firewall allows outbound connections on ports 587 (SMTP) and 993 (IMAP)
- Ensure you have internet connectivity

### No Emails Received
- The script only retrieves UNSEEN (unread) emails
- Try marking some emails as unread or send new test emails
- Check that you're looking at the correct mailbox

## Other Email Providers

This script works with any email provider that supports SMTP and IMAP. Update the server settings in `.env`:

### Outlook/Hotmail
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
IMAP_SERVER=outlook.office365.com
```

### Yahoo Mail
```
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
IMAP_SERVER=imap.mail.yahoo.com
```

## Security Notes

- Never commit credentials to version control
- Use app-specific passwords when available
- The `.env` file is excluded via `.gitignore`
- Always use encrypted connections (TLS/SSL)

## License

This project is for educational and demonstration purposes.

## Contributing

Feel free to submit issues and enhancement requests!