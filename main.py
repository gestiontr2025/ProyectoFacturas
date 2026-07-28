"""
==========================================================
PROYECTO
==========================================================

ProyectoFacturas

Versión
--------
0.5

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

- Conexión interna con Gmail.
- Búsqueda interna de correos.
- Interpretación interna de mensajes.
- Lectura de archivos PDF.
- Creación de carpetas.
- Renombrado de facturas.

Su función es organizar el flujo general del programa
llamando a las funciones correspondientes de cada módulo.

En esta versión, main.py coordina:

- La conexión con Gmail.
- La búsqueda de todos los correos.
- La lectura del correo más reciente.
- La extracción de sus encabezados principales.
- La presentación de esos datos en la terminal.

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
# - leer_correo()
# - obtener_datos_correo()
#
# Más adelante también contendrá funciones para:
#
# - Detectar archivos adjuntos.
# - Identificar archivos PDF.
# - Descargar archivos adjuntos.
# ----------------------------------------------------------

import gmail_client


# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE FUNCIONES
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

        Es la lista de identificadores obtenida mediante:

            gmail_client.buscar_todos_los_correos()

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

    print("--------------------------------")

    # ------------------------------------------------------
    # FIN DEL BLOQUE DE RESULTADO
    # ------------------------------------------------------

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_resultado_busqueda()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_resultado_lectura()
# ==========================================================

def mostrar_resultado_lectura(id_correo, mensaje):
    """
    ==========================================================
    FUNCIÓN
    ==========================================================

    mostrar_resultado_lectura(id_correo, mensaje)

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Mostrar una confirmación de que un correo individual fue
    obtenido e interpretado correctamente.

    Esta función permite comprobar que:

        gmail_client.leer_correo()

    funciona correctamente.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    id_correo:

        Es el identificador IMAP del correo que fue solicitado.

        Por ejemplo:

            b'1323'

    mensaje:

        Es el objeto EmailMessage devuelto por:

            gmail_client.leer_correo()

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Esta función no devuelve ningún valor.

    Solamente muestra información en la terminal.

    ----------------------------------------------------------
    IMPORTANTE
    ----------------------------------------------------------

    Esta función no analiza el contenido del mensaje.

    Solamente confirma:

    - Qué identificador fue utilizado.
    - Qué tipo de objeto devolvió leer_correo().
    - Que el correo no fue guardado en el disco.
    - Que no se descargaron archivos adjuntos.

    ==========================================================
    """

    # ------------------------------------------------------
    # type() permite conocer el tipo de un objeto.
    #
    # En este caso esperamos recibir:
    #
    #     <class 'email.message.EmailMessage'>
    # ------------------------------------------------------

    tipo_mensaje = type(mensaje)


    # ------------------------------------------------------
    # INICIO DEL BLOQUE DE RESULTADO
    # ------------------------------------------------------

    print()
    print("--------------------------------")
    print("RESULTADO DE LA LECTURA")
    print("--------------------------------")

    print("Correo obtenido correctamente.")

    print()

    print("Identificador IMAP:")
    print(id_correo)

    print()

    print("Tipo de objeto recibido:")
    print(tipo_mensaje)

    print()

    print(
        "El correo fue descargado temporalmente en memoria, "
        "pero no fue guardado en el disco."
    )

    print()

    print(
        "Durante esta prueba no se descargó ningún "
        "archivo adjunto."
    )

    print("--------------------------------")

    # ------------------------------------------------------
    # FIN DEL BLOQUE DE RESULTADO
    # ------------------------------------------------------

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_resultado_lectura()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_datos_correo()
# ==========================================================

def mostrar_datos_correo(datos_correo):
    """
    ==========================================================
    FUNCIÓN
    ==========================================================

    mostrar_datos_correo(datos_correo)

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Mostrar en la terminal los encabezados principales de
    un correo electrónico.

    La información fue extraída previamente mediante:

        gmail_client.obtener_datos_correo()

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    datos_correo:

        Es un diccionario que contiene los encabezados
        principales del correo.

        Su estructura esperada es:

        {
            "Subject": "...",
            "From": "...",
            "To": "...",
            "Date": "..."
        }

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Esta función no devuelve ningún valor.

    Solamente muestra información mediante print().

    ----------------------------------------------------------
    RESPONSABILIDAD
    ----------------------------------------------------------

    Esta función solamente presenta los datos.

    No se conecta con Gmail.

    No descarga el correo.

    No interpreta los encabezados.

    No descarga archivos adjuntos.

    ==========================================================
    """

    # ------------------------------------------------------
    # Obtenemos los valores almacenados dentro del
    # diccionario.
    #
    # Para acceder al valor de una clave utilizamos:
    #
    #     diccionario["nombre_de_la_clave"]
    #
    # Por ejemplo:
    #
    #     datos_correo["Subject"]
    #
    # devuelve el asunto del correo.
    # ------------------------------------------------------

    asunto = datos_correo["Subject"]

    remitente = datos_correo["From"]

    destinatario = datos_correo["To"]

    fecha = datos_correo["Date"]


    # ------------------------------------------------------
    # INICIO DEL BLOQUE DE PRESENTACIÓN
    # ------------------------------------------------------

    print()
    print("--------------------------------")
    print("DATOS PRINCIPALES DEL CORREO")
    print("--------------------------------")


    # ------------------------------------------------------
    # Mostramos el asunto del correo.
    # ------------------------------------------------------

    print("Asunto:")
    print(asunto)

    print()


    # ------------------------------------------------------
    # Mostramos el remitente del correo.
    # ------------------------------------------------------

    print("Remitente:")
    print(remitente)

    print()


    # ------------------------------------------------------
    # Mostramos el destinatario del correo.
    # ------------------------------------------------------

    print("Destinatario:")
    print(destinatario)

    print()


    # ------------------------------------------------------
    # Mostramos la fecha original informada por el correo.
    #
    # Por el momento se presenta exactamente con el formato
    # en el que fue enviada.
    #
    # Más adelante podremos convertirla a un formato más
    # fácil de leer.
    # ------------------------------------------------------

    print("Fecha:")
    print(fecha)


    print("--------------------------------")

    # ------------------------------------------------------
    # FIN DEL BLOQUE DE PRESENTACIÓN
    # ------------------------------------------------------

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_datos_correo()
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
    5. Comprueba que la lista no esté vacía.
    6. Toma el identificador del correo más reciente.
    7. Obtiene el correo completo desde Gmail.
    8. Confirma que el mensaje fue interpretado.
    9. Extrae los encabezados principales.
    10. Muestra los encabezados en la terminal.
    11. Cierra correctamente la conexión.

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
    # PASO 1: MOSTRAR LA INFORMACIÓN DEL PROYECTO
    #
    # La función no devuelve ningún valor.
    #
    # Solamente imprime la información general en la
    # terminal.
    # ------------------------------------------------------

    mostrar_informacion_proyecto()


    # ------------------------------------------------------
    # Creamos la variable conexion y le asignamos inicialmente
    # el valor None.
    #
    # None significa:
    #
    #     "Todavía no hay ningún valor".
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
    # - La lectura de un mensaje.
    # - La extracción de sus datos.
    # ------------------------------------------------------

    try:
        # Todo lo que tiene esta indentación pertenece al try.


        # --------------------------------------------------
        # PASO 2: CONECTARSE CON GMAIL
        #
        # gmail_client.conectar() abre la conexión y la
        # devuelve mediante return.
        #
        # Guardamos esa conexión dentro de la variable:
        #
        #     conexion
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
        # PASO 3: BUSCAR TODOS LOS CORREOS
        #
        # Entregamos la conexión activa a:
        #
        #     buscar_todos_los_correos()
        #
        # Esa función:
        #
        # - Localiza la carpeta "Todos".
        # - La selecciona en modo de solo lectura.
        # - Busca mensajes leídos y no leídos.
        # - Devuelve sus identificadores.
        # --------------------------------------------------

        identificadores_correos = (
            gmail_client.buscar_todos_los_correos(
                conexion
            )
        )


        # --------------------------------------------------
        # PASO 4: MOSTRAR EL RESULTADO DE LA BÚSQUEDA
        #
        # Pasamos la lista obtenida a:
        #
        #     mostrar_resultado_busqueda()
        #
        # Esa función utiliza len() para contar cuántos
        # mensajes fueron encontrados.
        # --------------------------------------------------

        mostrar_resultado_busqueda(
            identificadores_correos
        )


        # --------------------------------------------------
        # PASO 5: COMPROBAR SI SE ENCONTRARON CORREOS
        #
        # Antes de intentar acceder a un elemento de la lista,
        # debemos comprobar que no esté vacía.
        #
        # Si la lista estuviera vacía, no existiría ningún
        # identificador que pudiéramos utilizar.
        # --------------------------------------------------


        # --------------------------------------------------
        # INICIO DEL BLOQUE IF:
        # comprobación de lista vacía
        # --------------------------------------------------

        if not identificadores_correos:
            # Este bloque solamente se ejecutará si la lista
            # no contiene ningún identificador.

            raise RuntimeError(
                "No se encontró ningún correo para realizar "
                "la prueba de lectura."
            )

        # --------------------------------------------------
        # FIN DEL BLOQUE IF:
        # comprobación de lista vacía
        # --------------------------------------------------


        # --------------------------------------------------
        # PASO 6: SELECCIONAR EL CORREO MÁS RECIENTE
        #
        # Los identificadores están guardados en una lista.
        #
        # Por ejemplo:
        #
        #     [b'1', b'2', b'3', b'4']
        #
        # En Python, el índice:
        #
        #     -1
        #
        # representa el último elemento de una colección.
        #
        # Por lo tanto:
        #
        #     identificadores_correos[-1]
        #
        # obtiene el último identificador de la lista.
        # --------------------------------------------------

        id_correo_prueba = identificadores_correos[-1]


        # --------------------------------------------------
        # PASO 7: LEER UN ÚNICO CORREO
        #
        # Llamamos a gmail_client.leer_correo() y le
        # entregamos:
        #
        # - La conexión activa.
        # - El identificador del correo elegido.
        #
        # La función solicitará el mensaje completo a Gmail
        # y convertirá sus bytes en un objeto EmailMessage.
        #
        # El objeto devuelto se guarda en:
        #
        #     mensaje
        # --------------------------------------------------

        mensaje = gmail_client.leer_correo(
            conexion,
            id_correo_prueba
        )


        # --------------------------------------------------
        # PASO 8: MOSTRAR EL RESULTADO DE LA LECTURA
        #
        # Confirmamos:
        #
        # - Qué identificador fue utilizado.
        # - Qué tipo de objeto devolvió leer_correo().
        # - Que no se guardaron archivos en el disco.
        # --------------------------------------------------

        mostrar_resultado_lectura(
            id_correo_prueba,
            mensaje
        )


        # --------------------------------------------------
        # PASO 9: EXTRAER LOS DATOS PRINCIPALES
        #
        # Entregamos el objeto EmailMessage a la nueva
        # función:
        #
        #     obtener_datos_correo()
        #
        # Esa función obtiene:
        #
        # - Subject.
        # - From.
        # - To.
        # - Date.
        #
        # Después organiza los resultados dentro de un
        # diccionario.
        #
        # Guardamos el diccionario recibido en:
        #
        #     datos_correo
        # --------------------------------------------------

        datos_correo = gmail_client.obtener_datos_correo(
            mensaje
        )


        # --------------------------------------------------
        # PASO 10: MOSTRAR LOS DATOS DEL CORREO
        #
        # Entregamos el diccionario a:
        #
        #     mostrar_datos_correo()
        #
        # Esta función se encargará únicamente de presentar
        # sus valores en la terminal.
        # --------------------------------------------------

        mostrar_datos_correo(
            datos_correo
        )

    # ------------------------------------------------------
    # FIN DEL BLOQUE TRY
    #
    # El bloque finally comienza nuevamente al nivel de
    # indentación del try.
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
# FIN DEL BLOQUE DE FUNCIONES
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