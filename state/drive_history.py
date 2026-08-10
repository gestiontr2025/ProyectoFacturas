"""Historial persistente de archivos descargados desde Google Drive.

El historial comparte la misma base SQLite del proyecto, pero utiliza una tabla
independiente de Gmail. De esta manera todas las fuentes de entrada conservan
estado transaccional sin multiplicar archivos JSON de control.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3


COMPLETED_DRIVE_STATUSES = frozenset({"downloaded", "local_duplicate"})


@dataclass(frozen=True)
class DriveIdentity:
    """Identidad estable y metadatos mínimos de un archivo de Drive."""

    file_id: str
    source_name: str
    folder_id: str
    file_name: str
    modified_time: str | None = None


@dataclass(frozen=True)
class DriveRecord:
    """Fila legible del historial de Drive."""

    file_id: str
    source_name: str
    file_name: str
    status: str
    attempts: int
    local_path: str | None
    last_error: str | None
    downloaded_at: str | None


class DriveHistory:
    """Administrar el estado local de descargas de Google Drive."""

    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS drive_history (
                    file_id TEXT PRIMARY KEY,
                    source_name TEXT NOT NULL DEFAULT '',
                    folder_id TEXT NOT NULL DEFAULT '',
                    file_name TEXT NOT NULL DEFAULT '',
                    modified_time TEXT,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    first_seen_at TEXT NOT NULL,
                    last_attempt_at TEXT NOT NULL,
                    downloaded_at TEXT,
                    local_path TEXT,
                    last_error TEXT
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_drive_history_status "
                "ON drive_history(status)"
            )

    def is_completed(self, file_id: str) -> bool:
        """Indicar si el archivo ya terminó correctamente en otra ejecución."""

        with self._connect() as connection:
            row = connection.execute(
                "SELECT status FROM drive_history WHERE file_id = ?",
                (file_id,),
            ).fetchone()
        return bool(row and row["status"] in COMPLETED_DRIVE_STATUSES)

    def mark_success(
        self,
        identity: DriveIdentity,
        *,
        local_path: Path | str,
        status: str = "downloaded",
    ) -> None:
        """Registrar una descarga completa o una copia local ya existente."""

        if status not in COMPLETED_DRIVE_STATUSES:
            raise ValueError(f"Estado de éxito de Drive inválido: {status}")

        now = _utc_now()
        self._upsert(
            identity,
            status=status,
            downloaded_at=now,
            local_path=str(local_path),
            last_error=None,
            attempted_at=now,
        )

    def mark_error(self, identity: DriveIdentity, error: BaseException) -> None:
        """Registrar un fallo dejando el archivo disponible para reintento."""

        now = _utc_now()
        self._upsert(
            identity,
            status="error",
            downloaded_at=None,
            local_path=None,
            last_error=f"{type(error).__name__}: {error}",
            attempted_at=now,
        )

    def _upsert(
        self,
        identity: DriveIdentity,
        *,
        status: str,
        downloaded_at: str | None,
        local_path: str | None,
        last_error: str | None,
        attempted_at: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO drive_history (
                    file_id,
                    source_name,
                    folder_id,
                    file_name,
                    modified_time,
                    status,
                    attempts,
                    first_seen_at,
                    last_attempt_at,
                    downloaded_at,
                    local_path,
                    last_error
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
                ON CONFLICT(file_id) DO UPDATE SET
                    source_name = excluded.source_name,
                    folder_id = excluded.folder_id,
                    file_name = excluded.file_name,
                    modified_time = excluded.modified_time,
                    status = excluded.status,
                    attempts = drive_history.attempts + 1,
                    last_attempt_at = excluded.last_attempt_at,
                    downloaded_at = excluded.downloaded_at,
                    local_path = excluded.local_path,
                    last_error = excluded.last_error
                """,
                (
                    identity.file_id,
                    identity.source_name,
                    identity.folder_id,
                    identity.file_name,
                    identity.modified_time,
                    status,
                    attempted_at,
                    attempted_at,
                    downloaded_at,
                    local_path,
                    last_error,
                ),
            )

    def import_legacy_json(
        self,
        json_path: Path | str,
        *,
        source_name: str = "legacy_drive_test",
        folder_id: str = "legacy",
    ) -> int:
        """Migrar el antiguo ``drive_downloaded.json`` una sola vez.

        La importación usa ``INSERT OR IGNORE``. Por eso puede ejecutarse en cada
        arranque sin duplicar registros ni incrementar intentos existentes.
        """

        legacy_path = Path(json_path)
        if not legacy_path.exists():
            return 0

        try:
            data = json.loads(legacy_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return 0

        file_ids = {
            item.strip()
            for item in data.get("downloaded_file_ids", [])
            if isinstance(item, str) and item.strip()
        }
        if not file_ids:
            return 0

        now = _utc_now()
        inserted = 0
        with self._connect() as connection:
            for file_id in sorted(file_ids):
                cursor = connection.execute(
                    """
                    INSERT OR IGNORE INTO drive_history (
                        file_id,
                        source_name,
                        folder_id,
                        file_name,
                        modified_time,
                        status,
                        attempts,
                        first_seen_at,
                        last_attempt_at,
                        downloaded_at,
                        local_path,
                        last_error
                    ) VALUES (?, ?, ?, '', NULL, 'downloaded', 1, ?, ?, ?, NULL, NULL)
                    """,
                    (
                        file_id,
                        source_name,
                        folder_id,
                        now,
                        now,
                        now,
                    ),
                )
                inserted += cursor.rowcount
        return inserted

    def summary(self) -> dict[str, int]:
        """Contar registros por estado para diagnóstico."""

        totals = {
            "downloaded": 0,
            "local_duplicate": 0,
            "error": 0,
            "total": 0,
        }
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT status, COUNT(*) AS amount "
                "FROM drive_history GROUP BY status"
            ).fetchall()
        for row in rows:
            totals[row["status"]] = row["amount"]
            totals["total"] += row["amount"]
        return totals

    def list_errors(self) -> list[DriveRecord]:
        """Obtener archivos de Drive cuyo último intento falló."""

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT file_id, source_name, file_name, status, attempts,
                       local_path, last_error, downloaded_at
                FROM drive_history
                WHERE status = 'error'
                ORDER BY last_attempt_at DESC
                """
            ).fetchall()
        return [DriveRecord(**dict(row)) for row in rows]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
