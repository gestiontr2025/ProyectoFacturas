"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Archivo
-------
invoice_parser.py

Descripción
-----------
Este módulo se encarga de extraer información estructurada
desde el texto de una factura o comprobante.

Forma parte del desarrollo de la versión 0.15 del proyecto.

Responsabilidades
-----------------
Este módulo puede:

- Recibir texto extraído previamente desde un archivo PDF.
- Normalizar el texto para facilitar su análisis.
- Detectar el tipo de comprobante.
- Detectar la letra del comprobante.
- Detectar el número del comprobante.
- Detectar la fecha de emisión.
- Detectar el CUIT del emisor.
- Detectar el CUIT del receptor.
- Detectar la moneda.
- Detectar el subtotal.
- Detectar impuestos.
- Detectar el importe total.
- Detectar el CAE.
- Detectar la fecha de vencimiento del CAE.
- Devolver los resultados mediante estructuras ordenadas.

Regla de moneda
---------------
Debido a que la gran mayoría de los comprobantes procesados
por este proyecto estarán expresados en pesos argentinos,
se utiliza la siguiente regla:

- Si el documento contiene una indicación explícita de
  dólares, se devuelve USD.

- En cualquier otro caso, se devuelve ARS.

Indicaciones reconocidas como dólares:

- USD
- U$S
- US$
- DÓLAR
- DÓLARES

No debe
-------
Este módulo no debe:

- Conectarse con Gmail.
- Descargar archivos adjuntos.
- Abrir directamente archivos PDF.
- Detectar el proveedor comercial.
- Crear carpetas.
- Mover archivos.
- Renombrar facturas.
- Mostrar la salida definitiva del programa principal.

Autor
-----
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# INICIO DEL BLOQUE DE IMPORTACIONES
# ==========================================================

from __future__ import annotations

import re
import unicodedata

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional

from fiscal import (
    analizar_encabezado_fiscal as _analizar_encabezado_fiscal,
    detectar_fecha_emision as _detectar_fecha_fiscal,
    detectar_letra_comprobante as _detectar_letra_fiscal,
    detectar_numero_comprobante as _detectar_numero_fiscal,
    detectar_tipo_comprobante as _detectar_tipo_fiscal,
)

# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE CONSTANTES
# ==========================================================

# ----------------------------------------------------------
# Letras de comprobante contempladas inicialmente.
# ----------------------------------------------------------

LETRAS_COMPROBANTE_VALIDAS: set[str] = {
    "A",
    "B",
    "C",
    "E",
    "M",
    "T",
}


# ----------------------------------------------------------
# Tipos de comprobantes contemplados inicialmente.
#
# El orden resulta importante: se buscan primero las
# expresiones más específicas.
# ----------------------------------------------------------

TIPOS_COMPROBANTE_VALIDOS: tuple[str, ...] = (
    "NOTA DE CREDITO",
    "NOTA DE DEBITO",
    "FACTURA",
    "RECIBO",
    "TICKET",
)


# ----------------------------------------------------------
# Patrón reutilizable para reconocer importes.
#
# Ejemplos:
#
#     100000
#     100.000,00
#     100,000.00
#     121000,50
#
# El patrón no incluye el símbolo monetario. Los símbolos
# son tratados por las funciones que utilizan este patrón.
# ----------------------------------------------------------

PATRON_IMPORTE = (
    r"("
    r"-?"
    r"(?:"
    r"\d{1,3}(?:[.,]\d{3})+"
    r"|"
    r"\d+"
    r")"
    r"(?:[.,]\d{1,2})?"
    r")"
)


# ----------------------------------------------------------
# Patrón reutilizable para reconocer fechas.
#
# IMPORTANTE:
#
# Se busca primero el año de cuatro dígitos.
#
# La alternativa correcta es:
#
#     \d{4}|\d{2}
#
# y no:
#
#     \d{2}|\d{4}
#
# Si se buscaban primero dos dígitos, Python podía tomar
# solamente "20" dentro del año "2026".
# ----------------------------------------------------------

PATRON_FECHA = (
    r"("
    r"\d{1,2}"
    r"[./-]"
    r"\d{1,2}"
    r"[./-]"
    r"(?:\d{4}|\d{2})"
    r")"
)

# ==========================================================
# FIN DEL BLOQUE DE CONSTANTES
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE ESTRUCTURAS DE DATOS
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA CLASE DatosFactura
# ----------------------------------------------------------

