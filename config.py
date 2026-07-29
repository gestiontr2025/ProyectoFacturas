"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Archivo
-------
config.py

Descripción
-----------
Este archivo contiene la configuración general del
proyecto.

Su responsabilidad es centralizar aquellos valores que
podrían cambiar en el futuro.

Por ejemplo:

- Nombre del proyecto.
- Autor.
- Correo electrónico utilizado para acceder a Gmail.
- Contraseña de aplicación de Gmail.
- Cantidad de correos procesados por ejecución.
- Carpeta donde se guardarán las facturas.

La versión del proyecto ya no se encuentra en este archivo.

La versión se guarda exclusivamente en:

    version.py

De esta manera, para actualizarla solamente es necesario
modificar un archivo cuya única responsabilidad es contener
la versión actual.

Seguridad
---------
Los datos sensibles, como el correo electrónico y la
contraseña de aplicación, NO se escriben directamente
dentro de este archivo.

Esos datos se guardan en un archivo privado llamado:

    .env

El archivo .env deberá estar incluido dentro de:

    .gitignore

Esto evita que Git registre las credenciales y que puedan
publicarse accidentalmente en GitHub.

Responsabilidades
-----------------
- Guardar la información general del proyecto.
- Cargar las variables privadas desde el archivo .env.
- Validar que las variables necesarias existan.
- Definir el límite de correos procesados.
- Definir la carpeta principal de almacenamiento.

No debe
-------
- Conectarse con Gmail.
- Buscar correos.
- Descargar archivos.
- Crear carpetas mensuales.
- Leer o modificar archivos PDF.
- Guardar la versión del proyecto.

Autor
-----
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# INICIO DEL BLOQUE DE IMPORTACIONES
# ==========================================================

# ----------------------------------------------------------
# Importamos el módulo os.
#
# Este módulo forma parte de la biblioteca estándar de
# Python.
#
# En este archivo utilizamos:
#
#     os.getenv()
#
# Esta función permite obtener el contenido de una variable
# de entorno.
#
# Por ejemplo:
#
#     os.getenv("EMAIL")
#
# significa:
#
#     "Buscá una variable de entorno llamada EMAIL y
#      devolveme su contenido".
#
# Si la variable no existe, os.getenv() devuelve None.
# ----------------------------------------------------------

import os


# ----------------------------------------------------------
# Importamos la clase Path desde el módulo pathlib.
#
# pathlib forma parte de la biblioteca estándar de Python
# y proporciona una manera moderna y segura de trabajar
# con rutas de archivos y carpetas.
#
# En lugar de construir rutas manualmente utilizando
# barras invertidas, podremos realizar operaciones como:
#
#     SAVE_FOLDER / "2026" / "07 - Julio"
#
# Path se encargará de formar correctamente la ruta según
# el sistema operativo utilizado.
# ----------------------------------------------------------

from pathlib import Path


# ----------------------------------------------------------
# Importamos load_dotenv() desde la biblioteca
# python-dotenv.
#
# Esta biblioteca no viene instalada de manera
# predeterminada con Python.
#
# Para instalarla se utiliza:
#
#     pip install python-dotenv
#
# La función load_dotenv() lee el archivo .env y carga sus
# variables para que puedan recuperarse mediante:
#
#     os.getenv()
# ----------------------------------------------------------

from dotenv import load_dotenv

# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DE LA CARGA DEL ARCHIVO .ENV
# ==========================================================

# ----------------------------------------------------------
# Ejecutamos load_dotenv() para buscar y leer el archivo
# llamado:
#
#     .env
#
# El archivo debe encontrarse en la carpeta principal del
# proyecto, junto a config.py y main.py.
#
# Su contenido deberá tener una estructura parecida a:
#
#     EMAIL=tu_correo@gmail.com
#     APP_PASSWORD=tu_contraseña_de_aplicacion
#
# Después de ejecutar load_dotenv(), esas variables podrán
# recuperarse utilizando os.getenv().
# ----------------------------------------------------------

load_dotenv()

# ==========================================================
# FIN DE LA CARGA DEL ARCHIVO .ENV
# ==========================================================


# ==========================================================
# INICIO DE LA INFORMACIÓN GENERAL DEL PROYECTO
# ==========================================================

# ----------------------------------------------------------
# Nombre oficial del proyecto.
#
# Se utiliza para mostrar mensajes informativos en la
# terminal y para identificar el programa.
# ----------------------------------------------------------

PROJECT_NAME = "Proyecto Facturas"


# ----------------------------------------------------------
# Autor principal del proyecto.
#
# Este valor es informativo y puede utilizarse en mensajes,
# documentación o registros del programa.
# ----------------------------------------------------------

PROJECT_AUTHOR = "Diego"

# ==========================================================
# FIN DE LA INFORMACIÓN GENERAL DEL PROYECTO
# ==========================================================


