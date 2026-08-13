# jobparser

Read emails from IMAP accounts, find likely job adverts, and score whether they are worth applying to against a supplied CV.

## Usage

```python
import os

from jobparser import IMAPAccount, JobAdvertParser

parser = JobAdvertParser.from_cv_file("cv.txt")
credential = os.environ["IMAP_PASSWORD"]
account = IMAPAccount("imap.example.com", "me@example.com", credential)

matches = parser.process_account(account, unseen_only=True, limit=25)
for match in matches:
    print(match.email.subject, match.score, match.worth_applying)
```

The implementation uses Python's standard library to:

- connect to IMAP mailboxes
- parse plain text or HTML email bodies
- detect likely job adverts from email content
- compare advert keywords with CV keywords to estimate relevance
