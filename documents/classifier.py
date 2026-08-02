"""Clasificación defensiva de documentos PDF.

No todo PDF administrativo es un comprobante fiscal. Clasificar antes de usar
el parser de facturas mantiene ``_Pendientes`` reservado para casos realmente
ambiguos y permite archivar material auxiliar en carpetas comprensibles.
"""

from dataclasses import dataclass
from enum import Enum
import re
import unicodedata


class TipoDocumento(str, Enum):
    """Tipos generales que reconoce actualmente la aplicación."""

    FACTURA = "factura"
    LISTA_PRECIOS = "lista_de_precios"
    COMPROBANTE_PAGO = "comprobante_de_pago"
    ORDEN_PAGO = "orden_de_pago"
    DESCONOCIDO = "desconocido"


@dataclass(frozen=True)
class ResultadoClasificacion:
    """Resultado explicable de la clasificación de un PDF."""

    tipo: TipoDocumento
    puntaje_factura: int
    puntaje_lista: int
    motivo: str


def _normalizar(texto: str) -> str:
    """Preparar texto para comparar palabras sin depender de tildes o mayúsculas."""

    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return re.sub(r"\s+", " ", texto.upper()).strip()


def clasificar_documento(texto: str, nombre_archivo: str = "") -> ResultadoClasificacion:
    """Clasificar un PDF usando varias señales y prioridades explícitas.

    El nombre aporta evidencia secundaria, mientras que el contenido es la
    fuente principal. Una señal fiscal fuerte siempre tiene prioridad para no
    confundir el detalle de una factura con una lista comercial.
    """

    contenido = _normalizar(f"{texto}\n{nombre_archivo}")
    puntaje_factura = 0
    puntaje_lista = 0

    if re.search(r"F\s*A\s*C\s*T\s*U\s*R\s*A|NOTA\s+DE\s+(?:CREDITO|DEBITO)", contenido):
        puntaje_factura += 5
    if re.search(r"\b[ABCEMT]\s+\d{1,5}\s*[-/]\s*\d{1,8}\b", contenido):
        puntaje_factura += 4
    if re.search(r"\b(?:CAE|CUIT|PUNTO DE VENTA|RESPONSABLE INSCRIPTO)\b", contenido):
        puntaje_factura += 2
    if re.search(r"\b\d{1,2}/\d{1,2}/\d{4}\b", contenido):
        puntaje_factura += 1

    indicadores_lista = (
        "LISTA", "CODIGO", "PRESENTACION", "PRECIO", "PRECIO SUGERIDO",
        "$ X BOT", "$ X BOTELLA", "$ X UNID",
    )
    puntaje_lista += sum(1 for indicador in indicadores_lista if indicador in contenido)

    if puntaje_factura >= 5:
        return ResultadoClasificacion(
            TipoDocumento.FACTURA, puntaje_factura, puntaje_lista,
            "El documento contiene evidencia fiscal suficiente.",
        )

    # Estas categorías se evalúan después de descartar una factura clara. Una
    # orden de pago puede mencionar facturas imputadas, pero no es una factura.
    if re.search(r"\bORDEN(?:\s+DE)?\s+PAGO\b|\bOP\s*\d{1,5}\s*[-/]\s*\d+|OP\d{1,5}-\d+", contenido):
        return ResultadoClasificacion(
            TipoDocumento.ORDEN_PAGO, puntaje_factura, puntaje_lista,
            "El contenido o el nombre identifica una orden de pago.",
        )

    if re.search(r"\bCOMPROBANTE\s+DE\s+PAGO\b|COMPROBANTEDEPAGO|\bPAGO\s+REALIZADO\b|\bIMPORTE\s+PAGADO\b", contenido):
        return ResultadoClasificacion(
            TipoDocumento.COMPROBANTE_PAGO, puntaje_factura, puntaje_lista,
            "El contenido o el nombre identifica un comprobante de pago.",
        )

    if puntaje_lista >= 4 and puntaje_factura < 3:
        return ResultadoClasificacion(
            TipoDocumento.LISTA_PRECIOS, puntaje_factura, puntaje_lista,
            "Predominan señales de una lista comercial y no de una factura.",
        )

    return ResultadoClasificacion(
        TipoDocumento.DESCONOCIDO, puntaje_factura, puntaje_lista,
        "No existe evidencia suficiente para clasificar automáticamente.",
    )
