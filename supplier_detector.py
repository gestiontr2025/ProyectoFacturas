"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Archivo
-------
supplier_detector.py

Descripción
-----------
Este módulo contiene las funciones relacionadas con la
detección del proveedor o emisor de una factura.

Su responsabilidad principal consiste en recibir el texto
extraído previamente desde un archivo PDF y analizarlo para
intentar determinar quién emitió el comprobante.

Este módulo no abre archivos PDF.

Tampoco descarga correos, guarda archivos ni imprime
información en la consola.

La separación de responsabilidades queda de la siguiente
manera:

gmail_client.py:

    Se ocupa de conectarse con Gmail y leer los correos.

file_manager.py:

    Se ocupa de guardar y administrar archivos.

pdf_reader.py:

    Se ocupa de abrir archivos PDF y extraer su texto.

supplier_detector.py:

    Se ocupa de analizar el texto extraído y detectar al
    proveedor.

Importante
----------
Esta primera implementación utiliza una lista de proveedores
conocidos.

Más adelante se podrá ampliar para:

- Extraer automáticamente razones sociales desconocidas.
- Detectar CUIT mediante expresiones regulares.
- Diferenciar entre proveedor y cliente.
- Utilizar reglas específicas para distintos formatos.
- Guardar proveedores conocidos en un archivo externo.
- Incorporar niveles de confianza más avanzados.

Autor
-----
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# INICIO DEL BLOQUE DE IMPORTACIONES
# ==========================================================

import re

# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE CONSTANTES
# ==========================================================

# ----------------------------------------------------------
# PROVEEDORES_CONOCIDOS
# ----------------------------------------------------------
#
# Este diccionario contiene información sobre proveedores
# que ya aparecieron en las facturas utilizadas durante las
# pruebas del proyecto.
#
# La clave principal es un identificador interno.
#
# Cada proveedor contiene:
#
# - nombre:
#
#       Nombre que deseamos utilizar dentro del programa.
#
# - razones_sociales:
#
#       Posibles formas en las que puede aparecer el nombre
#       del proveedor dentro del texto extraído del PDF.
#
# - cuits:
#
#       Uno o más CUIT que permiten identificar al proveedor.
#
# Importante:
#
# La lista puede ampliarse sin modificar el funcionamiento
# general del módulo.
# ----------------------------------------------------------

PROVEEDORES_CONOCIDOS = {
    "arta_verduleros": {
        "nombre": "Arta Verduleros",
        "razones_sociales": [
            "ARTA DE GONZALEZ S.R.L.",
            "ARTA DE GONZALEZ SRL",
            "ARTA DE GONZALEZ"
        ],
        "cuits": [
            "30-71867492-8"
        ]
    },

    "all_online_solutions": {
        "nombre": "All Online Solutions SAU",
        "razones_sociales": [
            "ALL ONLINE SOLUTIONS SAU",
            "COLPPY - ALL ONLINE SOLUTIONS SAU",
            "COLPPY"
        ],
        "cuits": [
            "30-71246122-1"
        ]
    },

    "storni_maria": {
        "nombre": "Storni Maria",
        "razones_sociales": [
            "STORNI MARIA"
        ],
        "cuits": [
            "27-30595013-6"
        ]
    },

    "davila_juan_ignacio": {
        "nombre": "Davila Juan Ignacio",
        "razones_sociales": [
            "DAVILA JUAN IGNACIO"
        ],
        "cuits": [
            "24-36502047-3"
        ]
    },

    "volf": {
        "nombre": "VOLF S.A.",
        "razones_sociales": [
            "VOLF S.A.",
            "VOLF SA"
        ],
        "cuits": []
    }
}

# ==========================================================
# FIN DEL BLOQUE DE CONSTANTES
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN validar_texto_factura()
# ==========================================================

def validar_texto_factura(texto):
    """
    Validar el texto recibido para el análisis.

    Parámetros
    ----------
    texto:

        Texto completo extraído desde un archivo PDF.

    Retorna
    -------
    str

        Texto convertido a cadena y sin espacios innecesarios
        al comienzo o al final.

    Excepciones
    -----------
    ValueError:

        Se produce cuando:

        - El texto es None.
        - El texto está vacío.
        - El texto contiene solamente espacios.
    """

    if texto is None:

        raise ValueError(
            "No se recibió ningún texto para analizar."
        )

    texto = str(
        texto
    ).strip()

    if not texto:

        raise ValueError(
            "El texto recibido está vacío."
        )

    return texto

# ==========================================================
# FIN DE LA FUNCIÓN validar_texto_factura()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN normalizar_texto()
# ==========================================================

