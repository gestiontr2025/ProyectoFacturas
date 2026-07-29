"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Versión
--------
0.11

Archivo
--------
invoice_organizer.py

Descripción
-----------
Este módulo contiene las funciones encargadas de determinar
en qué carpeta debe guardarse una factura.

La estructura actual es:

    Carpeta principal
        └── Remitente
            └── Año
                └── Número - Mes

Ejemplo:

    Facturas
        └── Arta verdurleros
            └── 2026
                └── 07 - Julio

En esta versión, el nombre de la carpeta se obtiene del
remitente del correo.

Todavía no se analiza el contenido interno del PDF para
identificar al proveedor real.

Autor
------
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# INICIO DEL BLOQUE DE IMPORTACIONES
# ==========================================================

from email.utils import parseaddr
from email.utils import parsedate_to_datetime
from pathlib import Path

# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE CONSTANTES
# ==========================================================

MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

# ==========================================================
# FIN DEL BLOQUE DE CONSTANTES
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN sanitizar_nombre_carpeta()
# ==========================================================

def sanitizar_nombre_carpeta(nombre):
    """
    Preparar un texto para utilizarlo como nombre de carpeta.

    Parámetros
    ----------
    nombre:

        Texto original que deseamos utilizar como nombre.

    Retorna
    -------
    str

        Nombre compatible con el sistema de archivos.

    Funcionamiento
    --------------
    Windows no permite algunos caracteres dentro de los
    nombres de archivos y carpetas.

    Los caracteres problemáticos son:

        < > : " / \\ | ? *

    Esta función los reemplaza por guiones.
    """

    caracteres_no_permitidos = '<>:"/\\|?*'

    nombre_limpio = str(nombre).strip()

    for caracter in caracteres_no_permitidos:

        nombre_limpio = nombre_limpio.replace(
            caracter,
            "-"
        )

    # ------------------------------------------------------
    # Eliminamos espacios repetidos.
    #
    # split() separa el texto por espacios.
    # join() vuelve a unirlo utilizando un solo espacio.
    # ------------------------------------------------------

    nombre_limpio = " ".join(
        nombre_limpio.split()
    )

    # ------------------------------------------------------
    # Windows también puede producir problemas si el nombre
    # termina con un punto o un espacio.
    # ------------------------------------------------------

    nombre_limpio = nombre_limpio.rstrip(
        ". "
    )

    if not nombre_limpio:

        return "Remitente desconocido"

    return nombre_limpio

# ==========================================================
# FIN DE LA FUNCIÓN sanitizar_nombre_carpeta()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN obtener_nombre_remitente()
# ==========================================================

def obtener_nombre_remitente(remitente):
    """
    Extraer un nombre útil del encabezado From del correo.

    Parámetros
    ----------
    remitente:

        Contenido del encabezado From.

        Ejemplo:

            Arta verdurleros
            <administracion@artaverduleros.com.ar>

    Retorna
    -------
    str

        Nombre que se utilizará para crear la carpeta.

    Ejemplos
    --------
    Si recibimos:

        Arta verdurleros
        <administracion@artaverduleros.com.ar>

    devuelve:

        Arta verdurleros

    Si el correo no incluye un nombre visible, se utiliza la
    dirección de correo electrónico.
    """

    nombre_visible, direccion_email = parseaddr(
        remitente or ""
    )

    if nombre_visible:

        nombre_carpeta = nombre_visible

    elif direccion_email:

        # --------------------------------------------------
        # Si no existe un nombre visible, utilizamos la parte
        # anterior al símbolo @.
        #
        # Ejemplo:
        #
        # ventas@elcriollosrl.com
        #
        # se transforma en:
        #
        # ventas
        # --------------------------------------------------

        nombre_carpeta = direccion_email.split(
            "@"
        )[0]

    else:

        nombre_carpeta = "Remitente desconocido"

    return sanitizar_nombre_carpeta(
        nombre_carpeta
    )

# ==========================================================
# FIN DE LA FUNCIÓN obtener_nombre_remitente()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN obtener_anio_y_mes()
# ==========================================================

def obtener_anio_y_mes(fecha_correo):
    """
    Obtener el año y el mes de la fecha de un correo.

    Parámetros
    ----------
    fecha_correo:

        Contenido del encabezado Date del correo.

        Ejemplo:

            Wed, 29 Jul 2026 06:38:13 -0300

    Retorna
    -------
    tuple

        Tupla con dos elementos:

            año
            número del mes

        Ejemplo:

            (2026, 7)

    Errores
    -------
    ValueError

        Se produce si el correo no posee una fecha válida.
    """

    if not fecha_correo:

        raise ValueError(
            "El correo no contiene una fecha válida."
        )

    fecha_convertida = parsedate_to_datetime(
        fecha_correo
    )

    if fecha_convertida is None:

        raise ValueError(
            "No fue posible interpretar la fecha del correo."
        )

    return (
        fecha_convertida.year,
        fecha_convertida.month
    )

# ==========================================================
# FIN DE LA FUNCIÓN obtener_anio_y_mes()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN construir_nombre_mes()
# ==========================================================

def construir_nombre_mes(numero_mes):
    """
    Crear el nombre de la carpeta correspondiente a un mes.

    Parámetros
    ----------
    numero_mes:

        Número del mes entre 1 y 12.

    Retorna
    -------
    str

        Nombre con el formato:

            07 - Julio
    """

    if numero_mes not in MESES:

        raise ValueError(
            f"El número de mes no es válido: {numero_mes}"
        )

    nombre_mes = MESES[numero_mes]

    return f"{numero_mes:02d} - {nombre_mes}"

# ==========================================================
# FIN DE LA FUNCIÓN construir_nombre_mes()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN construir_carpeta_factura()
# ==========================================================

def construir_carpeta_factura(
    carpeta_principal,
    datos_correo
):
    """
    Construir la carpeta donde se guardarán los adjuntos de
    un correo.

    Parámetros
    ----------
    carpeta_principal:

        Carpeta general configurada para las facturas.

    datos_correo:

        Diccionario devuelto por:

            gmail_client.obtener_datos_correo()

        Debe contener al menos:

            "From"
            "Date"

    Retorna
    -------
    Path

        Ruta con la estructura:

            carpeta_principal
                / remitente
                / año
                / mes

    Ejemplo
    -------
    Podría devolver:

        C:\\Facturas
            \\Arta verdurleros
            \\2026
            \\07 - Julio
    """

    remitente = datos_correo.get(
        "From",
        ""
    )

    fecha_correo = datos_correo.get(
        "Date",
        ""
    )

    nombre_remitente = obtener_nombre_remitente(
        remitente
    )

    anio, numero_mes = obtener_anio_y_mes(
        fecha_correo
    )

    nombre_mes = construir_nombre_mes(
        numero_mes
    )

    carpeta_factura = (
        Path(carpeta_principal)
        / nombre_remitente
        / str(anio)
        / nombre_mes
    )

    return carpeta_factura

# ==========================================================
# FIN DE LA FUNCIÓN construir_carpeta_factura()
# ==========================================================


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================