"""Persistencia del estado local del Proyecto Facturas.

Cada fuente de entrada conserva su propio historial lógico dentro de una misma
base SQLite. Así Gmail y Google Drive pueden reanudar ejecuciones sin volver a
procesar elementos ya completados.
"""

from state.drive_history import DriveHistory, DriveIdentity, DriveRecord
from state.email_history import EmailHistory, EmailIdentity, EmailRecord

__all__ = [
    "DriveHistory",
    "DriveIdentity",
    "DriveRecord",
    "EmailHistory",
    "EmailIdentity",
    "EmailRecord",
]
