from imapclient import IMAPClient


class EmailClient(IMAPClient):
    def __init__(self, *args, **kwargs):
        self._authenticated = False
        super().__init__(*args, **kwargs)

    def ensure_authenticated(self):
        if not self._authenticated:
            self._connect()
            self._authenticated = True

    def connect(self):
        self.ensure_authenticated()
        return self

    def fetch(self, messages, data, modifiers=None):
        self.ensure_authenticated()
        import pdb; pdb.set_trace() # noqa E702
        return super().fetch(messages, data, modifiers)
