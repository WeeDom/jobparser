from imapclient import IMAPClient


class EmailClient(IMAPClient):
    def fetch(self):
        if not self.server:
            self._connect()

        self._fetch()

    def connect(self):
        self._connect()
        return self
