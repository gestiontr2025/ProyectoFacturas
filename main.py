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
main.py

Descripción
-----------
Este archivo es el punto de entrada principal del programa.

Cuando ejecutamos:

    python main.py

Python comienza leyendo este archivo.

La responsabilidad de main.py es coordinar el trabajo
de los distintos módulos del proyecto.

Este archivo NO debe contener la lógica específica
de Gmail, PDFs o carpetas.

Su función es organizar el flujo general del programa.

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
# Importamos el módulo de configuración.
#
# Este módulo contiene toda la información configurable
# del proyecto.
#
# Por ejemplo:
#
# - Nombre del proyecto.
# - Versión actual.
# - Autor.
# - Correo electrónico.
# - Contraseña de aplicación.
# - Carpeta donde se guardarán las facturas.
# ----------------------------------------------------------

import config


# ----------------------------------------------------------
# Importamos el módulo encargado de todas las tareas
# relacionadas con Gmail.
#
# Actualmente contiene:
#
# - conectar()
#
# Más adelante contendrá:
#
# - buscar_correos()
# - descargar_adjuntos()
# - cerrar_conexion()
# ----------------------------------------------------------

import gmail_client


# ==========================================================
# INICIO DEL PROGRAMA
# ==========================================================

# ----------------------------------------------------------
# Mostramos información general del proyecto.
#
# Estos datos se obtienen desde config.py.
#
# Gracias a esto existe una única fuente de verdad.
#
# Si en el futuro cambia el nombre del proyecto o la
# versión, solamente habrá que modificar config.py.
# ----------------------------------------------------------

print("==================================================")
print(config.PROJECT_NAME)
print(f"Versión {config.PROJECT_VERSION}")
print(f"Autor: {config.PROJECT_AUTHOR}")
print("==================================================")

print()


# ==========================================================
# MOSTRAR CONFIGURACIÓN ACTUAL
# ==========================================================

# ----------------------------------------------------------
# Mostramos la configuración principal que utilizará
# el programa durante esta ejecución.
#
# Esto resulta útil para verificar rápidamente que:
#
# - Estamos utilizando la cuenta correcta.
# - La carpeta de trabajo es la esperada.
#
# Si existe algún error de configuración podremos
# detectarlo antes de conectarnos a Gmail.
# ----------------------------------------------------------

print("Correo configurado:")
print(config.EMAIL)

print()

print("Carpeta de trabajo:")
print(config.SAVE_FOLDER)

print()


# ==========================================================
# CONECTARSE A GMAIL
# ==========================================================

# ----------------------------------------------------------
# Llamamos a la función conectar() ubicada dentro del
# módulo gmail_client.
#
# Esta función abrirá una conexión segura con Gmail
# utilizando las credenciales configuradas en config.py.
#
# La conexión abierta será devuelta mediante "return"
# y almacenada dentro de la variable "conexion".
#
# A partir de este momento podremos utilizar dicha
# variable para interactuar con Gmail.
# ----------------------------------------------------------

conexion = gmail_client.conectar()


# ==========================================================
# CONFIRMACIÓN DE RECEPCIÓN DE LA CONEXIÓN
# ==========================================================

# ----------------------------------------------------------
# Este mensaje existe únicamente con fines educativos.
#
# Nos permite comprobar que:
#
# 1) gmail_client.py creó correctamente la conexión.
#
# 2) La función conectar() devolvió esa conexión.
#
# 3) main.py recibió correctamente el objeto devuelto.
#
# Más adelante este mensaje probablemente desaparezca,
# porque ya no será necesario para las pruebas.
# ----------------------------------------------------------

print()

print("--------------------------------")
print("La conexión fue recibida correctamente por main.py.")
print("--------------------------------")


# ==========================================================
# CERRAR LA CONEXIÓN
# ==========================================================

# ----------------------------------------------------------
# Finalizamos correctamente la sesión con Gmail.
#
# logout() es un método proporcionado por la biblioteca
# imaplib.
#
# Su función es informar a Gmail que la conexión ha
# terminado y puede cerrarse de forma segura.
#
# Más adelante probablemente moveremos esta tarea a
# gmail_client.py mediante una función específica llamada
# cerrar_conexion().
#
# Por ahora mantenemos logout() aquí porque estamos
# aprendiendo cómo funcionan los objetos y métodos.
# ----------------------------------------------------------

conexion.logout()

print("Conexión cerrada correctamente.")