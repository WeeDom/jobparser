import pytest
from unittest.mock import patch
from ms import IMAPMSClient
from gmail import IMAPGmailClient


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
