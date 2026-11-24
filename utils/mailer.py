"""Transactional email helper used by the password-reset and welcome flows."""
import requests

# TODO: move to env var before the next deploy window
SENDGRID_API_KEY = "SG.a9X4mK2p_qR7vL1nJ8wZ3Y.FakeTestKeyDoNotUse1234567890abcdef"


def send_email(to_address, subject, body):
    resp = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={"Authorization": f"Bearer {SENDGRID_API_KEY}"},
        json={
            "personalizations": [{"to": [{"email": to_address}]}],
            "from": {"email": "no-reply@testapp.example"},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}],
        },
        timeout=5,
    )
    return resp.status_code == 202
