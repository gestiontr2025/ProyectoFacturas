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
main.py

Descripción
-----------
Este archivo funciona como punto de entrada principal del
programa.

Su responsabilidad consiste en coordinar las funciones
definidas en otros módulos.

Actualmente, el programa realiza los siguientes pasos:

1. Muestra la información general del proyecto.
2. Muestra la configuración utilizada.
3. Se conecta con Gmail.
4. Busca todos los correos de la cuenta.
5. Selecciona una cantidad limitada de correos recientes.
6. Recorre los correos seleccionados.
7. Lee cada correo completo.
8. Extrae sus encabezados principales.
9. Detecta sus archivos adjuntos.
10. Determina una carpeta según el remitente y la fecha.
11. Filtra únicamente los archivos PDF.
12. Evita guardar archivos que ya existan.
13. Guarda los PDF nuevos.
14. Muestra un resumen final del procesamiento.
15. Cierra correctamente la conexión con Gmail.

La estructura de carpetas utilizada en esta versión es:

    Facturas
        └── Remitente
            └── Año
                └── Número - Mes
                    └── factura.pdf

Ejemplo:

    Facturas
        └── Arta verdurleros
            └── 2026
                └── 07 - Julio
                    └── factura.pdf

El límite de correos procesados se configura mediante:

    config.EMAIL_PROCESSING_LIMIT

Autor
------
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# INICIO DEL BLOQUE DE IMPORTACIONES
# ==========================================================

import config
import file_manager
import gmail_client
import invoice_organizer

# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_informacion_proyecto()
# ==========================================================

