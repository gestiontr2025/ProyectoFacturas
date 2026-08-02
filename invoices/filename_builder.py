"""Construcción del nombre definitivo de una factura.

Formato acordado:

    DD-MMTipoYNumero_EMPRESA_PROVEEDOR.pdf

Ejemplo:

    31-07FCA00006-00343487_MADERO_ROOF_TOP_HORECA_SRL.pdf
"""

from datetime import datetime

import business_config

from fiscal.definitions import build_fiscal_code
from invoices.text_normalization import normalizar_componente_ruta, quitar_tipo_societario

FORMATOS_FECHA_ADMITIDOS = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d")


def convertir_fecha(fecha: str) -> datetime:
    """Convertir la fecha textual detectada por el parser en ``datetime``."""
    for formato in FORMATOS_FECHA_ADMITIDOS:
        try:
            return datetime.strptime(fecha, formato)
        except (TypeError, ValueError):
            continue
    raise ValueError(f"Formato de fecha no reconocido: {fecha!r}")


def construir_codigo_comprobante(tipo: str, letra: str, numero: str) -> str:
    """Unir el tipo, la letra y el número sin duplicar información.

    ``invoice_parser`` suele devolver ``FACTURA``, ``A`` y
    ``00006-00343487``. El código esperado es ``FCA00006-00343487``.
    """
    tipo_normalizado = normalizar_componente_ruta(tipo, "").replace("_", " ")
    letra_limpia = normalizar_componente_ruta(letra, "").replace("_", "")
    numero_limpio = str(numero or "").strip().replace(" ", "")
    codigo_fiscal = build_fiscal_code(tipo_normalizado, letra_limpia)

    if not codigo_fiscal or not numero_limpio:
        raise ValueError(
            "El tipo, la letra y el número no forman un comprobante fiscal "
            "soportado por el proyecto."
        )

    return f"{codigo_fiscal}{numero_limpio}"


def construir_nombre_factura(datos_factura, razon_social_proveedor: str) -> str:
    """Crear el nombre final a partir de datos ya validados."""
    fecha = convertir_fecha(datos_factura.fecha_emision)
    codigo = construir_codigo_comprobante(
        datos_factura.tipo_comprobante,
        datos_factura.letra_comprobante,
        datos_factura.numero_comprobante,
    )
    empresa = quitar_tipo_societario(business_config.RECEIVER_LEGAL_NAME)
    proveedor = normalizar_componente_ruta(razon_social_proveedor)
    return f"{fecha:%d-%m}{codigo}_{empresa}_{proveedor}.pdf"
