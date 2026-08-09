"""Detección del tipo general de comprobante fiscal.

Las familias admitidas se definen en :mod:`fiscal.definitions`. Este extractor
solo interpreta evidencias textuales y devuelve el nombre canónico.
"""

import re
from typing import Optional

from fiscal.definitions import DOCUMENT_DEFINITIONS
from fiscal.normalization import normalizar_para_busqueda


_NEGATED_INVOICE_PATTERNS = (
    r"\bNO\s+ES\s+FACTURA\b",
    r"\bNO\s+CORRESPONDE\s+A\s+FACTURA\b",
    r"\bDOCUMENTO\s+DE\s+TRASLADO\s*[-:]?\s*NO\s+ES\s+FACTURA\b",
)


def _remove_negated_invoice_mentions(texto: str) -> str:
    """Quitar menciones que dicen explícitamente que algo *no* es factura.

    Un remito suele imprimir ``NO ES FACTURA``. Buscar la palabra FACTURA sin
    considerar la negación convertía el propio aviso preventivo del documento
    en evidencia fiscal. Solo se elimina la frase negada, no expresiones como
    ``LA PRESENTE FACTURA NO ES COMPROBANTE DE PAGO`` porque allí la negación
    recae sobre el pago, no sobre la naturaleza de la factura.
    """
    for pattern in _NEGATED_INVOICE_PATTERNS:
        texto = re.sub(pattern, " ", texto)
    return texto


def _has_fiscal_support(texto: str) -> bool:
    """Exigir apoyo fiscal para rescatar un tipo perdido por OCR."""
    has_number = bool(
        re.search(r"\b\d{1,5}\s*[-/]\s*\d{1,8}\b", texto)
        or re.search(r"\b(?:NRO|NUMERO)\.?\s*[:\-]?\s*\d{1,5}\s*[-/]\s*\d{1,8}\b", texto)
    )
    has_fiscal_marker = bool(re.search(r"\b(?:CAE|CUIT|IVA)\b", texto))
    return has_number and has_fiscal_marker


def detectar_tipo_comprobante(texto: str) -> Optional[str]:
    """Detectar factura, nota de crédito o nota de débito.

    Las notas se buscan antes que las facturas porque un documento puede citar
    una factura original dentro de una nota. También se aceptan abreviaturas
    compactas como ``FCA``, ``NCB`` y ``NDC``.

    El OCR puede perder el título principal de una nota y conservar solamente
    un rótulo como ``TOTAL DEBITO``. Ese respaldo se acepta únicamente cuando
    también existe estructura fiscal suficiente (número y CAE/CUIT/IVA).
    """

    texto = normalizar_para_busqueda(texto)
    if not texto:
        return None

    texto_busqueda = _remove_negated_invoice_mentions(texto)

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
            r"\bFA\s*[-_/\"']+[ABC]\b",
        ),
    }

    for definition in DOCUMENT_DEFINITIONS:
        for pattern in patterns_by_type[definition.canonical_name]:
            if re.search(pattern, texto_busqueda):
                return definition.canonical_name

    # Rescate OCR: el encabezado grande puede desaparecer, pero los totales
    # semánticos sobreviven. No alcanza con la palabra DEBITO/CREDITO sola.
    if _has_fiscal_support(texto_busqueda):
        if re.search(r"\bTOTAL\s+(?:NOTA\s+DE\s+)?CREDITO\b", texto_busqueda):
            return "NOTA DE CREDITO"
        if re.search(r"\bTOTAL\s+(?:NOTA\s+DE\s+)?DEBITO\b", texto_busqueda):
            return "NOTA DE DEBITO"

    # Liquidaciones fiscales de gastos comunes sin la palabra FACTURA.
    if "LIQUIDACION DE GASTOS COMUNES" in texto_busqueda:
        has_number = re.search(
            r"\bN[ROº°]*\.?\s*[:;,.-]?\s*\d{1,5}\s*[-/]\s*\d{1,8}\b",
            texto_busqueda,
        )
        has_vat = re.search(r"\bIVA\s+(?:21|27)\s*%", texto_busqueda)
        has_cuit = re.search(r"\bCUIT\b", texto_busqueda)
        if has_number and has_vat and has_cuit:
            return "FACTURA"

    return None
