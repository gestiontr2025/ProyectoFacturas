"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Archivo
-------
business_config.py

Descripción
-----------
Este módulo contiene las reglas de negocio y los datos
canónicos de la empresa que utiliza el programa.

Su objetivo es mantener separados del código operativo
aquellos valores que pueden cambiar si el proyecto se
utiliza en otra empresa.

Actualmente define:

- Razón social oficial del receptor.
- Nombre comercial del receptor.
- CUIT oficial del receptor.
- Variantes aceptadas de la razón social.
- Variantes aceptadas del CUIT.
- Moneda utilizada de manera predeterminada.

Una única fuente de verdad
---------------------------
Los demás módulos deben importar estos valores desde este
archivo.

No deben escribir nuevamente estos datos dentro de:

- invoice_parser.py
- supplier_detector.py
- main.py
- invoice_organizer.py
- otros módulos futuros

Esto evita que diferentes archivos tengan versiones
contradictorias de la misma información.

Programación defensiva
----------------------
El texto extraído de un PDF puede contener:

- Diferencias de puntuación.
- Espacios adicionales.
- Letras omitidas.
- Caracteres unidos.
- Errores de tipeo del emisor.
- Diferencias entre "S.A.", "SA" y "S A".

Las variantes solamente sirven para reconocer el receptor.

El valor final que debe devolver el programa siempre será
el valor canónico definido en este archivo.

Autor
-----
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# INICIO DEL BLOQUE DE DATOS CANÓNICOS DEL RECEPTOR
# ==========================================================


# ----------------------------------------------------------
# Razón social oficial del receptor.
#
# Este es el valor que el programa debe guardar y mostrar,
# aunque el PDF contenga una variante diferente.
# ----------------------------------------------------------

RECEIVER_LEGAL_NAME = "MADERO ROOF TOP S.A."


# ----------------------------------------------------------
# Nombre comercial del receptor.
#
# Actualmente coincide prácticamente con la razón social,
# pero se mantiene como un dato independiente para permitir
# futuros cambios.
# ----------------------------------------------------------

RECEIVER_TRADE_NAME = "Tradition & Rebellion"


# ----------------------------------------------------------
# CUIT oficial normalizado del receptor.
#
# Este es el formato que debe utilizarse en los resultados
# estructurados del programa.
# ----------------------------------------------------------

RECEIVER_CUIT = "30-71834746-3"


# ----------------------------------------------------------
# CUIT oficial sin separadores.
#
# Algunos PDF muestran el CUIT sin guiones.
# ----------------------------------------------------------

RECEIVER_CUIT_DIGITS = "30718347463"


# ==========================================================
# FIN DEL BLOQUE DE DATOS CANÓNICOS DEL RECEPTOR
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE VARIANTES DEL RECEPTOR
# ==========================================================


# ----------------------------------------------------------
# Variantes aceptadas de la razón social.
#
# Estas variantes se utilizan exclusivamente para reconocer
# el receptor dentro del texto extraído.
#
# Nunca deben utilizarse como valor final.
#
# El resultado final siempre debe ser:
#
#     MADERO ROOF TOP S.A.
# ----------------------------------------------------------

RECEIVER_LEGAL_NAME_ALIASES: tuple[str, ...] = (
    "MADERO ROOF TOP S.A.",
    "MADERO ROOF TOP S. A.",
    "MADERO ROOF TOP SA",
    "MADERO ROOF TOP S A",
    "MADERO ROOF TOP S.A",
    "MADERO ROOF TOP",
    "MADERO_ROOF_TOP_S_A",
)


# ----------------------------------------------------------
# Variantes aceptadas del CUIT.
#
# Ambas representan el mismo CUIT.
#
# El resultado final siempre debe normalizarse como:
#
#     30-71834746-3
# ----------------------------------------------------------

RECEIVER_CUIT_ALIASES: tuple[str, ...] = (
    "30-71834746-3",
    "30718347463",
)


# ==========================================================
# FIN DEL BLOQUE DE VARIANTES DEL RECEPTOR
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE CONFIGURACIÓN MONETARIA
# ==========================================================


# ----------------------------------------------------------
# Moneda predeterminada.
#
# Más del noventa por ciento de las facturas del proyecto
# estarán expresadas en pesos argentinos.
#
# Por lo tanto:
#
# - Si el PDF indica USD explícitamente, se utilizará USD.
# - En cualquier otro caso, se utilizará ARS.
# ----------------------------------------------------------

