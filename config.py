"""
==========================================================
PROYECTO
==========================================================

ProyectoFacturas

Versión
--------
0.3

Archivo
--------
config.py

Descripción
-----------
Este archivo contiene la configuración general del
proyecto.

Su responsabilidad es centralizar todos aquellos valores
que podrían cambiar en el futuro.

Por ejemplo:

- Nombre del proyecto.
- Versión actual.
- Autor.
- Correo electrónico utilizado para acceder a Gmail.
- Contraseña de aplicación de Gmail.
- Carpeta donde se guardarán las facturas.

Centralizar la configuración evita tener que buscar y
modificar esos datos en distintos archivos del proyecto.

Seguridad
---------
Los datos sensibles, como el correo electrónico y la
contraseña de aplicación, NO se escriben directamente
dentro de este archivo.

Esos datos se guardan en un archivo privado llamado:

    .env

El archivo .env deberá estar incluido dentro de
.gitignore para evitar que Git lo registre y que las
credenciales sean publicadas accidentalmente en GitHub.

Responsabilidades
-----------------
✔ Guardar la información general del proyecto.
✔ Cargar las variables privadas desde el archivo .env.
✔ Validar que las variables necesarias existan.
✔ Definir la carpeta principal de almacenamiento.

No debe
--------
✘ Conectarse con Gmail.
✘ Buscar correos.
✘ Descargar archivos.
✘ Crear carpetas mensuales.
✘ Leer o modificar archivos PDF.

Autor
------
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# IMPORTACIONES
# ==========================================================

# ----------------------------------------------------------
# Importamos el módulo "os", incluido en la biblioteca
# estándar de Python.
#
# Este módulo permite interactuar con ciertas funciones
# proporcionadas por el sistema operativo.
#
# En este archivo utilizaremos:
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
#     "Buscá una variable de entorno llamada EMAIL
#      y devolveme su contenido".
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
# barras invertidas, podremos hacer operaciones como:
#
#     SAVE_FOLDER / "2026" / "Julio"
#
# Path se encargará de formar correctamente la ruta según
# el sistema operativo que estemos utilizando.
# ----------------------------------------------------------

from pathlib import Path


# ----------------------------------------------------------
# Importamos load_dotenv() desde la biblioteca
# python-dotenv.
#
# Esta biblioteca no viene instalada de manera
# predeterminada con Python.
#
# Para instalarla debemos ejecutar en la terminal:
#
#     pip install python-dotenv
#
# La función load_dotenv() lee el archivo ".env" y carga
# sus variables para que puedan ser recuperadas mediante
# os.getenv().
# ----------------------------------------------------------

from dotenv import load_dotenv


# ==========================================================
# CARGAR EL ARCHIVO .ENV
# ==========================================================

# ----------------------------------------------------------
# Ejecutamos load_dotenv() para buscar y leer el archivo
# llamado ".env".
#
# El archivo .env debe encontrarse en la carpeta principal
# del proyecto, junto a config.py y main.py.
#
# Su contenido tendrá una estructura parecida a esta:
#
#     EMAIL=tu_correo@gmail.com
#     APP_PASSWORD=tu_contraseña_de_aplicacion
#
# Después de ejecutar load_dotenv(), esas variables podrán
# recuperarse utilizando os.getenv().
# ----------------------------------------------------------

load_dotenv()


# ==========================================================
# INFORMACIÓN GENERAL DEL PROYECTO
# ==========================================================

# ----------------------------------------------------------
# Nombre oficial del proyecto.
#
# Se utiliza para mostrar mensajes informativos en la
# terminal y para identificar el programa.
# ----------------------------------------------------------

PROJECT_NAME = "Proyecto Facturas"


# ----------------------------------------------------------
# Versión actual del proyecto.
#
# Cambiamos la versión de 0.2 a 0.3 porque incorporamos una
# nueva mejora:
#
# - Las credenciales ya no se guardan directamente dentro
#   del código.
# - Ahora se leen desde un archivo privado llamado .env.
#
# Mientras el proyecto se encuentre en desarrollo,
# utilizaremos versiones que comiencen con 0.
#
# Por ejemplo:
#
#     0.3
#     0.4
#     0.5
#
# Cuando el programa alcance una primera versión completa
# y estable, podremos cambiar este valor a 1.0.
# ----------------------------------------------------------

PROJECT_VERSION = "0.7"


# ----------------------------------------------------------
# Autor principal del proyecto.
#
# Este valor es informativo y puede utilizarse en mensajes,
# documentación o registros del programa.
# ----------------------------------------------------------

PROJECT_AUTHOR = "Diego"


# ==========================================================
# DATOS DE GMAIL
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
# Si la variable EMAIL no existe, os.getenv() devolverá
# None.
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
# aplicaciones externas, como este programa, puedan
# conectarse con Gmail.
#
# Si APP_PASSWORD no existe en el entorno, os.getenv()
# devolverá None.
# ----------------------------------------------------------

APP_PASSWORD = os.getenv("APP_PASSWORD")


# ==========================================================
# VALIDACIÓN DE LAS VARIABLES DE ENTORNO
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
# Esta condición será verdadera si EMAIL contiene:
#
# - None.
# - Una cadena vacía: "".
#
# Si falta el correo, detenemos el programa utilizando
# raise ValueError().
#
# "raise" significa que provocamos deliberadamente una
# excepción para informar que existe un problema.
#
# ValueError indica que un valor necesario para ejecutar el
# programa es incorrecto o no está disponible.
#
# Esto es preferible a intentar conectarse con Gmail
# utilizando un valor vacío, porque el mensaje de error
# será mucho más claro.
# ----------------------------------------------------------

if not EMAIL:
    raise ValueError(
        "No se encontró la variable EMAIL. "
        "Verificá que exista el archivo .env y que contenga "
        "una línea con el formato EMAIL=tu_correo@gmail.com"
    )


# ----------------------------------------------------------
# Comprobamos que la contraseña de aplicación también haya
# sido encontrada.
#
# Si APP_PASSWORD no contiene un valor válido, detenemos el
# programa y mostramos un mensaje explicativo.
#
# La contraseña nunca se incluye en el mensaje de error.
# Tampoco deberíamos imprimirla en la terminal, guardarla
# en registros ni mostrarla durante las pruebas.
# ----------------------------------------------------------

if not APP_PASSWORD:
    raise ValueError(
        "No se encontró la variable APP_PASSWORD. "
        "Verificá que exista el archivo .env y que contenga "
        "una línea con el formato "
        "APP_PASSWORD=tu_contraseña_de_aplicacion"
    )


# ==========================================================
# CARPETA DONDE SE GUARDARÁN LAS FACTURAS
# ==========================================================

# ----------------------------------------------------------
# Definimos la carpeta principal en la que se almacenarán
# las facturas descargadas.
#
# Utilizamos Path() para convertir el texto de la ruta en
# un objeto especializado en rutas de archivos.
#
# La letra "r" colocada antes de las comillas significa
# "raw string" o cadena cruda.
#
# Esto le indica a Python que conserve las barras
# invertidas de Windows exactamente como fueron escritas.
#
# Sin la letra "r", algunas combinaciones podrían ser
# interpretadas como caracteres especiales.
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
# Más adelante, organizer.py utilizará esta ruta para crear
# carpetas como:
#
#     Facturas/
#     └── 2026/
#         └── Julio/
#             └── Nombre del proveedor/
# ----------------------------------------------------------

SAVE_FOLDER = Path(
    r"C:\Users\gesti\OneDrive\Documentos\Facturas"
)