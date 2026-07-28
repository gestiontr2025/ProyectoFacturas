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
gmail_client.py

Descripción
-----------
Este módulo contiene las funciones relacionadas con Gmail
y con la interpretación básica de los correos electrónicos.

Actualmente permite:

- Conectarse con Gmail mediante IMAP.
- Encontrar la carpeta que contiene todos los correos.
- Buscar los identificadores de todos los mensajes.
- Obtener un correo individual.
- Convertir los bytes del correo en un EmailMessage.
- Extraer los encabezados principales del mensaje.
- Detectar los archivos adjuntos del correo.

En esta versión todavía NO se descargan archivos adjuntos.

La función obtener_adjuntos() solamente:

- Recorre las partes internas del correo.
- Detecta cuáles parecen ser archivos adjuntos.
- Obtiene el nombre del archivo.
- Obtiene su tipo de contenido.
- Conserva la parte MIME para utilizarla más adelante.

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
# Importamos imaplib.
#
# Esta biblioteca forma parte de Python y permite trabajar
# con servidores de correo mediante el protocolo IMAP.
#
# IMAP nos permite:
#
# - Conectarnos con Gmail.
# - Iniciar sesión.
# - Seleccionar carpetas.
# - Buscar mensajes.
# - Obtener correos completos.
# ----------------------------------------------------------

import imaplib


# ----------------------------------------------------------
# Importamos el módulo email.
#
# Cuando Gmail nos entrega un mensaje mediante IMAP,
# normalmente lo recibimos como una secuencia de bytes.
#
# El módulo email nos permite transformar esos bytes en
# un objeto de Python que podemos consultar y recorrer.
# ----------------------------------------------------------

import email


# ----------------------------------------------------------
# Importamos policy desde email.
#
# La política policy.default indica cómo debe interpretarse
# el mensaje.
#
# Gracias a esta política, email.message_from_bytes()
# devuelve normalmente un objeto EmailMessage moderno.
# ----------------------------------------------------------

from email import policy


# ----------------------------------------------------------
# Importamos nuestro archivo config.py.
#
# Desde este módulo obtenemos:
#
# - La dirección de correo.
# - La contraseña de aplicación.
#
# De esta manera evitamos escribir esos valores directamente
# dentro de gmail_client.py.
# ----------------------------------------------------------

import config


# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE FUNCIONES
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN conectar()
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

    Abrir una conexión segura con el servidor IMAP de Gmail
    e iniciar sesión utilizando las credenciales guardadas
    en config.py.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    Esta función no recibe parámetros.

    Utiliza directamente:

        config.EMAIL
        config.APP_PASSWORD

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Devuelve el objeto de conexión IMAP autenticado.

    Ese objeto será utilizado posteriormente para:

    - Consultar las carpetas.
    - Seleccionar una carpeta.
    - Buscar mensajes.
    - Leer correos.
    - Cerrar la sesión.

    ----------------------------------------------------------
    POSIBLES ERRORES
    ----------------------------------------------------------

    La conexión podría fallar por diferentes motivos:

    - No hay conexión a Internet.
    - El correo configurado es incorrecto.
    - La contraseña de aplicación es incorrecta.
    - Gmail rechaza temporalmente la conexión.
    - El servidor IMAP no está disponible.

    ==========================================================
    """

    # ------------------------------------------------------
    # Mostramos un mensaje para indicar que comenzó el
    # proceso de conexión.
    # ------------------------------------------------------

    print()
    print("--------------------------------")
    print("Conectando con Gmail...")
    print("--------------------------------")


    # ------------------------------------------------------
    # Creamos una conexión segura con el servidor IMAP
    # de Gmail.
    #
    # IMAP4_SSL significa:
    #
    # - IMAP4: utilizamos la versión 4 del protocolo IMAP.
    # - SSL: la comunicación se realiza de forma cifrada.
    #
    # El servidor IMAP oficial de Gmail es:
    #
    #     imap.gmail.com
    # ------------------------------------------------------

    conexion = imaplib.IMAP4_SSL(
        "imap.gmail.com"
    )


    # ------------------------------------------------------
    # Iniciamos sesión en Gmail.
    #
    # Entregamos:
    #
    # 1. La dirección de correo.
    # 2. La contraseña de aplicación.
    #
    # No utilizamos la contraseña normal de Gmail.
    # Utilizamos una contraseña de aplicación creada
    # específicamente para este proyecto.
    # ------------------------------------------------------

    conexion.login(
        config.EMAIL,
        config.APP_PASSWORD
    )


    # ------------------------------------------------------
    # Si el programa llegó hasta este punto sin producir
    # una excepción, significa que el inicio de sesión fue
    # aceptado.
    # ------------------------------------------------------

    print("Conexión realizada correctamente.")


    # ------------------------------------------------------
    # Devolvemos el objeto de conexión.
    #
    # Gracias a return, main.py puede guardar este objeto
    # dentro de una variable y utilizarlo en otras funciones.
    # ------------------------------------------------------

    return conexion

# ==========================================================
# FIN DE LA FUNCIÓN conectar()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN encontrar_carpeta_todos()
# ==========================================================

def encontrar_carpeta_todos(conexion):
    """
    ==========================================================
    FUNCIÓN
    ==========================================================

    encontrar_carpeta_todos(conexion)

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Buscar dentro de la cuenta de Gmail la carpeta que
    representa todos los correos.

    En Gmail en español, normalmente se llama:

        [Gmail]/Todos

    Sin embargo, el nombre puede variar según el idioma
    configurado en la cuenta.

    Por ese motivo, la función consulta las carpetas
    disponibles e intenta localizar la carpeta correcta.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    conexion:

        Es el objeto de conexión IMAP devuelto previamente
        por la función conectar().

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Devuelve el nombre de la carpeta de todos los correos.

    Por ejemplo:

        [Gmail]/Todos

    ----------------------------------------------------------
    POSIBLES ERRORES
    ----------------------------------------------------------

    La función genera un RuntimeError si:

    - Gmail no permite obtener la lista de carpetas.
    - La respuesta está vacía.
    - No puede localizar la carpeta de todos los correos.

    ==========================================================
    """

    # ------------------------------------------------------
    # Solicitamos al servidor IMAP la lista de carpetas
    # disponibles.
    #
    # list() devuelve dos valores:
    #
    # estado:
    #     Indica si la operación fue exitosa.
    #
    # carpetas:
    #     Contiene las carpetas devueltas por Gmail.
    # ------------------------------------------------------

    estado, carpetas = conexion.list()


    # ------------------------------------------------------
    # Comprobamos que Gmail haya respondido correctamente.
    #
    # El valor esperado es:
    #
    #     "OK"
    # ------------------------------------------------------

    if estado != "OK":
        raise RuntimeError(
            "Gmail no permitió obtener la lista de carpetas."
        )


    # ------------------------------------------------------
    # Verificamos que la respuesta contenga carpetas.
    # ------------------------------------------------------

    if not carpetas:
        raise RuntimeError(
            "Gmail devolvió una lista de carpetas vacía."
        )


    # ------------------------------------------------------
    # Recorremos cada una de las carpetas.
    #
    # Cada carpeta suele llegar como bytes.
    #
    # Por ejemplo:
    #
    #     b'(\\HasNoChildren) "/" "[Gmail]/Todos"'
    #
    # Para poder buscar palabras dentro de ese valor,
    # primero lo convertimos en texto utilizando decode().
    # ------------------------------------------------------

    for carpeta_bytes in carpetas:

        # --------------------------------------------------
        # Ignoramos cualquier elemento que no sea bytes.
        # --------------------------------------------------

        if not isinstance(carpeta_bytes, bytes):
            continue


        # --------------------------------------------------
        # Convertimos los bytes en texto.
        #
        # errors="replace" evita que una codificación extraña
        # detenga completamente el programa.
        # --------------------------------------------------

        carpeta_texto = carpeta_bytes.decode(
            "utf-8",
            errors="replace"
        )


        # --------------------------------------------------
        # Convertimos temporalmente el texto a minúsculas.
        #
        # Esto permite comparar:
        #
        #     Todos
        #     TODOS
        #     todos
        #
        # como si fueran la misma palabra.
        # --------------------------------------------------

        carpeta_minusculas = carpeta_texto.lower()


        # --------------------------------------------------
        # Buscamos nombres habituales de la carpeta que
        # contiene todos los correos.
        #
        # En español:
        #
        #     todos
        #
        # En inglés:
        #
        #     all mail
        # --------------------------------------------------

        es_carpeta_todos = (
            "todos" in carpeta_minusculas
            or "all mail" in carpeta_minusculas
        )


        # --------------------------------------------------
        # Si esta carpeta no parece ser la carpeta "Todos",
        # continuamos con el siguiente elemento.
        # --------------------------------------------------

        if not es_carpeta_todos:
            continue


        # --------------------------------------------------
        # El nombre de la carpeta suele aparecer después
        # del último separador:
        #
        #     " "
        #
        # Utilizamos rsplit() para dividir solamente desde
        # la derecha.
        #
        # El número 1 indica que queremos realizar una única
        # división.
        # --------------------------------------------------

        partes = carpeta_texto.rsplit(
            " ",
            1
        )


        # --------------------------------------------------
        # Comprobamos que la división haya producido dos
        # elementos.
        # --------------------------------------------------

        if len(partes) != 2:
            continue


        # --------------------------------------------------
        # Tomamos el último elemento, que debería contener
        # el nombre de la carpeta.
        #
        # strip('"') elimina las comillas dobles externas.
        # --------------------------------------------------

        nombre_carpeta = partes[-1].strip('"')


        # --------------------------------------------------
        # Mostramos la carpeta encontrada.
        # --------------------------------------------------

        print()
        print("--------------------------------")
        print("Carpeta de todos los correos encontrada:")
        print(nombre_carpeta)
        print("--------------------------------")


        # --------------------------------------------------
        # Devolvemos inmediatamente el nombre.
        #
        # Una vez encontrada la carpeta correcta, no hace
        # falta continuar recorriendo la lista.
        # --------------------------------------------------

        return nombre_carpeta


    # ------------------------------------------------------
    # Si el recorrido terminó sin ejecutar return,
    # significa que no encontramos una carpeta compatible.
    # ------------------------------------------------------

    raise RuntimeError(
        "No fue posible encontrar la carpeta que contiene "
        "todos los correos."
    )

# ==========================================================
# FIN DE LA FUNCIÓN encontrar_carpeta_todos()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN buscar_todos_los_correos()
# ==========================================================

def buscar_todos_los_correos(conexion):
    """
    ==========================================================
    FUNCIÓN
    ==========================================================

    buscar_todos_los_correos(conexion)

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Seleccionar la carpeta que contiene todos los correos y
    buscar los identificadores de todos los mensajes.

    La búsqueda incluye:

    - Correos leídos.
    - Correos no leídos.
    - Correos archivados.
    - Correos que no aparecen en la bandeja principal.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    conexion:

        Es el objeto de conexión IMAP autenticado.

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Devuelve una lista de identificadores IMAP.

    Por ejemplo:

        [b'1', b'2', b'3', b'4']

    Cada identificador representa un correo dentro de la
    carpeta seleccionada.

    ----------------------------------------------------------
    IMPORTANTE
    ----------------------------------------------------------

    Estos identificadores pertenecen a la sesión y a la
    carpeta IMAP seleccionada.

    No deben confundirse con el encabezado Message-ID
    de un correo electrónico.

    ==========================================================
    """

    # ------------------------------------------------------
    # Primero localizamos la carpeta de todos los correos.
    # ------------------------------------------------------

    carpeta_todos = encontrar_carpeta_todos(
        conexion
    )


    # ------------------------------------------------------
    # Seleccionamos la carpeta encontrada.
    #
    # readonly=True significa que abrimos la carpeta en modo
    # de solo lectura.
    #
    # Esto reduce el riesgo de modificar accidentalmente:
    #
    # - El estado de lectura.
    # - Las etiquetas.
    # - La ubicación de los correos.
    # ------------------------------------------------------

    estado_seleccion, _ = conexion.select(
        carpeta_todos,
        readonly=True
    )


    # ------------------------------------------------------
    # Comprobamos que Gmail haya permitido seleccionar
    # la carpeta.
    # ------------------------------------------------------

    if estado_seleccion != "OK":
        raise RuntimeError(
            "No fue posible seleccionar la carpeta "
            "de todos los correos."
        )


    # ------------------------------------------------------
    # Realizamos la búsqueda.
    #
    # El criterio ALL significa:
    #
    #     Buscar todos los mensajes de la carpeta.
    # ------------------------------------------------------

    estado_busqueda, respuesta_busqueda = conexion.search(
        None,
        "ALL"
    )


    # ------------------------------------------------------
    # Verificamos que la búsqueda haya sido exitosa.
    # ------------------------------------------------------

    if estado_busqueda != "OK":
        raise RuntimeError(
            "Gmail no pudo completar la búsqueda de correos."
        )


    # ------------------------------------------------------
    # Comprobamos que exista una respuesta.
    # ------------------------------------------------------

    if not respuesta_busqueda:
        raise RuntimeError(
            "Gmail devolvió una respuesta vacía durante "
            "la búsqueda de correos."
        )


    # ------------------------------------------------------
    # Normalmente Gmail devuelve los identificadores dentro
    # del primer elemento.
    #
    # Por ejemplo:
    #
    #     [b'1 2 3 4 5']
    #
    # Tomamos ese primer elemento.
    # ------------------------------------------------------

    identificadores_bytes = respuesta_busqueda[0]


    # ------------------------------------------------------
    # Verificamos que el elemento sea bytes.
    # ------------------------------------------------------

    if not isinstance(identificadores_bytes, bytes):
        raise RuntimeError(
            "La respuesta de Gmail no contiene los "
            "identificadores en el formato esperado."
        )


    # ------------------------------------------------------
    # split() separa los identificadores utilizando los
    # espacios.
    #
    # Convierte:
    #
    #     b'1 2 3 4'
    #
    # en:
    #
    #     [b'1', b'2', b'3', b'4']
    # ------------------------------------------------------

    identificadores_correos = identificadores_bytes.split()


    # ------------------------------------------------------
    # Devolvemos la lista completa.
    # ------------------------------------------------------

    return identificadores_correos

# ==========================================================
# FIN DE LA FUNCIÓN buscar_todos_los_correos()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN leer_correo()
# ==========================================================

def leer_correo(conexion, id_correo):
    """
    ==========================================================
    FUNCIÓN
    ==========================================================

    leer_correo(conexion, id_correo)

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Obtener un correo completo desde Gmail y convertirlo
    desde bytes en un objeto EmailMessage.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    conexion:

        Es el objeto de conexión IMAP autenticado.

    id_correo:

        Es el identificador IMAP del correo que queremos leer.

        Por ejemplo:

            b'1324'

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Devuelve un objeto:

        email.message.EmailMessage

    Este objeto permite consultar:

    - Los encabezados.
    - El cuerpo.
    - Las partes MIME.
    - Los archivos adjuntos.

    ----------------------------------------------------------
    IMPORTANTE
    ----------------------------------------------------------

    Esta función obtiene el mensaje en memoria.

    No guarda el correo en el disco.

    Tampoco guarda los archivos adjuntos.

    ==========================================================
    """

    # ------------------------------------------------------
    # Solicitamos el contenido completo del mensaje.
    #
    # RFC822 indica que queremos obtener el correo completo,
    # incluyendo:
    #
    # - Encabezados.
    # - Cuerpo.
    # - Partes MIME.
    # - Archivos adjuntos.
    # ------------------------------------------------------

    estado, respuesta = conexion.fetch(
        id_correo,
        "(RFC822)"
    )


    # ------------------------------------------------------
    # Verificamos que Gmail haya completado correctamente
    # la operación.
    # ------------------------------------------------------

    if estado != "OK":
        raise RuntimeError(
            f"No fue posible obtener el correo con ID "
            f"{id_correo!r}."
        )


    # ------------------------------------------------------
    # Comprobamos que exista una respuesta.
    # ------------------------------------------------------

    if not respuesta:
        raise RuntimeError(
            "Gmail devolvió una respuesta vacía al intentar "
            "leer el correo."
        )


    # ------------------------------------------------------
    # El primer elemento suele ser una tupla.
    #
    # Una estructura simplificada sería:
    #
    #     (
    #         información_del_mensaje,
    #         bytes_del_correo
    #     )
    # ------------------------------------------------------

    primer_elemento = respuesta[0]


    # ------------------------------------------------------
    # Verificamos que realmente sea una tupla.
    # ------------------------------------------------------

    if not isinstance(primer_elemento, tuple):
        raise RuntimeError(
            "La respuesta recibida no tiene la estructura "
            "esperada."
        )


    # ------------------------------------------------------
    # Comprobamos que la tupla tenga al menos dos elementos.
    # ------------------------------------------------------

    if len(primer_elemento) < 2:
        raise RuntimeError(
            "La respuesta del correo está incompleta."
        )


    # ------------------------------------------------------
    # El segundo elemento contiene los bytes del correo.
    # ------------------------------------------------------

    correo_bytes = primer_elemento[1]


    # ------------------------------------------------------
    # Verificamos que el contenido realmente sea bytes.
    # ------------------------------------------------------

    if not isinstance(correo_bytes, bytes):
        raise RuntimeError(
            "El contenido del correo no fue recibido "
            "en formato bytes."
        )


    # ------------------------------------------------------
    # Convertimos los bytes en un objeto EmailMessage.
    #
    # message_from_bytes() interpreta la estructura completa
    # del correo.
    #
    # policy.default permite utilizar la interfaz moderna
    # del módulo email.
    # ------------------------------------------------------

    mensaje = email.message_from_bytes(
        correo_bytes,
        policy=policy.default
    )


    # ------------------------------------------------------
    # Devolvemos el mensaje ya interpretado.
    # ------------------------------------------------------

    return mensaje

# ==========================================================
# FIN DE LA FUNCIÓN leer_correo()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN obtener_datos_correo()
# ==========================================================

def obtener_datos_correo(mensaje):
    """
    ==========================================================
    FUNCIÓN
    ==========================================================

    obtener_datos_correo(mensaje)

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Extraer los encabezados principales de un correo.

    Actualmente obtiene:

    - Subject.
    - From.
    - To.
    - Date.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    mensaje:

        Es un objeto EmailMessage devuelto por leer_correo().

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Devuelve un diccionario con esta estructura:

        {
            "Subject": "...",
            "From": "...",
            "To": "...",
            "Date": "..."
        }

    ----------------------------------------------------------
    IMPORTANTE
    ----------------------------------------------------------

    Esta función no imprime los datos.

    Tampoco descarga archivos.

    Su única responsabilidad consiste en extraer y organizar
    los encabezados principales.

    ==========================================================
    """

    # ------------------------------------------------------
    # Obtenemos el asunto.
    #
    # El segundo argumento de get() es el valor que se
    # utilizará si el encabezado no existe.
    # ------------------------------------------------------

    asunto = mensaje.get(
        "Subject",
        "Sin asunto"
    )


    # ------------------------------------------------------
    # Obtenemos el remitente.
    # ------------------------------------------------------

    remitente = mensaje.get(
        "From",
        "Remitente no informado"
    )


    # ------------------------------------------------------
    # Obtenemos el destinatario.
    # ------------------------------------------------------

    destinatario = mensaje.get(
        "To",
        "Destinatario no informado"
    )


    # ------------------------------------------------------
    # Obtenemos la fecha.
    # ------------------------------------------------------

    fecha = mensaje.get(
        "Date",
        "Fecha no informada"
    )


    # ------------------------------------------------------
    # Creamos un diccionario para agrupar los datos.
    # ------------------------------------------------------

    datos_correo = {
        "Subject": asunto,
        "From": remitente,
        "To": destinatario,
        "Date": fecha
    }


    # ------------------------------------------------------
    # Devolvemos el diccionario.
    # ------------------------------------------------------

    return datos_correo

# ==========================================================
# FIN DE LA FUNCIÓN obtener_datos_correo()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN obtener_adjuntos()
# ==========================================================

def obtener_adjuntos(mensaje):
    """
    ==========================================================
    FUNCIÓN
    ==========================================================

    obtener_adjuntos(mensaje)

    ----------------------------------------------------------
    OBJETIVO
    ----------------------------------------------------------

    Recorrer las partes internas de un correo electrónico
    y detectar cuáles representan archivos adjuntos.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    mensaje:

        Es un objeto EmailMessage devuelto previamente por:

            leer_correo()

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Devuelve una lista de diccionarios.

    Cada diccionario representa un archivo adjunto detectado.

    Por ejemplo:

        [
            {
                "nombre": "factura.pdf",
                "tipo_contenido": "application/pdf",
                "parte": parte
            }
        ]

    Si el correo no contiene adjuntos, devuelve una lista
    vacía:

        []

    ----------------------------------------------------------
    INFORMACIÓN GUARDADA
    ----------------------------------------------------------

    nombre:

        Es el nombre original del archivo adjunto.

        Por ejemplo:

            factura.pdf

    tipo_contenido:

        Es el tipo MIME informado por el correo.

        Por ejemplo:

            application/pdf

            image/jpeg

            application/vnd.ms-excel

    parte:

        Es el objeto MIME que representa el adjunto.

        Por ahora solamente lo guardamos.

        En una futura versión, este objeto nos permitirá
        obtener el contenido real del archivo mediante:

            parte.get_payload(decode=True)

    ----------------------------------------------------------
    IMPORTANTE
    ----------------------------------------------------------

    Esta función NO descarga archivos.

    Esta función NO crea carpetas.

    Esta función NO escribe información en el disco.

    Solamente detecta y organiza información sobre los
    archivos adjuntos.

    ==========================================================
    """

    # ------------------------------------------------------
    # Creamos una lista vacía.
    #
    # En esta lista iremos agregando los adjuntos encontrados.
    #
    # Si no encontramos ninguno, la lista seguirá vacía y
    # será devuelta como:
    #
    #     []
    # ------------------------------------------------------

    adjuntos = []


    # ------------------------------------------------------
    # mensaje.walk() recorre todas las partes internas del
    # correo electrónico.
    #
    # Un correo puede contener múltiples elementos:
    #
    # - Texto plano.
    # - Contenido HTML.
    # - Imágenes insertadas.
    # - Firmas.
    # - Archivos PDF.
    # - Hojas de cálculo.
    # - Otros adjuntos.
    #
    # Cada elemento es representado por una "parte MIME".
    #
    # walk() nos entrega cada una de esas partes, una por una.
    # ------------------------------------------------------

    for parte in mensaje.walk():

        # --------------------------------------------------
        # multipart significa que esta parte funciona como
        # un contenedor de otras partes.
        #
        # Por ejemplo, un correo podría tener una estructura
        # parecida a esta:
        #
        # correo
        # ├── texto
        # ├── HTML
        # └── adjunto PDF
        #
        # El contenedor principal no es un archivo adjunto.
        #
        # Por eso, si la parte es multipart, continuamos
        # directamente con la siguiente.
        # --------------------------------------------------

        if parte.is_multipart():
            continue


        # --------------------------------------------------
        # Obtenemos el nombre del archivo.
        #
        # get_filename() intenta leer el nombre informado
        # en los encabezados MIME de esta parte.
        #
        # Algunos ejemplos:
        #
        #     factura.pdf
        #     comprobante.jpg
        #     detalle.xlsx
        #
        # Si la parte no tiene nombre de archivo,
        # get_filename() devuelve None.
        # --------------------------------------------------

        nombre_archivo = parte.get_filename()


        # --------------------------------------------------
        # Obtenemos la disposición del contenido.
        #
        # La disposición nos ayuda a saber cómo pretendía
        # presentarse esa parte del correo.
        #
        # Los valores más habituales son:
        #
        # attachment:
        #     Archivo enviado como adjunto.
        #
        # inline:
        #     Contenido pensado para mostrarse dentro del
        #     cuerpo del correo, como una imagen de una firma.
        #
        # None:
        #     El correo no informó una disposición.
        # --------------------------------------------------

        disposicion = parte.get_content_disposition()


        # --------------------------------------------------
        # Determinamos si esta parte debe considerarse
        # un archivo adjunto.
        #
        # Utilizamos dos señales:
        #
        # 1. Que Content-Disposition sea "attachment".
        #
        # 2. Que exista un nombre de archivo.
        #
        # Esta combinación es más flexible que comprobar
        # únicamente la palabra "attachment", porque algunos
        # sistemas de facturación generan correos que no están
        # perfectamente construidos, pero igualmente incluyen
        # un nombre de archivo válido.
        # --------------------------------------------------

        es_adjunto = (
            disposicion == "attachment"
            or nombre_archivo is not None
        )


        # --------------------------------------------------
        # Si esta parte no parece ser un adjunto, utilizamos
        # continue.
        #
        # continue significa:
        #
        #     "Dejá de procesar esta parte y pasá a la
        #      siguiente vuelta del for".
        # --------------------------------------------------

        if not es_adjunto:
            continue


        # --------------------------------------------------
        # Algunos correos podrían indicar attachment pero no
        # proporcionar un nombre.
        #
        # En ese caso utilizamos un nombre descriptivo para
        # que el dato nunca quede como None.
        #
        # Más adelante podremos mejorar este comportamiento
        # generando nombres automáticos.
        # --------------------------------------------------

        if nombre_archivo is None:
            nombre_archivo = "archivo_sin_nombre"


        # --------------------------------------------------
        # Obtenemos el tipo MIME de la parte.
        #
        # get_content_type() devuelve valores como:
        #
        #     application/pdf
        #     image/jpeg
        #     image/png
        #     text/plain
        #
        # El tipo de contenido será especialmente importante
        # cuando filtremos solamente archivos PDF.
        # --------------------------------------------------

        tipo_contenido = parte.get_content_type()


        # --------------------------------------------------
        # Creamos un diccionario con la información del
        # adjunto actual.
        #
        # También guardamos el objeto parte.
        #
        # Todavía no descargamos su contenido, pero conservar
        # esta referencia nos permitirá hacerlo más adelante
        # sin volver a recorrer todo el mensaje.
        # --------------------------------------------------

        datos_adjunto = {
            "nombre": nombre_archivo,
            "tipo_contenido": tipo_contenido,
            "parte": parte
        }


        # --------------------------------------------------
        # Agregamos el diccionario a la lista.
        #
        # append() incorpora un nuevo elemento al final de
        # una lista.
        #
        # Si adjuntos era:
        #
        #     []
        #
        # después de append() será:
        #
        #     [
        #         {
        #             "nombre": "...",
        #             "tipo_contenido": "...",
        #             "parte": ...
        #         }
        #     ]
        # --------------------------------------------------

        adjuntos.append(
            datos_adjunto
        )


    # ------------------------------------------------------
    # Cuando el for termina, devolvemos la lista completa.
    #
    # Puede contener:
    #
    # - Ningún elemento.
    # - Un adjunto.
    # - Varios adjuntos.
    # ------------------------------------------------------

    return adjuntos

# ==========================================================
# FIN DE LA FUNCIÓN obtener_adjuntos()
# ==========================================================


# ==========================================================
# FIN DEL BLOQUE DE FUNCIONES
# ==========================================================