DEFAULT_CURRENCY = "ARS"


# ----------------------------------------------------------
# Identificadores explícitos de dólares estadounidenses.
#
# La presencia de cualquiera de estos valores debe impedir
# que se aplique ARS como moneda predeterminada.
# ----------------------------------------------------------

USD_CURRENCY_ALIASES: tuple[str, ...] = (
    "USD",
    "U$S",
    "US$",
    "DOLAR",
    "DOLARES",
    "DÓLAR",
    "DÓLARES",
)


# ==========================================================
# FIN DEL BLOQUE DE CONFIGURACIÓN MONETARIA
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE FUNCIONES DE VALIDACIÓN
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN obtener_datos_receptor()
# ----------------------------------------------------------

def obtener_datos_receptor() -> dict[str, str]:
    """
    Devolver los datos canónicos del receptor.

    Esta función permite que otros módulos recuperen todos
    los datos principales mediante una única operación.

    Retorna
    -------
    dict

        Diccionario con:

        - razon_social
        - nombre_comercial
        - cuit
        - cuit_sin_guiones
    """

    return {
        "razon_social": RECEIVER_LEGAL_NAME,
        "nombre_comercial": RECEIVER_TRADE_NAME,
        "cuit": RECEIVER_CUIT,
        "cuit_sin_guiones": RECEIVER_CUIT_DIGITS,
    }

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN obtener_datos_receptor()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN es_cuit_receptor()
# ----------------------------------------------------------

def es_cuit_receptor(cuit: object) -> bool:
    """
    Comprobar si un valor representa el CUIT del receptor.

    La función acepta el CUIT:

    - Con guiones.
    - Sin guiones.
    - Con espacios u otros separadores.

    Parámetros
    ----------
    cuit:

        Valor que deseamos comprobar.

    Retorna
    -------
    bool

        True si corresponde al receptor.

        False en cualquier otro caso.
    """

    if cuit is None:
        return False

    texto_cuit = str(
        cuit
    )

    solo_digitos = "".join(
        caracter
        for caracter in texto_cuit
        if caracter.isdigit()
    )

    return solo_digitos == RECEIVER_CUIT_DIGITS

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN es_cuit_receptor()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN normalizar_cuit_receptor()
# ----------------------------------------------------------

def normalizar_cuit_receptor(
    cuit: object
) -> str | None:
    """
    Normalizar el CUIT del receptor.

    Parámetros
    ----------
    cuit:

        Valor encontrado en el PDF.

    Retorna
    -------
    str | None

        Devuelve siempre:

            30-71834746-3

        si el valor representa el CUIT del receptor.

        Devuelve None si no coincide.
    """

    if not es_cuit_receptor(cuit):
        return None

    return RECEIVER_CUIT

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN normalizar_cuit_receptor()
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE FUNCIONES DE VALIDACIÓN
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE VALIDACIÓN INTERNA
# ==========================================================


# ----------------------------------------------------------
# Validamos que el CUIT con formato y el CUIT sin formato
# representen exactamente el mismo número.
#
# Este control se realiza al importar el módulo.
#
# Si alguien modifica uno de los valores pero olvida
# modificar el otro, el programa se detendrá con un mensaje
# claro en lugar de trabajar con datos contradictorios.
# ----------------------------------------------------------

_cuit_canonico_solo_digitos = "".join(
    caracter
    for caracter in RECEIVER_CUIT
    if caracter.isdigit()
)


if _cuit_canonico_solo_digitos != RECEIVER_CUIT_DIGITS:

    raise ValueError(
        "La configuración del receptor es inconsistente. "
        "RECEIVER_CUIT y RECEIVER_CUIT_DIGITS no representan "
        "el mismo CUIT."
    )


# ----------------------------------------------------------
# Validamos que la razón social canónica no esté vacía.
# ----------------------------------------------------------

if not RECEIVER_LEGAL_NAME.strip():

    raise ValueError(
        "RECEIVER_LEGAL_NAME no puede estar vacío."
    )


# ----------------------------------------------------------
# Validamos que la moneda predeterminada sea una de las
# monedas contempladas actualmente.
# ----------------------------------------------------------

if DEFAULT_CURRENCY not in {"ARS", "USD"}:

    raise ValueError(
        "DEFAULT_CURRENCY debe ser ARS o USD."
    )


# ==========================================================
# FIN DEL BLOQUE DE VALIDACIÓN INTERNA
# ==========================================================


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================