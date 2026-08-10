import json
from pathlib import Path

from state import DriveHistory, DriveIdentity


def identity(file_id: str = "drive-file-123") -> DriveIdentity:
    return DriveIdentity(
        file_id=file_id,
        source_name="proveedor",
        folder_id="folder-abc",
        file_name="factura.pdf",
        modified_time="2026-08-09T20:00:00.000Z",
    )


def test_successful_drive_file_is_skipped_on_future_runs(tmp_path: Path):
    history = DriveHistory(tmp_path / "state.sqlite3")
    item = identity()

    assert history.is_completed(item.file_id) is False

    history.mark_success(item, local_path=tmp_path / "factura.pdf")

    assert history.is_completed(item.file_id) is True
    assert history.summary() == {
        "downloaded": 1,
        "local_duplicate": 0,
        "error": 0,
        "total": 1,
    }


def test_drive_error_remains_retryable(tmp_path: Path):
    history = DriveHistory(tmp_path / "state.sqlite3")
    item = identity("drive-file-error")

    history.mark_error(item, RuntimeError("temporary network error"))

    assert history.is_completed(item.file_id) is False
    errors = history.list_errors()
    assert len(errors) == 1
    assert errors[0].attempts == 1
    assert "temporary network error" in errors[0].last_error


def test_later_drive_success_replaces_previous_error(tmp_path: Path):
    history = DriveHistory(tmp_path / "state.sqlite3")
    item = identity("drive-file-retry")

    history.mark_error(item, RuntimeError("first attempt"))
    history.mark_success(item, local_path=tmp_path / "factura.pdf")

    assert history.is_completed(item.file_id) is True
    assert history.summary()["error"] == 0
    assert history.summary()["downloaded"] == 1


def test_legacy_json_is_migrated_without_duplicates(tmp_path: Path):
    history = DriveHistory(tmp_path / "state.sqlite3")
    legacy = tmp_path / "drive_downloaded.json"
    legacy.write_text(
        json.dumps(
            {
                "downloaded_file_ids": [
                    "legacy-1",
                    "legacy-2",
                    "legacy-1",
                ]
            }
        ),
        encoding="utf-8",
    )

    assert history.import_legacy_json(legacy) == 2
    assert history.import_legacy_json(legacy) == 0
    assert history.is_completed("legacy-1") is True
    assert history.is_completed("legacy-2") is True
    assert history.summary()["total"] == 2
