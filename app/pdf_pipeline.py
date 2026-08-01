"""Etapas que trabajan con el contenido de los archivos PDF.

Primero se extrae el texto y luego se intenta identificar al proveedor. Estas
funciones no saben nada sobre Gmail: reciben resultados de archivos y devuelven
nuevos resultados para la siguiente etapa del proceso.
"""

import pdf_reader
import supplier_detector

LIMITE_VISTA_PREVIA_PDF = 500

def crear_vista_previa_texto(
    texto,
    limite=LIMITE_VISTA_PREVIA_PDF
):
    """
    Crear una versión abreviada del texto de un PDF.

    El texto completo continúa disponible en el resultado de
    pdf_reader.leer_pdf(). Esta función solamente limita el
    contenido mostrado en la consola.
    """

    if not texto:

        return ""

    texto = str(
        texto
    ).strip()

    if len(texto) <= limite:

        return texto

    vista_previa = texto[
        :limite
    ].rstrip()

    vista_previa += "\n[...]"

    return vista_previa

def leer_archivos_pdf(resultados_archivos):
    """
    Leer todos los archivos PDF detectados en un correo.

    Si un PDF individual produce un error, el error se guarda
    dentro de su resultado y el programa continúa con los
    demás documentos.
    """

    resultados_lectura = []

    for resultado_archivo in resultados_archivos:

        ruta_pdf = resultado_archivo["ruta"]

        try:

            resultado_lectura = pdf_reader.leer_pdf(
                ruta_pdf
            )

            informacion = {
                "nombre": resultado_archivo["nombre"],
                "ruta": ruta_pdf,
                "lectura_correcta": True,
                "contiene_texto": (
                    resultado_lectura["contiene_texto"]
                ),
                "resultado_lectura": resultado_lectura,
                "error": None
            }

        except Exception as error:

            informacion = {
                "nombre": resultado_archivo["nombre"],
                "ruta": ruta_pdf,
                "lectura_correcta": False,
                "contiene_texto": False,
                "resultado_lectura": None,
                "error": error
            }

        resultados_lectura.append(
            informacion
        )

    return resultados_lectura

def detectar_proveedores_pdf(resultados_lectura):
    """
    Intentar detectar el proveedor de cada PDF leído.

    Parámetros
    ----------
    resultados_lectura:
        Lista devuelta por leer_archivos_pdf().

    Retorna
    -------
    list
        Lista con un resultado de detección por cada PDF.

    Casos posibles
    --------------
    1. El PDF fue leído, contiene texto y la detección pudo
       realizarse.

    2. El PDF fue leído, pero no contiene texto extraíble.

    3. El PDF no pudo leerse.

    4. Se produjo un error específico durante la detección.

    Un error en un documento no detiene el procesamiento de
    los demás PDF.
    """

    resultados_proveedores = []

    for resultado_lectura in resultados_lectura:

        nombre = resultado_lectura["nombre"]
        ruta = resultado_lectura["ruta"]

        # --------------------------------------------------
        # Si el PDF no pudo leerse, tampoco podemos analizar
        # su texto para detectar un proveedor.
        # --------------------------------------------------

        if not resultado_lectura["lectura_correcta"]:

            informacion = {
                "nombre": nombre,
                "ruta": ruta,
                "deteccion_realizada": False,
                "motivo_no_realizada": (
                    "El PDF no pudo ser leído."
                ),
                "resultado_proveedor": None,
                "error": None
            }

            resultados_proveedores.append(
                informacion
            )

            continue

        # --------------------------------------------------
        # Si el documento fue leído pero no tiene texto,
        # supplier_detector no dispone de contenido sobre el
        # cual realizar la búsqueda.
        # --------------------------------------------------

        if not resultado_lectura["contiene_texto"]:

            informacion = {
                "nombre": nombre,
                "ruta": ruta,
                "deteccion_realizada": False,
                "motivo_no_realizada": (
                    "El PDF no contiene texto extraíble."
                ),
                "resultado_proveedor": None,
                "error": None
            }

            resultados_proveedores.append(
                informacion
            )

            continue

        try:

            datos_lectura = resultado_lectura[
                "resultado_lectura"
            ]

            texto_completo = datos_lectura[
                "texto_completo"
            ]

            # El contenido del PDF es la evidencia principal. El nombre del
            # adjunto se agrega como evidencia secundaria porque algunos PDF
            # extraen importes y datos fiscales, pero omiten el encabezado con
            # la razón social. Esto ocurre, por ejemplo, cuando el encabezado
            # está dibujado como imagen o con una fuente no extraíble.
            texto_para_deteccion = (
                f"{texto_completo}\n\n"
                f"NOMBRE ORIGINAL DEL ARCHIVO: {nombre}"
            )
            resultado_proveedor = supplier_detector.detectar_proveedor(
                texto_para_deteccion
            )

            informacion = {
                "nombre": nombre,
                "ruta": ruta,
                "deteccion_realizada": True,
                "motivo_no_realizada": None,
                "resultado_proveedor": resultado_proveedor,
                "error": None
            }

        except Exception as error:

            informacion = {
                "nombre": nombre,
                "ruta": ruta,
                "deteccion_realizada": False,
                "motivo_no_realizada": (
                    "Se produjo un error durante la "
                    "detección del proveedor."
                ),
                "resultado_proveedor": None,
                "error": error
            }

        resultados_proveedores.append(
            informacion
        )

    return resultados_proveedores



def organizar_facturas_pdf(
    resultados_archivos,
    resultados_lectura,
    resultados_proveedores,
    carpeta_raiz,
):
    """Organizar cada PDF utilizando los resultados de las etapas anteriores.

    Las tres listas conservan el mismo orden: el elemento cero de cada una
    representa el mismo archivo. Centralizar aquí esa unión evita que
    ``email_processor`` necesite conocer detalles del parser o del organizador.
    """
    from invoices.processor import procesar_factura

    resultados_organizacion = []

    for archivo, lectura, proveedor in zip(
        resultados_archivos,
        resultados_lectura,
        resultados_proveedores,
    ):
        if not lectura["lectura_correcta"] or not lectura["contiene_texto"]:
            resultados_organizacion.append(
                {
                    "organizada": False,
                    "ruta_original": archivo["ruta"],
                    "ruta_final": archivo["ruta"],
                    "datos_factura": None,
                    "motivo_pendiente": "El PDF no contiene texto utilizable.",
                }
            )
            continue

        texto = lectura["resultado_lectura"]["texto_completo"]
        resultado = procesar_factura(
            archivo["ruta"],
            texto,
            proveedor.get("resultado_proveedor"),
            carpeta_raiz,
        )
        resultado_dict = {
            "organizada": resultado.organizada,
            "ruta_original": resultado.ruta_original,
            "ruta_final": resultado.ruta_final,
            "datos_factura": resultado.datos_factura,
            "motivo_pendiente": resultado.motivo_pendiente,
            "tipo_documento": resultado.tipo_documento,
        }
        resultados_organizacion.append(resultado_dict)

        # Las pantallas y el resumen final ya consumen la clave ``ruta``.
        # La actualizamos para que informen la ubicación definitiva después
        # del movimiento y no una ruta temporal que ya dejó de existir.
        if resultado.organizada:
            archivo["ruta"] = resultado.ruta_final
            archivo["nombre"] = resultado.ruta_final.name
            lectura["ruta"] = resultado.ruta_final
            lectura["nombre"] = resultado.ruta_final.name
            proveedor["ruta"] = resultado.ruta_final
            proveedor["nombre"] = resultado.ruta_final.name

    return resultados_organizacion
