"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Versión
--------
0.6

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
11. Cierra correctamente la conexión con Gmail.

En esta versión todavía NO se descargan archivos.

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
# Desde config.py obtenemos información general del proyecto
# y datos de configuración, como:
#
# - El nombre del proyecto.
# - La versión actual.
# - El autor.
# - La dirección de correo.
# - El nombre de la carpeta de destino.
#
# De esta manera evitamos repetir esos valores dentro de
# diferentes archivos.
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
    proyecto.

    Actualmente muestra:

    - Nombre del proyecto.
    - Versión.
    - Autor.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    Esta función no recibe parámetros.

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Esta función no devuelve ningún valor.

    Solamente imprime información en pantalla.

    ==========================================================
    """

    # ------------------------------------------------------
    # Mostramos un separador visual.
    # ------------------------------------------------------

    print()
    print("==================================================")
    print("INFORMACIÓN DEL PROYECTO")
    print("==================================================")


    # ------------------------------------------------------
    # Obtenemos los valores directamente desde config.py.
    #
    # Esto permite modificar el nombre, la versión o el autor
    # en un único archivo.
    # ------------------------------------------------------

    print("Proyecto:")
    print(config.PROJECT_NAME)

    print()

    print("Versión:")
    print(config.PROJECT_VERSION)

    print()

    print("Autor:")
    print(config.PROJECT_AUTHOR)


    # ------------------------------------------------------
    # Cerramos la sección con otro separador.
    # ------------------------------------------------------

    print("==================================================")

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_informacion_proyecto()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_configuracion()
# ==========================================================

def mostrar_configuracion():
    """
    ==========================================================
    FUNCIÓN
    ==========================================================

    mostrar_configuracion()

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Mostrar algunos valores de configuración utilizados por
    el programa.

    Actualmente muestra:

    - La cuenta de Gmail configurada.
    - La carpeta donde se guardarán las facturas más adelante.

    ----------------------------------------------------------
    SEGURIDAD
    ----------------------------------------------------------

    Esta función NO debe mostrar la contraseña de aplicación.

    La contraseña es información privada y nunca debe
    imprimirse en la terminal.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    Esta función no recibe parámetros.

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Esta función no devuelve ningún valor.

    ==========================================================
    """

    print()
    print("==================================================")
    print("CONFIGURACIÓN")
    print("==================================================")


    # ------------------------------------------------------
    # Mostramos la dirección de correo configurada.
    # ------------------------------------------------------

    print("Cuenta de Gmail:")
    print(config.EMAIL)

    print()


    # ------------------------------------------------------
    # Mostramos el nombre de la carpeta que utilizaremos
    # más adelante para guardar las facturas.
    #
    # En esta versión todavía no guardamos archivos.
    # ------------------------------------------------------

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
    ==========================================================
    FUNCIÓN
    ==========================================================

    mostrar_resultado_busqueda(identificadores_correos)

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Mostrar cuántos correos fueron encontrados por Gmail.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    identificadores_correos:

        Es la lista devuelta por:

            gmail_client.buscar_todos_los_correos()

        Por ejemplo:

            [b'1', b'2', b'3']

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Esta función no devuelve ningún valor.

    Solamente muestra información en pantalla.

    ==========================================================
    """

    print()
    print("==================================================")
    print("RESULTADO DE LA BÚSQUEDA")
    print("==================================================")


    # ------------------------------------------------------
    # len() devuelve la cantidad de elementos presentes
    # dentro de una lista.
    #
    # Por ejemplo:
    #
    #     len([b'1', b'2', b'3'])
    #
    # devuelve:
    #
    #     3
    # ------------------------------------------------------

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
    ==========================================================
    FUNCIÓN
    ==========================================================

    mostrar_resultado_lectura(id_correo, mensaje)

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Mostrar información técnica básica sobre el correo que
    fue leído.

    Actualmente muestra:

    - El identificador IMAP del correo.
    - El tipo de objeto creado por Python.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    id_correo:

        Identificador IMAP del mensaje.

        Por ejemplo:

            b'1324'

    mensaje:

        Objeto EmailMessage devuelto por:

            gmail_client.leer_correo()

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Esta función no devuelve ningún valor.

    ==========================================================
    """

    print()
    print("==================================================")
    print("RESULTADO DE LA LECTURA")
    print("==================================================")


    # ------------------------------------------------------
    # Mostramos el identificador del correo elegido.
    # ------------------------------------------------------

    print("ID del correo:")
    print(id_correo)

    print()


    # ------------------------------------------------------
    # type() permite conocer el tipo de objeto almacenado
    # dentro de una variable.
    #
    # El resultado esperado es parecido a:
    #
    #     <class 'email.message.EmailMessage'>
    #
    # Esto confirma que los bytes fueron interpretados
    # correctamente.
    # ------------------------------------------------------

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
    ==========================================================
    FUNCIÓN
    ==========================================================

    mostrar_datos_correo(datos_correo)

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Mostrar en pantalla los encabezados principales de un
    correo electrónico.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    datos_correo:

        Es el diccionario devuelto por:

            gmail_client.obtener_datos_correo()

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

    Su responsabilidad consiste únicamente en mostrar los
    datos recibidos.

    ==========================================================
    """

    print()
    print("==================================================")
    print("DATOS PRINCIPALES DEL CORREO")
    print("==================================================")


    # ------------------------------------------------------
    # Accedemos a cada valor utilizando su clave.
    #
    # Por ejemplo:
    #
    #     datos_correo["Subject"]
    #
    # busca dentro del diccionario el valor asociado a la
    # clave "Subject".
    # ------------------------------------------------------

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
    ==========================================================
    FUNCIÓN
    ==========================================================

    mostrar_adjuntos(adjuntos)

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Mostrar información sobre los archivos adjuntos
    detectados dentro de un correo.

    Actualmente muestra:

    - La cantidad total de adjuntos.
    - El número de cada adjunto.
    - El nombre del archivo.
    - El tipo de contenido MIME.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    adjuntos:

        Es la lista devuelta por:

            gmail_client.obtener_adjuntos()

        Cada elemento de la lista es un diccionario.

        Por ejemplo:

            {
                "nombre": "factura.pdf",
                "tipo_contenido": "application/pdf",
                "parte": parte
            }

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Esta función no devuelve ningún valor.

    ----------------------------------------------------------
    IMPORTANTE
    ----------------------------------------------------------

    Esta función no muestra el valor guardado en la clave:

        "parte"

    Esa clave contiene el objeto MIME completo del adjunto.

    Su representación técnica podría ser extensa y difícil
    de leer.

    La utilizaremos más adelante para obtener el contenido
    real del archivo.

    ==========================================================
    """

    print()
    print("==================================================")
    print("ARCHIVOS ADJUNTOS")
    print("==================================================")


    # ------------------------------------------------------
    # Obtenemos la cantidad total de adjuntos utilizando
    # len().
    # ------------------------------------------------------

    cantidad_adjuntos = len(
        adjuntos
    )


    print("Cantidad de adjuntos encontrados:")
    print(cantidad_adjuntos)


    # ------------------------------------------------------
    # Una lista vacía se considera False dentro de una
    # condición.
    #
    # Por eso:
    #
    #     if not adjuntos:
    #
    # significa:
    #
    #     "Si la lista no contiene ningún elemento".
    # ------------------------------------------------------

    if not adjuntos:

        print()
        print("El correo no contiene archivos adjuntos.")

        print("==================================================")


        # --------------------------------------------------
        # return finaliza inmediatamente la función.
        #
        # Como no existen adjuntos, no hace falta ejecutar
        # el recorrido que aparece más abajo.
        # --------------------------------------------------

        return


    # ------------------------------------------------------
    # enumerate() permite recorrer una lista y obtener al
    # mismo tiempo:
    #
    # - La posición del elemento.
    # - El propio elemento.
    #
    # Sin enumerate(), podríamos recorrer solamente:
    #
    #     for adjunto in adjuntos:
    #
    # Con enumerate(), obtenemos:
    #
    #     numero_adjunto
    #     adjunto
    #
    # start=1 indica que la numeración debe comenzar en 1.
    #
    # Sin start=1, Python comenzaría desde 0.
    # ------------------------------------------------------

    for numero_adjunto, adjunto in enumerate(
        adjuntos,
        start=1
    ):

        print()
        print("--------------------------------")
        print(f"Adjunto número {numero_adjunto}")
        print("--------------------------------")


        # --------------------------------------------------
        # Obtenemos el nombre desde el diccionario.
        # --------------------------------------------------

        nombre_archivo = adjunto["nombre"]


        # --------------------------------------------------
        # Obtenemos el tipo MIME desde el diccionario.
        # --------------------------------------------------

        tipo_contenido = adjunto["tipo_contenido"]


        # --------------------------------------------------
        # Mostramos solamente la información útil para una
        # persona.
        #
        # No mostramos:
        #
        #     adjunto["parte"]
        #
        # porque contiene el objeto MIME interno.
        # --------------------------------------------------

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

    Coordinar el flujo completo del programa.

    Esta función no contiene directamente toda la lógica de
    Gmail.

    En cambio, llama a funciones especializadas de otros
    módulos.

    ----------------------------------------------------------
    FLUJO ACTUAL
    ----------------------------------------------------------

    1. Mostrar información del proyecto.
    2. Mostrar configuración.
    3. Conectarse con Gmail.
    4. Buscar todos los correos.
    5. Verificar que haya correos.
    6. Elegir el correo más reciente.
    7. Leerlo.
    8. Obtener sus encabezados.
    9. Mostrar sus encabezados.
    10. Detectar adjuntos.
    11. Mostrar información de los adjuntos.
    12. Cerrar la conexión.

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Esta función no devuelve ningún valor.

    ==========================================================
    """

    # ------------------------------------------------------
    # Mostramos la información inicial.
    # ------------------------------------------------------

    mostrar_informacion_proyecto()

    mostrar_configuracion()


    # ------------------------------------------------------
    # Creamos inicialmente la variable conexion con el valor
    # None.
    #
    # Esto es importante porque la conexión podría fallar
    # antes de llegar a crearse.
    #
    # Más adelante, dentro de finally, comprobaremos si la
    # variable contiene realmente una conexión.
    # ------------------------------------------------------

    conexion = None


    # ------------------------------------------------------
    # Utilizamos try para ejecutar el bloque principal.
    #
    # Si aparece un error, el bloque except podrá capturarlo.
    #
    # El bloque finally se ejecutará tanto si el programa
    # funciona correctamente como si aparece un error.
    # ------------------------------------------------------

    try:

        # --------------------------------------------------
        # Abrimos la conexión con Gmail.
        # --------------------------------------------------

        conexion = gmail_client.conectar()


        # --------------------------------------------------
        # Buscamos todos los correos.
        #
        # La función devuelve una lista de identificadores.
        # --------------------------------------------------

        identificadores_correos = (
            gmail_client.buscar_todos_los_correos(
                conexion
            )
        )


        # --------------------------------------------------
        # Mostramos cuántos correos fueron encontrados.
        # --------------------------------------------------

        mostrar_resultado_busqueda(
            identificadores_correos
        )


        # --------------------------------------------------
        # Antes de intentar acceder a un correo, comprobamos
        # que la lista no esté vacía.
        #
        # Intentar acceder al último elemento de una lista
        # vacía produciría un error.
        # --------------------------------------------------

        if not identificadores_correos:
            print()
            print(
                "No se encontraron correos para procesar."
            )

            return


        # --------------------------------------------------
        # Elegimos el último identificador de la lista.
        #
        # En Python:
        #
        #     lista[-1]
        #
        # representa el último elemento.
        #
        # En este caso, normalmente será el correo más
        # reciente dentro de la carpeta seleccionada.
        # --------------------------------------------------

        id_correo_prueba = identificadores_correos[-1]


        # --------------------------------------------------
        # Leemos el correo completo.
        #
        # El resultado será un objeto EmailMessage.
        # --------------------------------------------------

        mensaje = gmail_client.leer_correo(
            conexion,
            id_correo_prueba
        )


        # --------------------------------------------------
        # Mostramos información técnica sobre la lectura.
        # --------------------------------------------------

        mostrar_resultado_lectura(
            id_correo_prueba,
            mensaje
        )


        # --------------------------------------------------
        # Extraemos los encabezados principales.
        #
        # El resultado será un diccionario.
        # --------------------------------------------------

        datos_correo = gmail_client.obtener_datos_correo(
            mensaje
        )


        # --------------------------------------------------
        # Mostramos los encabezados obtenidos.
        # --------------------------------------------------

        mostrar_datos_correo(
            datos_correo
        )


        # --------------------------------------------------
        # Detectamos los archivos adjuntos del mensaje.
        #
        # obtener_adjuntos() recorre las partes MIME y
        # devuelve una lista.
        #
        # En esta etapa no descarga archivos.
        # --------------------------------------------------

        adjuntos = gmail_client.obtener_adjuntos(
            mensaje
        )


        # --------------------------------------------------
        # Mostramos la cantidad, el nombre y el tipo MIME
        # de los adjuntos encontrados.
        # --------------------------------------------------

        mostrar_adjuntos(
            adjuntos
        )


    # ------------------------------------------------------
    # except captura errores producidos durante la ejecución.
    #
    # Exception es una categoría general que incluye muchos
    # tipos de errores.
    #
    # Guardamos el error dentro de la variable:
    #
    #     error
    #
    # para poder mostrarlo.
    # ------------------------------------------------------

    except Exception as error:

        print()
        print("==================================================")
        print("SE PRODUJO UN ERROR")
        print("==================================================")

        print(type(error).__name__)
        print(error)

        print("==================================================")


    # ------------------------------------------------------
    # finally se ejecuta siempre.
    #
    # Esto permite intentar cerrar la conexión incluso si
    # apareció un error durante la búsqueda o la lectura.
    # ------------------------------------------------------

    finally:

        # --------------------------------------------------
        # Verificamos si la conexión fue creada.
        #
        # Si conectar() falló antes de devolver un objeto,
        # conexion todavía tendrá el valor None.
        # --------------------------------------------------

        if conexion is not None:

            try:

                # ------------------------------------------
                # logout() cierra correctamente la sesión
                # IMAP con Gmail.
                # ------------------------------------------

                conexion.logout()

                print()
                print(
                    "Conexión cerrada correctamente."
                )


            # ----------------------------------------------
            # También podría aparecer un error al intentar
            # cerrar una conexión que ya fue interrumpida.
            #
            # En ese caso mostramos una advertencia, pero no
            # detenemos el programa nuevamente.
            # ----------------------------------------------

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
# Python asigna el valor "__main__" a la variable especial
# __name__ cuando ejecutamos directamente este archivo:
#
#     python main.py
#
# La condición evita que main() se ejecute automáticamente
# si este archivo es importado desde otro módulo.
# ----------------------------------------------------------

if __name__ == "__main__":
    main()


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================