@dataclass
class DatosFactura:
    """
    Representar los datos principales extraídos de una
    factura.

    Todos los campos son opcionales.

    Un campo contiene None cuando:

    - El dato no aparece en el documento.
    - El texto no pudo extraerse correctamente.
    - El formato todavía no está contemplado.
    - El dato se encuentra dentro de una imagen.
    """

    tipo_comprobante: Optional[str] = None
    letra_comprobante: Optional[str] = None
    numero_comprobante: Optional[str] = None
    fecha_emision: Optional[str] = None

    cuit_emisor: Optional[str] = None
    razon_social_emisor: Optional[str] = None

    cuit_receptor: Optional[str] = None
    razon_social_receptor: Optional[str] = None

    moneda: Optional[str] = None
    subtotal: Optional[str] = None
    impuestos: Optional[str] = None
    importe_total: Optional[str] = None

    cae: Optional[str] = None
    vencimiento_cae: Optional[str] = None


    # ------------------------------------------------------
    # INICIO DE LA FUNCIÓN convertir_a_diccionario()
    # ------------------------------------------------------

    def convertir_a_diccionario(
        self
    ) -> dict[str, Optional[str]]:
        """
        Convertir DatosFactura en un diccionario común.

        Esto será útil para:

        - Mostrar los datos.
        - Guardarlos en JSON.
        - Guardarlos en Excel.
        - Crear nombres de archivo.
        - Enviarlos a otros módulos.

        Retorna
        -------
        dict

            Diccionario con todos los campos.
        """

        return asdict(self)

    # ------------------------------------------------------
    # FIN DE LA FUNCIÓN convertir_a_diccionario()
    # ------------------------------------------------------


# ----------------------------------------------------------
# FIN DE LA CLASE DatosFactura
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA CLASE ResultadoParseoFactura
# ----------------------------------------------------------

@dataclass
class ResultadoParseoFactura:
    """
    Representar el resultado completo del análisis.

    Atributos
    ---------
    exito:

        Indica si el texto pudo analizarse.

    datos:

        Estructura DatosFactura con los valores encontrados.

    mensaje:

        Descripción general del resultado.

    texto_normalizado:

        Texto limpio utilizado durante el análisis.
    """

    exito: bool
    datos: DatosFactura
    mensaje: str
    texto_normalizado: str = ""
    analisis_fiscal: object | None = None


    # ------------------------------------------------------
    # INICIO DE LA FUNCIÓN convertir_a_diccionario()
    # ------------------------------------------------------

    def convertir_a_diccionario(self) -> dict:
        """
        Convertir el resultado completo en un diccionario.

        Retorna
        -------
        dict

            Diccionario con el estado, el mensaje, los datos
            y el texto normalizado.
        """

        return {
            "exito": self.exito,
            "mensaje": self.mensaje,
            "datos": self.datos.convertir_a_diccionario(),
            "texto_normalizado": self.texto_normalizado,
            "analisis_fiscal": (
                self.analisis_fiscal.to_dict()
                if hasattr(self.analisis_fiscal, "to_dict")
                else self.analisis_fiscal
            ),
        }

    # ------------------------------------------------------
    # FIN DE LA FUNCIÓN convertir_a_diccionario()
    # ------------------------------------------------------


# ----------------------------------------------------------
# FIN DE LA CLASE ResultadoParseoFactura
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE ESTRUCTURAS DE DATOS
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE NORMALIZACIÓN DE TEXTO
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN normalizar_texto()
# ----------------------------------------------------------

