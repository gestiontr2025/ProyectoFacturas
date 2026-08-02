import os

os.environ.setdefault("EMAIL", "test@example.com")
os.environ.setdefault("APP_PASSWORD", "test-password")

from gmail.messages import obtener_identidad_correo


class FakeConnection:
    def __init__(self, response):
        self.response = response
        self.last_query = None

    def fetch(self, email_id, query):
        self.last_query = (email_id, query)
        return self.response


def test_identity_prefers_gmail_global_message_id():
    headers = (
        b"Message-ID: <abc@example.com>\r\n"
        b"Subject: Factura julio\r\n"
        b"Date: Sat, 1 Aug 2026 10:00:00 -0300\r\n\r\n"
    )
    connection = FakeConnection(
        ("OK", [(b"1 (X-GM-MSGID 987654 BODY[HEADER.FIELDS] {120}", headers), b")"])
    )

    result = obtener_identidad_correo(connection, b"1")

    assert result.source_key == "gmail:987654"
    assert result.gmail_message_id == "987654"
    assert result.rfc_message_id == "<abc@example.com>"
    assert result.subject == "Factura julio"
    assert "BODY.PEEK" in connection.last_query[1]


def test_identity_falls_back_to_rfc_message_id():
    headers = b"Message-ID: <fallback@example.com>\r\nSubject: Test\r\n\r\n"
    connection = FakeConnection(("OK", [(b"1 (BODY[HEADER.FIELDS] {60}", headers)]))

    result = obtener_identidad_correo(connection, b"1")

    assert result.source_key == "message-id:<fallback@example.com>"
    assert result.gmail_message_id is None
