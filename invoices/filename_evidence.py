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

    tipo_comprobante: Optional[str] = None
    letra_comprobante: Optional[str] = None
    numero_comprobante: Optional[str] = None
    metodo: Optional[str] = None


# Relación oficial entre códigos AFIP y comprobantes comunes A, B y C.
#
# Guardamos tipo y letra por separado porque el resto del proyecto trabaja con
# esos conceptos de forma independiente. Esto permite construir FCA, NCB o NDC
# sin duplicar lógica ni depender de nueve casos especiales.
CODIGO_AFIP_A_COMPROBANTE = {
    "001": ("FACTURA", "A"),
    "002": ("NOTA DE DEBITO", "A"),
    "003": ("NOTA DE CREDITO", "A"),
    "006": ("FACTURA", "B"),
    "007": ("NOTA DE DEBITO", "B"),
    "008": ("NOTA DE CREDITO", "B"),
    "011": ("FACTURA", "C"),
    "012": ("NOTA DE DEBITO", "C"),
    "013": ("NOTA DE CREDITO", "C"),
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
    patrones_tipo_letra_numero = (
        # Formatos espaciados: FC A 0003-00025066, NC B ..., ND C ...
        r"\b(FC|NC|ND)\s*[-_ ]*([ABC])\s*[-_ ]*(\d{1,5})\s*[-_]\s*(\d{1,8})\b",
        # Formatos compactos: FCA000600343487, NCB000300001234...
        r"\b(FC|NC|ND)([ABC])(\d{4,5})(\d{8})\b",
        # Variante histórica FA-A usada por algunos emisores.
        r"\b(FA)\s*[-_ ]*([ABC])\s*[-_ ]*(\d{1,5})\s*[-_]\s*(\d{1,8})\b",
    )
    prefijos = {"FC": "FACTURA", "FA": "FACTURA", "NC": "NOTA DE CREDITO", "ND": "NOTA DE DEBITO"}

    for patron in patrones_tipo_letra_numero:
        coincidencia = re.search(patron, nombre)
        if coincidencia:
            prefijo, letra, punto_venta, numero = coincidencia.groups()
            return EvidenciaNombreArchivo(
                tipo_comprobante=prefijos[prefijo],
                letra_comprobante=letra,
                numero_comprobante=_normalizar_numero(punto_venta, numero),
                metodo="nombre_con_tipo_letra_y_numero",
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
        tipo_y_letra = CODIGO_AFIP_A_COMPROBANTE.get(codigo_afip)
        tipo = tipo_y_letra[0] if tipo_y_letra else None
        letra = tipo_y_letra[1] if tipo_y_letra else None

        # Si el código no está en la tabla, no inferimos tipo ni letra. El
        # número sí puede recuperarse porque su estructura es inequívoca.
        return EvidenciaNombreArchivo(
            tipo_comprobante=tipo,
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
