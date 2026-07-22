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
main.py

Descripción
-----------
Este archivo es el punto de entrada principal del programa.

Cuando ejecutamos:

    python main.py

Python comienza leyendo este archivo.

La responsabilidad de main.py es coordinar el trabajo
de los distintos módulos del proyecto.

Este archivo NO debe contener la lógica específica de:

- Conexión con Gmail.
- Búsqueda interna de correos.
- Lectura de PDFs.
- Creación de carpetas.
- Renombrado de facturas.

Su función es organizar el flujo general del programa
llamando a las funciones correspondientes de cada módulo.

Autor
------
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# INICIO DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ----------------------------------------------------------
# Importamos el módulo de configuración.
#
# Este módulo contiene la información configurable
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
# Importamos el módulo encargado de las tareas relacionadas
# con Gmail.
#
# Actualmente contiene:
#
# - conectar()
# - encontrar_carpeta_todos()
# - buscar_todos_los_correos()
#
# Más adelante también contendrá funciones para:
#
# - Leer mensajes individuales.
# - Detectar archivos adjuntos.
# - Descargar archivos adjuntos.
# - Cerrar la conexión.
# ----------------------------------------------------------

import gmail_client


# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_informacion_proyecto()
# ==========================================================

def mostrar_informacion_proyecto():
    """
    ==========================================================
    FUNCIÓN
    ==========================================================

    mostrar_informacion_proyecto()

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Mostrar en la terminal la información general del
    proyecto y la configuración principal de la ejecución.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    Esta función no recibe parámetros.

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Esta función no devuelve ningún valor.

    Solamente muestra información mediante print().

    ==========================================================
    """

    # ------------------------------------------------------
    # INICIO DEL BLOQUE DE INFORMACIÓN GENERAL
    # ------------------------------------------------------

    print("==================================================")
    print(config.PROJECT_NAME)
    print(f"Versión {config.PROJECT_VERSION}")
    print(f"Autor: {config.PROJECT_AUTHOR}")
    print("==================================================")

    print()

    # ------------------------------------------------------
    # FIN DEL BLOQUE DE INFORMACIÓN GENERAL
    # ------------------------------------------------------


    # ------------------------------------------------------
    # INICIO DEL BLOQUE DE CONFIGURACIÓN ACTUAL
    #
    # Mostramos la configuración principal que utilizará
    # el programa durante esta ejecución.
    #
    # Esto permite comprobar rápidamente:
    #
    # - Que estamos utilizando la cuenta correcta.
    # - Que la carpeta de trabajo es la esperada.
    #
    # IMPORTANTE:
    #
    # Nunca mostramos la contraseña de aplicación.
    # ------------------------------------------------------

    print("Correo configurado:")
    print(config.EMAIL)

    print()

    print("Carpeta de trabajo:")
    print(config.SAVE_FOLDER)

    print()

    # ------------------------------------------------------
    # FIN DEL BLOQUE DE CONFIGURACIÓN ACTUAL
    # ------------------------------------------------------

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_informacion_proyecto()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_resultado_busqueda()
# ==========================================================

def mostrar_resultado_busqueda(identificadores_correos):
    """
    ==========================================================
    FUNCIÓN
    ==========================================================

    mostrar_resultado_busqueda(identificadores_correos)

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Mostrar cuántos correos fueron encontrados durante
    la búsqueda realizada en Gmail.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    identificadores_correos:

        Es la lista de identificadores obtenida mediante
        gmail_client.buscar_todos_los_correos().

        Un ejemplo de esta lista sería:

            [b'1', b'2', b'3', b'4']

        Cada elemento representa un mensaje encontrado.

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Esta función no devuelve ningún valor.

    Solamente muestra información en la terminal.

    ==========================================================
    """

    # ------------------------------------------------------
    # len() cuenta cuántos elementos contiene una colección.
    #
    # En este caso, cuenta cuántos identificadores de correo
    # existen dentro de la lista.
    #
    # Si la lista fuera:
    #
    #     [b'1', b'2', b'3']
    #
    # len() devolvería:
    #
    #     3
    # ------------------------------------------------------

    cantidad_correos = len(identificadores_correos)


    # ------------------------------------------------------
    # INICIO DEL BLOQUE DE RESULTADO
    # ------------------------------------------------------

    print()
    print("--------------------------------")
    print("RESULTADO DE LA BÚSQUEDA")
    print("--------------------------------")

    print(f"Se encontraron {cantidad_correos} correos.")

    print()
    print(
        "Durante esta prueba no se descargó ningún correo "
        "ni archivo adjunto."
    )

    print("--------------------------------")

    # ------------------------------------------------------
    # FIN DEL BLOQUE DE RESULTADO
    # ------------------------------------------------------

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_resultado_busqueda()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN main()
# ==========================================================

