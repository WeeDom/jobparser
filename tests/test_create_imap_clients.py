import pytest
from unittest.mock import patch
from ms import IMAPMSClient
from gmail import IMAPGmailClient
from models import IMAPClient


MS_SERVER_ADDRESS = "outlook.office365.com"
GMAIL_SERVER_ADDRESS = "imap.gmail.com"

def test_create_msclient(create_msclient):

    with patch("models.IMAPClient.__init__", return_value=None) as init:
        IMAPMSClient()

    init.assert_called_once_with(MS_SERVER_ADDRESS, use_uid=True)


def test_create_gmail_client(create_msclient):

    with patch("models.IMAPClient.__init__", return_value=None) as init:
        IMAPGmailClient()

    init.assert_called_once_with(GMAIL_SERVER_ADDRESS, use_uid=True)


def test_fetch_authenticates_and_preserves_imapclient_api():
    with patch("models.IMAPClient.__init__", return_value=None):
        client = IMAPGmailClient()

    with (
        patch.object(client, "_connect") as connect,
        patch.object(IMAPClient, "fetch", return_value={1: {}}) as fetch,
    ):
        result = client.fetch([1], ["ENVELOPE"])

    connect.assert_called_once_with()
    fetch.assert_called_once_with([1], ["ENVELOPE"], None)
    assert result == {1: {}}


def test_fetch_job_emails_searches_before_fetching():
    with patch("models.IMAPClient.__init__", return_value=None):
        client = IMAPGmailClient()
    client._authenticated = True

    with (
        patch.object(client, "search", return_value=[12, 15]) as search,
        patch.object(client, "fetch", return_value={12: {}, 15: {}}) as fetch,
    ):
        result = client.fetch_job_emails()

    search.assert_called_once_with(["UNSEEN", "FROM", "Indeed"])
    fetch.assert_called_once_with(
        [12, 15],
        [
            "ENVELOPE",
            "BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)]",
            "BODY.PEEK[TEXT]",
        ],
    )
    assert result == {12: {}, 15: {}}
