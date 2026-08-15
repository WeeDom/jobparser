#! /usr/bin/env python
import os
import msal
from dotenv import load_dotenv
from ms import IMAPMSClient

load_dotenv()

if __name__ == "__main__":
    msclient = IMAPMSClient()
    msclient.connect()
    print("Hello, World")