def main():
    """
    ==========================================================
    FUNCIÓN PRINCIPAL
    ==========================================================

    main()

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Coordinar el flujo principal del programa.

    En esta versión, la función realiza estos pasos:

    1. Muestra la información del proyecto.
    2. Se conecta con Gmail.
    3. Busca todos los correos de la cuenta.
    4. Cuenta cuántos mensajes fueron encontrados.
    5. Cierra correctamente la conexión.

    ----------------------------------------------------------
    IMPORTANTE
    ----------------------------------------------------------

    main() coordina las tareas, pero no implementa la lógica
    interna de Gmail.

    La lógica específica permanece dentro de:

        gmail_client.py

    Esta separación ayuda a mantener el proyecto:

    - Ordenado.
    - Fácil de entender.
    - Fácil de probar.
    - Fácil de modificar.

    ==========================================================
    """

    # ------------------------------------------------------
    # Primero mostramos la información general del proyecto.
    #
    # La función no devuelve ningún valor. Solamente imprime
    # la información en la terminal.
    # ------------------------------------------------------

    mostrar_informacion_proyecto()


    # ------------------------------------------------------
    # Creamos la variable conexion y le asignamos inicialmente
    # el valor None.
    #
    # None significa:
    #
    #     "Todavía no hay ningún valor"
    #
    # Hacemos esto antes del try porque luego necesitaremos
    # comprobar si la conexión llegó a abrirse correctamente.
    # ------------------------------------------------------

    conexion = None


    # ------------------------------------------------------
    # INICIO DEL BLOQUE TRY
    #
    # try significa:
    #
    #     "Intentá ejecutar este código".
    #
    # Colocamos aquí las operaciones que podrían producir
    # errores, como:
    #
    # - La conexión a Internet.
    # - El inicio de sesión.
    # - La selección de una carpeta.
    # - La búsqueda de correos.
    # ------------------------------------------------------

    try:
        # Todo lo que tiene esta indentación pertenece al try.


        # --------------------------------------------------
        # PASO 1: CONECTARSE CON GMAIL
        #
        # gmail_client.conectar() abre la conexión y la
        # devuelve mediante return.
        #
        # Guardamos esa conexión dentro de la variable
        # llamada conexion.
        # --------------------------------------------------

        conexion = gmail_client.conectar()


        # --------------------------------------------------
        # Este mensaje tiene fines educativos.
        #
        # Confirma que:
        #
        # 1. gmail_client.py abrió la conexión.
        # 2. conectar() devolvió el objeto.
        # 3. main.py recibió correctamente ese objeto.
        # --------------------------------------------------

        print()

        print("--------------------------------")
        print(
            "La conexión fue recibida correctamente "
            "por main.py."
        )
        print("--------------------------------")


        # --------------------------------------------------
        # PASO 2: BUSCAR TODOS LOS CORREOS
        #
        # Le entregamos la conexión activa a la función
        # buscar_todos_los_correos().
        #
        # Esa función:
        #
        # - Localiza la carpeta "Todos".
        # - La selecciona en modo de solo lectura.
        # - Busca mensajes leídos y no leídos.
        # - Devuelve sus identificadores.
        #
        # Todavía no descarga los mensajes completos ni
        # sus archivos adjuntos.
        # --------------------------------------------------

        identificadores_correos = (
            gmail_client.buscar_todos_los_correos(
                conexion
            )
        )


        # --------------------------------------------------
        # PASO 3: MOSTRAR EL RESULTADO
        #
        # Pasamos la lista obtenida a nuestra función
        # mostrar_resultado_busqueda().
        #
        # Esa función utilizará len() para contar cuántos
        # mensajes fueron encontrados.
        # --------------------------------------------------

        mostrar_resultado_busqueda(
            identificadores_correos
        )

    # ------------------------------------------------------
    # FIN DEL BLOQUE TRY
    #
    # El bloque finally que aparece a continuación comienza
    # nuevamente al nivel de indentación del try.
    # ------------------------------------------------------


    # ------------------------------------------------------
    # INICIO DEL BLOQUE FINALLY
    #
    # finally significa:
    #
    #     "Ejecutá este código siempre".
    #
    # Se ejecutará tanto si todo salió correctamente como
    # si ocurrió un error dentro del try.
    #
    # Esto resulta ideal para cerrar recursos importantes,
    # como una conexión con Gmail.
    # ------------------------------------------------------

    finally:
        # Todo lo indentado aquí pertenece al finally.


        # --------------------------------------------------
        # INICIO DEL BLOQUE IF
        #
        # Comprobamos que conexion sea diferente de None.
        #
        # Si sigue siendo None, significa que la conexión
        # nunca llegó a abrirse.
        #
        # En ese caso no debemos intentar llamar logout(),
        # porque no existe ninguna sesión que cerrar.
        # --------------------------------------------------

        if conexion is not None:
            # Este código solamente se ejecutará si realmente
            # existe un objeto de conexión.


            # ----------------------------------------------
            # Cerramos correctamente la sesión IMAP.
            # ----------------------------------------------

            conexion.logout()


            # ----------------------------------------------
            # Mostramos una confirmación.
            # ----------------------------------------------

            print()
            print("Conexión cerrada correctamente.")

        # --------------------------------------------------
        # FIN DEL BLOQUE IF
        # ------------------------------------------------------

    # ------------------------------------------------------
    # FIN DEL BLOQUE FINALLY
    # ------------------------------------------------------

# ==========================================================
# FIN DE LA FUNCIÓN main()
# ==========================================================


# ==========================================================
# INICIO DEL PUNTO DE ENTRADA DEL PROGRAMA
# ==========================================================

# ----------------------------------------------------------
# Esta condición comprueba si main.py está siendo ejecutado
# directamente.
#
# Cuando usamos:
#
#     python main.py
#
# Python asigna a la variable especial __name__ el valor:
#
#     "__main__"
#
# Por eso la condición será verdadera y se llamará a main().
#
# En cambio, si en el futuro otro archivo importa main.py,
# esta condición será falsa y el programa no comenzará a
# ejecutarse automáticamente.
#
# Esto permite reutilizar las funciones de main.py sin
# iniciar todo el programa accidentalmente.
# ----------------------------------------------------------

if __name__ == "__main__":
    # INICIO DEL BLOQUE IF

    main()

    # FIN DEL BLOQUE IF

# ==========================================================
# FIN DEL PUNTO DE ENTRADA DEL PROGRAMA
# ==========================================================