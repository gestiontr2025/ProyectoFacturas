"""Excepciones mínimas basadas en documentos revisados manualmente.

Este módulo no es un parser general. Solo contiene datos de archivos concretos
cuya capa de texto perdió información visible en la página, pero que fueron
verificados contra el PDF original. Mantener estas excepciones separadas evita
ocultar valores especiales dentro del flujo principal.
"""
from __future__ import annotations

from pathlib import Path

_VALIDATED_ISSUE_DATES = {
    "#1026 FACB0002100001477.PDF": "08/07/2025",
}


def get_validated_issue_date(filename: str) -> str | None:
    """Devolver una fecha solo para un archivo previamente verificado."""
    return _VALIDATED_ISSUE_DATES.get(Path(filename).name.upper())
