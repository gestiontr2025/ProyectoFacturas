"""Resultado uniforme de una operación sobre un documento."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from models.fiscal_document import FiscalDocument
from models.supplier import Supplier


class ProcessingStatus(str, Enum):
    """Estados posibles, escritos como texto para facilitar su serialización."""

    ORGANIZED = "organizada"
    PENDING = "pendiente"
    ARCHIVED = "archivada"
    ERROR = "error"


@dataclass
class ProcessingResult:
    """Describir de manera uniforme qué ocurrió con un archivo.

    El objeto no mueve archivos. Solo transporta el resultado, lo que permite
    que consola, logs y futuras interfaces gráficas presenten la misma verdad.
    """

    status: ProcessingStatus
    original_path: Path
    final_path: Path
    document: Optional[FiscalDocument] = None
    supplier: Optional[Supplier] = None
    detail: Optional[str] = None
    document_category: str = "factura"

    @property
    def successful(self) -> bool:
        return self.status in {ProcessingStatus.ORGANIZED, ProcessingStatus.ARCHIVED}
