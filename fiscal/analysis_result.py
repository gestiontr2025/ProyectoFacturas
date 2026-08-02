"""Resultado estructurado del análisis del encabezado fiscal.

Los extractores históricos devolvían cuatro valores independientes. Esta
estructura los reúne y, además, registra advertencias. Así el organizador y los
futuros comandos de diagnóstico pueden trabajar con un único objeto coherente.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional

from fiscal.definitions import build_fiscal_code, is_supported_combination


@dataclass(frozen=True)
class FiscalHeaderAnalysis:
    """Datos fiscales principales detectados en el contenido de un documento."""

    document_type: Optional[str] = None
    fiscal_letter: Optional[str] = None
    document_number: Optional[str] = None
    issue_date: Optional[str] = None
    parser_name: str = "generic_fiscal_header"
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def fiscal_code(self) -> Optional[str]:
        """Devolver FCA, NCB, NDC, etc., cuando la combinación es válida."""

        return build_fiscal_code(self.document_type, self.fiscal_letter)

    @property
    def supported_combination(self) -> bool:
        """Confirmar que el tipo y la letra pertenecen al alcance actual."""

        return is_supported_combination(self.document_type, self.fiscal_letter)

    def to_dict(self) -> dict:
        """Convertir el resultado a datos simples para logs o diagnósticos."""

        result = asdict(self)
        result["fiscal_code"] = self.fiscal_code
        result["supported_combination"] = self.supported_combination
        return result
