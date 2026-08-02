"""Reglas de alta confianza para documentos de Recursos Humanos."""

from __future__ import annotations

from documents.rules.common import contains_any, matches_any


def score_hr_subcategories(content: str, filename: str) -> dict[str, int]:
    """Calcular puntajes para altas/bajas, liquidaciones y recibos/legajos.

    El nombre del archivo aporta evidencia fuerte porque los sistemas de
    liquidación suelen generar nombres muy descriptivos. El contenido mantiene
    prioridad cuando incluye expresiones inequívocas como ``RECIBO DE HABERES``.
    """

    joined = f"{filename} {content}"

    alta_baja = 0
    alta_baja += 5 * contains_any(filename, ("ALTA ARCA", "BAJA ARCA", "ALTA TEMPRANA"))
    if contains_any(filename, ("ALTA ARCA", "BAJA ARCA")) and contains_any(filename, ("EMPLEADO", "EMPLEADOS")):
        alta_baja += 4
    alta_baja += 8 * matches_any(filename, (r"^ALTAS?\b", r"^BAJAS?\b"))
    alta_baja += 4 * contains_any(content, ("ALTA TEMPRANA", "BAJA TEMPRANA"))
    if "ARCA" in joined and matches_any(joined, (r"\bALTA\b", r"\bBAJA\b")):
        alta_baja += 5

    liquidacion = 0
    liquidacion += 8 * contains_any(filename, ("LIQUIDACION", "LIQ FINAL", "1 SAC", "SAC"))
    liquidacion += 7 * contains_any(content, ("LIQUIDACION DE SUELDOS", "LIQUIDACION FINAL"))
    liquidacion += 3 * contains_any(joined, ("SUELDO", "VACACIONES", "INDEMNIZACION"))

    recibo_legajo = 0
    recibo_legajo += 6 * contains_any(filename, ("LEGAJO", "EMPLEADO", "EMPLEADOR"))
    recibo_legajo += 8 * contains_any(content, ("RECIBO DE HABERES", "RECIBO DE SUELDO"))
    recibo_legajo += 4 * contains_any(joined, ("REMUNERACION", "APORTES", "CONTRIBUCIONES"))

    return {
        "recursos_humanos_altas_bajas": alta_baja,
        "recursos_humanos_liquidaciones": liquidacion,
        "recursos_humanos_recibos_legajos": recibo_legajo,
    }
