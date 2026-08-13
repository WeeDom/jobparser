from __future__ import annotations

from dataclasses import dataclass
from email import message_from_bytes
from email.header import decode_header, make_header
from email.message import Message
import html
import imaplib
import re
from typing import Iterable


JOB_KEYWORDS = {
    "apply",
    "career",
    "hiring",
    "job",
    "opportunity",
    "position",
    "recruiter",
    "role",
    "vacancy",
}

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#\-.]{1,}")
TAG_RE = re.compile(r"<[^>]+>")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
    "you",
    "your",
}


@dataclass(frozen=True)
class IMAPAccount:
    host: str
    username: str
    password: str
    mailbox: str = "INBOX"
    port: int = 993
    use_ssl: bool = True


@dataclass(frozen=True)
class ParsedEmail:
    uid: str
    subject: str
    sender: str
    body: str
    raw_message: bytes


@dataclass(frozen=True)
class JobAdvertAssessment:
    email: ParsedEmail
    is_job_advert: bool
    score: float
    worth_applying: bool
    matched_terms: tuple[str, ...]
    missing_terms: tuple[str, ...]


class JobAdvertParser:
    def __init__(
        self,
        cv_text: str,
        *,
        job_keywords: Iterable[str] = JOB_KEYWORDS,
        threshold: float = 0.2,
    ) -> None:
        self.cv_text = cv_text
        self.job_keywords = {keyword.lower() for keyword in job_keywords}
        self.threshold = threshold
        self.cv_terms = self._extract_terms(cv_text)

    @classmethod
    def from_cv_file(
        cls, path: str, **kwargs: object
    ) -> "JobAdvertParser":
        with open(path, "r", encoding="utf-8") as handle:
            return cls(handle.read(), **kwargs)

    def fetch_messages(
        self, account: IMAPAccount, *, unseen_only: bool = False, limit: int | None = None
    ) -> list[ParsedEmail]:
        client = self._create_client(account)
        try:
            client.login(account.username, account.password)
            status, _ = client.select(account.mailbox)
            if status != "OK":
                raise RuntimeError(f"unable to select mailbox {account.mailbox!r}")

            status, data = client.search(None, "UNSEEN" if unseen_only else "ALL")
            if status != "OK":
                raise RuntimeError("unable to search mailbox")

            message_ids = self._normalise_message_ids(data)
            if limit is not None:
                message_ids = message_ids[:limit]

            messages = []
            for message_id in message_ids:
                status, payload = client.fetch(message_id, "(RFC822)")
                if status != "OK":
                    continue
                raw_message = self._extract_rfc822(payload)
                if raw_message is None:
                    continue
                messages.append(self.parse_message(raw_message, uid=message_id))
            return messages
        finally:
            try:
                client.logout()
            except Exception:
                pass

    def process_account(
        self, account: IMAPAccount, *, unseen_only: bool = False, limit: int | None = None
    ) -> list[JobAdvertAssessment]:
        return [
            assessment
            for assessment in (
                self.assess_message(message)
                for message in self.fetch_messages(account, unseen_only=unseen_only, limit=limit)
            )
            if assessment.is_job_advert
        ]

    def parse_message(self, raw_message: bytes, *, uid: str = "") -> ParsedEmail:
        message = message_from_bytes(raw_message)
        subject = self._decode_header(message.get("Subject", ""))
        sender = self._decode_header(message.get("From", ""))
        body = self._extract_body(message)
        return ParsedEmail(uid=uid, subject=subject, sender=sender, body=body, raw_message=raw_message)

    def assess_message(self, message: ParsedEmail) -> JobAdvertAssessment:
        advert_text = f"{message.subject}\n{message.body}"
        advert_terms = self._extract_terms(advert_text)
        keyword_hit = any(keyword in advert_text.lower() for keyword in self.job_keywords)
        matched_terms = tuple(sorted(advert_terms & self.cv_terms))
        missing_terms = tuple(sorted(advert_terms - self.cv_terms))
        score = 0.0 if not advert_terms else len(matched_terms) / len(advert_terms)
        worth_applying = keyword_hit and score >= self.threshold and bool(matched_terms)
        return JobAdvertAssessment(
            email=message,
            is_job_advert=keyword_hit,
            score=round(score, 3),
            worth_applying=worth_applying,
            matched_terms=matched_terms,
            missing_terms=missing_terms,
        )

    def _create_client(self, account: IMAPAccount) -> imaplib.IMAP4:
        if account.use_ssl:
            return imaplib.IMAP4_SSL(account.host, account.port)
        return imaplib.IMAP4(account.host, account.port)

    def _decode_header(self, value: str) -> str:
        if not value:
            return ""
        return str(make_header(decode_header(value)))

    def _extract_body(self, message: Message) -> str:
        if message.is_multipart():
            parts = [
                self._decode_part(part)
                for part in message.walk()
                if part.get_content_type() == "text/plain"
                and "attachment" not in (part.get("Content-Disposition", "").lower())
            ]
            if parts:
                return "\n".join(part for part in parts if part).strip()

            html_parts = [
                self._decode_part(part)
                for part in message.walk()
                if part.get_content_type() == "text/html"
            ]
            if html_parts:
                return self._html_to_text("\n".join(html_parts)).strip()
            return ""

        content = self._decode_part(message)
        if message.get_content_type() == "text/html":
            return self._html_to_text(content).strip()
        return content.strip()

    def _decode_part(self, part: Message) -> str:
        payload = part.get_payload(decode=True)
        if payload is None:
            raw_payload = part.get_payload()
            return raw_payload if isinstance(raw_payload, str) else ""
        charset = part.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace")

    def _extract_terms(self, text: str) -> set[str]:
        return {
            token.lower()
            for token in TOKEN_RE.findall(text)
            if token.lower() not in STOP_WORDS
        }

    def _html_to_text(self, value: str) -> str:
        return html.unescape(TAG_RE.sub(" ", value))

    def _normalise_message_ids(self, data: list[bytes]) -> list[str]:
        if not data or not data[0]:
            return []
        return [part for part in data[0].decode("utf-8").split() if part]

    def _extract_rfc822(self, payload: list[object]) -> bytes | None:
        for item in payload:
            if isinstance(item, tuple) and len(item) > 1 and isinstance(item[1], bytes):
                return item[1]
        return None
