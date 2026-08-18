#! /usr/bin/env python

from gmail import IMAPGmailClient
import sys
import json


jobsites = [
    "Indeed"
        ]

if __name__ == "__main__":
    # msclient = IMAPMSClient()
    # msconn = msclient.connect()

    gmailclient = IMAPGmailClient()
    gmconn = gmailclient.connect()

    gmconn.select_folder("jobparser", readonly=True)

    # these commented out lines should force a fresh connection.
    # commented out because it's a bit slow for testing
    # gmconn.idle()
    # try:
    # changes = gmconn.idle_check(timeout=10)
    # finally:
    # gmconn.idle_done()
    changes = 1
    if changes:
        emails = {}
        for msgid, data in gmconn.fetch_job_emails(["OR", "FROM", "Indeed",
                                                    "SUBJECT", "FW"]).items():
            envelope = data[b"ENVELOPE"]
            body = data[b"BODY[TEXT]"]
            emails[str(msgid)] =  {
                    "from": str(envelope.from_),
                    "subject": envelope.subject.decode(errors="ignore"),
                    "body": body.decode(errors="ignore")
            }

        with open("emails.txt", "w") as op:
            json.dump(emails, op, indent=4)
    else:
        print("found no changes")
    print("those were all the messages")
