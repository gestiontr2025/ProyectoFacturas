"""
==========================================================
PROYECTO
==========================================================

ProyectoFacturas

Versión
--------
0.2

Archivo
--------
gmail_client.py

Descripción
-----------
Este módulo contiene todas las funciones relacionadas
con Gmail.

Responsabilidades
-----------------
✔ Conectarse a Gmail.
✔ Buscar correos.
✔ Descargar archivos adjuntos.
✔ Cerrar la conexión.

No debe
--------
✘ Leer PDFs.
✘ Crear carpetas.
✘ Renombrar archivos.

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
# Biblioteca oficial de Python para trabajar con el protocolo
# IMAP.
#
# IMAP nos permite acceder a los correos almacenados en Gmail.
#
# Gracias a esta biblioteca podremos:
#
# - Conectarnos.
# - Buscar correos.
# - Descargar adjuntos.
# - Cerrar la sesión.
# ----------------------------------------------------------

import imaplib


# ----------------------------------------------------------
# Importamos nuestro módulo de configuración.
#
# Desde aquí obtendremos:
#
# - EMAIL
# - APP_PASSWORD
#
# Esto evita escribir esos datos nuevamente en este archivo.
# ----------------------------------------------------------

import config


# ==========================================================
# FUNCIONES
# ==========================================================

def conectar():

    """
    ==========================================================
    FUNCIÓN
    ==========================================================

    conectar()

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Establecer una conexión segura con Gmail utilizando
    el protocolo IMAP.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    Esta función no recibe parámetros.

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Devuelve el objeto que representa la conexión abierta
    con Gmail.

    Ese objeto será utilizado posteriormente por otras
    funciones del proyecto.

    ----------------------------------------------------------
    IMPORTANTE
    ----------------------------------------------------------

    Esta función solamente se encarga de conectar.

    No busca correos.

    No descarga archivos.

    No procesa PDFs.

    ==========================================================
    """

    print()

    print("--------------------------------")
    print("Conectando con Gmail...")
    print("--------------------------------")


    # ------------------------------------------------------
    # Creamos una conexión segura con Gmail.
    #
    # La variable "mail" representará la conexión abierta.
    #
    # A partir de este momento podremos comunicarnos
    # con los servidores de Gmail.
    # ------------------------------------------------------

    mail = imaplib.IMAP4_SSL("imap.gmail.com")


    # ------------------------------------------------------
    # Iniciamos sesión utilizando las credenciales
    # almacenadas en config.py.
    # ------------------------------------------------------

    mail.login(config.EMAIL, config.APP_PASSWORD)


    print("Conexión realizada correctamente.")


    # ------------------------------------------------------
    # MUY IMPORTANTE
    #
    # En lugar de cerrar la conexión aquí,
    # la devolvemos al programa principal.
    #
    # Gracias a esto otras funciones podrán reutilizar
    # exactamente la misma conexión.
    # ------------------------------------------------------

    return mail