def normalizar_texto(texto):
    """
    Normalizar un texto para facilitar las comparaciones.

    Parámetros
    ----------
    texto:

        Texto que deseamos normalizar.

    Retorna
    -------
    str

        Texto convertido a mayúsculas y con espacios
        consecutivos reducidos a un único espacio.

    Ejemplo
    -------
    El texto:

        "All   Online\nSolutions SAU"

    se convierte en:

        "ALL ONLINE SOLUTIONS SAU"

    Importante
    ----------
    Esta función no intenta corregir caracteres extraídos
    incorrectamente desde el PDF.

    Su objetivo solamente consiste en reducir diferencias de
    mayúsculas, saltos de línea y espacios.
    """

    texto = str(
        texto
    ).upper()

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    texto = texto.strip()

    return texto

# ==========================================================
# FIN DE LA FUNCIÓN normalizar_texto()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN normalizar_cuit()
# ==========================================================

def normalizar_cuit(cuit):
    """
    Normalizar un CUIT eliminando caracteres no numéricos.

    Parámetros
    ----------
    cuit:

        CUIT que puede contener guiones, puntos o espacios.

    Retorna
    -------
    str

        CUIT compuesto solamente por números.

    Ejemplo
    -------
    El CUIT:

        30-71246122-1

    se convierte en:

        30712461221
    """

    cuit_normalizado = re.sub(
        r"\D",
        "",
        str(cuit)
    )

    return cuit_normalizado

# ==========================================================
# FIN DE LA FUNCIÓN normalizar_cuit()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN buscar_razon_social()
# ==========================================================

def buscar_razon_social(
    texto_normalizado,
    razones_sociales
):
    """
    Buscar si alguna razón social aparece dentro del texto.

    Parámetros
    ----------
    texto_normalizado:

        Texto completo de la factura ya normalizado.

    razones_sociales:

        Lista de posibles nombres del proveedor.

    Retorna
    -------
    str | None

        Devuelve la razón social encontrada.

        Devuelve None si ninguna coincidencia fue detectada.
    """

    for razon_social in razones_sociales:

        razon_social_normalizada = normalizar_texto(
            razon_social
        )

        if razon_social_normalizada in texto_normalizado:

            return razon_social

    return None

# ==========================================================
# FIN DE LA FUNCIÓN buscar_razon_social()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN buscar_cuit()
# ==========================================================

def buscar_cuit(texto, cuits):
    """
    Buscar si alguno de los CUIT conocidos aparece en el
    texto de la factura.

    Parámetros
    ----------
    texto:

        Texto completo de la factura.

    cuits:

        Lista de CUIT asociados a un proveedor.

    Retorna
    -------
    str | None

        Devuelve el CUIT conocido que fue encontrado.

        Devuelve None cuando no existe ninguna coincidencia.

    Funcionamiento
    --------------
    Se eliminan todos los caracteres no numéricos tanto del
    texto como de los CUIT conocidos.

    Esto permite detectar estas variantes como equivalentes:

        30-71246122-1
        30712461221
        30 71246122 1
    """

    texto_numerico = re.sub(
        r"\D",
        "",
        texto
    )

    for cuit in cuits:

        cuit_normalizado = normalizar_cuit(
            cuit
        )

        if cuit_normalizado in texto_numerico:

            return cuit

    return None

# ==========================================================
# FIN DE LA FUNCIÓN buscar_cuit()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN evaluar_proveedor()
# ==========================================================

def evaluar_proveedor(texto, proveedor):
    """
    Evaluar las coincidencias de un proveedor específico.

    Parámetros
    ----------
    texto:

        Texto original de la factura.

    proveedor:

        Diccionario perteneciente a PROVEEDORES_CONOCIDOS.

    Retorna
    -------
    dict

        Diccionario con las coincidencias encontradas:

            {
                "razon_social_encontrada": ...,
                "cuit_encontrado": ...,
                "puntaje": ...
            }

    Puntaje utilizado
    -----------------
    Razón social encontrada:

        2 puntos.

    CUIT encontrado:

        3 puntos.

    El CUIT recibe un valor mayor porque normalmente es un
    identificador más específico que el nombre comercial.
    """

    texto_normalizado = normalizar_texto(
        texto
    )

    razon_social_encontrada = buscar_razon_social(
        texto_normalizado,
        proveedor["razones_sociales"]
    )

    cuit_encontrado = buscar_cuit(
        texto,
        proveedor["cuits"]
    )

    puntaje = 0

    if razon_social_encontrada is not None:

        puntaje += 2

    if cuit_encontrado is not None:

        puntaje += 3

    return {
        "razon_social_encontrada": (
            razon_social_encontrada
        ),
        "cuit_encontrado": cuit_encontrado,
        "puntaje": puntaje
    }

# ==========================================================
# FIN DE LA FUNCIÓN evaluar_proveedor()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN determinar_metodo_deteccion()
# ==========================================================

def determinar_metodo_deteccion(
    razon_social_encontrada,
    cuit_encontrado
):
    """
    Determinar qué método permitió identificar al proveedor.

    Retorna
    -------
    str

        Puede devolver:

        - razon_social_y_cuit
        - cuit
        - razon_social
        - sin_coincidencias
    """

    if (
        razon_social_encontrada is not None
        and
        cuit_encontrado is not None
    ):

        return "razon_social_y_cuit"

    if cuit_encontrado is not None:

        return "cuit"

    if razon_social_encontrada is not None:

        return "razon_social"

    return "sin_coincidencias"

