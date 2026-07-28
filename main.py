"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Versión
--------
0.7

Archivo
--------
main.py

Descripción
-----------
Este archivo funciona como punto de entrada principal del
programa.

Su responsabilidad consiste en coordinar las funciones
definidas en otros módulos.

Actualmente, el programa realiza los siguientes pasos:

1. Muestra la información general del proyecto.
2. Muestra parte de la configuración utilizada.
3. Se conecta con Gmail.
4. Busca todos los correos de la cuenta.
5. Selecciona el correo más reciente.
6. Lee el correo completo.
7. Extrae sus encabezados principales.
8. Muestra esos encabezados.
9. Detecta los archivos adjuntos.
10. Muestra el nombre y el tipo de cada adjunto.
11. Crea la carpeta principal de destino.
12. Guarda los archivos adjuntos.
13. Muestra las rutas de los archivos guardados.
14. Cierra correctamente la conexión con Gmail.

En esta versión se guardan todos los adjuntos encontrados
en el correo más reciente.

Todavía no se filtran exclusivamente archivos PDF.

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
# Importamos el módulo config.
#
# Desde config.py obtenemos:
#
# - El nombre del proyecto.
# - La versión actual.
# - El autor.
# - La cuenta de Gmail.
# - La carpeta donde se guardarán las facturas.
#
# Las credenciales privadas son cargadas desde el archivo
# .env por config.py.
# ----------------------------------------------------------

import config


# ----------------------------------------------------------
# Importamos gmail_client.
#
# Este módulo contiene las funciones relacionadas con Gmail:
#
# - conectar()
# - encontrar_carpeta_todos()
# - buscar_todos_los_correos()
# - leer_correo()
# - obtener_datos_correo()
# - obtener_adjuntos()
# ----------------------------------------------------------

import gmail_client


# ----------------------------------------------------------
# Importamos file_manager.
#
# Este módulo contiene las funciones relacionadas con el
# sistema de archivos:
#
# - Crear la carpeta de destino.
# - Guardar un adjunto.
# - Guardar todos los adjuntos.
# - Evitar sobrescribir archivos existentes.
# ----------------------------------------------------------

