from flask import Flask, jsonify
import os
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

app = Flask(__name__)


# ---------- Gmail connection ----------
def get_gmail_service():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


# ---------- Extract sender ----------
def extract_sender(headers):
    sender = "Unknown"

    for h in headers:
        if h.get("name", "").lower() == "from":
            sender = h.get("value", "")

    # clean "Name <email>"
    match = re.search(r"<(.+?)>", sender)
    if match:
        sender = match.group(1)

    return sender


# ---------- API ----------
@app.route('/emails')
def get_emails():
    service = get_gmail_service()

    results = service.users().messages().list(
        userId='me',
        maxResults=15   # ⚡ keep small for speed
    ).execute()

    messages = results.get('messages', [])
    email_list = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',   # ⚡ FASTEST
            metadataHeaders=['Subject', 'From']
        ).execute()

        headers = msg_data.get("payload", {}).get("headers", [])

        subject = "No Subject"
        for h in headers:
            if h["name"].lower() == "subject":
                subject = h["value"]

        sender = extract_sender(headers)
        snippet = msg_data.get("snippet", "")

        email_list.append({
            "sender": sender,
            "subject": subject,
            "snippet": snippet
        })

    return jsonify(email_list)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
