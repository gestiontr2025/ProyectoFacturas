from pathlib import Path

from state import EmailHistory, EmailIdentity


def identity(key: str = "gmail:123") -> EmailIdentity:
    return EmailIdentity(
        source_key=key,
        gmail_message_id=key.split(":", 1)[1],
        rfc_message_id="<example@example.com>",
        subject="Factura",
        message_date="Sat, 1 Aug 2026 10:00:00 -0300",
    )


def test_successful_email_is_skipped_on_future_runs(tmp_path: Path):
    history = EmailHistory(tmp_path / "state.sqlite3")
    item = identity()

    assert history.is_completed(item.source_key) is False

    history.mark_success(item, pdf_count=1)

    assert history.is_completed(item.source_key) is True
    assert history.summary() == {
        "processed": 1,
        "no_pdf": 0,
        "error": 0,
        "total": 1,
    }


def test_email_without_pdf_is_also_completed(tmp_path: Path):
    history = EmailHistory(tmp_path / "state.sqlite3")
    item = identity("gmail:456")

    history.mark_success(item, pdf_count=0)

    assert history.is_completed(item.source_key) is True
    assert history.summary()["no_pdf"] == 1


def test_error_is_recorded_but_remains_retryable(tmp_path: Path):
    history = EmailHistory(tmp_path / "state.sqlite3")
    item = identity("gmail:789")

    history.mark_error(item, RuntimeError("temporary failure"))

    assert history.is_completed(item.source_key) is False
    errors = history.list_errors()
    assert len(errors) == 1
    assert errors[0].attempts == 1
    assert "temporary failure" in errors[0].last_error


def test_later_success_replaces_previous_error(tmp_path: Path):
    history = EmailHistory(tmp_path / "state.sqlite3")
    item = identity("gmail:999")

    history.mark_error(item, ValueError("first attempt"))
    history.mark_success(item, pdf_count=2)

    assert history.is_completed(item.source_key) is True
    assert history.summary()["error"] == 0
    assert history.summary()["processed"] == 1


def test_reset_deletes_all_records(tmp_path: Path):
    history = EmailHistory(tmp_path / "state.sqlite3")
    history.mark_success(identity("gmail:1"), pdf_count=0)
    history.mark_success(identity("gmail:2"), pdf_count=1)

    assert history.reset() == 2
    assert history.summary()["total"] == 0