import file_manager


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
    Mostrar en la terminal la información general del
    proyecto.

    Actualmente muestra:

    - Nombre del proyecto.
    - Versión.
    - Autor.

    Esta función no recibe parámetros y no devuelve ningún
    valor.
    """

    print()
    print("==================================================")
    print("INFORMACIÓN DEL PROYECTO")
    print("==================================================")

    print("Proyecto:")
    print(config.PROJECT_NAME)

    print()

    print("Versión:")
    print(config.PROJECT_VERSION)

    print()

    print("Autor:")
    print(config.PROJECT_AUTHOR)

    print("==================================================")

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_informacion_proyecto()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_configuracion()
# ==========================================================

def mostrar_configuracion():
    """
    Mostrar algunos valores de configuración utilizados por
    el programa.

    Actualmente muestra:

    - La cuenta de Gmail configurada.
    - La carpeta donde se guardarán los archivos.

    Esta función nunca debe mostrar la contraseña de
    aplicación.
    """

    print()
    print("==================================================")
    print("CONFIGURACIÓN")
    print("==================================================")

    print("Cuenta de Gmail:")
    print(config.EMAIL)

    print()

    print("Carpeta de destino:")
    print(config.SAVE_FOLDER)

    print("==================================================")

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_configuracion()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_resultado_busqueda()
# ==========================================================

def mostrar_resultado_busqueda(identificadores_correos):
    """
    Mostrar cuántos correos fueron encontrados.

    Parámetros
    ----------
    identificadores_correos:

        Lista de identificadores IMAP devuelta por:

            gmail_client.buscar_todos_los_correos()

        Ejemplo:

            [b'1', b'2', b'3']
    """

    print()
    print("==================================================")
    print("RESULTADO DE LA BÚSQUEDA")
    print("==================================================")

    cantidad_correos = len(
        identificadores_correos
    )

    print("Cantidad de correos encontrados:")
    print(cantidad_correos)

    print("==================================================")

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_resultado_busqueda()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_resultado_lectura()
# ==========================================================

def mostrar_resultado_lectura(id_correo, mensaje):
    """
    Mostrar información técnica básica sobre el correo leído.

    Parámetros
    ----------
    id_correo:

        Identificador IMAP del correo.

        Ejemplo:

            b'1332'

    mensaje:

        Objeto EmailMessage devuelto por:

            gmail_client.leer_correo()
    """

    print()
    print("==================================================")
    print("RESULTADO DE LA LECTURA")
    print("==================================================")

    print("ID del correo:")
    print(id_correo)

    print()

    print("Tipo de objeto creado:")
    print(type(mensaje))

    print("==================================================")

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_resultado_lectura()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_datos_correo()
# ==========================================================

def mostrar_datos_correo(datos_correo):
    """
    Mostrar los encabezados principales de un correo.

    Parámetros
    ----------
    datos_correo:

        Diccionario devuelto por:

            gmail_client.obtener_datos_correo()

        Su estructura esperada es:

            {
                "Subject": "...",
                "From": "...",
                "To": "...",
                "Date": "..."
            }
    """

    print()
    print("==================================================")
    print("DATOS PRINCIPALES DEL CORREO")
    print("==================================================")

    print("Asunto:")
    print(datos_correo["Subject"])

    print()

    print("Remitente:")
    print(datos_correo["From"])

    print()

    print("Destinatario:")
    print(datos_correo["To"])

    print()

    print("Fecha:")
    print(datos_correo["Date"])

    print("==================================================")

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_datos_correo()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_adjuntos()
# ==========================================================

def mostrar_adjuntos(adjuntos):
    """
    Mostrar información sobre los archivos adjuntos
    detectados dentro de un correo.

    Parámetros
    ----------
    adjuntos:

        Lista devuelta por:

            gmail_client.obtener_adjuntos()

        Cada elemento tiene una estructura parecida a:

            {
                "nombre": "factura.pdf",
                "tipo_contenido": "application/pdf",
                "parte": parte_mime
            }

    La clave "parte" no se muestra porque contiene el objeto
    MIME interno del archivo.
    """

    print()
    print("==================================================")
    print("ARCHIVOS ADJUNTOS")
    print("==================================================")

    cantidad_adjuntos = len(
        adjuntos
    )

    print("Cantidad de adjuntos encontrados:")
    print(cantidad_adjuntos)

    # ------------------------------------------------------
    # Si la lista está vacía, informamos que el correo no
    # contiene adjuntos y terminamos la función.
    # ------------------------------------------------------

    if not adjuntos:

        print()
        print("El correo no contiene archivos adjuntos.")

        print("==================================================")

        return

    # ------------------------------------------------------
    # enumerate() permite obtener al mismo tiempo:
    #
    # - El número del adjunto.
    # - El diccionario correspondiente al adjunto.
    #
    # start=1 hace que la numeración comience desde 1.
    # ------------------------------------------------------

    for numero_adjunto, adjunto in enumerate(
        adjuntos,
        start=1
    ):

        print()
        print("--------------------------------")
        print(f"Adjunto número {numero_adjunto}")
        print("--------------------------------")

        nombre_archivo = adjunto["nombre"]
        tipo_contenido = adjunto["tipo_contenido"]

        print("Nombre:")
        print(nombre_archivo)

        print()

        print("Tipo de contenido:")
        print(tipo_contenido)

    print()
    print("==================================================")

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_adjuntos()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_archivos_guardados()
# ==========================================================

def mostrar_archivos_guardados(archivos_guardados):
    """
    Mostrar las rutas de los archivos guardados.

    Parámetros
    ----------
    archivos_guardados:

        Lista de objetos Path devuelta por:

            file_manager.guardar_adjuntos()

        Cada objeto Path representa la ubicación final de un
        archivo guardado.
    """

    print()
    print("==================================================")
    print("ARCHIVOS GUARDADOS")
    print("==================================================")

    cantidad_archivos = len(
        archivos_guardados
    )

    print("Cantidad de archivos guardados:")
    print(cantidad_archivos)

    # ------------------------------------------------------
    # Si la lista está vacía, no hay rutas para mostrar.
    # ------------------------------------------------------

    if not archivos_guardados:

        print()
        print("No se guardó ningún archivo.")

        print("==================================================")

        return

    # ------------------------------------------------------
    # Recorremos las rutas de los archivos guardados.
    # ------------------------------------------------------

    for numero_archivo, ruta_archivo in enumerate(
        archivos_guardados,
        start=1
    ):

        print()
        print("--------------------------------")
        print(f"Archivo número {numero_archivo}")
        print("--------------------------------")

        print("Guardado en:")
        print(ruta_archivo)

    print()
    print("==================================================")

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_archivos_guardados()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN main()
# ==========================================================

def main():
    """
    Coordinar el flujo completo del programa.

    Flujo actual
    ------------
    1. Mostrar información del proyecto.
    2. Mostrar la configuración.
    3. Conectarse con Gmail.
    4. Buscar todos los correos.
    5. Verificar que haya correos.
    6. Seleccionar el correo más reciente.
    7. Leer el correo completo.
    8. Mostrar información técnica de la lectura.
    9. Extraer los encabezados.
    10. Mostrar los encabezados.
    11. Detectar los archivos adjuntos.
    12. Mostrar información de los adjuntos.
    13. Crear la carpeta de destino.
    14. Guardar los adjuntos.
    15. Mostrar las rutas finales.
    16. Cerrar la conexión con Gmail.
    """

    # ------------------------------------------------------
    # Mostramos la información general antes de conectarnos.
    # ------------------------------------------------------

    mostrar_informacion_proyecto()

    mostrar_configuracion()

    # ------------------------------------------------------
    # Inicializamos la variable con None.
    #
    # Si la conexión falla antes de crearse, finalmente
    # podremos comprobar que no existe una conexión abierta.
    # ------------------------------------------------------

    conexion = None

    # ------------------------------------------------------
    # El bloque try contiene el flujo principal.
    #
    # Si aparece un error, será capturado por except.
    #
    # finally intentará cerrar la conexión en todos los
    # casos.
    # ------------------------------------------------------

    try:

        # --------------------------------------------------
        # Abrimos la conexión IMAP con Gmail.
        # --------------------------------------------------

        conexion = gmail_client.conectar()

        # --------------------------------------------------
        # Buscamos todos los correos disponibles dentro de
        # la carpeta utilizada por gmail_client.
        # --------------------------------------------------

        identificadores_correos = (
            gmail_client.buscar_todos_los_correos(
                conexion
            )
        )

        # --------------------------------------------------
        # Mostramos la cantidad de mensajes encontrados.
        # --------------------------------------------------

        mostrar_resultado_busqueda(
            identificadores_correos
        )

        # --------------------------------------------------
        # Si la lista está vacía, no podemos seleccionar un
        # mensaje.
        # --------------------------------------------------

        if not identificadores_correos:

            print()
            print(
                "No se encontraron correos para procesar."
            )

            return

        # --------------------------------------------------
        # Seleccionamos el último identificador.
        #
        # En Python, [-1] representa el último elemento de
        # una lista.
        #
        # Normalmente será el correo más reciente.
        # --------------------------------------------------

        id_correo_prueba = identificadores_correos[-1]

        # --------------------------------------------------
        # Leemos el correo completo y lo convertimos en un
        # objeto EmailMessage.
        # --------------------------------------------------

        mensaje = gmail_client.leer_correo(
            conexion,
            id_correo_prueba
        )

        # --------------------------------------------------
        # Mostramos el identificador y el tipo de objeto.
        # --------------------------------------------------

        mostrar_resultado_lectura(
            id_correo_prueba,
            mensaje
        )

        # --------------------------------------------------
        # Extraemos los encabezados principales.
        # --------------------------------------------------

        datos_correo = gmail_client.obtener_datos_correo(
            mensaje
        )

        # --------------------------------------------------
        # Mostramos los encabezados.
        # --------------------------------------------------

        mostrar_datos_correo(
            datos_correo
        )

        # --------------------------------------------------
        # Detectamos las partes MIME consideradas adjuntos.
        #
        # El resultado será una lista de diccionarios.
        # --------------------------------------------------

        adjuntos = gmail_client.obtener_adjuntos(
            mensaje
        )

        # --------------------------------------------------
        # Mostramos los adjuntos detectados.
        # --------------------------------------------------

        mostrar_adjuntos(
            adjuntos
        )

        # --------------------------------------------------
        # Guardamos los adjuntos dentro de la carpeta
        # configurada en config.py.
        #
        # file_manager.guardar_adjuntos() también se ocupa
        # de crear la carpeta si todavía no existe.
        #
        # En esta versión se guardan todos los adjuntos.
        #
        # El filtro exclusivo para archivos PDF se añadirá
        # más adelante.
        # --------------------------------------------------

        archivos_guardados = file_manager.guardar_adjuntos(
            adjuntos,
            config.SAVE_FOLDER
        )

        # --------------------------------------------------
        # Mostramos las rutas finales de los archivos
        # guardados.
        # --------------------------------------------------

        mostrar_archivos_guardados(
            archivos_guardados
        )

    # ------------------------------------------------------
    # Capturamos cualquier excepción producida durante:
    #
    # - La conexión.
    # - La búsqueda.
    # - La lectura.
    # - La detección de adjuntos.
    # - La creación de la carpeta.
    # - El guardado de archivos.
    # ------------------------------------------------------

    except Exception as error:

        print()
        print("==================================================")
        print("SE PRODUJO UN ERROR")
        print("==================================================")

        print("Tipo de error:")
        print(type(error).__name__)

        print()

        print("Descripción:")
        print(error)

        print("==================================================")

    # ------------------------------------------------------
    # finally se ejecuta siempre.
    #
    # Su objetivo es cerrar la conexión incluso si apareció
    # un error durante el procesamiento.
    # ------------------------------------------------------

    finally:

        # --------------------------------------------------
        # Comprobamos que la conexión haya sido creada.
        # --------------------------------------------------

        if conexion is not None:

            try:

                # ------------------------------------------
                # Cerramos correctamente la sesión IMAP.
                # ------------------------------------------

                conexion.logout()

                print()
                print(
                    "Conexión cerrada correctamente."
                )

            except Exception as error_cierre:

                print()
                print(
                    "No fue posible cerrar la conexión "
                    "de forma normal."
                )

                print(error_cierre)

# ==========================================================
# FIN DE LA FUNCIÓN main()
# ==========================================================


# ==========================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# ==========================================================


# ----------------------------------------------------------
# Cuando ejecutamos:
#
#     python main.py
#
# Python asigna "__main__" a la variable especial __name__.
#
# Esta condición evita que main() se ejecute automáticamente
# si el archivo es importado desde otro módulo.
# ----------------------------------------------------------

if __name__ == "__main__":
    main()


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================