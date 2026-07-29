"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Versión
--------
0.12

Archivo
--------
console_output.py

Descripción
-----------
Este módulo centraliza la salida visual que el programa
muestra en la consola.

Su objetivo es evitar repetir constantemente estructuras
como:

    print()
    print("==================================================")
    print("TÍTULO")
    print("==================================================")

Al concentrar estas tareas en un único módulo, conseguimos:

- Reducir código repetido.
- Mantener un formato visual consistente.
- Facilitar futuros cambios en la apariencia de la consola.
- Preparar el proyecto para incorporar un sistema de logs
  más completo en versiones posteriores.

Este módulo no contiene lógica relacionada con Gmail,
archivos PDF o carpetas.

Su única responsabilidad es mostrar información en pantalla.

Autor
------
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# INICIO DEL BLOQUE DE CONSTANTES
# ==========================================================

SEPARADOR_PRINCIPAL = "=" * 50

SEPARADOR_SECUNDARIO = "-" * 32

SEPARADOR_PROCESAMIENTO = "#" * 50

# ==========================================================
# FIN DEL BLOQUE DE CONSTANTES
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN linea_en_blanco()
# ==========================================================

def linea_en_blanco():
    """
    Imprimir una línea vacía en la consola.

    Esta función ayuda a mantener el espaciado visual sin
    tener que escribir print() directamente en otros módulos.
    """

    print()

# ==========================================================
# FIN DE LA FUNCIÓN linea_en_blanco()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_titulo()
# ==========================================================

def mostrar_titulo(titulo):
    """
    Mostrar un título rodeado por separadores principales.

    Parámetros
    ----------
    titulo:

        Texto que se mostrará como encabezado.

    Ejemplo
    -------
    mostrar_titulo("CONFIGURACIÓN")

    Resultado:

        ==================================================
        CONFIGURACIÓN
        ==================================================
    """

    print(SEPARADOR_PRINCIPAL)
    print(titulo)
    print(SEPARADOR_PRINCIPAL)

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_titulo()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_subtitulo()
# ==========================================================

def mostrar_subtitulo(titulo):
    """
    Mostrar un subtítulo rodeado por separadores secundarios.

    Parámetros
    ----------
    titulo:

        Texto que se mostrará como subtítulo.

    Ejemplo
    -------
    mostrar_subtitulo("Adjunto número 1")

    Resultado:

        --------------------------------
        Adjunto número 1
        --------------------------------
    """

    print(SEPARADOR_SECUNDARIO)
    print(titulo)
    print(SEPARADOR_SECUNDARIO)

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_subtitulo()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_inicio_procesamiento()
# ==========================================================

def mostrar_inicio_procesamiento(
    numero_actual,
    cantidad_total
):
    """
    Mostrar el comienzo del procesamiento de un elemento.

    Parámetros
    ----------
    numero_actual:

        Posición actual dentro del recorrido.

    cantidad_total:

        Cantidad total de elementos que serán procesados.

    Ejemplo
    -------
    mostrar_inicio_procesamiento(1, 10)

    Resultado:

        ##################################################
        PROCESANDO CORREO 1 DE 10
        ##################################################
    """

    print(SEPARADOR_PROCESAMIENTO)

    print(
        f"PROCESANDO CORREO "
        f"{numero_actual} DE {cantidad_total}"
    )

    print(SEPARADOR_PROCESAMIENTO)

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_inicio_procesamiento()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_etiqueta_valor()
# ==========================================================

def mostrar_etiqueta_valor(
    etiqueta,
    valor,
    espacio_despues=True
):
    """
    Mostrar una etiqueta y su valor en líneas separadas.

    Parámetros
    ----------
    etiqueta:

        Texto descriptivo del dato.

    valor:

        Valor que se mostrará debajo de la etiqueta.

    espacio_despues:

        Indica si debe imprimirse una línea vacía después.

        El valor predeterminado es True.

    Ejemplo
    -------
    mostrar_etiqueta_valor(
        "Proyecto:",
        "Proyecto Facturas"
    )

    Resultado:

        Proyecto:
        Proyecto Facturas
    """

    print(etiqueta)
    print(valor)

    if espacio_despues:

        print()

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_etiqueta_valor()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_mensaje()
# ==========================================================

def mostrar_mensaje(
    mensaje,
    espacio_despues=False
):
    """
    Mostrar un mensaje simple en la consola.

    Parámetros
    ----------
    mensaje:

        Texto que se desea mostrar.

    espacio_despues:

        Indica si debe imprimirse una línea vacía después.

        El valor predeterminado es False.
    """

    print(mensaje)

    if espacio_despues:

        print()

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_mensaje()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_error()
# ==========================================================

def mostrar_error(
    titulo,
    error
):
    """
    Mostrar información básica sobre una excepción.

    Parámetros
    ----------
    titulo:

        Encabezado que identifica el tipo de error.

    error:

        Excepción capturada por el programa.

    Resultado
    ---------
    Muestra:

    - El título del error.
    - El tipo de excepción.
    - La descripción.
    """

    linea_en_blanco()

    mostrar_titulo(
        titulo
    )

    mostrar_etiqueta_valor(
        "Tipo de error:",
        type(error).__name__
    )

    mostrar_etiqueta_valor(
        "Descripción:",
        error,
        espacio_despues=False
    )

    print(SEPARADOR_PRINCIPAL)

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_error()
# ==========================================================


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================