import os
import smtplib
import time
import random
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
CLIENT_SECRET_FILE = 'client_secret.json'  # OAuth 2.0 credentials
TOKEN_FILE = 'token.json'                  # User token
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
SMTP_SERVERS = [
    'smtp.gmail.com',  # Primary SMTP server
    'smtp.office365.com'  # Backup SMTP server
]
PROXY_LIST = ['proxy1.example.com', 'proxy2.example.com']  # Example proxy IPs

# Initialize Gmail API
def initialize_gmail_api():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception('OAuth 2.0 credentials not found or invalid.')
    return build('gmail', 'v1', credentials=creds)

# Read Emails
def read_emails(service, label='INBOX'):
    results = service.users().messages().list(userId='me', labelIds=[label]).execute()
    messages = results.get('messages', [])
    for msg in messages:
        msg_id = msg['id']
        email = service.users().messages().get(userId='me', id=msg_id).execute()
        print(f"From: {email['payload']['headers'][16]['value']}")
        print(f"Subject: {email['payload']['headers'][17]['value']}")
        print(f"Snippet: {email['snippet']}\n")

# Send Email
def send_email(subject, body, to_email, smtp_server):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = 'your mail'
    msg['To'] = to_email
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, 587) as server:
            server.starttls()
            server.login('your mail', 'password')
            server.sendmail('your_email@example.com', [to_email], msg.as_string())
        print(f"Email sent to {to_email} using {smtp_server}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Pull Emails from Spam/Promotion
def pull_emails_from_spam(service):
    spam_results = service.users().messages().list(userId='me', labelIds=['SPAM']).execute()
    promotion_results = service.users().messages().list(userId='me', labelIds=['CATEGORY_PROMOTIONS']).execute()
    messages = spam_results.get('messages', []) + promotion_results.get('messages', [])
    for msg in messages:
        msg_id = msg['id']
        service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['SPAM', 'CATEGORY_PROMOTIONS']}).execute()
        print(f"Pulled email {msg_id} from spam/promotion.")

# Rotate IP and SMTP Server
def rotate_ip_and_smtp():
    smtp_server = random.choice(SMTP_SERVERS)
    proxy = random.choice(PROXY_LIST)
    print(f"Using SMTP server: {smtp_server} and proxy: {proxy}")
    return smtp_server

# Main Function
def main():
    service = initialize_gmail_api()

    # Read Emails
    print("Reading emails from INBOX:")
    read_emails(service)

    # Pull Emails from Spam/Promotion
    print("Pulling emails from spam/promotion:")
    pull_emails_from_spam(service)

    # Send Email
    subject = "Test Email"
    body = "This is a test email sent from the email control program."
    to_email = "to mail"
    smtp_server = rotate_ip_and_smtp()
    send_email(subject, body, to_email, smtp_server)

if __name__ == '__main__':
    main()