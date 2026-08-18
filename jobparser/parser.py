#! /usr/bin/env python

import json


class jobParser():
    def find_jobs(self, emails):
        print(emails)


if __name__ == "__main__":
    with open("emails.txt", encoding="utf-8") as em:
        emails = json.load(em)
        parser = jobParser()
        parser.find_jobs(em)
