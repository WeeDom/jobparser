from dotenv import load_dotenv
import os
from models import EmailClient

load_dotenv()

CLIENT_ID = os.getenv("MS_CLIENTID")
IMAP_HOST = os.getenv("GMAIL_SERVER", "imap.gmail.com")
IMAP_USERNAME = os.getenv("GMAIL_USERNAME")
IMAP_PASSWORD = os.getenv("GMAIL_PASSWORD")


class IMAPGmailClient(EmailClient):
    def __init__(self):
        super().__init__(IMAP_HOST, use_uid=True)

    def _connect(self):
        self.login(IMAP_USERNAME, IMAP_PASSWORD)

    def fetch_job_emails(self, search_criteria=None):
        """Fetch unread messages that are likely to contain job data."""
        import pdb; pdb.set_trace() # noqa E702
        self.ensure_authenticated()
        self.select_folder("jobparser")
        criteria = search_criteria or ["FROM", "Indeed"]
        message_ids = self.search(criteria)

        if not message_ids:
            print("no messages found")
            return {}

        return self.fetch(
            message_ids,
            [
                "ENVELOPE",
                "BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)]",
                "BODY.PEEK[TEXT]",
            ],
        )
