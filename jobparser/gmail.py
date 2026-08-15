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

    def fetch(self):
        if not self.server:
            self._connect()
