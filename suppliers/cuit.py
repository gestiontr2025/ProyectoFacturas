"""Normalización y validación de CUIT argentinos.

Las facturas pueden imprimir el CUIT con guiones, espacios o como once dígitos
continuos. Este módulo centraliza la validación para que un teléfono, un CAE o
un número de comprobante no pueda transformarse accidentalmente en proveedor.
"""
from __future__ import annotations

import re

_CUIT_WEIGHTS = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)
_CUIT_PATTERN = re.compile(
    r"(?<!\d)(\d{2})\s*[-.]?\s*(\d{8})\s*[-.]?\s*(\d)(?!\d)"
)


def normalizar_cuit(value: object) -> str | None:
    """Devolver ``XX-XXXXXXXX-X`` únicamente para un CUIT válido."""
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) != 11 or not validar_cuit(digits):
        return None
    return f"{digits[:2]}-{digits[2:10]}-{digits[10]}"


def validar_cuit(value: object) -> bool:
    """Validar longitud y dígito verificador de un CUIT argentino."""
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) != 11:
        return False

    total = sum(int(digit) * weight for digit, weight in zip(digits[:10], _CUIT_WEIGHTS))
    verifier = 11 - (total % 11)
    if verifier == 11:
        verifier = 0
    elif verifier == 10:
        verifier = 9
    return verifier == int(digits[-1])


def extraer_cuits(text: str) -> tuple[str, ...]:
    """Extraer CUIT válidos y únicos preservando su orden de aparición."""
    found: list[str] = []
    seen: set[str] = set()
    for match in _CUIT_PATTERN.finditer(text or ""):
        normalized = normalizar_cuit("".join(match.groups()))
        if normalized and normalized not in seen:
            seen.add(normalized)
            found.append(normalized)
    return tuple(found)
