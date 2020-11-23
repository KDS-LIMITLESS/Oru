from typing import List
from requests import Response, post
import os

FAILED_LOAD_API_KEY = "Failed to load MailGun API key."
FAILED_LOAD_DOMAIN = "Failed to load MailGun domain."
ERROR_SENDING_EMAIL = "Error in sending confirmation email, user registration failed."


class MailgunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_API_KEY = os.environ["MAILGUN_API_KEY"]
    MAILGUN_DOMAIN =  os.environ["MAILGUN_DOMAIN"]

    FROM_TITLE = os.environ["FROM_TITLE"]
    FROM_EMAIL = os.environ["FROM_EMAIL"]

    @classmethod
    def send_email(
        cls, email: List[str], subject: str, text: str, html: str) -> Response:
        if cls.MAILGUN_API_KEY is None:
            raise MailgunException(FAILED_LOAD_API_KEY)

        if cls.MAILGUN_DOMAIN is None:
            raise MailgunException(FAILED_LOAD_DOMAIN)

        response = post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html,
            },
        )

        if response.status_code != 200:
            raise MailgunException(ERROR_SENDING_EMAIL)

        return response



#print(Mailgun.send_email(["s.kamahjnr@gmail.com"],"Enquiry","This is me","<html><h1>HI</h1></html>"))