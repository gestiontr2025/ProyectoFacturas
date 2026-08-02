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
import unicodedata
from typing import Optional

from fiscal.definitions import AFIP_CODE_TO_TYPE_AND_LETTER


@dataclass(frozen=True)
class EvidenciaNombreArchivo:
    """Datos fiscales que pudieron inferirse del nombre del archivo."""

    tipo_comprobante: Optional[str] = None
    letra_comprobante: Optional[str] = None
    numero_comprobante: Optional[str] = None
    metodo: Optional[str] = None


# La relación entre códigos AFIP y comprobantes vive en ``fiscal.definitions``.
# Aquí se crea únicamente una vista con claves de tres dígitos porque los
# nombres exportados por ARCA suelen utilizar ``001``, ``006`` o ``011``.
CODIGO_AFIP_A_COMPROBANTE = {
    str(code).zfill(3): value
    for code, value in AFIP_CODE_TO_TYPE_AND_LETTER.items()
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
    # Los nombres pueden contener tildes (CRÉDITO). Normalizamos solo la
    # versión usada para comparar; el nombre real del archivo no se modifica.
    nombre = "".join(
        caracter for caracter in unicodedata.normalize("NFD", nombre)
        if unicodedata.category(caracter) != "Mn"
    )

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

    # Variantes compactas utilizadas por sistemas de gestión:
    #
    #   FACA0000200000032   -> Factura A 00002-00000032
    #   FACB0000700207517   -> Factura B 00007-00207517
    #
    # ``FAC`` significa factura y la letra siguiente pertenece al
    # comprobante. Exigimos 4 o 5 dígitos de punto de venta y exactamente
    # 8 de número para no partir cadenas numéricas de manera arbitraria.
    coincidencia = re.search(
        r"FAC([ABC])(\d{4,5})(\d{8})(?:_ORIG)?$", nombre
    )
    if coincidencia:
        letra, punto_venta, numero = coincidencia.groups()
        return EvidenciaNombreArchivo(
            tipo_comprobante="FACTURA",
            letra_comprobante=letra,
            numero_comprobante=_normalizar_numero(punto_venta, numero),
            metodo="nombre_fac_compacto",
        )

    # Exportaciones de ARCA y nombres descriptivos:
    #
    #   factura_ARCA_A_0022-00001544
    #   Factura de Venta N° A-00002-00002325
    coincidencia = re.search(
        r"\bFACTURA(?:[_ ]+DE[_ ]+VENTA)?(?:[_ ]+ARCA)?[_ ]*(?:NRO|N)?[_ °º]*([ABC])[_ -]*(\d{1,5})[-_](\d{1,8})\b",
        nombre,
    )
    if coincidencia:
        letra, punto_venta, numero = coincidencia.groups()
        return EvidenciaNombreArchivo(
            tipo_comprobante="FACTURA",
            letra_comprobante=letra,
            numero_comprobante=_normalizar_numero(punto_venta, numero),
            metodo="nombre_factura_descriptiva",
        )

    # Algunos ERPs exportan ``Comprobante-FCVTA-A-1-12511``. FCVTA es una
    # abreviatura inequívoca de factura de venta.
    coincidencia = re.search(
        r"\b(?:COMPROBANTE[-_ ]*)?FCVTA[-_ ]*([ABC])[-_ ]*(\d{1,5})[-_ ]*(\d{1,8})\b",
        nombre,
    )
    if coincidencia:
        letra, punto_venta, numero = coincidencia.groups()
        return EvidenciaNombreArchivo(
            tipo_comprobante="FACTURA",
            letra_comprobante=letra,
            numero_comprobante=_normalizar_numero(punto_venta, numero),
            metodo="nombre_fcvta",
        )

    # Notas de crédito y débito escritas de forma descriptiva o compacta:
    # ``Nota de Crédito N° A-00006-00001390`` y ``N_DA0000200000002``.
    coincidencia = re.search(
        r"\bNOTA[_ ]+(?:DE[_ ]+)?(CREDITO|DEBITO)(?:[_ ]+NRO|[_ ]+N)?[_ °º]*([ABC])[-_ ]*(\d{1,5})[-_](\d{1,8})\b",
        nombre,
    )
    if coincidencia:
        clase, letra, punto_venta, numero = coincidencia.groups()
        return EvidenciaNombreArchivo(
            tipo_comprobante="NOTA DE CREDITO" if clase == "CREDITO" else "NOTA DE DEBITO",
            letra_comprobante=letra,
            numero_comprobante=_normalizar_numero(punto_venta, numero),
            metodo="nombre_nota_descriptiva",
        )

    coincidencia = re.search(
        r"\bN[_ -]*D([ABC])(\d{4,5})(\d{8})\b",
        nombre,
    )
    if coincidencia:
        letra, punto_venta, numero = coincidencia.groups()
        return EvidenciaNombreArchivo(
            tipo_comprobante="NOTA DE DEBITO",
            letra_comprobante=letra,
            numero_comprobante=_normalizar_numero(punto_venta, numero),
            metodo="nombre_nd_compacto",
        )


    # Variantes de sistemas de gestión que anteponen palabras comerciales:
    #
    #   Venta_A00013-00032324
    #   M-FACTA0006-00006544
    #
    # Ambos nombres contienen tipo, letra, punto de venta y número de forma
    # inequívoca. Se normalizan sin depender del texto interno del PDF.
    coincidencia = re.search(
        r"\b(?:VENTA[_ -]*A|M[_ -]*FACTA)(\d{1,5})[-_](\d{1,8})\b",
        nombre,
    )
    if coincidencia:
        punto_venta, numero = coincidencia.groups()
        return EvidenciaNombreArchivo(
            tipo_comprobante="FACTURA",
            letra_comprobante="A",
            numero_comprobante=_normalizar_numero(punto_venta, numero),
            metodo="nombre_factura_sistema_gestion",
        )

    # Algunas notas se exportan como ``N CB0001000000768``. La separación
    # irregular no cambia la semántica: NC = Nota de Crédito y B = letra.
    coincidencia = re.search(
        r"\bN[_ -]*C[_ -]*([ABC])(\d{4,5})(\d{8})\b",
        nombre,
    )
    if coincidencia:
        letra, punto_venta, numero = coincidencia.groups()
        return EvidenciaNombreArchivo(
            tipo_comprobante="NOTA DE CREDITO",
            letra_comprobante=letra,
            numero_comprobante=_normalizar_numero(punto_venta, numero),
            metodo="nombre_nc_compacto_flexible",
        )

    # Exportaciones SAP/legacy como:
    # ``V072_CUIT_30504155354_CUIT_30718347463_FACT_A002600360215``.
    # FACT_A va seguido por cuatro dígitos de punto de venta y ocho de número.
    coincidencia = re.search(
        r"FACT[_ -]*([ABC])(\d{4,5})(\d{8})\b",
        nombre,
    )
    if coincidencia:
        letra, punto_venta, numero = coincidencia.groups()
        return EvidenciaNombreArchivo(
            tipo_comprobante="FACTURA",
            letra_comprobante=letra,
            numero_comprobante=_normalizar_numero(punto_venta, numero),
            metodo="nombre_fact_sap_compacto",
        )

    # Un CUIT seguido por ``A-0006-00001163`` aporta letra y número aunque el
    # nombre no incluya la palabra FACTURA. La regla exige el CUIT inicial y
    # ambos componentes numéricos para evitar capturar referencias sueltas.
    coincidencia = re.search(
        r"\b\d{11}[_ -]+([ABC])[-_](\d{1,5})[-_](\d{1,8})\b",
        nombre,
    )
    if coincidencia:
        letra, punto_venta, numero = coincidencia.groups()
        return EvidenciaNombreArchivo(
            letra_comprobante=letra,
            numero_comprobante=_normalizar_numero(punto_venta, numero),
            metodo="nombre_cuit_letra_numero",
        )

    # Formato habitual de ciertos comprobantes electrónicos:
    #   CUIT_CODIGO_AFIP_PUNTO_VENTA_NUMERO.pdf
    # Ejemplo:
    #   27305950136_011_00004_00000375.pdf
    coincidencia = re.search(
        r"\b\d{11}[_-](\d{2,3})[_-](\d{1,5})[_-](\d{1,8})\b",
        nombre,
    )
    if coincidencia:
        codigo_afip, punto_venta, numero = coincidencia.groups()
        tipo_y_letra = CODIGO_AFIP_A_COMPROBANTE.get(codigo_afip.zfill(3))
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
