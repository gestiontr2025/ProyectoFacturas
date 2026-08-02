"""Reglas para documentos administrativos que no son comprobantes fiscales."""

from __future__ import annotations

from documents.rules.common import contains_any, matches_any


def score_administrative_categories(content: str, filename: str) -> dict[str, int]:
    """Puntuar instructivos, retenciones/transferencias y administrativos."""

    joined = f"{filename} {content}"

    instructions = 0
    instructions += 9 * contains_any(filename, ("INSTRUCTIVO", "MANUAL DE", "GUIA DE"))
    instructions += 7 * contains_any(content, ("INSTRUCTIVO", "PASO A PASO", "INSTRUCCIONES"))

    retention_transfer = 0
    retention_transfer += 7 * contains_any(filename, ("RETENCION", "TRANSFERENCIA"))
    retention_transfer += 10 * contains_any(content, ("CERTIFICADO DE RETENCION", "COMPROBANTE DE TRANSFERENCIA"))
    retention_transfer += 3 * contains_any(joined, ("GANANCIAS", "INGRESOS BRUTOS", "SIRCREB"))

    administrative = 0
    administrative += 8 * contains_any(filename, ("ENCUESTA", "CALENDARIO", "ORDEN_TRABAJO", "ORDEN DE TRABAJO", "CHANGEREPORT"))
    administrative += 6 * contains_any(content, ("ENCUESTA DE SATISFACCION", "ORDEN DE TRABAJO"))

    communication = 0
    communication += 9 * contains_any(filename, ("NOTA A CLIENTES", "COMUNICACION A CLIENTES", "CIRCULAR A CLIENTES"))
    communication += 8 * contains_any(content, ("COMUNICACION A CLIENTES", "PROGRAMA DE INTEGRIDAD"))
    communication += 3 * contains_any(content, ("CODIGO DE ETICA", "POLITICA ANTICORRUPCION", "SALUDAMOS A UDS"))

    taxes_services = 0
    taxes_services += 10 * contains_any(joined, ("INMOBILIARIO Y ABL", "IMPUESTO INMOBILIARIO", "ALUMBRADO BARRIDO LIMPIEZA"))

    operational = 0
    operational += 10 * contains_any(filename, ("MEP PLAZAS",))
    operational += 6 * contains_any(content, ("PREPARACIONES PRODUCIR", "CANTIDAD DE RECETA", "PLAZA 1"))

    consortium = 0
    consortium += 10 * contains_any(filename, ("CCF 000", "CCF_000"))
    consortium += 10 * contains_any(content, ("LIQUIDACION DE GASTOS COMUNES", "CONSORCIO COPROPIETARIOS"))

    return {
        "instructivos": instructions,
        "retenciones_y_transferencias": retention_transfer,
        "administrativos": administrative,
        "comunicaciones": communication,
        "impuestos_y_servicios": taxes_services,
        "operativos": operational,
        "consorcio_y_gastos_comunes": consortium,
    }


# ---------------------------------------------------------------------------
# Evidencias inequívocas adicionales observadas durante el escaneo completo.
# Estas reglas se basan en nombres descriptivos y no deben confundirse con una
# factura que simplemente menciona un pago dentro de sus condiciones.
# ---------------------------------------------------------------------------

def puntuar_por_nombre_descriptivo(nombre_normalizado: str) -> dict[str, int]:
    """Asignar puntajes altos a documentos administrativos explícitos."""

    puntajes: dict[str, int] = {}
    if "COMPROBANTE DE PAGO" in nombre_normalizado:
        puntajes["comprobante_de_pago"] = 12
    if "TRANSFERENCIA" in nombre_normalizado:
        puntajes["retenciones_y_transferencias"] = 10
    if "PAGO DE SERVICIOS" in nombre_normalizado:
        puntajes["administrativos"] = 10
    if "ACCESO" in nombre_normalizado and "FACTURA YA" in nombre_normalizado:
        puntajes["instructivos"] = 12
    if nombre_normalizado.startswith("CCF ") or nombre_normalizado.startswith("CCF_"):
        puntajes["consorcio_y_gastos_comunes"] = 12
    if "MEP PLAZAS" in nombre_normalizado:
        puntajes["operativos"] = 12
    if nombre_normalizado in {"3702130 PDF", "3702144 PDF"} or "INMOBILIARIO Y ABL" in nombre_normalizado:
        puntajes["impuestos_y_servicios"] = 12
    if nombre_normalizado.startswith("RDRC"):
        puntajes["remitos_y_recibos"] = 12
    return puntajes
