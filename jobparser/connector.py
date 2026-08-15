#! /usr/bin/env python

from ms import IMAPMSClient

if __name__ == "__main__":
    msclient = IMAPMSClient()
    conn = msclient.connect()
