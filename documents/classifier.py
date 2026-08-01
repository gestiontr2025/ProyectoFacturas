"""Clasificación defensiva de documentos PDF.

No todo PDF adjunto a un correo administrativo es una factura. También pueden
llegar listas de precios, catálogos o material informativo. Este módulo decide
qué recorrido debe seguir cada documento antes de ejecutar el parser fiscal.
"""

from dataclasses import dataclass
from enum import Enum
import re
import unicodedata


class TipoDocumento(str, Enum):
    """Tipos generales que reconoce actualmente la aplicación."""

    FACTURA = "factura"
    LISTA_PRECIOS = "lista_de_precios"
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
    """Clasificar un PDF utilizando varias señales, no una única palabra.

    La clasificación usa puntajes para evitar decisiones frágiles. La palabra
    ``IVA``, por ejemplo, puede aparecer tanto en una factura como en una lista
    de precios; en cambio, la combinación ``FACTURA`` + número fiscal + fecha
    ofrece evidencia mucho más fuerte.
    """

    contenido = _normalizar(f"{texto}\n{nombre_archivo}")

    puntaje_factura = 0
    puntaje_lista = 0

    if re.search(r"F\s*A\s*C\s*T\s*U\s*R\s*A", contenido):
        puntaje_factura += 5
    if re.search(r"\b[ABCEMT]\s+\d{1,5}\s*[-/]\s*\d{1,8}\b", contenido):
        puntaje_factura += 4
    if re.search(r"\b(?:CAE|CUIT|PUNTO DE VENTA|RESPONSABLE INSCRIPTO)\b", contenido):
        puntaje_factura += 2
    if re.search(r"\b\d{1,2}/\d{1,2}/\d{4}\b", contenido):
        puntaje_factura += 1

    indicadores_lista = (
        "LISTA",
        "CODIGO",
        "PRESENTACION",
        "PRECIO",
        "PRECIO SUGERIDO",
        "$ X BOT",
        "$ X BOTELLA",
        "$ X UNID",
    )
    puntaje_lista += sum(1 for indicador in indicadores_lista if indicador in contenido)

    # Una factura claramente identificada siempre tiene prioridad sobre señales
    # comerciales secundarias que también podrían aparecer en su detalle.
    if puntaje_factura >= 5:
        return ResultadoClasificacion(
            tipo=TipoDocumento.FACTURA,
            puntaje_factura=puntaje_factura,
            puntaje_lista=puntaje_lista,
            motivo="El documento contiene evidencia fiscal suficiente.",
        )

    if puntaje_lista >= 4 and puntaje_factura < 3:
        return ResultadoClasificacion(
            tipo=TipoDocumento.LISTA_PRECIOS,
            puntaje_factura=puntaje_factura,
            puntaje_lista=puntaje_lista,
            motivo="Predominan señales de una lista comercial y no de una factura.",
        )

    return ResultadoClasificacion(
        tipo=TipoDocumento.DESCONOCIDO,
        puntaje_factura=puntaje_factura,
        puntaje_lista=puntaje_lista,
        motivo="No existe evidencia suficiente para clasificar automáticamente.",
    )
