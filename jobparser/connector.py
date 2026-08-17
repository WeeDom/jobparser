#! /usr/bin/env python

from gmail import IMAPGmailClient


if __name__ == "__main__":
    # msclient = IMAPMSClient()
    # msconn = msclient.connect()

    gmailclient = IMAPGmailClient()
    gmconn = gmailclient.connect()

    gmconn.select_folder("jobparser", readonly=True)

    # gmconn.idle()
    # try:
        # changes = gmconn.idle_check(timeout=10)
    # finally:
        # gmconn.idle_done()
    changes = 1
    if changes:
        print("found changes")
        for msgid, data in gmconn.fetch_job_emails().items():
            envelope = data[b"ENVELOPE"]
            print(msgid, envelope.from_, envelope.subject)
    else:
        print("found no changes")
    print("those were all the messages")
