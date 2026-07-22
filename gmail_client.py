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

Responsabilidades futuras
-------------------------
✔ Leer correos individuales.
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
# FIN DEL BLOQUE DE FUNCIONES
# ==========================================================