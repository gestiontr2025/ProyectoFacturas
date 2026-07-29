"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Archivo
-------
main.py

Descripción
-----------
Este archivo funciona como punto de entrada principal del
programa.

Su responsabilidad consiste en coordinar las funciones
definidas en los demás módulos.

La versión actual del proyecto no se encuentra escrita
directamente en este archivo.

Cada vez que el programa se ejecuta, main.py importa:

    version.py

y obtiene el valor de:

    version.PROJECT_VERSION

Esto permite actualizar la versión modificando solamente
el archivo version.py.

La salida visual de la consola se encuentra centralizada
parcialmente dentro del módulo:

    console_output.py

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
14. Muestra un resumen final.
15. Cierra correctamente la conexión con Gmail.

La estructura de carpetas utilizada es:

    Facturas
        └── Remitente
            └── Año
                └── Número - Mes
                    └── factura.pdf

Autor
-----
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# INICIO DEL BLOQUE DE IMPORTACIONES
# ==========================================================

import config
import console_output
import file_manager
import gmail_client
import invoice_organizer
import version

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
    - Versión obtenida desde version.py.
    - Autor.
    """

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "INFORMACIÓN DEL PROYECTO"
    )

    console_output.mostrar_etiqueta_valor(
        "Proyecto:",
        config.PROJECT_NAME
    )

    console_output.mostrar_etiqueta_valor(
        "Versión:",
        version.PROJECT_VERSION
    )

    console_output.mostrar_etiqueta_valor(
        "Autor:",
        config.PROJECT_AUTHOR,
        espacio_despues=False
    )

    print(console_output.SEPARADOR_PRINCIPAL)

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

    La contraseña de aplicación nunca debe mostrarse.
    """

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "CONFIGURACIÓN"
    )

    console_output.mostrar_etiqueta_valor(
        "Cuenta de Gmail:",
        config.EMAIL
    )

    console_output.mostrar_etiqueta_valor(
        "Carpeta de destino:",
        config.SAVE_FOLDER
    )

    console_output.mostrar_etiqueta_valor(
        "Límite de correos por ejecución:",
        config.EMAIL_PROCESSING_LIMIT,
        espacio_despues=False
    )

    print(console_output.SEPARADOR_PRINCIPAL)

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
    """

    cantidad_correos = len(
        identificadores_correos
    )

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "RESULTADO DE LA BÚSQUEDA"
    )

    console_output.mostrar_etiqueta_valor(
        "Cantidad total de correos encontrados:",
        cantidad_correos,
        espacio_despues=False
    )

    print(console_output.SEPARADOR_PRINCIPAL)

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

    if not isinstance(limite, int):

        raise TypeError(
            "EMAIL_PROCESSING_LIMIT debe ser un número "
            "entero."
        )

    if limite <= 0:

        raise ValueError(
            "EMAIL_PROCESSING_LIMIT debe ser mayor que cero."
        )

    correos_recientes = identificadores_correos[
        -limite:
    ]

    correos_recientes = list(
        reversed(correos_recientes)
    )

    return correos_recientes

# ==========================================================
# FIN DE LA FUNCIÓN seleccionar_correos_recientes()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_correos_seleccionados()
# ==========================================================

def mostrar_correos_seleccionados(cantidad_seleccionada):
    """
    Mostrar la cantidad de correos que serán procesados.

    Parámetros
    ----------
    cantidad_seleccionada:

        Cantidad de correos elegidos según el límite
        configurado.
    """

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "CORREOS SELECCIONADOS"
    )

    console_output.mostrar_etiqueta_valor(
        "Cantidad de correos que serán procesados:",
        cantidad_seleccionada,
        espacio_despues=False
    )

    print(console_output.SEPARADOR_PRINCIPAL)

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_correos_seleccionados()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_inicio_correo()
# ==========================================================

def mostrar_inicio_correo(
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

        Identificador IMAP del correo actual.
    """

    console_output.linea_en_blanco()
    console_output.linea_en_blanco()

    console_output.mostrar_inicio_procesamiento(
        numero_correo,
        cantidad_correos
    )

    console_output.mostrar_etiqueta_valor(
        "ID del correo:",
        id_correo,
        espacio_despues=False
    )

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_inicio_correo()
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
    """

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "DATOS PRINCIPALES DEL CORREO"
    )

    console_output.mostrar_etiqueta_valor(
        "Asunto:",
        datos_correo["Subject"]
    )

    console_output.mostrar_etiqueta_valor(
        "Remitente:",
        datos_correo["From"]
    )

    console_output.mostrar_etiqueta_valor(
        "Destinatario:",
        datos_correo["To"]
    )

    console_output.mostrar_etiqueta_valor(
        "Fecha:",
        datos_correo["Date"],
        espacio_despues=False
    )

    print(console_output.SEPARADOR_PRINCIPAL)

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
    """

    cantidad_adjuntos = len(
        adjuntos
    )

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "ARCHIVOS ADJUNTOS"
    )

    console_output.mostrar_etiqueta_valor(
        "Cantidad de adjuntos encontrados:",
        cantidad_adjuntos,
        espacio_despues=False
    )

    if not adjuntos:

        console_output.linea_en_blanco()

        console_output.mostrar_mensaje(
            "El correo no contiene archivos adjuntos."
        )

        print(console_output.SEPARADOR_PRINCIPAL)

        return

    for numero_adjunto, adjunto in enumerate(
        adjuntos,
        start=1
    ):

        console_output.linea_en_blanco()

        console_output.mostrar_subtitulo(
            f"Adjunto número {numero_adjunto}"
        )

        console_output.mostrar_etiqueta_valor(
            "Nombre:",
            adjunto["nombre"]
        )

        console_output.mostrar_etiqueta_valor(
            "Tipo de contenido:",
            adjunto["tipo_contenido"],
            espacio_despues=False
        )

    console_output.linea_en_blanco()

    print(console_output.SEPARADOR_PRINCIPAL)

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_adjuntos()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_carpeta_asignada()
# ==========================================================

