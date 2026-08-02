"""Firmas textuales altamente específicas para encabezados no extraíbles.

Estas reglas son un último respaldo. Solo se utilizan cuando una marca o alias
operativo observado en facturas reales identifica de forma inequívoca a un
proveedor conocido. El resultado siempre se traduce a la identidad canónica
del catálogo antes de llegar al detector general.
"""

import re
from typing import Optional


_CONTENT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    # La factura de Cantine se comercializa bajo IVINI. El encabezado gráfico
    # no aparece en pypdf, pero el alias bancario sí se extrae completo.
    (re.compile(r"\bIVINI[ ._-]*GALICIA\b", re.IGNORECASE), "cantine_s_r_l"),
)


def detectar_identificador_por_contenido(texto: str) -> Optional[str]:
    """Devolver un proveedor solo cuando una firma exclusiva está presente."""

    for patron, identificador in _CONTENT_PATTERNS:
        if patron.search(texto or ""):
            return identificador
    return None