def normalizar_texto(texto: str) -> str:
    """
    Normalizar el texto extraído desde un PDF.

    La función:

    - Unifica caracteres Unicode.
    - Normaliza saltos de línea.
    - Elimina tabulaciones.
    - Reduce espacios repetidos.
    - Elimina líneas vacías.
    - Conserva la separación por líneas.

    Parámetros
    ----------
    texto:

        Texto original extraído desde el PDF.

    Retorna
    -------
    str

        Texto normalizado.

        Devuelve una cadena vacía si el valor recibido no es
        una cadena.
    """

    if not isinstance(texto, str):
        return ""

    texto_normalizado = unicodedata.normalize(
        "NFKC",
        texto
    )

    texto_normalizado = texto_normalizado.replace(
        "\r\n",
        "\n"
    )

    texto_normalizado = texto_normalizado.replace(
        "\r",
        "\n"
    )

    lineas_limpias: list[str] = []

    for linea in texto_normalizado.split("\n"):

        linea = re.sub(
            r"[ \t]+",
            " ",
            linea
        )

        linea = linea.strip()

        if linea:

            lineas_limpias.append(
                linea
            )

    return "\n".join(
        lineas_limpias
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN normalizar_texto()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN normalizar_texto_para_busqueda()
# ----------------------------------------------------------

def normalizar_texto_para_busqueda(texto: str) -> str:
    """
    Crear una versión simplificada del texto para realizar
    búsquedas.

    La función:

    - Convierte el texto a mayúsculas.
    - Elimina acentos.
    - Normaliza espacios horizontales.
    - Conserva los saltos de línea.
    - Conserva números y signos importantes.

    Parámetros
    ----------
    texto:

        Texto original o previamente normalizado.

    Retorna
    -------
    str

        Texto preparado para búsquedas.
    """

    texto_normalizado = normalizar_texto(
        texto
    )

    if not texto_normalizado:
        return ""

    texto_descompuesto = unicodedata.normalize(
        "NFD",
        texto_normalizado
    )

    texto_sin_acentos = "".join(
        caracter
        for caracter in texto_descompuesto
        if unicodedata.category(caracter) != "Mn"
    )

    texto_busqueda = texto_sin_acentos.upper()

    texto_busqueda = re.sub(
        r"[ \t]+",
        " ",
        texto_busqueda
    )

    return texto_busqueda.strip()

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN normalizar_texto_para_busqueda()
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE NORMALIZACIÓN DE TEXTO
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE FUNCIONES DE LIMPIEZA
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN limpiar_cuit()
# ----------------------------------------------------------

def limpiar_cuit(cuit: Optional[str]) -> Optional[str]:
    """
    Limpiar y normalizar un CUIT argentino.

    Formatos admitidos:

        30-12345678-9
        30 12345678 9
        30123456789

    Resultado:

        30-12345678-9

    Parámetros
    ----------
    cuit:

        Texto que contiene el CUIT.

    Retorna
    -------
    str | None

        CUIT normalizado o None.
    """

    if not cuit:
        return None

    solo_digitos = re.sub(
        r"\D",
        "",
        cuit
    )

    if len(solo_digitos) != 11:
        return None

    return (
        f"{solo_digitos[0:2]}-"
        f"{solo_digitos[2:10]}-"
        f"{solo_digitos[10]}"
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN limpiar_cuit()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN limpiar_numero_comprobante()
# ----------------------------------------------------------

def limpiar_numero_comprobante(
    numero_comprobante: Optional[str],
) -> Optional[str]:
    """
    Normalizar un número de comprobante argentino.

    Ejemplos:

        3-1234
        00003-00001234
        00003 / 00001234

    Resultado:

        00003-00001234

    Parámetros
    ----------
    numero_comprobante:

        Texto que contiene el número.

    Retorna
    -------
    str | None

        Número normalizado o None.
    """

    if not numero_comprobante:
        return None

    coincidencia = re.search(
        r"(?<!\d)"
        r"(\d{1,5})"
        r"\s*[-/ ]\s*"
        r"(\d{1,8})"
        r"(?!\d)",
        numero_comprobante
    )

    if not coincidencia:
        return None

    punto_venta = coincidencia.group(1).zfill(5)
    numero = coincidencia.group(2).zfill(8)

    return f"{punto_venta}-{numero}"

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN limpiar_numero_comprobante()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN limpiar_fecha()
# ----------------------------------------------------------

def limpiar_fecha(fecha: Optional[str]) -> Optional[str]:
    """
    Normalizar una fecha al formato DD/MM/AAAA.

    Formatos admitidos:

        31/07/2026
        31-07-2026
        31.07.2026
        31/07/26

    Para años de dos dígitos:

        00 a 79 -> 2000 a 2079
        80 a 99 -> 1980 a 1999

    Parámetros
    ----------
    fecha:

        Texto que contiene la fecha.

    Retorna
    -------
    str | None

        Fecha normalizada o None.
    """

    if not fecha:
        return None

    # ------------------------------------------------------
    # Se buscan primero cuatro dígitos para evitar que:
    #
    #     2026
    #
    # sea interpretado solamente como:
    #
    #     20
    # ------------------------------------------------------

    coincidencia = re.search(
        r"(?<!\d)"
        r"(\d{1,2})"
        r"[./-]"
        r"(\d{1,2})"
        r"[./-]"
        r"(\d{4}|\d{2})"
        r"(?!\d)",
        fecha
    )

    if not coincidencia:
        return None

    dia = int(
        coincidencia.group(1)
    )

    mes = int(
        coincidencia.group(2)
    )

    texto_anio = coincidencia.group(3)

    if len(texto_anio) == 2:

        anio_corto = int(
            texto_anio
        )

        if anio_corto <= 79:

            anio = 2000 + anio_corto

        else:

            anio = 1900 + anio_corto

    else:

        anio = int(
            texto_anio
        )

    try:

        fecha_validada = datetime(
            year=anio,
            month=mes,
            day=dia
        )

    except ValueError:

        return None

    return fecha_validada.strftime(
        "%d/%m/%Y"
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN limpiar_fecha()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN limpiar_importe()
# ----------------------------------------------------------

def limpiar_importe(
    importe: Optional[str]
) -> Optional[str]:
    """
    Normalizar un importe monetario.

    Ejemplos:

        $ 1.234,56
        1234,56
        1,234.56
        ARS 1234
        USD 1,234.56

    Resultado:

        1234.56

    Parámetros
    ----------
    importe:

        Texto que contiene el importe.

    Retorna
    -------
    str | None

        Importe normalizado o None.
    """

    if not importe:
        return None

    valor = str(
        importe
    ).upper()

    valor = re.sub(
        r"\b(?:ARS|USD|PESOS?|DOLARES?)\b",
        "",
        valor
    )

    valor = valor.replace(
        "U$S",
        ""
    )

    valor = valor.replace(
        "US$",
        ""
    )

    valor = valor.replace(
        "$",
        ""
    )

    valor = re.sub(
        r"[^0-9,.\-]",
        "",
        valor
    )

    if not valor:
        return None

    if valor.count("-") > 1:
        return None

    es_negativo = valor.startswith(
        "-"
    )

    valor = valor.replace(
        "-",
        ""
    )

    if not valor:
        return None

    ultima_coma = valor.rfind(
        ","
    )

    ultimo_punto = valor.rfind(
        "."
    )

    if "," in valor and "." in valor:

        if ultima_coma > ultimo_punto:

            # Formato argentino:
            #
            #     1.234,56
            #
            # se convierte en:
            #
            #     1234.56

            valor = valor.replace(
                ".",
                ""
            )

            valor = valor.replace(
                ",",
                "."
            )

        else:

            # Formato internacional:
            #
            #     1,234.56
            #
            # se convierte en:
            #
            #     1234.56

            valor = valor.replace(
                ",",
                ""
            )

    elif "," in valor:

        partes = valor.split(
            ","
        )

        if len(partes[-1]) in (1, 2):

            parte_entera = "".join(
                partes[:-1]
            )

            parte_decimal = partes[-1]

            valor = (
                f"{parte_entera}."
                f"{parte_decimal}"
            )

        else:

            valor = "".join(
                partes
            )

    elif "." in valor:

        partes = valor.split(
            "."
        )

        if len(partes[-1]) in (1, 2):

            parte_entera = "".join(
                partes[:-1]
            )

            parte_decimal = partes[-1]

            valor = (
                f"{parte_entera}."
                f"{parte_decimal}"
            )

        else:

            valor = "".join(
                partes
            )

    if valor.count(".") > 1:
        return None

    parte_entera, separador, parte_decimal = valor.partition(
        "."
    )

    if not parte_entera:

        parte_entera = "0"

    parte_entera = (
        parte_entera.lstrip("0")
        or
        "0"
    )

    if separador:

        parte_decimal = parte_decimal.ljust(
            2,
            "0"
        )[:2]

        valor_normalizado = (
            f"{parte_entera}."
            f"{parte_decimal}"
        )

    else:

        valor_normalizado = (
            f"{parte_entera}.00"
        )

    if es_negativo:

        valor_normalizado = (
            f"-{valor_normalizado}"
        )

    return valor_normalizado

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN limpiar_importe()
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE FUNCIONES DE LIMPIEZA
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE FUNCIONES AUXILIARES PARA CUIT
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN extraer_cuits_en_orden()
# ----------------------------------------------------------

def extraer_cuits_en_orden(texto: str) -> list[str]:
    """
    Extraer todos los CUIT respetando su orden de aparición.

    Los CUIT duplicados se devuelven una sola vez.

    Parámetros
    ----------
    texto:

        Texto de la factura.

    Retorna
    -------
    list

        Lista de CUIT normalizados.
    """

    if not isinstance(texto, str):
        return []

    patron_cuit = (
        r"(?<!\d)"
        r"(\d{2})"
        r"\s*[- ]?\s*"
        r"(\d{8})"
        r"\s*[- ]?\s*"
        r"(\d)"
        r"(?!\d)"
    )

    cuits_encontrados: list[str] = []

    for coincidencia in re.finditer(
        patron_cuit,
        texto
    ):

        cuit_sin_formato = "".join(
            coincidencia.groups()
        )

        cuit_normalizado = limpiar_cuit(
            cuit_sin_formato
        )

        if not cuit_normalizado:
            continue

        if cuit_normalizado not in cuits_encontrados:

            cuits_encontrados.append(
                cuit_normalizado
            )

    return cuits_encontrados

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN extraer_cuits_en_orden()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN buscar_cuit_cerca_de_etiquetas()
# ----------------------------------------------------------

def buscar_cuit_cerca_de_etiquetas(
    texto: str,
    etiquetas: tuple[str, ...],
) -> Optional[str]:
    """
    Buscar un CUIT ubicado después de una etiqueta.

    Parámetros
    ----------
    texto:

        Texto normalizado para búsquedas.

    etiquetas:

        Tupla de expresiones regulares.

    Retorna
    -------
    str | None

        CUIT normalizado o None.
    """

    patron_cuit = (
        r"(\d{2}"
        r"\s*[- ]?\s*"
        r"\d{8}"
        r"\s*[- ]?\s*"
        r"\d)"
    )

    for etiqueta in etiquetas:

        patron_completo = (
            etiqueta
            +
            r"\s*[:\-]?\s*"
            +
            patron_cuit
        )

        coincidencia = re.search(
            patron_completo,
            texto
        )

        if coincidencia:

            return limpiar_cuit(
                coincidencia.group(1)
            )

    return None

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN buscar_cuit_cerca_de_etiquetas()
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE FUNCIONES AUXILIARES PARA CUIT
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE FUNCIONES AUXILIARES PARA IMPORTES
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN buscar_importe_por_etiquetas()
# ----------------------------------------------------------

def buscar_importe_por_etiquetas(
    texto: str,
    etiquetas: tuple[str, ...],
) -> Optional[str]:
    """
    Buscar un importe ubicado después de una etiqueta.

    Ejemplos:

        SUBTOTAL: $ 100.000,00
        TOTAL: 121.000,00
        NETO GRAVADO $ 70.661,16

    Parámetros
    ----------
    texto:

        Texto de la factura.

    etiquetas:

        Tupla de expresiones regulares.

    Retorna
    -------
    str | None

        Importe normalizado o None.
    """

    texto_busqueda = normalizar_texto_para_busqueda(
        texto
    )

    if not texto_busqueda:
        return None

    for etiqueta in etiquetas:

        patron_completo = (
            etiqueta
            +
            r"\s*"
            r"[:\-]?"
            r"\s*"
            r"(?:ARS|USD|U\$S|US\$|\$)?"
            r"\s*"
            +
            PATRON_IMPORTE
        )

        coincidencia = re.search(
            patron_completo,
            texto_busqueda
        )

        if coincidencia:

            importe_normalizado = limpiar_importe(
                coincidencia.group(1)
            )

            if importe_normalizado:

                return importe_normalizado

    return None

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN buscar_importe_por_etiquetas()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN buscar_importe_iva()
# ----------------------------------------------------------

def buscar_importe_iva(texto: str) -> Optional[str]:
    """
    Buscar el importe correspondiente al IVA.

    Esta función evita confundir el porcentaje del IVA con
    el importe monetario.

    Ejemplo:

        IVA 21%: $ 21.000,00

    Resultado correcto:

        21000.00

    Resultado incorrecto que debemos evitar:

        21.00

    Estrategia
    ----------
    Primero se buscan patrones con porcentaje:

        IVA 21%
        IVA 10,5%
        IVA 27%

    El porcentaje es consumido completamente por el patrón
    antes de buscar el importe.

    Después se buscan formas sin porcentaje:

        IVA: $ 21.000,00
        IMPORTE IVA: 21.000,00
        TOTAL IVA: 21.000,00

    Parámetros
    ----------
    texto:

        Texto de la factura.

    Retorna
    -------
    str | None

        Importe del IVA normalizado o None.
    """

    texto_busqueda = normalizar_texto_para_busqueda(
        texto
    )

    if not texto_busqueda:
        return None

    # ------------------------------------------------------
    # Primera estrategia:
    # IVA acompañado por una alícuota porcentual.
    #
    # Ejemplos:
    #
    #     IVA 21%: $ 21.000,00
    #     IVA 10,5% 16.259,25
    # ------------------------------------------------------

    patron_con_porcentaje = (
        r"\bI\.?V\.?A\.?\b"
        r"\s*"
        r"\d{1,2}(?:[.,]\d+)?"
        r"\s*%"
        r"\s*"
        r"[:\-]?"
        r"\s*"
        r"(?:ARS|USD|U\$S|US\$|\$)?"
        r"\s*"
        +
        PATRON_IMPORTE
    )

    coincidencia = re.search(
        patron_con_porcentaje,
        texto_busqueda
    )

    if coincidencia:

        importe_normalizado = limpiar_importe(
            coincidencia.group(1)
        )

        if importe_normalizado:

            return importe_normalizado

    # ------------------------------------------------------
    # Segunda estrategia:
    # etiquetas específicas sin porcentaje.
    # ------------------------------------------------------

    etiquetas_sin_porcentaje = (
        r"\bTOTAL\s+I\.?V\.?A\.?\b",
        r"\bIMPORTE\s+I\.?V\.?A\.?\b",
        r"\bI\.?V\.?A\.?\b",
    )

    return buscar_importe_por_etiquetas(
        texto_busqueda,
        etiquetas_sin_porcentaje
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN buscar_importe_iva()
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE FUNCIONES AUXILIARES PARA IMPORTES
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE DETECTORES INDIVIDUALES
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN detectar_tipo_comprobante()
# ----------------------------------------------------------

def detectar_tipo_comprobante(texto: str) -> Optional[str]:
    """Delegar la detección del tipo al motor fiscal modular.

    Esta función se conserva como fachada de compatibilidad. Los módulos que
    ya importaban ``invoice_parser.detectar_tipo_comprobante`` no necesitan
    cambiar mientras la implementación interna evoluciona.
    """
    return _detectar_tipo_fiscal(texto)

def detectar_letra_comprobante(texto: str) -> Optional[str]:
    """Delegar la detección de la letra al motor fiscal modular."""
    return _detectar_letra_fiscal(texto)

def detectar_numero_comprobante(texto: str) -> Optional[str]:
    """Delegar la extracción del número al motor fiscal modular."""
    return _detectar_numero_fiscal(texto)

def detectar_fecha_emision(texto: str) -> Optional[str]:
    """Delegar la detección de fecha al motor fiscal modular."""
    return _detectar_fecha_fiscal(texto)

def detectar_cuits_factura(
    texto: str
) -> tuple[Optional[str], Optional[str]]:
    """
    Intentar distinguir el CUIT del emisor y del receptor.

    Estrategia:

    1. Buscar etiquetas explícitas.
    2. Utilizar el orden de aparición como respaldo.

    Retorna
    -------
    tuple

        Tupla:

            (cuit_emisor, cuit_receptor)
    """

    texto_busqueda = normalizar_texto_para_busqueda(
        texto
    )

    if not texto_busqueda:
        return None, None

    etiquetas_emisor = (
        r"\bCUIT\s+DEL\s+EMISOR\b",
        r"\bCUIT\s+EMISOR\b",
        r"\bCUIT\s+DEL\s+VENDEDOR\b",
        r"\bCUIT\s+VENDEDOR\b",
    )

    etiquetas_receptor = (
        r"\bCUIT\s+DEL\s+RECEPTOR\b",
        r"\bCUIT\s+RECEPTOR\b",
        r"\bCUIT\s+DEL\s+CLIENTE\b",
        r"\bCUIT\s+CLIENTE\b",
        r"\bCUIT\s+DEL\s+COMPRADOR\b",
        r"\bCUIT\s+COMPRADOR\b",
    )

    cuit_emisor = buscar_cuit_cerca_de_etiquetas(
        texto_busqueda,
        etiquetas_emisor
    )

    cuit_receptor = buscar_cuit_cerca_de_etiquetas(
        texto_busqueda,
        etiquetas_receptor
    )

    todos_los_cuits = extraer_cuits_en_orden(
        texto_busqueda
    )

    if cuit_emisor is None and todos_los_cuits:

        cuit_emisor = todos_los_cuits[0]

    if cuit_receptor is None:

        for cuit in todos_los_cuits:

            if cuit != cuit_emisor:

                cuit_receptor = cuit

                break

    return cuit_emisor, cuit_receptor

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN detectar_cuits_factura()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN detectar_moneda()
# ----------------------------------------------------------

def detectar_moneda(texto: str) -> str:
    """
    Detectar la moneda utilizada en el comprobante.

    Regla del proyecto
    ------------------
    La mayoría de las facturas estarán expresadas en pesos
    argentinos.

    Por ese motivo:

    - Si el documento indica dólares explícitamente,
      devuelve USD.

    - En cualquier otro caso, devuelve ARS.

    Indicaciones de dólares reconocidas:

        USD
        U$S
        US$
        DOLAR
        DOLARES

    Parámetros
    ----------
    texto:

        Texto de la factura.

    Retorna
    -------
    str

        USD o ARS.
    """

    texto_busqueda = normalizar_texto_para_busqueda(
        texto
    )

    patrones_usd = (
        r"\bUSD\b",
        r"\bDOLAR\b",
        r"\bDOLARES\b",
        r"U\$S",
        r"US\$",
    )

    for patron in patrones_usd:

        if re.search(
            patron,
            texto_busqueda
        ):

            return "USD"

    # ------------------------------------------------------
    # Si no existe una indicación explícita de dólares,
    # aplicamos la moneda predeterminada del proyecto.
    # ------------------------------------------------------

    return "ARS"

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN detectar_moneda()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN detectar_subtotal()
# ----------------------------------------------------------

def detectar_subtotal(
    texto: str
) -> Optional[str]:
    """
    Detectar el subtotal del comprobante.

    Etiquetas reconocidas:

        SUBTOTAL
        SUB TOTAL
        NETO GRAVADO
        IMPORTE NETO

    Retorna
    -------
    str | None

        Subtotal normalizado o None.
    """

    etiquetas = (
        r"\bSUBTOTAL\b",
        r"\bSUB\s+TOTAL\b",
        r"\bNETO\s+GRAVADO\b",
        r"\bIMPORTE\s+NETO\b",
    )

    return buscar_importe_por_etiquetas(
        texto,
        etiquetas
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN detectar_subtotal()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN detectar_impuestos()
# ----------------------------------------------------------

def detectar_impuestos(
    texto: str
) -> Optional[str]:
    """
    Detectar el importe principal del IVA.

    Esta función no debe confundir:

        IVA 21%

    con el importe:

        $ 21.000,00

    Por eso utiliza buscar_importe_iva(), que consume el
    porcentaje antes de capturar el importe monetario.

    Retorna
    -------
    str | None

        Importe de IVA normalizado o None.
    """

    return buscar_importe_iva(
        texto
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN detectar_impuestos()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN detectar_importe_total()
# ----------------------------------------------------------

def detectar_importe_total(
    texto: str
) -> Optional[str]:
    """
    Detectar el importe total del comprobante.

    Etiquetas reconocidas:

        IMPORTE TOTAL
        TOTAL A PAGAR
        TOTAL FACTURA
        TOTAL

    Retorna
    -------
    str | None

        Importe total normalizado o None.
    """

    etiquetas = (
        r"\bIMPORTE\s+TOTAL\b",
        r"\bTOTAL\s+A\s+PAGAR\b",
        r"\bTOTAL\s+FACTURA\b",
        r"(?<!SUB)\bTOTAL\b",
    )

    return buscar_importe_por_etiquetas(
        texto,
        etiquetas
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN detectar_importe_total()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN detectar_cae()
# ----------------------------------------------------------

def detectar_cae(
    texto: str
) -> Optional[str]:
    """
    Detectar el Código de Autorización Electrónico.

    El CAE normalmente contiene catorce dígitos.

    Formatos reconocidos:

        CAE: 12345678901234
        CAE N°: 12345678901234
        12345678901234 CAE

    Retorna
    -------
    str | None

        CAE detectado o None.
    """

    texto_busqueda = normalizar_texto_para_busqueda(
        texto
    )

    if not texto_busqueda:
        return None

    patrones = (
        (
            r"\bCAE\b"
            r"(?:\s*N[°º])?"
            r"\s*[:\-]?\s*"
            r"(?<!\d)"
            r"(\d{14})"
            r"(?!\d)"
        ),
        (
            r"(?<!\d)"
            r"(\d{14})"
            r"(?!\d)"
            r"\s*\bCAE\b"
        ),
    )

    for patron in patrones:

        coincidencia = re.search(
            patron,
            texto_busqueda
        )

        if coincidencia:

            return coincidencia.group(1)

    return None

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN detectar_cae()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN detectar_vencimiento_cae()
# ----------------------------------------------------------

def detectar_vencimiento_cae(
    texto: str
) -> Optional[str]:
    """
    Detectar la fecha de vencimiento del CAE.

    Formatos reconocidos:

        Vencimiento CAE: 10/08/2026
        Fecha de Vto. de CAE: 10/08/2026
        10/08/2026 Vencimiento CAE

    Retorna
    -------
    str | None

        Fecha normalizada o None.
    """

    texto_busqueda = normalizar_texto_para_busqueda(
        texto
    )

    if not texto_busqueda:
        return None

    patrones = (
        (
            r"\bFECHA\s+DE\s+VTO\.?"
            r"\s+DE\s+CAE\b"
            r"\s*[:\-]?\s*"
            +
            PATRON_FECHA
        ),
        (
            r"\bVENCIMIENTO\s+CAE\b"
            r"\s*[:\-]?\s*"
            +
            PATRON_FECHA
        ),
        (
            r"\bFECHA\s+DE\s+VENCIMIENTO"
            r"\s+DEL\s+CAE\b"
            r"\s*[:\-]?\s*"
            +
            PATRON_FECHA
        ),
        (
            PATRON_FECHA
            +
            r"\s*"
            r"\bVENCIMIENTO\s+CAE\b"
        ),
    )

    for patron in patrones:

        coincidencia = re.search(
            patron,
            texto_busqueda
        )

        if coincidencia:

            fecha_normalizada = limpiar_fecha(
                coincidencia.group(1)
            )

            if fecha_normalizada:

                return fecha_normalizada

    return None

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN detectar_vencimiento_cae()
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE DETECTORES INDIVIDUALES
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN PRINCIPAL DEL MÓDULO
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN extraer_datos_factura()
# ----------------------------------------------------------

def extraer_datos_factura(
    texto: str
) -> ResultadoParseoFactura:
    """
    Extraer los datos principales desde el texto de una
    factura.

    Flujo
    -----
    1. Valida el texto.
    2. Normaliza el contenido.
    3. Detecta los CUIT.
    4. Ejecuta los detectores individuales.
    5. Construye DatosFactura.
    6. Cuenta los campos detectados.
    7. Devuelve ResultadoParseoFactura.

    Parámetros
    ----------
    texto:

        Texto extraído desde el archivo PDF.

    Retorna
    -------
    ResultadoParseoFactura

        Resultado completo del análisis.
    """

    if not isinstance(texto, str):

        return ResultadoParseoFactura(
            exito=False,
            datos=DatosFactura(),
            mensaje=(
                "El valor recibido no es una cadena "
                "de caracteres."
            ),
        )

    texto_normalizado = normalizar_texto(
        texto
    )

    if not texto_normalizado:

        return ResultadoParseoFactura(
            exito=False,
            datos=DatosFactura(),
            mensaje=(
                "No se recibió texto válido para analizar."
            ),
        )

    cuit_emisor, cuit_receptor = detectar_cuits_factura(
        texto_normalizado
    )

    # Tipo, letra, número y fecha forman un mismo encabezado fiscal.
    # Se analizan mediante un coordinador único para que el resto del parser
    # reciba un resultado coherente y pueda conocer advertencias o el nombre
    # de la estrategia utilizada sin volver a ejecutar detectores dispersos.
    analisis_fiscal = _analizar_encabezado_fiscal(texto_normalizado)

    datos = DatosFactura(
        tipo_comprobante=analisis_fiscal.document_type,
        letra_comprobante=analisis_fiscal.fiscal_letter,
        numero_comprobante=analisis_fiscal.document_number,
        fecha_emision=analisis_fiscal.issue_date,
        cuit_emisor=cuit_emisor,
        cuit_receptor=cuit_receptor,
        moneda=detectar_moneda(
            texto_normalizado
        ),
        subtotal=detectar_subtotal(
            texto_normalizado
        ),
        impuestos=detectar_impuestos(
            texto_normalizado
        ),
        importe_total=detectar_importe_total(
            texto_normalizado
        ),
        cae=detectar_cae(
            texto_normalizado
        ),
        vencimiento_cae=detectar_vencimiento_cae(
            texto_normalizado
        ),
    )

    cantidad_datos_detectados = sum(
        valor is not None
        for valor in (
            datos.convertir_a_diccionario().values()
        )
    )

    if cantidad_datos_detectados == 0:

        mensaje = (
            "El texto pudo analizarse, pero todavía no se "
            "detectaron datos reconocibles."
        )

    else:

        mensaje = (
            "Análisis completado. "
            f"Se detectaron {cantidad_datos_detectados} "
            "datos."
        )

    return ResultadoParseoFactura(
        exito=True,
        datos=datos,
        mensaje=mensaje,
        texto_normalizado=texto_normalizado,
        analisis_fiscal=analisis_fiscal,
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN extraer_datos_factura()
# ----------------------------------------------------------


# ==========================================================
# FIN DE LA FUNCIÓN PRINCIPAL DEL MÓDULO
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE PRUEBAS MANUALES
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN mostrar_resultado_prueba()
# ----------------------------------------------------------

def mostrar_resultado_prueba(
    nombre_prueba: str,
    texto_prueba: str,
) -> None:
    """
    Ejecutar una prueba manual y mostrar el resultado.

    Esta función se utiliza únicamente cuando ejecutamos:

        python invoice_parser.py

    Parámetros
    ----------
    nombre_prueba:

        Nombre descriptivo de la prueba.

    texto_prueba:

        Texto simulado de una factura.
    """

    resultado = extraer_datos_factura(
        texto_prueba
    )

    print("=" * 70)
    print(nombre_prueba)
    print("=" * 70)

    print(f"Éxito: {resultado.exito}")
    print(f"Mensaje: {resultado.mensaje}")

    print()

    print("Datos detectados:")

    for nombre_campo, valor in (
        resultado.datos.convertir_a_diccionario().items()
    ):

        print(
            f"- {nombre_campo}: {valor}"
        )

    print()

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN mostrar_resultado_prueba()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DEL PUNTO DE ENTRADA DE PRUEBAS
# ----------------------------------------------------------

if __name__ == "__main__":
    """
    Estas pruebas comprueban:

    - Años de cuatro dígitos.
    - Años de dos dígitos.
    - Facturas A, B y C.
    - ARS como moneda predeterminada.
    - USD cuando aparece indicado expresamente.
    - IVA con porcentaje.
    - IVA sin porcentaje.
    - Subtotal.
    - Total.
    - CAE.
    - Vencimiento del CAE.
    """

    # ------------------------------------------------------
    # Esta prueba contiene:
    #
    #     IVA 21%: $ 21.000,00
    #
    # El resultado correcto debe ser:
    #
    #     impuestos: 21000.00
    #
    # y no:
    #
    #     impuestos: 21.00
    #
    # No colocamos "Moneda: ARS" para verificar que ARS sea
    # aplicado automáticamente por defecto.
    # ------------------------------------------------------

    texto_prueba_factura_a = """
    FACTURA A

    Comp. Nro: 00003-00001234
    Fecha de Emisión: 31/07/2026

    Razón Social: Proveedor de Prueba S.A.
    CUIT: 30-12345678-9

    Cliente: Empresa Receptora S.A.
    CUIT Receptor: 20-98765432-1

    Subtotal: $ 100.000,00
    IVA 21%: $ 21.000,00
    Importe Total: $ 121.000,00

    CAE N°: 12345678901234
    Fecha de Vto. de CAE: 10/08/2026
    """

    # ------------------------------------------------------
    # Esta prueba también utiliza ARS por defecto.
    #
    # La fecha del vencimiento tiene año de dos dígitos:
    #
    #     09/08/26
    #
    # y debe convertirse en:
    #
    #     09/08/2026
    # ------------------------------------------------------

    texto_prueba_factura_b = """
    FACTURA B

    Comprobante Nro. 00015-00004567
    Fecha Emisión: 30-07-2026

    Distribuidora El Criollo SRL
    CUIT Emisor: 30-11111111-9

    Cliente:
    Bar de Prueba S.A.
    CUIT Cliente: 30-22222222-7

    Neto Gravado: 70.661,16
    IVA: 14.838,84
    Total a Pagar: $ 85.500,00

    98765432109876 CAE
    09/08/26 Vencimiento CAE
    """

    # ------------------------------------------------------
    # Esta prueba contiene una indicación explícita:
    #
    #     Moneda: USD
    #
    # Por lo tanto, debe devolver:
    #
    #     moneda: USD
    # ------------------------------------------------------

    texto_prueba_factura_c = """
    FACTURA C

    Factura N° 7-893
    Fecha del Comprobante: 29.07.26

    Horeca SRL
    CUIT del Emisor: 30-33333333-5

    Receptor:
    Consumidor de Prueba
    CUIT del Receptor: 20-44444444-3

    Moneda: USD
    Sub Total: U$S 35.000,00
    IVA 21%: U$S 7.350,50
    Total Factura: U$S 42.350,50

    CAE: 11112222333344
    Vencimiento CAE: 12/08/2026
    """

    mostrar_resultado_prueba(
        nombre_prueba="PRUEBA 1 - FACTURA A EN ARS",
        texto_prueba=texto_prueba_factura_a,
    )

    mostrar_resultado_prueba(
        nombre_prueba="PRUEBA 2 - FACTURA B EN ARS",
        texto_prueba=texto_prueba_factura_b,
    )

    mostrar_resultado_prueba(
        nombre_prueba="PRUEBA 3 - FACTURA C EN USD",
        texto_prueba=texto_prueba_factura_c,
    )

# ----------------------------------------------------------
# FIN DEL PUNTO DE ENTRADA DE PRUEBAS
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE PRUEBAS MANUALES
# ==========================================================


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================