def mostrar_carpeta_asignada(carpeta_factura):
    """
    Mostrar la carpeta asignada al correo actual.
    """

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "CARPETA ASIGNADA"
    )

    console_output.mostrar_etiqueta_valor(
        "Los archivos PDF de este correo se guardarán en:",
        carpeta_factura,
        espacio_despues=False
    )

    print(console_output.SEPARADOR_PRINCIPAL)

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
    """

    cantidad_archivos = len(
        archivos_guardados
    )

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "ARCHIVOS NUEVOS GUARDADOS"
    )

    console_output.mostrar_etiqueta_valor(
        "Cantidad de archivos nuevos guardados:",
        cantidad_archivos,
        espacio_despues=False
    )

    if not archivos_guardados:

        console_output.linea_en_blanco()

        console_output.mostrar_mensaje(
            "No se guardó ningún archivo nuevo."
        )

        console_output.mostrar_mensaje(
            "El correo puede no contener archivos PDF o "
            "los archivos pueden existir previamente."
        )

        print(console_output.SEPARADOR_PRINCIPAL)

        return

    for numero_archivo, ruta_archivo in enumerate(
        archivos_guardados,
        start=1
    ):

        console_output.linea_en_blanco()

        console_output.mostrar_subtitulo(
            f"Archivo número {numero_archivo}"
        )

        console_output.mostrar_etiqueta_valor(
            "Guardado en:",
            ruta_archivo,
            espacio_despues=False
        )

    console_output.linea_en_blanco()

    print(console_output.SEPARADOR_PRINCIPAL)

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_archivos_guardados()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN procesar_correo()
# ==========================================================

def procesar_correo(conexion, id_correo):
    """
    Leer y procesar un único correo.

    Retorna una lista con las rutas de los archivos PDF
    nuevos que fueron guardados.
    """

    mensaje = gmail_client.leer_correo(
        conexion,
        id_correo
    )

    datos_correo = gmail_client.obtener_datos_correo(
        mensaje
    )

    mostrar_datos_correo(
        datos_correo
    )

    adjuntos = gmail_client.obtener_adjuntos(
        mensaje
    )

    mostrar_adjuntos(
        adjuntos
    )

    carpeta_factura = (
        invoice_organizer.construir_carpeta_factura(
            config.SAVE_FOLDER,
            datos_correo
        )
    )

    mostrar_carpeta_asignada(
        carpeta_factura
    )

    archivos_guardados = file_manager.guardar_adjuntos(
        adjuntos,
        carpeta_factura
    )

    mostrar_archivos_guardados(
        archivos_guardados
    )

    return archivos_guardados

# ==========================================================
# FIN DE LA FUNCIÓN procesar_correo()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_error_correo()
# ==========================================================

def mostrar_error_correo(id_correo, error_correo):
    """
    Mostrar información sobre un error producido al procesar
    un correo específico.
    """

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "ERROR AL PROCESAR EL CORREO"
    )

    console_output.mostrar_etiqueta_valor(
        "ID del correo:",
        id_correo
    )

    console_output.mostrar_etiqueta_valor(
        "Tipo de error:",
        type(error_correo).__name__
    )

    console_output.mostrar_etiqueta_valor(
        "Descripción:",
        error_correo
    )

    console_output.mostrar_mensaje(
        "El programa continuará con el siguiente correo."
    )

    print(console_output.SEPARADOR_PRINCIPAL)

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_error_correo()
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
    """

    console_output.linea_en_blanco()
    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "RESUMEN FINAL"
    )

    console_output.mostrar_etiqueta_valor(
        "Correos seleccionados:",
        cantidad_seleccionada
    )

    console_output.mostrar_etiqueta_valor(
        "Correos procesados correctamente:",
        cantidad_procesada
    )

    console_output.mostrar_etiqueta_valor(
        "Correos con errores:",
        cantidad_errores
    )

    console_output.mostrar_etiqueta_valor(
        "Total de archivos PDF nuevos guardados:",
        len(archivos_guardados),
        espacio_despues=False
    )

    if archivos_guardados:

        console_output.linea_en_blanco()

        console_output.mostrar_mensaje(
            "Archivos guardados durante esta ejecución:"
        )

        for numero_archivo, ruta_archivo in enumerate(
            archivos_guardados,
            start=1
        ):

            console_output.linea_en_blanco()

            console_output.mostrar_mensaje(
                f"{numero_archivo}. {ruta_archivo}"
            )

    console_output.linea_en_blanco()

    print(console_output.SEPARADOR_PRINCIPAL)

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_resumen_final()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN main()
# ==========================================================