# ==========================================================
# FIN DE LA FUNCIÓN determinar_metodo_deteccion()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN determinar_nivel_confianza()
# ==========================================================

def determinar_nivel_confianza(puntaje):
    """
    Convertir el puntaje obtenido en un nivel de confianza.

    Parámetros
    ----------
    puntaje:

        Puntaje total de coincidencias.

    Retorna
    -------
    str

        Puede devolver:

        - alta
        - media
        - baja
        - ninguna
    """

    if puntaje >= 5:

        return "alta"

    if puntaje >= 3:

        return "media"

    if puntaje >= 2:

        return "baja"

    return "ninguna"

# ==========================================================
# FIN DE LA FUNCIÓN determinar_nivel_confianza()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN crear_resultado_no_detectado()
# ==========================================================

def crear_resultado_no_detectado():
    """
    Crear la estructura utilizada cuando no se detecta ningún
    proveedor.

    Retorna
    -------
    dict
    """

    return {
        "proveedor_detectado": False,
        "identificador": None,
        "nombre_proveedor": None,
        "razon_social_encontrada": None,
        "cuit_encontrado": None,
        "metodo_deteccion": "sin_coincidencias",
        "nivel_confianza": "ninguna",
        "puntaje": 0
    }

# ==========================================================
# FIN DE LA FUNCIÓN crear_resultado_no_detectado()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN detectar_proveedor()
# ==========================================================

def detectar_proveedor(texto):
    """
    Detectar el proveedor de una factura.

    Esta es la función principal del módulo.

    Parámetros
    ----------
    texto:

        Texto completo extraído mediante:

            pdf_reader.leer_pdf()

    Retorna
    -------
    dict

        Cuando se detecta un proveedor:

            {
                "proveedor_detectado": True,
                "identificador": "all_online_solutions",
                "nombre_proveedor": (
                    "All Online Solutions SAU"
                ),
                "razon_social_encontrada": (
                    "ALL ONLINE SOLUTIONS SAU"
                ),
                "cuit_encontrado": "30-71246122-1",
                "metodo_deteccion": (
                    "razon_social_y_cuit"
                ),
                "nivel_confianza": "alta",
                "puntaje": 5
            }

        Cuando no se detecta ningún proveedor:

            {
                "proveedor_detectado": False,
                "identificador": None,
                "nombre_proveedor": None,
                "razon_social_encontrada": None,
                "cuit_encontrado": None,
                "metodo_deteccion": (
                    "sin_coincidencias"
                ),
                "nivel_confianza": "ninguna",
                "puntaje": 0
            }

    Funcionamiento
    --------------
    1. Valida el texto.

    2. Recorre todos los proveedores conocidos.

    3. Busca coincidencias de razón social y CUIT.

    4. Calcula un puntaje para cada proveedor.

    5. Selecciona el proveedor con mayor puntaje.

    6. Si ninguno alcanza una coincidencia mínima, informa
       que el proveedor no pudo ser detectado.
    """

    texto = validar_texto_factura(
        texto
    )

    mejor_identificador = None
    mejor_proveedor = None
    mejor_evaluacion = None
    mejor_puntaje = 0

    for identificador, proveedor in (
        PROVEEDORES_CONOCIDOS.items()
    ):

        evaluacion = evaluar_proveedor(
            texto,
            proveedor
        )

        puntaje = evaluacion["puntaje"]

        if puntaje > mejor_puntaje:

            mejor_identificador = identificador
            mejor_proveedor = proveedor
            mejor_evaluacion = evaluacion
            mejor_puntaje = puntaje

    if (
        mejor_proveedor is None
        or
        mejor_evaluacion is None
        or
        mejor_puntaje == 0
    ):

        return crear_resultado_no_detectado()

    razon_social_encontrada = mejor_evaluacion[
        "razon_social_encontrada"
    ]

    cuit_encontrado = mejor_evaluacion[
        "cuit_encontrado"
    ]

    metodo_deteccion = determinar_metodo_deteccion(
        razon_social_encontrada,
        cuit_encontrado
    )

    nivel_confianza = determinar_nivel_confianza(
        mejor_puntaje
    )

    return {
        "proveedor_detectado": True,
        "identificador": mejor_identificador,
        "nombre_proveedor": mejor_proveedor["nombre"],
        "razon_social_encontrada": (
            razon_social_encontrada
        ),
        "cuit_encontrado": cuit_encontrado,
        "metodo_deteccion": metodo_deteccion,
        "nivel_confianza": nivel_confianza,
        "puntaje": mejor_puntaje
    }

# ==========================================================
# FIN DE LA FUNCIÓN detectar_proveedor()
# ==========================================================


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================