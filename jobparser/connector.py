#! /usr/bin/env python

from ms import IMAPMSClient
from gmail import IMAPGmailClient


if __name__ == "__main__":
    msclient = IMAPMSClient()
    msconn = msclient.connect()

    gmailclient = IMAPGmailClient()
    gmconn = gmailclient.connect()

    gmconn.select_folder("INBOX", readonly=True)

    messages = gmconn.search("UNSEEN")
    print(f"{len(messages)} found")
    # for uid, message_data in gmconn.fetch(messages, "RFC822").items():
    #     email_message = email.message_from_bytes(message_data[b"RFC822"])
    #     print(uid, email_message.get("From"), email_message.get("Subject"))