def main():
    """
    Coordinar el flujo completo del programa.
    """

    mostrar_informacion_proyecto()

    mostrar_configuracion()

    conexion = None

    try:

        conexion = gmail_client.conectar()

        identificadores_correos = (
            gmail_client.buscar_todos_los_correos(
                conexion
            )
        )

        mostrar_resultado_busqueda(
            identificadores_correos
        )

        if not identificadores_correos:

            console_output.linea_en_blanco()

            console_output.mostrar_mensaje(
                "No se encontraron correos para procesar."
            )

            return

        correos_seleccionados = (
            seleccionar_correos_recientes(
                identificadores_correos,
                config.EMAIL_PROCESSING_LIMIT
            )
        )

        cantidad_seleccionada = len(
            correos_seleccionados
        )

        mostrar_correos_seleccionados(
            cantidad_seleccionada
        )

        cantidad_procesada = 0

        cantidad_errores = 0

        todos_los_archivos_guardados = []

        for numero_correo, id_correo in enumerate(
            correos_seleccionados,
            start=1
        ):

            mostrar_inicio_correo(
                numero_correo,
                cantidad_seleccionada,
                id_correo
            )

            try:

                archivos_guardados = procesar_correo(
                    conexion,
                    id_correo
                )

                todos_los_archivos_guardados.extend(
                    archivos_guardados
                )

                cantidad_procesada += 1

            except Exception as error_correo:

                cantidad_errores += 1

                mostrar_error_correo(
                    id_correo,
                    error_correo
                )

        mostrar_resumen_final(
            cantidad_seleccionada,
            cantidad_procesada,
            cantidad_errores,
            todos_los_archivos_guardados
        )

    except Exception as error:

        console_output.mostrar_error(
            "SE PRODUJO UN ERROR GENERAL",
            error
        )

    finally:

        if conexion is not None:

            try:

                conexion.logout()

                console_output.linea_en_blanco()

                console_output.mostrar_mensaje(
                    "Conexión cerrada correctamente."
                )

            except Exception as error_cierre:

                console_output.linea_en_blanco()

                console_output.mostrar_mensaje(
                    "No fue posible cerrar la conexión "
                    "de forma normal."
                )

                console_output.mostrar_mensaje(
                    error_cierre
                )

# ==========================================================
# FIN DE LA FUNCIÓN main()
# ==========================================================


# ==========================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# ==========================================================

if __name__ == "__main__":

    main()


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================