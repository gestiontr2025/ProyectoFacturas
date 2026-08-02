"""Clasificación defensiva y explicable de documentos PDF.

El proyecto recibe adjuntos heterogéneos: facturas, listas, liquidaciones,
instructivos y documentos administrativos. Este módulo decide qué flujo debe
recibir cada PDF. Las reglas específicas viven en ``documents.rules`` para que
agregar una categoría no convierta este archivo en una lista interminable de
``if``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re
import unicodedata

from documents.rules.administrative import puntuar_por_nombre_descriptivo
from documents.rules import (
    score_administrative_categories,
    score_commercial_categories,
    score_hr_subcategories,
)


class TipoDocumento(str, Enum):
    """Categorías generales reconocidas por la aplicación."""

    FACTURA = "factura"
    LISTA_PRECIOS = "lista_de_precios"
    COMPROBANTE_PAGO = "comprobante_de_pago"
    ORDEN_PAGO = "orden_de_pago"
    RRHH_ALTAS_BAJAS = "recursos_humanos_altas_bajas"
    RRHH_LIQUIDACIONES = "recursos_humanos_liquidaciones"
    RRHH_RECIBOS_LEGAJOS = "recursos_humanos_recibos_legajos"
    RETENCIONES_TRANSFERENCIAS = "retenciones_y_transferencias"
    ESTADO_CUENTA = "estados_de_cuenta"
    MENUS_CARTAS = "menus_y_cartas"
    INSTRUCTIVO = "instructivos"
    ADMINISTRATIVO = "administrativos"
    COMUNICACION = "comunicaciones"
    REMITO_RECIBO = "remitos_y_recibos"
    IMPUESTOS_SERVICIOS = "impuestos_y_servicios"
    OPERATIVO = "operativos"
    CONSORCIO = "consorcio_y_gastos_comunes"
    DESCONOCIDO = "desconocido"


_TYPE_BY_VALUE = {tipo.value: tipo for tipo in TipoDocumento}


@dataclass(frozen=True)
class ResultadoClasificacion:
    """Resultado de clasificación con evidencia útil para diagnóstico."""

    tipo: TipoDocumento
    puntaje_factura: int
    puntaje_lista: int
    motivo: str
    puntajes: dict[str, int] = field(default_factory=dict)
    confianza: str = "ninguna"


def _normalizar(texto: str) -> str:
    """Comparar palabras sin depender de tildes, mayúsculas o saltos de línea."""

    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return re.sub(r"\s+", " ", texto.upper()).strip()


def _score_fiscal(content: str) -> int:
    """Medir evidencia de un comprobante fiscal real.

    No alcanza con encontrar la palabra ``factura``: órdenes de pago y estados
    de cuenta también pueden mencionarla. Por eso se combinan encabezado,
    numeración, datos tributarios y CAE.
    """

    score = 0
    if re.search(r"F\s*A\s*C\s*T\s*U\s*R\s*A|NOTA\s+DE\s+(?:CREDITO|DEBITO)", content):
        score += 5
    if re.search(r"\b(?:FCA|FCB|FCC|NCA|NCB|NCC|NDA|NDB|NDC)\b", content):
        score += 5
    if re.search(r"\b[ABCEMT]\s+\d{1,5}\s*[-/]\s*\d{1,8}\b", content):
        score += 4
    if re.search(r"\b(?:PUNTO DE VENTA|COMP\.?\s*NRO|N[ROº°]*\s*:?\s*\d{1,5}\s*[-/]\s*\d+)", content):
        score += 3
    if "CAE" in content:
        score += 4
    if "CUIT" in content:
        score += 1
    if "RESPONSABLE INSCRIPTO" in content:
        score += 1
    if re.search(r"\b\d{1,2}/\d{1,2}/\d{4}\b", content):
        score += 1
    return score


def _special_payment_type(content: str) -> TipoDocumento | None:
    """Detectar documentos de pago antes de evaluar categorías genéricas."""

    if re.search(r"\bORDEN(?:\s+DE)?\s+PAGO\b|\bOP\s*\d{1,5}\s*[-/]\s*\d+|OP\d{1,5}-\d+", content):
        return TipoDocumento.ORDEN_PAGO
    if re.search(r"\bCOMPROBANTE\s+DE\s+PAGO\b|COMPROBANTEDEPAGO|\bPAGO\s+REALIZADO\b|\bIMPORTE\s+PAGADO\b", content):
        return TipoDocumento.COMPROBANTE_PAGO
    return None


def clasificar_documento(texto: str, nombre_archivo: str = "") -> ResultadoClasificacion:
    """Clasificar un PDF mediante puntajes y umbrales conservadores.

    Una categoría no fiscal se archiva automáticamente solo cuando obtiene al
    menos ocho puntos y supera por tres puntos a la segunda opción. Los casos
    cercanos permanecen en ``_Pendientes`` para evitar movimientos erróneos.
    """

    normalized_text = _normalizar(texto)
    normalized_name = _normalizar(nombre_archivo)
    combined = _normalizar(f"{texto}\n{nombre_archivo}")

    invoice_score = _score_fiscal(combined)
    scores: dict[str, int] = {}
    scores.update(score_hr_subcategories(normalized_text, normalized_name))
    scores.update(score_commercial_categories(normalized_text, normalized_name))
    scores.update(score_administrative_categories(normalized_text, normalized_name))
    for category, points in puntuar_por_nombre_descriptivo(normalized_name).items():
        scores[category] = scores.get(category, 0) + points

    payment_type = _special_payment_type(combined)
    if payment_type is not None and invoice_score < 8:
        return ResultadoClasificacion(
            payment_type,
            invoice_score,
            scores.get(TipoDocumento.LISTA_PRECIOS.value, 0),
            f"El contenido o el nombre identifica un {payment_type.value.replace('_', ' ')}.",
            scores,
            "alta",
        )

    # Algunas categorías no fiscales contienen referencias a facturas, CAE o
    # números de comprobantes relacionados. Un recibo X, una transferencia o
    # una lista de precios no debe convertirse en factura solo por mencionar
    # esos términos. Cuando la categoría alcanza un puntaje inequívoco (10 o
    # más), se le da precedencia antes del parser fiscal.
    strong_non_fiscal = {
        TipoDocumento.INSTRUCTIVO.value,
        TipoDocumento.LISTA_PRECIOS.value,
        TipoDocumento.RETENCIONES_TRANSFERENCIAS.value,
        TipoDocumento.REMITO_RECIBO.value,
        TipoDocumento.CONSORCIO.value,
        TipoDocumento.IMPUESTOS_SERVICIOS.value,
        TipoDocumento.OPERATIVO.value,
        TipoDocumento.ESTADO_CUENTA.value,
    }
    strongest = max(
        ((name, score) for name, score in scores.items() if name in strong_non_fiscal),
        key=lambda item: item[1],
        default=("", 0),
    )
    if strongest[1] >= 10:
        document_type = _TYPE_BY_VALUE[strongest[0]]
        return ResultadoClasificacion(
            document_type,
            invoice_score,
            scores.get(TipoDocumento.LISTA_PRECIOS.value, 0),
            f"La categoría {strongest[0].replace('_', ' ')} reúne evidencia explícita y prioritaria.",
            scores,
            "alta",
        )

    # Una factura con varias señales fiscales independientes mantiene prioridad
    # sobre palabras comerciales que también pueden aparecer en su detalle.
    if invoice_score >= 8:
        return ResultadoClasificacion(
            TipoDocumento.FACTURA,
            invoice_score,
            scores.get(TipoDocumento.LISTA_PRECIOS.value, 0),
            "El documento contiene evidencia fiscal suficiente.",
            scores,
            "alta",
        )

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_name, best_score = ranked[0] if ranked else ("", 0)
    second_score = ranked[1][1] if len(ranked) > 1 else 0

    if best_score >= 8 and best_score - second_score >= 3:
        document_type = _TYPE_BY_VALUE[best_name]
        return ResultadoClasificacion(
            document_type,
            invoice_score,
            scores.get(TipoDocumento.LISTA_PRECIOS.value, 0),
            f"La categoría {best_name.replace('_', ' ')} reúne evidencia suficiente y no ambigua.",
            scores,
            "alta",
        )

    reason = "No existe evidencia suficiente para clasificar automáticamente."
    if best_score:
        reason += f" Mejor candidato: {best_name.replace('_', ' ')} ({best_score} puntos)."
    return ResultadoClasificacion(
        TipoDocumento.DESCONOCIDO,
        invoice_score,
        scores.get(TipoDocumento.LISTA_PRECIOS.value, 0),
        reason,
        scores,
        "ninguna" if best_score == 0 else "baja",
    )
