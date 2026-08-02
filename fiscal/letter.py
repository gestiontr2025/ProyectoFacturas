"""Detección defensiva de la letra fiscal A, B o C.

La letra de un comprobante puede aparecer en distintos lugares según el
programa que generó el PDF. Algunos extractores devuelven ``FACTURA C``;
otros invierten el orden y producen ``C FACTURA``. Los comprobantes emitidos
por ARCA también incluyen un código numérico que permite confirmar la letra.

Este módulo combina esas evidencias sin aceptar una letra aislada: una simple
``A`` podría pertenecer a una dirección o a la descripción de un producto.
"""

import re
from typing import Optional

from fiscal.normalization import normalizar_para_busqueda
from fiscal.type_detector import detectar_tipo_comprobante

LETRAS_VALIDAS = {"A", "B", "C"}

# Códigos de comprobantes utilizados por ARCA/AFIP. La clave combina el tipo
# fiscal y el código numérico normalizado sin ceros a la izquierda.
#
# Ejemplos reales:
#   COD 01  + FACTURA -> A
#   COD 011 + FACTURA -> C
_CODIGOS_POR_TIPO = {
    "FACTURA": {1: "A", 6: "B", 11: "C"},
    "NOTA DE DEBITO": {2: "A", 7: "B", 12: "C"},
    "NOTA DE CREDITO": {3: "A", 8: "B", 13: "C"},
}


def _detectar_por_codigo_arca(texto: str, tipo: str) -> Optional[str]:
    """Inferir la letra a partir de ``COD`` cuando el tipo ya es conocido.

    El código no se interpreta solo. Vincularlo con el tipo evita, por ejemplo,
    confundir el código 11 de una Factura C con otro número administrativo que
    aparezca casualmente en el documento.
    """
    mapa = _CODIGOS_POR_TIPO.get(tipo)
    if not mapa:
        return None

    for coincidencia in re.finditer(r"COD(?:IGO)?\.?\s*[:\-]?\s*0*(\d{1,3})\b", texto):
        codigo = int(coincidencia.group(1))
        letra = mapa.get(codigo)
        if letra:
            return letra
    return None


def detectar_letra_comprobante(texto: str) -> Optional[str]:
    """Detectar la letra únicamente cuando existe contexto fiscal suficiente.

    Estrategia, de mayor a menor evidencia:

    1. Tipo seguido por letra: ``FACTURA A``.
    2. Letra antes del tipo: ``C FACTURA`` o ``A COD 01 FACTURA``.
    3. Abreviaturas fiscales: ``FC A``, ``NC B`` o ``ND C``.
    4. Etiqueta explícita: ``LETRA: A``.
    5. Código oficial ARCA/AFIP compatible con el tipo detectado.
    6. Letra inmediatamente unida al número fiscal.

    Si ninguna evidencia es suficientemente específica se devuelve ``None``.
    Es preferible revisar manualmente un documento antes que asignarle una
    letra incorrecta y archivarlo con un nombre fiscal falso.
    """
    texto = normalizar_para_busqueda(texto)
    if not texto:
        return None

    tipo = detectar_tipo_comprobante(texto)

    patrones = (
        # Formato tradicional: FACTURA A / NOTA DE CREDITO B.
        r"\b(?:FACTURA|NOTA\s+(?:DE\s+)?CREDITO|NOTA\s+(?:DE\s+)?DEBITO)\s*[-:]?\s*([ABC])\b",
        # Formato ARCA y Colppy: C FACTURA o A COD 01 FACTURA.
        r"\b([ABC])\s+(?:COD(?:IGO)?\.?\s*0*\d{1,3}\s+)?(?:FACTURA|NOTA\s+(?:DE\s+)?CREDITO|NOTA\s+(?:DE\s+)?DEBITO)\b",
        r"\b(?:FC|NC|ND)\s*[-_/ ]*([ABC])\b",
        r"\bLETRA\s*[:\-]?\s*([ABC])\b",
    )
    for patron in patrones:
        coincidencia = re.search(patron, texto)
        if coincidencia:
            return coincidencia.group(1)

    if tipo:
        letra_por_codigo = _detectar_por_codigo_arca(texto, tipo)
        if letra_por_codigo:
            return letra_por_codigo

        coincidencia = re.search(
            r"\b([ABC])\s+(\d{1,5})\s*[-/]\s*(\d{1,8})\b", texto
        )
        if coincidencia:
            return coincidencia.group(1)

    return None
