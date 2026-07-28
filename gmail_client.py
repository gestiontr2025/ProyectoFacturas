"""
==========================================================
PROYECTO
==========================================================

ProyectoFacturas

Versión
--------
0.4

Archivo
--------
gmail_client.py

Descripción
-----------
Este módulo contiene todas las funciones relacionadas
con la comunicación con Gmail.

Responsabilidades actuales
--------------------------
✔ Conectarse a Gmail.
✔ Localizar la carpeta "Todos".
✔ Seleccionar la carpeta "Todos".
✔ Buscar todos los correos.
✔ Devolver los identificadores de los correos.
✔ Obtener un correo individual desde Gmail.
✔ Convertir el contenido del correo en un objeto EmailMessage.

Responsabilidades futuras
-------------------------
✔ Mostrar los datos principales de los correos.
✔ Detectar archivos adjuntos.
✔ Descargar archivos adjuntos.

No debe
--------
✘ Leer el contenido interno de los PDFs.
✘ Crear la estructura final de carpetas.
✘ Analizar datos fiscales.
✘ Renombrar definitivamente las facturas.

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
# Biblioteca oficial de Python para trabajar con el protocolo
# IMAP.
#
# IMAP nos permite acceder a los correos almacenados en Gmail.
#
# Gracias a esta biblioteca podremos:
#
# - Conectarnos con Gmail.
# - Seleccionar carpetas.
# - Buscar correos.
# - Leer mensajes.
# - Descargar adjuntos.
# - Cerrar la sesión.
# ----------------------------------------------------------

import imaplib


# ----------------------------------------------------------
# Biblioteca oficial de Python para interpretar correos
# electrónicos.
#
# Gmail entrega el contenido de los mensajes en formato
# bytes, es decir, como una secuencia de datos binarios.
#
# El módulo email permite convertir esos bytes en un objeto
# de correo electrónico que Python puede comprender.
#
# Una vez convertido el mensaje, podremos acceder a datos
# como:
#
# - El asunto.
# - El remitente.
# - El destinatario.
# - La fecha.
# - El cuerpo del mensaje.
# - Los archivos adjuntos.
# ----------------------------------------------------------

import email


# ----------------------------------------------------------
# Importamos policy desde el módulo email.
#
# Una "policy" define cómo debe interpretar Python la
# estructura interna de un correo electrónico.
#
# policy.default utiliza el comportamiento moderno recomendado
# por Python y genera objetos EmailMessage.
#
# Los objetos EmailMessage son más cómodos de utilizar que
# los objetos producidos por el comportamiento antiguo del
# módulo email.
# ----------------------------------------------------------

from email import policy


# ----------------------------------------------------------
# Importamos nuestro propio módulo config.py.
#
# Desde allí obtenemos:
#
# - EMAIL
# - APP_PASSWORD
#
# Las credenciales reales están almacenadas en el archivo
# .env y config.py se encarga de cargarlas.
#
# De esta manera evitamos escribir datos privados directamente
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

    # ------------------------------------------------------
    # INICIO DEL BLOQUE DE MENSAJES DE CONEXIÓN
    # ------------------------------------------------------

    print()

    print("--------------------------------")
    print("Conectando con Gmail...")
    print("--------------------------------")

    # ------------------------------------------------------
    # FIN DEL BLOQUE DE MENSAJES DE CONEXIÓN
    # ------------------------------------------------------


    # ------------------------------------------------------
    # Creamos una conexión segura con Gmail.
    #
    # La variable "mail" representa la conexión abierta.
    #
    # IMAP4_SSL significa que utilizaremos IMAP mediante una
    # conexión cifrada y segura.
    #
    # "imap.gmail.com" es la dirección del servidor IMAP
    # oficial de Gmail.
    # ------------------------------------------------------

    mail = imaplib.IMAP4_SSL("imap.gmail.com")


    # ------------------------------------------------------
    # Iniciamos sesión utilizando las credenciales
    # almacenadas en config.py.
    #
    # config.EMAIL contiene la dirección de correo.
    #
    # config.APP_PASSWORD contiene la contraseña de aplicación
    # creada específicamente para este programa.
    # ------------------------------------------------------

    mail.login(
        config.EMAIL,
        config.APP_PASSWORD
    )


    # ------------------------------------------------------
    # Este mensaje solo se mostrará si login() terminó
    # correctamente.
    #
    # Si Gmail rechazara las credenciales, Python produciría
    # un error antes de llegar a esta línea.
    # ------------------------------------------------------

    print("Conexión realizada correctamente.")


    # ------------------------------------------------------
    # MUY IMPORTANTE
    #
    # En lugar de cerrar la conexión dentro de esta función,
    # la devolvemos al programa principal mediante return.
    #
    # Gracias a esto, main.py y las demás funciones podrán
    # reutilizar exactamente la misma conexión.
    # ------------------------------------------------------

    return mail

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

    Encontrar automáticamente la carpeta especial de Gmail
    que contiene todos los correos de la cuenta.

    En la interfaz de Gmail esta carpeta puede aparecer como:

    - Todos
    - Todos los correos
    - All Mail

    El nombre visible puede cambiar según el idioma de Gmail.

    Sin embargo, Gmail identifica internamente esta carpeta
    mediante la marca especial:

        \\All

    Por esa razón, esta función busca la marca interna y no
    depende del idioma configurado en la cuenta.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    conexion:

        Es el objeto de conexión IMAP devuelto anteriormente
        por la función conectar().

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Devuelve un texto con el nombre exacto de la carpeta.

    Por ejemplo:

        [Gmail]/All Mail

    o alguna variante equivalente en español.

    ----------------------------------------------------------
    POSIBLES ERRORES
    ----------------------------------------------------------

    La función produce un RuntimeError si:

    - Gmail no permite consultar las carpetas.
    - No se encuentra ninguna carpeta marcada como \\All.

    ==========================================================
    """

    # ------------------------------------------------------
    # conexion.list() solicita a Gmail una lista con todas
    # las carpetas o etiquetas disponibles.
    #
    # El resultado se divide en dos variables:
    #
    # estado:
    #     Indica si la operación terminó correctamente.
    #     Normalmente tendrá el valor "OK".
    #
    # carpetas:
    #     Contiene la información de todas las carpetas
    #     encontradas.
    # ------------------------------------------------------

    estado, carpetas = conexion.list()


    # ------------------------------------------------------
    # INICIO DEL BLOQUE IF:
    # comprobación de la respuesta de Gmail
    # ------------------------------------------------------

    if estado != "OK":
        # Todo lo que tiene esta indentación pertenece al if.
        #
        # Solo se ejecutará si Gmail no respondió con "OK".

        raise RuntimeError(
            "Gmail no permitió obtener la lista de carpetas."
        )

    # ------------------------------------------------------
    # FIN DEL BLOQUE IF
    #
    # La siguiente línea ya no pertenece al if porque regresó
    # al mismo nivel de indentación anterior.
    # ------------------------------------------------------


    # ------------------------------------------------------
    # INICIO DEL BLOQUE IF:
    # comprobación de que la lista no esté vacía
    # ------------------------------------------------------

    if not carpetas:
        # "not carpetas" será verdadero si la lista está vacía
        # o si Gmail devolvió None.

        raise RuntimeError(
            "Gmail respondió correctamente, pero no devolvió carpetas."
        )

    # ------------------------------------------------------
    # FIN DEL BLOQUE IF
    # ------------------------------------------------------


    # ------------------------------------------------------
    # INICIO DEL BUCLE FOR
    #
    # Recorremos una por una todas las carpetas devueltas
    # por Gmail.
    #
    # La variable carpeta_bytes cambiará en cada vuelta del
    # bucle y contendrá una carpeta diferente.
    # ------------------------------------------------------

    for carpeta_bytes in carpetas:
        # Todo lo indentado a partir de aquí pertenece al for.


        # --------------------------------------------------
        # Gmail entrega esta información en formato bytes.
        #
        # Los bytes son datos binarios y suelen verse así:
        #
        #     b'(...)'
        #
        # Para poder buscar palabras dentro de esos datos,
        # utilizamos decode() y los convertimos en texto.
        #
        # errors="replace" evita que el programa se detenga si
        # encuentra algún carácter que no puede interpretar.
        # --------------------------------------------------

        carpeta_texto = carpeta_bytes.decode(
            "utf-8",
            errors="replace"
        )


        # --------------------------------------------------
        # INICIO DEL BLOQUE IF:
        # búsqueda de la marca especial \All
        # --------------------------------------------------

        if "\\All" in carpeta_texto:
            # Este bloque solamente se ejecutará si la carpeta
            # actual contiene la marca especial \All.


            # ----------------------------------------------
            # Una respuesta típica de Gmail puede verse así:
            #
            # (\HasNoChildren \All) "/" "[Gmail]/All Mail"
            #
            # El nombre de la carpeta aparece al final,
            # normalmente encerrado entre comillas.
            #
            # rsplit('"', maxsplit=2) divide el texto desde
            # la derecha utilizando las comillas.
            #
            # El resultado esperado será parecido a:
            #
            # [
            #     '(\HasNoChildren \\All) "/" ',
            #     '[Gmail]/All Mail',
            #     ''
            # ]
            # ----------------------------------------------

            partes = carpeta_texto.rsplit(
                '"',
                maxsplit=2
            )


            # ----------------------------------------------
            # INICIO DEL BLOQUE IF:
            # comprobación de formato con comillas
            # ----------------------------------------------

            if len(partes) >= 2:
                # Si la respuesta tiene el formato esperado,
                # el elemento ubicado en la posición 1
                # contendrá el nombre de la carpeta.

                nombre_carpeta = partes[1]


                # ------------------------------------------
                # Devolvemos el nombre encontrado.
                #
                # return finaliza inmediatamente la función.
                # El bucle for también termina porque ya no
                # es necesario seguir buscando.
                # ------------------------------------------

                return nombre_carpeta

            # ----------------------------------------------
            # FIN DEL BLOQUE IF:
            # comprobación de formato con comillas
            # ----------------------------------------------


            # ----------------------------------------------
            # Este bloque funciona como alternativa por si
            # Gmail devolviera el nombre sin comillas.
            #
            # rsplit(" ", maxsplit=1) divide el texto una sola
            # vez desde la derecha y toma la última parte.
            # ----------------------------------------------

            nombre_carpeta = carpeta_texto.rsplit(
                " ",
                maxsplit=1
            )[-1]


            # ----------------------------------------------
            # strip('"') elimina posibles comillas sobrantes
            # al principio o al final del texto.
            # ----------------------------------------------

            nombre_carpeta = nombre_carpeta.strip('"')


            # ----------------------------------------------
            # Devolvemos el nombre encontrado.
            # ----------------------------------------------

            return nombre_carpeta

        # --------------------------------------------------
        # FIN DEL BLOQUE IF:
        # búsqueda de la marca especial \All
        # --------------------------------------------------

    # ------------------------------------------------------
    # FIN DEL BUCLE FOR
    #
    # La siguiente parte ya no está indentada dentro del for.
    # Solo llegaremos aquí si recorrimos todas las carpetas
    # y ninguna contenía la marca \All.
    # ------------------------------------------------------


    # ------------------------------------------------------
    # Si la función llega hasta aquí, significa que no pudo
    # encontrar la carpeta de todos los correos.
    #
    # raise interrumpe la ejecución y muestra un error claro.
    # ------------------------------------------------------

    raise RuntimeError(
        "No se encontró la carpeta de Gmail que contiene "
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

    Seleccionar la carpeta que contiene todos los correos
    y obtener los identificadores de todos sus mensajes.

    Esta función incluye:

    - Correos leídos.
    - Correos no leídos.
    - Correos antiguos.
    - Correos recientes.

    ----------------------------------------------------------
    IMPORTANTE
    ----------------------------------------------------------

    Esta función todavía NO:

    - Descarga correos completos.
    - Descarga archivos adjuntos.
    - Lee PDFs.
    - Renombra facturas.
    - Modifica mensajes.

    Solamente obtiene una lista de identificadores.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    conexion:

        Es la conexión IMAP activa, devuelta por conectar().

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Devuelve una lista de identificadores de mensajes.

    Por ejemplo:

        [b'1', b'2', b'3', b'4']

    Cada identificador representa un correo y nos permitirá
    solicitar su contenido más adelante.

    ==========================================================
    """

    # ------------------------------------------------------
    # Primero llamamos a encontrar_carpeta_todos().
    #
    # El resultado se guarda en la variable carpeta_todos.
    #
    # Esta variable podría contener algo como:
    #
    #     [Gmail]/All Mail
    # ------------------------------------------------------

    carpeta_todos = encontrar_carpeta_todos(
        conexion
    )


    # ------------------------------------------------------
    # Mostramos el nombre exacto encontrado.
    #
    # Esto es especialmente útil durante el aprendizaje y
    # las primeras pruebas, porque nos permite confirmar qué
    # carpeta está utilizando realmente el programa.
    # ------------------------------------------------------

    print()
    print("--------------------------------")
    print("Carpeta de todos los correos encontrada:")
    print(carpeta_todos)
    print("--------------------------------")


    # ------------------------------------------------------
    # conexion.select() selecciona la carpeta sobre la cual
    # realizaremos las búsquedas.
    #
    # readonly=True significa "solo lectura".
    #
    # Esta opción es muy importante durante las pruebas:
    #
    # - No marca mensajes como leídos.
    # - No mueve mensajes.
    # - No elimina mensajes.
    # - Reduce el riesgo de modificar la cuenta.
    # ------------------------------------------------------

    estado, cantidad_informada = conexion.select(
        carpeta_todos,
        readonly=True
    )


    # ------------------------------------------------------
    # INICIO DEL BLOQUE IF:
    # comprobación de selección de carpeta
    # ------------------------------------------------------

    if estado != "OK":
        # Este bloque solo se ejecuta si Gmail no permitió
        # seleccionar la carpeta.

        raise RuntimeError(
            f"No fue posible seleccionar la carpeta: "
            f"{carpeta_todos}"
        )

    # ------------------------------------------------------
    # FIN DEL BLOQUE IF
    # ------------------------------------------------------


    # ------------------------------------------------------
    # conexion.search() realiza una búsqueda dentro de la
    # carpeta seleccionada.
    #
    # None:
    #     Indica que no estamos especificando una codificación
    #     especial para el criterio de búsqueda.
    #
    # "ALL":
    #     Significa que queremos obtener todos los mensajes.
    #
    # No importa si están leídos o no leídos.
    # ------------------------------------------------------

    estado, resultado = conexion.search(
        None,
        "ALL"
    )


    # ------------------------------------------------------
    # INICIO DEL BLOQUE IF:
    # comprobación de la búsqueda
    # ------------------------------------------------------

    if estado != "OK":
        # Este bloque solo se ejecutará si Gmail no pudo
        # realizar correctamente la búsqueda.

        raise RuntimeError(
            "Gmail no pudo realizar la búsqueda de correos."
        )

    # ------------------------------------------------------
    # FIN DEL BLOQUE IF
    # ------------------------------------------------------


    # ------------------------------------------------------
    # INICIO DEL BLOQUE IF:
    # comprobación de resultado vacío o inválido
    # ------------------------------------------------------

    if not resultado or not resultado[0]:
        # Si Gmail no encontró ningún mensaje, devolvemos una
        # lista vacía.
        #
        # Devolver [] es mejor que producir un error, porque
        # encontrar cero correos es un resultado válido.

        return []

    # ------------------------------------------------------
    # FIN DEL BLOQUE IF
    # ------------------------------------------------------


    # ------------------------------------------------------
    # Gmail suele devolver los identificadores agrupados
    # dentro del primer elemento de la lista.
    #
    # Por ejemplo:
    #
    #     [b'1 2 3 4 5']
    #
    # resultado[0] obtiene:
    #
    #     b'1 2 3 4 5'
    #
    # split() separa la secuencia por sus espacios:
    #
    #     [b'1', b'2', b'3', b'4', b'5']
    # ------------------------------------------------------

    identificadores = resultado[0].split()


    # ------------------------------------------------------
    # Devolvemos la lista de identificadores.
    #
    # La función main.py podrá usar len() para contar cuántos
    # correos fueron encontrados.
    # ------------------------------------------------------

    return identificadores

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

    Obtener un único correo completo desde Gmail utilizando
    su identificador IMAP.

    Gmail entrega el contenido del correo en formato bytes.

    La función convierte esos bytes en un objeto EmailMessage
    que posteriormente podrá ser utilizado por otras funciones
    para consultar:

    - El asunto.
    - El remitente.
    - El destinatario.
    - La fecha.
    - El cuerpo del mensaje.
    - Los archivos adjuntos.

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    conexion:

        Es la conexión IMAP activa devuelta por conectar().

        La carpeta correspondiente debe haber sido seleccionada
        previamente mediante buscar_todos_los_correos().

    id_correo:

        Es el identificador IMAP del mensaje que queremos
        obtener.

        Estos identificadores son devueltos por la función
        buscar_todos_los_correos().

        Por ejemplo:

            b'1'
            b'25'
            b'1315'

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Devuelve un objeto EmailMessage que representa el correo
    electrónico completo.

    Por ejemplo, más adelante podremos consultar:

        mensaje["Subject"]
        mensaje["From"]
        mensaje["To"]
        mensaje["Date"]

    ----------------------------------------------------------
    POSIBLES ERRORES
    ----------------------------------------------------------

    La función produce un RuntimeError si:

    - Gmail no puede obtener el correo solicitado.
    - Gmail devuelve una respuesta vacía.
    - La respuesta no tiene la estructura esperada.
    - El contenido del mensaje no se encuentra en bytes.

    ----------------------------------------------------------
    IMPORTANTE
    ----------------------------------------------------------

    Esta función solamente obtiene e interpreta el correo.

    NO:

    - Muestra los datos del correo en pantalla.
    - Guarda el correo en el disco.
    - Descarga archivos adjuntos.
    - Guarda archivos PDF.
    - Analiza facturas.
    - Renombra archivos.

    ==========================================================
    """

    # ------------------------------------------------------
    # conexion.fetch() solicita a Gmail el contenido de un
    # correo específico.
    #
    # Recibe dos argumentos:
    #
    # id_correo:
    #     Es el identificador del mensaje que queremos leer.
    #
    # "(RFC822)":
    #     Le indica a Gmail que queremos recibir el mensaje
    #     electrónico completo.
    #
    # RFC822 es un formato estándar utilizado para representar
    # mensajes de correo electrónico.
    #
    # El resultado se divide en dos variables:
    #
    # estado:
    #     Indica si la operación se realizó correctamente.
    #     Normalmente tendrá el valor "OK".
    #
    # datos_correo:
    #     Contiene la respuesta enviada por Gmail, incluyendo
    #     el contenido completo del mensaje.
    # ------------------------------------------------------

    estado, datos_correo = conexion.fetch(
        id_correo,
        "(RFC822)"
    )


    # ------------------------------------------------------
    # INICIO DEL BLOQUE IF:
    # comprobación de la respuesta de Gmail
    # ------------------------------------------------------

    if estado != "OK":
        # Este bloque solamente se ejecutará si Gmail no pudo
        # obtener correctamente el correo solicitado.

        raise RuntimeError(
            f"Gmail no pudo obtener el correo con ID "
            f"{id_correo!r}."
        )

    # ------------------------------------------------------
    # FIN DEL BLOQUE IF:
    # comprobación de la respuesta de Gmail
    # ------------------------------------------------------


    # ------------------------------------------------------
    # INICIO DEL BLOQUE IF:
    # comprobación de respuesta vacía
    # ------------------------------------------------------

    if not datos_correo:
        # "not datos_correo" será verdadero si Gmail devuelve:
        #
        # - Una lista vacía.
        # - El valor None.
        # - Cualquier otro valor considerado vacío.
        #
        # Aunque el estado haya sido "OK", necesitamos confirmar
        # que Gmail realmente haya enviado información.

        raise RuntimeError(
            f"Gmail respondió sin datos para el correo con ID "
            f"{id_correo!r}."
        )

    # ------------------------------------------------------
    # FIN DEL BLOQUE IF:
    # comprobación de respuesta vacía
    # ------------------------------------------------------


    # ------------------------------------------------------
    # Gmail normalmente devuelve una estructura parecida a:
    #
    # [
    #     (
    #         b'1 (RFC822 {cantidad_de_bytes})',
    #         b'contenido completo del correo'
    #     ),
    #     b')'
    # ]
    #
    # datos_correo[0] obtiene el primer elemento de la lista.
    #
    # Ese primer elemento debería ser una tupla.
    #
    # Una tupla es una colección ordenada, parecida a una
    # lista, pero que normalmente se utiliza para agrupar
    # valores relacionados.
    # ------------------------------------------------------

    primer_elemento = datos_correo[0]


    # ------------------------------------------------------
    # INICIO DEL BLOQUE IF:
    # comprobación del tipo de dato recibido
    # ------------------------------------------------------

    if not isinstance(primer_elemento, tuple):
        # isinstance() comprueba si un valor pertenece a un
        # tipo determinado.
        #
        # En este caso preguntamos:
        #
        #     ¿primer_elemento es una tupla?
        #
        # Si no es una tupla, la respuesta de Gmail no tiene
        # la estructura que esperábamos.

        raise RuntimeError(
            f"El correo con ID {id_correo!r} no tiene "
            f"la estructura esperada."
        )

    # ------------------------------------------------------
    # FIN DEL BLOQUE IF:
    # comprobación del tipo de dato recibido
    # ------------------------------------------------------


    # ------------------------------------------------------
    # INICIO DEL BLOQUE IF:
    # comprobación de la cantidad de elementos de la tupla
    # ------------------------------------------------------

    if len(primer_elemento) < 2:
        # La tupla debería contener al menos dos posiciones:
        #
        # Posición 0:
        #     Información técnica enviada por Gmail.
        #
        # Posición 1:
        #     Contenido completo del correo en bytes.
        #
        # Si tiene menos de dos elementos, no podremos acceder
        # al contenido del mensaje.

        raise RuntimeError(
            f"La respuesta del correo con ID {id_correo!r} "
            f"está incompleta."
        )

    # ------------------------------------------------------
    # FIN DEL BLOQUE IF:
    # comprobación de la cantidad de elementos de la tupla
    # ------------------------------------------------------


    # ------------------------------------------------------
    # Obtenemos el elemento ubicado en la posición 1.
    #
    # En Python, las posiciones comienzan desde cero:
    #
    # primer_elemento[0]
    #     Contiene la información técnica.
    #
    # primer_elemento[1]
    #     Contiene el correo completo en formato bytes.
    # ------------------------------------------------------

    correo_bytes = primer_elemento[1]


    # ------------------------------------------------------
    # INICIO DEL BLOQUE IF:
    # comprobación de que el correo esté en formato bytes
    # ------------------------------------------------------

    if not isinstance(correo_bytes, bytes):
        # Para que email.message_from_bytes() pueda interpretar
        # correctamente el mensaje, necesitamos que su contenido
        # sea un objeto de tipo bytes.

        raise RuntimeError(
            f"El contenido del correo con ID {id_correo!r} "
            f"no se encuentra en formato bytes."
        )

    # ------------------------------------------------------
    # FIN DEL BLOQUE IF:
    # comprobación de que el correo esté en formato bytes
    # ------------------------------------------------------


    # ------------------------------------------------------
    # email.message_from_bytes() interpreta el contenido
    # binario del correo.
    #
    # Recibe:
    #
    # correo_bytes:
    #     El contenido completo enviado por Gmail.
    #
    # policy=policy.default:
    #     Indica que queremos utilizar el comportamiento moderno
    #     recomendado por Python.
    #
    # El resultado será un objeto EmailMessage.
    #
    # Este objeto ya separa y organiza correctamente:
    #
    # - Los encabezados.
    # - El cuerpo.
    # - Las diferentes partes MIME.
    # - Los archivos adjuntos.
    # ------------------------------------------------------

    mensaje = email.message_from_bytes(
        correo_bytes,
        policy=policy.default
    )


    # ------------------------------------------------------
    # Devolvemos el objeto EmailMessage.
    #
    # Esta función no muestra nada en pantalla.
    #
    # La función que llame a leer_correo() decidirá qué hacer
    # con el mensaje recibido.
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

    Extraer los encabezados principales de un correo
    electrónico.

    Esta función recibe un objeto EmailMessage y obtiene la
    información más importante de sus encabezados.

    Actualmente extrae:

    - Subject (Asunto)
    - From (Remitente)
    - To (Destinatario)
    - Date (Fecha)

    ----------------------------------------------------------
    PARÁMETROS
    ----------------------------------------------------------

    mensaje:

        Es un objeto EmailMessage devuelto previamente por la
        función leer_correo().

    ----------------------------------------------------------
    RETORNA
    ----------------------------------------------------------

    Devuelve un diccionario con los encabezados principales
    del correo.

    Por ejemplo:

    {
        "Subject": "...",
        "From": "...",
        "To": "...",
        "Date": "..."
    }

    ----------------------------------------------------------
    IMPORTANTE
    ----------------------------------------------------------

    Esta función NO imprime información en pantalla.

    Su única responsabilidad consiste en leer los encabezados
    del mensaje y devolverlos organizados dentro de un
    diccionario.

    Si algún encabezado no existe, se devuelve un texto
    descriptivo en su lugar.

    ==========================================================
    """

    # ------------------------------------------------------
    # Los encabezados de un EmailMessage funcionan de manera
    # parecida a un diccionario.
    #
    # Por ejemplo:
    #
    # mensaje["Subject"]
    #
    # obtiene el asunto del correo.
    #
    # Sin embargo, algunos correos pueden no contener alguno
    # de estos encabezados.
    #
    # Para evitar obtener el valor None, utilizamos get(),
    # que nos permite indicar un valor por defecto.
    # ------------------------------------------------------

    # ------------------------------------------------------
    # Obtenemos el asunto.
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
    # Obtenemos la fecha del mensaje.
    # ------------------------------------------------------

    fecha = mensaje.get(
        "Date",
        "Fecha no informada"
    )


    # ------------------------------------------------------
    # Creamos un diccionario para agrupar todos los datos.
    #
    # Un diccionario es una colección formada por pares:
    #
    #     clave : valor
    #
    # En este caso utilizamos como claves los nombres reales
    # de los encabezados del correo electrónico.
    # ------------------------------------------------------

    datos_correo = {

        "Subject": asunto,

        "From": remitente,

        "To": destinatario,

        "Date": fecha

    }


    # ------------------------------------------------------
    # Devolvemos el diccionario completo.
    #
    # La función que llame a obtener_datos_correo() decidirá
    # posteriormente cómo mostrar esta información al usuario.
    # ------------------------------------------------------

    return datos_correo


# ==========================================================
# FIN DE LA FUNCIÓN obtener_datos_correo()
# ==========================================================


# ==========================================================
# FIN DEL BLOQUE DE FUNCIONES
# ==========================================================