# ==========================================================
# INICIO DE LOS DATOS DE GMAIL
# ==========================================================

# ----------------------------------------------------------
# Recuperamos la dirección de correo electrónico desde la
# variable EMAIL definida dentro del archivo .env.
#
# Ya no escribimos el correo directamente en config.py.
#
# Esto evita que el dato quede guardado dentro del código
# fuente o dentro del historial de Git.
#
# Si la variable EMAIL no existe, os.getenv() devolverá:
#
#     None
# ----------------------------------------------------------

EMAIL = os.getenv("EMAIL")


# ----------------------------------------------------------
# Recuperamos la contraseña de aplicación de Gmail desde
# la variable APP_PASSWORD definida dentro del archivo
# .env.
#
# IMPORTANTE:
#
# Esta contraseña no es la contraseña normal de la cuenta
# de Google.
#
# Es una contraseña especial creada para permitir que
# aplicaciones externas puedan conectarse con Gmail.
#
# Si APP_PASSWORD no existe, os.getenv() devolverá:
#
#     None
# ----------------------------------------------------------

APP_PASSWORD = os.getenv("APP_PASSWORD")

# ==========================================================
# FIN DE LOS DATOS DE GMAIL
# ==========================================================


# ==========================================================
# INICIO DE LA VALIDACIÓN DE VARIABLES DE ENTORNO
# ==========================================================

# ----------------------------------------------------------
# Comprobamos que la variable EMAIL haya sido encontrada.
#
# La expresión:
#
#     if not EMAIL:
#
# significa:
#
#     "Si EMAIL no contiene un valor válido".
#
# La condición será verdadera si EMAIL contiene:
#
# - None.
# - Una cadena vacía.
#
# Si falta el correo, detenemos el programa utilizando:
#
#     raise ValueError()
#
# Esto permite mostrar un mensaje más claro que el que
# produciría un intento de conexión con credenciales
# incompletas.
# ----------------------------------------------------------

if not EMAIL:

    raise ValueError(
        "No se encontró la variable EMAIL. "
        "Verificá que exista el archivo .env y que contenga "
        "una línea con el formato "
        "EMAIL=tu_correo@gmail.com"
    )


# ----------------------------------------------------------
# Comprobamos que la contraseña de aplicación también haya
# sido encontrada.
#
# La contraseña nunca se incluye dentro del mensaje de
# error.
#
# Tampoco debe:
#
# - Imprimirse en la terminal.
# - Guardarse en registros.
# - Incluirse en Git.
# - Publicarse en GitHub.
# ----------------------------------------------------------

if not APP_PASSWORD:

    raise ValueError(
        "No se encontró la variable APP_PASSWORD. "
        "Verificá que exista el archivo .env y que contenga "
        "una línea con el formato "
        "APP_PASSWORD=tu_contraseña_de_aplicacion"
    )

# ==========================================================
# FIN DE LA VALIDACIÓN DE VARIABLES DE ENTORNO
# ==========================================================


# ==========================================================
# INICIO DE LA CONFIGURACIÓN DE PROCESAMIENTO
# ==========================================================

# ----------------------------------------------------------
# Cantidad máxima de correos recientes que el programa
# procesará en cada ejecución.
#
# Utilizamos un límite para evitar procesar accidentalmente
# toda la cuenta de Gmail durante las primeras etapas del
# desarrollo.
#
# Actualmente, el programa seleccionará los 10 correos más
# recientes.
# ----------------------------------------------------------

EMAIL_PROCESSING_LIMIT = 10

# ==========================================================
# FIN DE LA CONFIGURACIÓN DE PROCESAMIENTO
# ==========================================================


# ==========================================================
# INICIO DE LA CARPETA DE DESTINO
# ==========================================================

# ----------------------------------------------------------
# Definimos la carpeta principal en la que se almacenarán
# las facturas descargadas.
#
# Utilizamos Path() para convertir el texto de la ruta en
# un objeto especializado en rutas de archivos.
#
# La letra r colocada antes de las comillas significa:
#
#     raw string
#
# o:
#
#     cadena cruda
#
# Esto le indica a Python que conserve las barras
# invertidas de Windows exactamente como fueron escritas.
#
# Sin la letra r, algunas combinaciones podrían
# interpretarse como caracteres especiales.
#
# Por ejemplo:
#
#     \n
#
# normalmente representa un salto de línea.
#
# La variable SAVE_FOLDER contiene solamente la carpeta
# principal.
#
# invoice_organizer.py utiliza esta ruta para construir
# carpetas como:
#
#     Facturas/
#     └── Remitente/
#         └── Año/
#             └── Número - Mes/
#                 └── factura.pdf
# ----------------------------------------------------------

SAVE_FOLDER = Path(
    r"C:\Users\gesti\OneDrive\Documentos\Facturas"
)

# ==========================================================
# FIN DE LA CARPETA DE DESTINO
# ==========================================================


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================