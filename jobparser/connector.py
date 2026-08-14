#! /usr/bin/env python

import email
from imapclient import IMAPClient
from dotenv import load_dotenv
import os

load_dotenv()

server = IMAPClient("imap.gmail.com", use_uid=True)
server.login(os.getenv("GMAIL_USERNAME"), os.getenv('GMAIL_PASSWORD'))
server.select_folder("INBOX", readonly=True)

messages = server.search("UNSEEN")
for uid, message_data in server.fetch(messages, "RFC822").items():
    email_message = email.message_from_bytes(message_data[b"RFC822"])
    print(uid, email_message.get("From"), email_message.get("Subject"))
