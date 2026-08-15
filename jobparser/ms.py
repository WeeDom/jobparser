import msal

from dotenv import load_dotenv
import os
from models import EmailClient

load_dotenv()

CLIENT_ID = os.getenv("MS_CLIENTID")
AUTHORITY = "https://login.microsoftonline.com/consumers"
SCOPES = [
    "https://outlook.office.com/IMAP.AccessAsUser.All"
]


class IMAPMSClient(EmailClient):
    def _connect(self):
        CACHE_FILE = ".msal_cache"

        cache = msal.SerializableTokenCache()

        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                cache.deserialize(f.read())

        app = msal.PublicClientApplication(
            CLIENT_ID,
            authority=AUTHORITY,
            token_cache=cache,
        )

        accounts = app.get_accounts()
        result = None

        try:
            if accounts:
                result = app.acquire_token_silent(
                    SCOPES,
                    account=accounts[0],
                )
            print("silently acquired a new refresh token")
        except Exception as e:
            print(e)

        if not result:
            flow = app.initiate_device_flow(scopes=SCOPES)

            print(flow["message"])

            result = app.acquire_token_by_device_flow(flow)

        if cache.has_state_changed:
            with open(CACHE_FILE, "w") as f:
                f.write(cache.serialize())
