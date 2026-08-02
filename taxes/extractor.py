"""Detectores semánticos de impuestos presentes en una factura.

El módulo identifica únicamente la *presencia* de cada concepto. No extrae ni
suma importes. Las expresiones regulares se mantienen centralizadas para que el
resto del proyecto no duplique variantes de escritura de IVA y percepciones.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata


@dataclass(frozen=True)
class TaxEvidence:
    """Indicar qué conceptos tributarios aparecen de forma explícita."""

    vat_27: bool = False
    vat_21: bool = False
    vat_10_5: bool = False
    vat_perception: bool = False
    iibb_caba_perception: bool = False
    iibb_bsas_perception: bool = False
    internal_taxes: bool = False


def _normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.upper().replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip()


def _has_vat_rate(text: str, rate_pattern: str) -> bool:
    # Exigimos que IVA esté vinculado al porcentaje. Así evitamos confundir
    # fechas, cantidades o tasas que pertenecen a otros tributos.
    patterns = (
        rf"\bI\s*\.?\s*V\s*\.?\s*A\s*\.?\s*(?:ALICUOTA\s*)?{rate_pattern}\s*%",
        rf"\bIVA\s*(?:ALICUOTA\s*)?{rate_pattern}\s*%",
        rf"\b{rate_pattern}\s*%\s*(?:DE\s*)?(?:I\s*\.?\s*V\s*\.?\s*A\s*\.?|IVA)\b",
        rf"\bIVA\b.{{0,120}}?\b{rate_pattern}\s*%",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def extract_tax_evidence(text: object) -> TaxEvidence:
    """Detectar alícuotas y percepciones observadas en el texto de un PDF."""
    normalized = _normalize(text)

    vat_perception_patterns = (
        r"\bPERCEP(?:CION)?\s*\.?\s*(?:DE\s*)?I\s*\.?\s*V\s*\.?\s*A\b",
        r"\bIVA\s+RG\s*3337\b",
        r"\bPERCEPCION\s+IVA\b",
    )
    caba_patterns = (
        r"\bPERCEP(?:CION)?\s*\.?\s*(?:DE\s*)?I\s*\.?\s*B\s*\.?\s*(?:B\s*\.?\s*)?(?:CABA|CAP\.?|CAPITAL(?:\s+FEDERAL)?)\b",
        r"\bIIBB\s+(?:CABA|CAPITAL(?:\s+FEDERAL)?)\b",
        r"\bINGRESOS\s+BRUTOS\s+(?:CABA|CAPITAL(?:\s+FEDERAL)?)\b",
    )
    bsas_patterns = (
        r"\bPERCEP(?:CION)?\s*\.?\s*(?:DE\s*)?I\s*\.?\s*B\s*\.?\s*B\s*\.?\s*(?:BS\.?\s*AS\.?|BUENOS\s+AIRES)\b",
        r"\bIIBB\s+(?:BS\.?\s*AS\.?|BUENOS\s+AIRES)\b",
        r"\bARBA\b",
    )
    internal_patterns = (
        r"\bIMPUESTOS?\s+INTERNOS?\b",
        r"\bIMP\.?\s*INT\.?\b",
        r"\bINTERNOS?\s+[0-9]+(?:[.,][0-9]+)?\s*%",
    )

    return TaxEvidence(
        vat_27=_has_vat_rate(normalized, r"27(?:[.,]0+)?"),
        vat_21=_has_vat_rate(normalized, r"21(?:[.,]0+)?"),
        vat_10_5=_has_vat_rate(normalized, r"10(?:[.,]5|[.,]50)"),
        vat_perception=any(re.search(pattern, normalized) for pattern in vat_perception_patterns),
        iibb_caba_perception=any(re.search(pattern, normalized) for pattern in caba_patterns),
        iibb_bsas_perception=any(re.search(pattern, normalized) for pattern in bsas_patterns),
        internal_taxes=any(re.search(pattern, normalized) for pattern in internal_patterns),
    )
