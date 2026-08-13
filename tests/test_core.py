import unittest
from email.message import EmailMessage
from unittest.mock import patch

from jobparser import IMAPAccount, JobAdvertParser


def build_email(subject: str, body: str, *, sender: str = "jobs@example.com", html: bool = False) -> bytes:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    if html:
        message.set_content(f"<html><body><p>{body}</p></body></html>", subtype="html")
    else:
        message.set_content(body)
    return message.as_bytes()


class FakeIMAPClient:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.logged_in = False
        self.selected_mailbox = None
        self.logged_out = False
        self.messages = {
            "1": build_email(
                "Python Developer role",
                "We are hiring a Python developer with Django and API experience.",
            ),
            "2": build_email(
                "Weekly newsletter",
                "This is a digest of community links.",
            ),
        }

    def login(self, username: str, password: str) -> tuple[str, list[bytes]]:
        self.logged_in = True
        return "OK", [b"logged in"]

    def select(self, mailbox: str) -> tuple[str, list[bytes]]:
        self.selected_mailbox = mailbox
        return "OK", [b"2"]

    def search(self, charset, criterion: str) -> tuple[str, list[bytes]]:
        self.last_search = criterion
        return "OK", [b"1 2"]

    def fetch(self, message_id: str, query: str):
        return "OK", [(b"RFC822", self.messages[message_id])]

    def logout(self) -> tuple[str, list[bytes]]:
        self.logged_out = True
        return "BYE", [b"logout"]


class JobAdvertParserTests(unittest.TestCase):
    def test_parse_message_prefers_html_when_plain_text_is_missing(self) -> None:
        raw_message = build_email("Backend opportunity", "Great role for Python and Flask engineers.", html=True)

        parser = JobAdvertParser("Python Flask")
        parsed = parser.parse_message(raw_message, uid="abc")

        self.assertEqual(parsed.uid, "abc")
        self.assertEqual(parsed.subject, "Backend opportunity")
        self.assertIn("Great role for Python and Flask engineers.", parsed.body)

    def test_assess_message_matches_job_advert_against_cv_terms(self) -> None:
        parser = JobAdvertParser("Python Django APIs mentoring")
        message = parser.parse_message(
            build_email(
                "Senior Python role",
                "Hiring a Python engineer with Django, APIs, and leadership experience.",
            ),
            uid="1",
        )

        assessment = parser.assess_message(message)

        self.assertTrue(assessment.is_job_advert)
        self.assertTrue(assessment.worth_applying)
        self.assertGreater(assessment.score, 0.2)
        self.assertIn("python", assessment.matched_terms)
        self.assertIn("django", assessment.matched_terms)

    def test_process_account_fetches_and_filters_imap_messages(self) -> None:
        parser = JobAdvertParser("Python Django API")
        account = IMAPAccount("imap.example.com", "user", "not-used")

        with patch("jobparser.core.imaplib.IMAP4_SSL", FakeIMAPClient):
            assessments = parser.process_account(account, unseen_only=True)

        self.assertEqual(len(assessments), 1)
        self.assertEqual(assessments[0].email.subject, "Python Developer role")
        self.assertTrue(assessments[0].worth_applying)


if __name__ == "__main__":
    unittest.main()
