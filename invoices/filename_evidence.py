"""Extracción de datos fiscales desde el nombre original de un PDF.

Este módulo funciona como una fuente de evidencia secundaria.

La información principal siempre debe obtenerse del contenido de la factura.
Sin embargo, algunos sistemas de facturación generan nombres de archivo muy
estructurados aunque el texto interno del PDF quede desordenado al extraerse.
En esos casos, el nombre puede completar datos faltantes sin reemplazar lo que
ya fue detectado dentro del documento.

Ejemplos reales contemplados:

- ``FC A 0003-00025066 MADERO ROOF TOP SA.pdf``
- ``FA-A 00040-00069092.pdf``
- ``27305950136_011_00004_00000375.pdf``

El código AFIP ``011`` representa una Factura C. La tabla se mantiene pequeña
y explícita para evitar inferencias silenciosas sobre códigos desconocidos.
"""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Optional


@dataclass(frozen=True)
class EvidenciaNombreArchivo:
    """Datos fiscales que pudieron inferirse del nombre del archivo."""

    letra_comprobante: Optional[str] = None
    numero_comprobante: Optional[str] = None
    metodo: Optional[str] = None


# Códigos de comprobante AFIP que aparecen en nombres generados por algunos
# sistemas. Solo incluimos códigos conocidos y usados por este proyecto.
CODIGO_AFIP_A_LETRA = {
    "001": "A",  # Factura A
    "006": "B",  # Factura B
    "011": "C",  # Factura C
}


def _normalizar_numero(punto_venta: str, numero: str) -> str:
    """Aplicar el ancho estándar usado por el proyecto."""

    return f"{punto_venta.zfill(5)}-{numero.zfill(8)}"


def extraer_evidencia_nombre_archivo(nombre_archivo: str) -> EvidenciaNombreArchivo:
    """Extraer letra y número desde formatos conocidos de nombres de PDF.

    La función no intenta adivinar datos. Solo devuelve valores cuando el
    nombre coincide con un patrón suficientemente específico.
    """

    nombre = Path(nombre_archivo).stem.upper()

    # Formatos como:
    #   FC A 0003-00025066 ...
    #   FA-A 00040-00069092
    #   FCA000600343487
    patrones_letra_y_numero = (
        r"\bF(?:ACTURA|C|A)?\s*[-_ ]*([ABC])\s*[-_ ]*(\d{1,5})\s*[-_]\s*(\d{1,8})\b",
        r"\bFC([ABC])(\d{4,5})(\d{8})\b",
    )

    for patron in patrones_letra_y_numero:
        coincidencia = re.search(patron, nombre)
        if coincidencia:
            letra, punto_venta, numero = coincidencia.groups()
            return EvidenciaNombreArchivo(
                letra_comprobante=letra,
                numero_comprobante=_normalizar_numero(punto_venta, numero),
                metodo="nombre_con_letra_y_numero",
            )

    # Formato habitual de ciertos comprobantes electrónicos:
    #   CUIT_CODIGO_AFIP_PUNTO_VENTA_NUMERO.pdf
    # Ejemplo:
    #   27305950136_011_00004_00000375.pdf
    coincidencia = re.search(
        r"\b\d{11}[_-](\d{3})[_-](\d{1,5})[_-](\d{1,8})\b",
        nombre,
    )
    if coincidencia:
        codigo_afip, punto_venta, numero = coincidencia.groups()
        letra = CODIGO_AFIP_A_LETRA.get(codigo_afip)

        # Si el código no está en la tabla, no inferimos la letra. El número sí
        # puede recuperarse porque su estructura es inequívoca.
        return EvidenciaNombreArchivo(
            letra_comprobante=letra,
            numero_comprobante=_normalizar_numero(punto_venta, numero),
            metodo="nombre_con_codigo_afip",
        )

    # Respaldo limitado: nombres como ``Factura 0004-00219487`` permiten
    # recuperar el número, pero no la letra. La letra seguirá pendiente hasta
    # que pueda detectarse dentro del PDF o mediante una regla específica.
    coincidencia = re.search(
        r"\bFACTURA\s*(\d{1,5})\s*[-_]\s*(\d{1,8})\b",
        nombre,
    )
    if coincidencia:
        punto_venta, numero = coincidencia.groups()
        return EvidenciaNombreArchivo(
            numero_comprobante=_normalizar_numero(punto_venta, numero),
            metodo="nombre_con_numero",
        )

    return EvidenciaNombreArchivo()
