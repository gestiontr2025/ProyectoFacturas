"""Detección del tipo general de comprobante fiscal."""

import re
from typing import Optional

from fiscal.normalization import normalizar_para_busqueda

TIPOS_CANONICOS = {
    "FACTURA": "FACTURA",
    "NOTA DE CREDITO": "NOTA DE CREDITO",
    "NOTA DE DEBITO": "NOTA DE DEBITO",
}


def detectar_tipo_comprobante(texto: str) -> Optional[str]:
    """Detectar factura, nota de crédito o nota de débito.

    Se prueban primero las expresiones más específicas. Esto evita que una nota
    de crédito que también contiene la palabra ``FACTURA`` en referencias o
    leyendas sea clasificada erróneamente como factura.
    """
    texto = normalizar_para_busqueda(texto)
    if not texto:
        return None

    patrones = (
        (r"\bNOTA\s+(?:DE\s+)?CREDITO\b|\bN\s*/?\s*C\b", "NOTA DE CREDITO"),
        (r"\bNOTA\s+(?:DE\s+)?DEBITO\b|\bN\s*/?\s*D\b", "NOTA DE DEBITO"),
        (r"\bFACTURA\b|F\s*A\s*C\s*T\s*U\s*R\s*A", "FACTURA"),
    )
    for patron, tipo in patrones:
        if re.search(patron, texto):
            return tipo
    return None