def mostrar_informacion_proyecto():
    """
    Mostrar la información general del proyecto.

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
    Mostrar los valores públicos de configuración utilizados
    por el programa.

    Actualmente muestra:

    - La cuenta de Gmail.
    - La carpeta principal de destino.
    - El límite de correos por ejecución.

    La contraseña de aplicación nunca debe mostrarse.
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

    print()

    print("Límite de correos por ejecución:")
    print(config.EMAIL_PROCESSING_LIMIT)

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

    cantidad_correos = len(
        identificadores_correos
    )

    print()
    print("==================================================")
    print("RESULTADO DE LA BÚSQUEDA")
    print("==================================================")

    print("Cantidad total de correos encontrados:")
    print(cantidad_correos)

    print("==================================================")

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_resultado_busqueda()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN seleccionar_correos_recientes()
# ==========================================================

def seleccionar_correos_recientes(
    identificadores_correos,
    limite
):
    """
    Seleccionar los correos más recientes.

    Parámetros
    ----------
    identificadores_correos:

        Lista completa de identificadores IMAP.

    limite:

        Cantidad máxima de correos que deseamos procesar.

    Retorna
    -------
    list

        Lista con los identificadores seleccionados.

        Los correos se devuelven ordenados desde el más
        reciente hasta el más antiguo.

    Ejemplo
    -------
    Si recibimos:

        [b'1', b'2', b'3', b'4', b'5']

    y el límite es 3, devuelve:

        [b'5', b'4', b'3']
    """

    # ------------------------------------------------------
    # Validamos que el límite sea un número entero.
    # ------------------------------------------------------

    if not isinstance(limite, int):

        raise TypeError(
            "EMAIL_PROCESSING_LIMIT debe ser un número "
            "entero."
        )

    # ------------------------------------------------------
    # Validamos que el límite sea mayor que cero.
    # ------------------------------------------------------

    if limite <= 0:

        raise ValueError(
            "EMAIL_PROCESSING_LIMIT debe ser mayor que cero."
        )

    # ------------------------------------------------------
    # [-limite:] selecciona los últimos elementos de la
    # lista.
    #
    # Normalmente, los últimos identificadores corresponden
    # a los correos más recientes.
    # ------------------------------------------------------

    correos_recientes = identificadores_correos[
        -limite:
    ]

    # ------------------------------------------------------
    # reversed() invierte el orden.
    #
    # De esta manera procesaremos primero el correo más
    # reciente.
    # ------------------------------------------------------

    correos_recientes = list(
        reversed(correos_recientes)
    )

    return correos_recientes

# ==========================================================
# FIN DE LA FUNCIÓN seleccionar_correos_recientes()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_inicio_procesamiento()
# ==========================================================

def mostrar_inicio_procesamiento(
    numero_correo,
    cantidad_correos,
    id_correo
):
    """
    Mostrar el comienzo del procesamiento de un correo.

    Parámetros
    ----------
    numero_correo:

        Posición actual dentro del recorrido.

    cantidad_correos:

        Cantidad total de correos seleccionados.

    id_correo:

        Identificador IMAP del mensaje actual.
    """

    print()
    print()
    print("##################################################")
    print(
        f"PROCESANDO CORREO "
        f"{numero_correo} DE {cantidad_correos}"
    )
    print("##################################################")

    print("ID del correo:")
    print(id_correo)

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_inicio_procesamiento()
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

    cantidad_adjuntos = len(
        adjuntos
    )

    print()
    print("==================================================")
    print("ARCHIVOS ADJUNTOS")
    print("==================================================")

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

        print("Nombre:")
        print(adjunto["nombre"])

        print()

        print("Tipo de contenido:")
        print(adjunto["tipo_contenido"])

    print()
    print("==================================================")

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_adjuntos()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_carpeta_asignada()
# ==========================================================

def mostrar_carpeta_asignada(carpeta_factura):
    """
    Mostrar la carpeta asignada al correo actual.

    Parámetros
    ----------
    carpeta_factura:

        Objeto Path devuelto por:

            invoice_organizer.construir_carpeta_factura()

    Esta carpeta se construye utilizando:

    - El remitente del correo.
    - El año del correo.
    - El mes del correo.
    """

    print()
    print("==================================================")
    print("CARPETA ASIGNADA")
    print("==================================================")

    print("Los archivos PDF de este correo se guardarán en:")
    print(carpeta_factura)

    print("==================================================")

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_carpeta_asignada()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_archivos_guardados()
# ==========================================================

def mostrar_archivos_guardados(archivos_guardados):
    """
    Mostrar las rutas de los archivos guardados durante el
    procesamiento del correo actual.

    Parámetros
    ----------
    archivos_guardados:

        Lista de objetos Path devuelta por:

            file_manager.guardar_adjuntos()

        Cada objeto Path representa la ubicación final de un
        archivo guardado.
    """

    cantidad_archivos = len(
        archivos_guardados
    )

    print()
    print("==================================================")
    print("ARCHIVOS NUEVOS GUARDADOS")
    print("==================================================")

    print("Cantidad de archivos nuevos guardados:")
    print(cantidad_archivos)

    # ------------------------------------------------------
    # Si la lista está vacía, no hay rutas para mostrar.
    # ------------------------------------------------------

    if not archivos_guardados:

        print()
        print(
            "No se guardó ningún archivo nuevo."
        )

        print(
            "El correo puede no contener archivos PDF o "
            "los archivos pueden existir previamente."
        )

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
# INICIO DE LA FUNCIÓN procesar_correo()
# ==========================================================

def procesar_correo(conexion, id_correo):
    """
    Leer y procesar un único correo.

    Parámetros
    ----------
    conexion:

        Conexión IMAP activa con Gmail.

    id_correo:

        Identificador IMAP del correo que se procesará.

    Retorna
    -------
    list

        Lista con las rutas de los archivos PDF nuevos que
        fueron guardados.

    Flujo
    -----
    1. Leer el correo.
    2. Obtener sus datos principales.
    3. Mostrar sus datos.
    4. Detectar sus adjuntos.
    5. Mostrar los adjuntos.
    6. Construir la carpeta correspondiente.
    7. Filtrar y guardar los PDF nuevos.
    8. Devolver las rutas guardadas.
    """

    # ------------------------------------------------------
    # Leemos el correo completo y lo convertimos en un
    # objeto EmailMessage.
    # ------------------------------------------------------

    mensaje = gmail_client.leer_correo(
        conexion,
        id_correo
    )

    # ------------------------------------------------------
    # Extraemos los encabezados principales.
    # ------------------------------------------------------

    datos_correo = gmail_client.obtener_datos_correo(
        mensaje
    )

    # ------------------------------------------------------
    # Mostramos los encabezados del correo.
    # ------------------------------------------------------

    mostrar_datos_correo(
        datos_correo
    )

    # ------------------------------------------------------
    # Detectamos las partes MIME consideradas adjuntos.
    # ------------------------------------------------------

    adjuntos = gmail_client.obtener_adjuntos(
        mensaje
    )

    # ------------------------------------------------------
    # Mostramos la información de los adjuntos detectados.
    # ------------------------------------------------------

    mostrar_adjuntos(
        adjuntos
    )

    # ------------------------------------------------------
    # Construimos una carpeta específica utilizando:
    #
    # - El remitente del correo.
    # - El año del correo.
    # - El mes del correo.
    #
    # Ejemplo:
    #
    # Facturas/
    #     Arta verdurleros/
    #         2026/
    #             07 - Julio/
    # ------------------------------------------------------

    carpeta_factura = (
        invoice_organizer.construir_carpeta_factura(
            config.SAVE_FOLDER,
            datos_correo
        )
    )

    # ------------------------------------------------------
    # Mostramos la carpeta asignada al correo.
    #
    # La creación física de la carpeta será realizada por
    # file_manager cuando tenga que guardar un archivo.
    # ------------------------------------------------------

    mostrar_carpeta_asignada(
        carpeta_factura
    )

    # ------------------------------------------------------
    # Guardamos únicamente los adjuntos PDF nuevos dentro de
    # la carpeta específica.
    #
    # file_manager.guardar_adjuntos() también se ocupa de:
    #
    # - Filtrar los PDF.
    # - Crear la carpeta si todavía no existe.
    # - Evitar duplicados por nombre.
    # ------------------------------------------------------

    archivos_guardados = file_manager.guardar_adjuntos(
        adjuntos,
        carpeta_factura
    )

    # ------------------------------------------------------
    # Mostramos las rutas de los archivos guardados.
    # ------------------------------------------------------

    mostrar_archivos_guardados(
        archivos_guardados
    )

    return archivos_guardados

# ==========================================================
# FIN DE LA FUNCIÓN procesar_correo()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_resumen_final()
# ==========================================================

def mostrar_resumen_final(
    cantidad_seleccionada,
    cantidad_procesada,
    cantidad_errores,
    archivos_guardados
):
    """
    Mostrar un resumen general al finalizar la ejecución.

    Parámetros
    ----------
    cantidad_seleccionada:

        Cantidad de correos seleccionados inicialmente.

    cantidad_procesada:

        Cantidad de correos procesados correctamente.

    cantidad_errores:

        Cantidad de correos que produjeron un error.

    archivos_guardados:

        Lista con todas las rutas guardadas durante la
        ejecución.
    """

    print()
    print()
    print("==================================================")
    print("RESUMEN FINAL")
    print("==================================================")

    print("Correos seleccionados:")
    print(cantidad_seleccionada)

    print()

    print("Correos procesados correctamente:")
    print(cantidad_procesada)

    print()

    print("Correos con errores:")
    print(cantidad_errores)

    print()

    print("Total de archivos PDF nuevos guardados:")
    print(len(archivos_guardados))

    # ------------------------------------------------------
    # Si se guardaron archivos, mostramos todas sus rutas.
    # ------------------------------------------------------

    if archivos_guardados:

        print()
        print("Archivos guardados durante esta ejecución:")

        for numero_archivo, ruta_archivo in enumerate(
            archivos_guardados,
            start=1
        ):

            print()
            print(
                f"{numero_archivo}. {ruta_archivo}"
            )

    print()
    print("==================================================")

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_resumen_final()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN main()
# ==========================================================

def main():
    """
    Coordinar el flujo completo del programa.

    Flujo actual
    ------------
    1. Mostrar la información del proyecto.
    2. Mostrar la configuración.
    3. Conectarse con Gmail.
    4. Buscar todos los correos.
    5. Seleccionar los correos más recientes.
    6. Procesar cada correo seleccionado.
    7. Construir una carpeta según remitente, año y mes.
    8. Guardar únicamente los PDF nuevos.
    9. Mostrar el resumen final.
    10. Cerrar la conexión con Gmail.
    """

    # ------------------------------------------------------
    # Mostramos información antes de abrir la conexión.
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
    # Si aparece un error general, será capturado por except.
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
        # Mostramos la cantidad total de mensajes.
        # --------------------------------------------------

        mostrar_resultado_busqueda(
            identificadores_correos
        )

        # --------------------------------------------------
        # Si la lista está vacía, no hay nada para procesar.
        # --------------------------------------------------

        if not identificadores_correos:

            print()
            print(
                "No se encontraron correos para procesar."
            )

            return

        # --------------------------------------------------
        # Seleccionamos solamente los correos más recientes
        # según el límite configurado.
        # --------------------------------------------------

        correos_seleccionados = (
            seleccionar_correos_recientes(
                identificadores_correos,
                config.EMAIL_PROCESSING_LIMIT
            )
        )

        cantidad_seleccionada = len(
            correos_seleccionados
        )

        print()
        print("==================================================")
        print("CORREOS SELECCIONADOS")
        print("==================================================")

        print("Cantidad de correos que serán procesados:")
        print(cantidad_seleccionada)

        print("==================================================")

        # --------------------------------------------------
        # Estas variables permiten construir el resumen
        # general al finalizar.
        # --------------------------------------------------

        cantidad_procesada = 0

        cantidad_errores = 0

        todos_los_archivos_guardados = []

        # --------------------------------------------------
        # Recorremos todos los correos seleccionados.
        # --------------------------------------------------

        for numero_correo, id_correo in enumerate(
            correos_seleccionados,
            start=1
        ):

            mostrar_inicio_procesamiento(
                numero_correo,
                cantidad_seleccionada,
                id_correo
            )

            # ----------------------------------------------
            # Cada correo tiene su propio bloque try.
            #
            # De esta forma, si un correo produce un error,
            # el programa informa el problema y continúa con
            # los demás mensajes.
            # ----------------------------------------------

            try:

                archivos_guardados = procesar_correo(
                    conexion,
                    id_correo
                )

                # ------------------------------------------
                # extend() agrega todos los elementos de una
                # lista dentro de otra lista.
                # ------------------------------------------

                todos_los_archivos_guardados.extend(
                    archivos_guardados
                )

                cantidad_procesada += 1

            except Exception as error_correo:

                cantidad_errores += 1

                print()
                print("==================================================")
                print("ERROR AL PROCESAR EL CORREO")
                print("==================================================")

                print("ID del correo:")
                print(id_correo)

                print()

                print("Tipo de error:")
                print(type(error_correo).__name__)

                print()

                print("Descripción:")
                print(error_correo)

                print()
                print(
                    "El programa continuará con el "
                    "siguiente correo."
                )

                print("==================================================")

        # --------------------------------------------------
        # Mostramos el resumen general después de terminar el
        # recorrido.
        # --------------------------------------------------

        mostrar_resumen_final(
            cantidad_seleccionada,
            cantidad_procesada,
            cantidad_errores,
            todos_los_archivos_guardados
        )

    # ------------------------------------------------------
    # Este bloque captura errores generales, por ejemplo:
    #
    # - Fallo al conectar con Gmail.
    # - Fallo al buscar mensajes.
    # - Configuración inválida.
    # ------------------------------------------------------

    except Exception as error:

        print()
        print("==================================================")
        print("SE PRODUJO UN ERROR GENERAL")
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