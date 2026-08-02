"""Detección del tipo general de comprobante fiscal.

Las familias admitidas se definen en :mod:`fiscal.definitions`. Este extractor
solo interpreta evidencias textuales y devuelve el nombre canónico.
"""

import re
from typing import Optional

from fiscal.definitions import DOCUMENT_DEFINITIONS
from fiscal.normalization import normalizar_para_busqueda


def detectar_tipo_comprobante(texto: str) -> Optional[str]:
    """Detectar factura, nota de crédito o nota de débito.

    Las notas se buscan antes que las facturas porque un documento puede citar
    una factura original dentro de una nota. También se aceptan abreviaturas
    compactas como ``FCA``, ``NCB`` y ``NDC``, siempre acompañadas por una
    letra soportada para evitar coincidencias demasiado amplias.
    """

    texto = normalizar_para_busqueda(texto)
    if not texto:
        return None

    patterns_by_type = {
        "NOTA DE CREDITO": (
            r"\bNOTA\s+(?:DE\s+)?CREDITO\b",
            r"\bN\s*/\s*C\b",
            r"\bNC\s*[-_/ ]*[ABC]\b",
        ),
        "NOTA DE DEBITO": (
            r"\bNOTA\s+(?:DE\s+)?DEBITO\b",
            r"\bN\s*/\s*D\b",
            r"\bND\s*[-_/ ]*[ABC]\b",
        ),
        "FACTURA": (
            r"\bFACTURA\b",
            r"F\s*A\s*C\s*T\s*U\s*R\s*A",
            r"\bFC\s*[-_/ ]*[ABC]\b",
            r"\bFAC\s*[-_/ ]*[ABC]\b",
        ),
    }

    # DOCUMENT_DEFINITIONS ya está ordenado desde las familias más específicas
    # hacia FACTURA. Reutilizar ese orden evita mantener dos prioridades.
    for definition in DOCUMENT_DEFINITIONS:
        for pattern in patterns_by_type[definition.canonical_name]:
            if re.search(pattern, texto):
                return definition.canonical_name
    return None
