"""Historial persistente de correos procesados mediante SQLite.

SQLite forma parte de la biblioteca estándar de Python. Por eso permite guardar
el progreso sin instalar ni administrar un servidor de base de datos.

La tabla utiliza como identidad principal el identificador global que Gmail
expone mediante IMAP (``X-GM-MSGID``). Ese valor permanece estable aunque el
correo cambie de posición dentro del buzón, a diferencia del número de secuencia
IMAP que solo es válido dentro de una sesión y carpeta concretas.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Iterable


COMPLETED_STATUSES = frozenset({"processed", "no_pdf"})


@dataclass(frozen=True)
class EmailIdentity:
    """Identidad estable y metadatos mínimos de un correo.

    ``source_key`` es la clave que el historial usa para decidir si el mensaje
    ya fue procesado. Se construye preferentemente a partir de ``X-GM-MSGID``;
    ``Message-ID`` funciona como segundo respaldo.
    """

    source_key: str
    gmail_message_id: str | None = None
    rfc_message_id: str | None = None
    subject: str = "Sin asunto"
    message_date: str = "Fecha no informada"


@dataclass(frozen=True)
class EmailRecord:
    """Representación legible de una fila almacenada en SQLite."""

    source_key: str
    status: str
    attempts: int
    pdf_count: int
    subject: str
    last_error: str | None
    processed_at: str | None


class EmailHistory:
    """Administrar el historial local de mensajes revisados.

    La conexión se abre solo durante cada operación. Este diseño evita mantener
    recursos abiertos durante toda la descarga y hace que cada actualización se
    confirme inmediatamente. Si la computadora se apaga a mitad de un escaneo,
    los correos ya terminados permanecen registrados.
    """

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
                CREATE TABLE IF NOT EXISTS email_history (
                    source_key TEXT PRIMARY KEY,
                    gmail_message_id TEXT,
                    rfc_message_id TEXT,
                    subject TEXT NOT NULL DEFAULT '',
                    message_date TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    pdf_count INTEGER NOT NULL DEFAULT 0,
                    first_seen_at TEXT NOT NULL,
                    last_attempt_at TEXT NOT NULL,
                    processed_at TEXT,
                    last_error TEXT
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_email_history_status "
                "ON email_history(status)"
            )

    def is_completed(self, source_key: str) -> bool:
        """Indicar si un correo terminó en un estado que no requiere repetición."""

        with self._connect() as connection:
            row = connection.execute(
                "SELECT status FROM email_history WHERE source_key = ?",
                (source_key,),
            ).fetchone()
        return bool(row and row["status"] in COMPLETED_STATUSES)

    def mark_success(
        self,
        identity: EmailIdentity,
        *,
        pdf_count: int,
    ) -> None:
        """Registrar una ejecución exitosa.

        Un correo sin PDF también queda completado. Volver a abrirlo cada día no
        aportaría información nueva, mientras que cualquier archivo pendiente ya
        fue guardado localmente y puede reprocesarse con el comando específico.
        """

        status = "processed" if pdf_count > 0 else "no_pdf"
        now = _utc_now()
        self._upsert(
            identity,
            status=status,
            pdf_count=pdf_count,
            processed_at=now,
            last_error=None,
            attempted_at=now,
        )

    def mark_error(self, identity: EmailIdentity, error: BaseException) -> None:
        """Registrar un fallo sin marcar el correo como completado.

        Los registros con estado ``error`` se vuelven a intentar en futuras
        ejecuciones. Esto evita perder una factura por un fallo temporal de red,
        disco o parsing.
        """

        now = _utc_now()
        self._upsert(
            identity,
            status="error",
            pdf_count=0,
            processed_at=None,
            last_error=f"{type(error).__name__}: {error}",
            attempted_at=now,
        )

    def _upsert(
        self,
        identity: EmailIdentity,
        *,
        status: str,
        pdf_count: int,
        processed_at: str | None,
        last_error: str | None,
        attempted_at: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO email_history (
                    source_key,
                    gmail_message_id,
                    rfc_message_id,
                    subject,
                    message_date,
                    status,
                    attempts,
                    pdf_count,
                    first_seen_at,
                    last_attempt_at,
                    processed_at,
                    last_error
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
                ON CONFLICT(source_key) DO UPDATE SET
                    gmail_message_id = excluded.gmail_message_id,
                    rfc_message_id = excluded.rfc_message_id,
                    subject = excluded.subject,
                    message_date = excluded.message_date,
                    status = excluded.status,
                    attempts = email_history.attempts + 1,
                    pdf_count = excluded.pdf_count,
                    last_attempt_at = excluded.last_attempt_at,
                    processed_at = excluded.processed_at,
                    last_error = excluded.last_error
                """,
                (
                    identity.source_key,
                    identity.gmail_message_id,
                    identity.rfc_message_id,
                    identity.subject,
                    identity.message_date,
                    status,
                    pdf_count,
                    attempted_at,
                    attempted_at,
                    processed_at,
                    last_error,
                ),
            )

    def summary(self) -> dict[str, int]:
        """Contar registros por estado para mostrar un diagnóstico breve."""

        totals = {"processed": 0, "no_pdf": 0, "error": 0, "total": 0}
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT status, COUNT(*) AS amount FROM email_history GROUP BY status"
            ).fetchall()
        for row in rows:
            totals[row["status"]] = row["amount"]
            totals["total"] += row["amount"]
        return totals

    def list_errors(self) -> list[EmailRecord]:
        """Obtener errores pendientes de reintento, ordenados por último intento."""

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT source_key, status, attempts, pdf_count, subject,
                       last_error, processed_at
                FROM email_history
                WHERE status = 'error'
                ORDER BY last_attempt_at DESC
                """
            ).fetchall()
        return [EmailRecord(**dict(row)) for row in rows]

    def reset(self) -> int:
        """Eliminar el historial y devolver cuántos registros fueron borrados."""

        with self._connect() as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM email_history"
            ).fetchone()[0]
            connection.execute("DELETE FROM email_history")
        return int(count)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
