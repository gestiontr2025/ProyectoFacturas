"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Archivo
-------
pdf_reader.py

Descripción
-----------
Este módulo contiene las funciones relacionadas con la
lectura del contenido interno de archivos PDF.

Su responsabilidad principal es:

- Recibir la ruta de un archivo PDF.
- Validar que la ruta sea correcta.
- Abrir el documento.
- Determinar cuántas páginas contiene.
- Extraer el texto de cada página.
- Unir el texto de todas las páginas.
- Detectar documentos que no contienen texto extraíble.
- Devolver los resultados sin imprimirlos directamente.

Separar estas tareas en un módulo independiente permite
mantener una responsabilidad clara dentro del proyecto.

Distribución actual de responsabilidades
----------------------------------------
gmail_client.py:

    Se conecta con Gmail y obtiene los correos y adjuntos.

file_manager.py:

    Valida, filtra y guarda los archivos PDF.

invoice_organizer.py:

    Construye las carpetas donde se guardan las facturas.

pdf_reader.py:

    Abre los PDF ya guardados y extrae su contenido textual.

console_output.py:

    Centraliza la información mostrada en la consola.

main.py:

    Coordina el funcionamiento general del programa.

Limitaciones
------------
Esta primera versión solamente puede extraer texto que se
encuentre almacenado como caracteres dentro del PDF.

Algunos documentos son imágenes escaneadas guardadas dentro
de un archivo PDF.

Esos documentos pueden verse correctamente al abrirlos, pero
no necesariamente contienen texto extraíble.

Para interpretar archivos escaneados será necesario agregar
OCR en una versión futura.

Este módulo no debe
-------------------
- Conectarse con Gmail.
- Descargar archivos.
- Crear carpetas de facturas.
- Detectar proveedores.
- Exportar información a Excel.
- Imprimir directamente los resultados en la consola.
- Modificar el contenido de los documentos.

Autor
-----
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# INICIO DEL BLOQUE DE IMPORTACIONES
# ==========================================================

# ----------------------------------------------------------
# Importamos Path desde pathlib.
#
# Path permite trabajar con rutas de archivos de una manera
# moderna, clara y compatible con distintos sistemas
# operativos.
# ----------------------------------------------------------

from pathlib import Path


# ----------------------------------------------------------
# Importamos PdfReader desde la biblioteca pypdf.
#
# PdfReader se encarga de abrir e interpretar la estructura
# interna de los documentos PDF.
#
# La biblioteca puede instalarse con:
#
#     python -m pip install pypdf
# ----------------------------------------------------------

from pypdf import PdfReader


# ----------------------------------------------------------
# Importamos PdfReadError.
#
# Esta excepción puede producirse cuando pypdf intenta abrir
# un archivo cuya estructura PDF es inválida, incompleta o
# está dañada.
#
# Importarla nos permite transformar ese error técnico en un
# mensaje más comprensible para el programa.
# ----------------------------------------------------------

from pypdf.errors import PdfReadError

try:
    import pymupdf  # API moderna de PyMuPDF.
except ImportError:  # La dependencia se valida solo cuando realmente hace falta.
    pymupdf = None

# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN validar_ruta_pdf()
# ==========================================================

def validar_ruta_pdf(ruta_pdf):
    """
    Validar que una ruta corresponda a un archivo PDF válido.

    Parámetros
    ----------
    ruta_pdf:

        Ruta del archivo que deseamos leer.

        Puede recibirse como:

        - Una cadena de texto.
        - Un objeto Path.

    Retorna
    -------
    Path

        Ruta convertida en un objeto Path después de superar
        todas las validaciones.

    Excepciones
    -----------
    ValueError:

        Se produce si la ruta está vacía o si la extensión
        del archivo no es .pdf.

    FileNotFoundError:

        Se produce si el archivo no existe.

    IsADirectoryError:

        Se produce si la ruta corresponde a una carpeta en
        lugar de un archivo.
    """

    # ------------------------------------------------------
    # Comprobamos primero que se haya recibido algún valor.
    #
    # Esto evita convertir accidentalmente una cadena vacía
    # en una ruta que apunte a la carpeta actual.
    # ------------------------------------------------------

    if ruta_pdf is None:

        raise ValueError(
            "No se recibió una ruta para leer el archivo PDF."
        )

    # ------------------------------------------------------
    # Convertimos el valor a texto para detectar cadenas
    # vacías o compuestas solamente por espacios.
    # ------------------------------------------------------

    ruta_como_texto = str(
        ruta_pdf
    ).strip()

    if not ruta_como_texto:

        raise ValueError(
            "La ruta del archivo PDF no puede estar vacía."
        )

    # ------------------------------------------------------
    # Convertimos la ruta recibida en un objeto Path.
    # ------------------------------------------------------

    ruta_pdf = Path(
        ruta_como_texto
    )

    # ------------------------------------------------------
    # Verificamos que la ruta exista.
    # ------------------------------------------------------

    if not ruta_pdf.exists():

        raise FileNotFoundError(
            "No se encontró el archivo PDF indicado: "
            f"{ruta_pdf}"
        )

    # ------------------------------------------------------
    # Una ruta existente puede representar un archivo o una
    # carpeta.
    #
    # is_file() debe devolver True para continuar.
    # ------------------------------------------------------

    if not ruta_pdf.is_file():

        raise IsADirectoryError(
            "La ruta indicada no corresponde a un archivo: "
            f"{ruta_pdf}"
        )

    # ------------------------------------------------------
    # Comprobamos la extensión sin distinguir entre
    # mayúsculas y minúsculas.
    #
    # Por lo tanto, se aceptan tanto:
    #
    #     factura.pdf
    #
    # como:
    #
    #     FACTURA.PDF
    # ------------------------------------------------------

    if ruta_pdf.suffix.lower() != ".pdf":

        raise ValueError(
            "El archivo indicado no posee extensión PDF: "
            f"{ruta_pdf.name}"
        )

    return ruta_pdf

# ==========================================================
# FIN DE LA FUNCIÓN validar_ruta_pdf()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN abrir_pdf()
# ==========================================================

def abrir_pdf(ruta_pdf):
    """
    Abrir un archivo PDF después de validar su ruta.

    Parámetros
    ----------
    ruta_pdf:

        Ruta del documento que deseamos abrir.

    Retorna
    -------
    PdfReader

        Objeto utilizado por pypdf para acceder al contenido
        y a las páginas del documento.

    Excepciones
    -----------
    ValueError:

        Puede producirse si el archivo está protegido con una
        contraseña que no permite abrirlo automáticamente.

    PdfReadError:

        Puede producirse si el documento no posee una
        estructura PDF válida.
    """

    ruta_pdf = validar_ruta_pdf(
        ruta_pdf
    )

    try:

        lector = PdfReader(
            ruta_pdf
        )

    except PdfReadError as error:

        raise PdfReadError(
            "No fue posible interpretar el archivo PDF. "
            "El documento puede estar dañado o tener una "
            "estructura inválida. "
            f"Archivo: {ruta_pdf}"
        ) from error

    # ------------------------------------------------------
    # Algunos documentos PDF se encuentran cifrados.
    #
    # En ciertos casos pueden abrirse utilizando una
    # contraseña vacía.
    #
    # Si eso no funciona, informamos que el documento está
    # protegido y no puede leerse automáticamente.
    # ------------------------------------------------------

    if lector.is_encrypted:

        try:

            resultado_desbloqueo = lector.decrypt(
                ""
            )

        except Exception as error:

            raise ValueError(
                "El archivo PDF está protegido y no fue "
                "posible desbloquearlo automáticamente. "
                f"Archivo: {ruta_pdf}"
            ) from error

        if resultado_desbloqueo == 0:

            raise ValueError(
                "El archivo PDF requiere una contraseña. "
                f"Archivo: {ruta_pdf}"
            )

    return lector

# ==========================================================
# FIN DE LA FUNCIÓN abrir_pdf()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN extraer_texto_pagina()
# ==========================================================

def extraer_texto_pagina(pagina):
    """
    Extraer el texto de una página individual.

    Parámetros
    ----------
    pagina:

        Página perteneciente a un objeto PdfReader.

    Retorna
    -------
    str

        Texto extraído de la página.

        Si la página no contiene texto extraíble, devuelve
        una cadena vacía.
    """

    texto_pagina = pagina.extract_text()

    # ------------------------------------------------------
    # extract_text() puede devolver None cuando no encuentra
    # texto extraíble.
    #
    # Para que el resto del programa siempre trabaje con
    # cadenas, reemplazamos None por una cadena vacía.
    # ------------------------------------------------------

    if texto_pagina is None:

        return ""

    # ------------------------------------------------------
    # Eliminamos espacios y saltos de línea sobrantes al
    # comienzo y al final.
    #
    # No alteramos el contenido interno del texto.
    # ------------------------------------------------------

    texto_pagina = texto_pagina.strip()

    return texto_pagina

# ==========================================================
# FIN DE LA FUNCIÓN extraer_texto_pagina()
# ==========================================================


# OCR se usa únicamente como último recurso cuando ninguna página contiene
# texto extraíble. Se limita a las primeras páginas para no penalizar el flujo
# normal de facturas digitales.
_OCR_DPI = 300
_OCR_MAX_PAGES = 2
# Una pasada CLI individual no debe inmovilizar un lote completo.
# Los PSM complementarios siguen disponibles como fallback; este límite
# simplemente permite abandonar una estrategia patológica y probar la siguiente.
_OCR_CLI_TIMEOUT_SECONDS = 25


def _resolver_tessdata() -> str | None:
    """Buscar la carpeta de datos de Tesseract de forma portable.

    PyMuPDF necesita los archivos ``tessdata`` para OCR. Primero respetamos
    ``OCR_TESSDATA_PATH`` o ``TESSDATA_PREFIX`` si el usuario los configuró;
    después probamos ubicaciones habituales de Windows. No modificamos el
    entorno global: la ruta se pasa explícitamente a PyMuPDF.
    """
    import os

    candidatos = [
        os.getenv("OCR_TESSDATA_PATH", "").strip(),
        os.getenv("TESSDATA_PREFIX", "").strip(),
        r"C:\Program Files\Tesseract-OCR\tessdata",
        r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
    ]
    for candidato in candidatos:
        if candidato and Path(candidato).is_dir():
            return candidato
    return None



def _resolver_tesseract_executable() -> str | None:
    """Localizar el ejecutable de Tesseract para un segundo OCR de rescate."""
    import os
    import shutil

    candidatos = [
        os.getenv("OCR_TESSERACT_PATH", "").strip(),
        shutil.which("tesseract") or "",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for candidato in candidatos:
        if candidato and Path(candidato).is_file():
            return candidato
    return None


def _puntuar_calidad_ocr(texto: str) -> int:
    """Puntuar una lectura OCR por evidencia fiscal *validada*.

    La versión anterior premiaba principalmente palabras clave. Eso ayuda a
    escoger una segmentación legible, pero puede preferir una lectura que
    deformó un CUIT o perdió la letra del comprobante. Esta versión incorpora
    validaciones del propio dominio: tipo, letra, número, fecha, CUIT válido e
    identidad de emisor. El OCR no inventa esos datos; únicamente gana puntos
    cuando los detectores existentes consiguen validarlos.
    """
    import re
    import unicodedata

    normalized = unicodedata.normalize("NFKD", texto or "")
    normalized = "".join(c for c in normalized if not unicodedata.combining(c)).upper()
    score = min(len(normalized) // 120, 4)

    # Evidencia textual básica. Sirve para desempates cuando dos OCR recuperan
    # la misma estructura fiscal.
    checks = (
        (r"\bNOTA\s+DE\s+(?:CREDITO|DEBITO)\b", 5),
        (r"\bFACTURA\b", 4),
        (r"\bREMITO\b", 3),
        (r"\bRAZON\s+SOCIAL\b", 3),
        (r"\bCUIT\b", 2),
        (r"\bPUNTO\s+DE\s+VENTA\b", 3),
        (r"\bCOMP(?:ROBANTE)?\.?\s+NRO\b", 3),
        (r"\bCAE\b", 1),
        (r"\bIVA\b", 1),
    )
    for pattern, points in checks:
        if re.search(pattern, normalized):
            score += points

    # Scoring fiscal real. Los imports locales evitan convertir pdf_reader en
    # una dependencia de alto nivel durante la importación normal del módulo.
    try:
        from fiscal.parser import analizar_encabezado_fiscal

        header = analizar_encabezado_fiscal(texto or "")
        if header.document_type:
            score += 9
        if header.fiscal_letter:
            score += 8
        if header.document_number:
            score += 10
        if header.issue_date:
            score += 7
        if all((header.document_type, header.fiscal_letter, header.document_number, header.issue_date)):
            score += 12
    except Exception:
        pass

    # Un CUIT con dígito verificador correcto es una señal especialmente útil
    # para elegir entre OCRs que difieren por un solo carácter numérico.
    try:
        from suppliers.cuit import extraer_cuits, normalizar_cuit

        valid_cuits = extraer_cuits(texto or "")
        score += min(len(valid_cuits), 3) * 8

        # Si la etiqueta CUIT contiene once dígitos pero ninguno valida,
        # penalizamos la lectura: suele ser exactamente el caso 9->0, 8->3, etc.
        for match in re.finditer(
            r"\bCUIT(?:\s+EMISOR|\s+RECEPTOR)?\s*[:NRO.°º-]*\s*([0-9 .-]{11,18})",
            normalized,
        ):
            digits = re.sub(r"\D", "", match.group(1))
            if len(digits) >= 11:
                candidate = digits[:11]
                if normalizar_cuit(candidate) is None:
                    score -= 10

        if re.search(r"\bCUIT\s+EMISOR\b", normalized) and valid_cuits:
            score += 4
    except Exception:
        pass

    # Una identidad de emisor completa demuestra que nombre y CUIT quedaron
    # relacionados de forma semánticamente útil, no solo que aparecen palabras.
    try:
        from suppliers.issuer_identity import extraer_identidad_emisor

        identity = extraer_identidad_emisor(texto or "")
        if identity is not None:
            score += 14
            score += min(max(identity.score, 0), 20) // 4
    except Exception:
        pass

    return score


def _ejecutar_tesseract_sobre_imagen(image_path: Path, executable: str, *, psm: int) -> str:
    """Ejecutar Tesseract sobre una imagen ya renderizada.

    Cada PSM es una estrategia alternativa. Si una de ellas queda atrapada en
    una imagen problemática, el timeout devuelve texto vacío y permite que el
    OCR adaptativo continúe con la siguiente estrategia. De este modo un solo
    escaneo no puede bloquear indefinidamente todo ``_Pendientes``.
    """
    import subprocess

    try:
        completed = subprocess.run(
            [
                executable,
                str(image_path),
                "stdout",
                "-l",
                "spa+eng",
                "--psm",
                str(psm),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=_OCR_CLI_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return ""

    if completed.returncode != 0:
        return ""
    return completed.stdout.decode("utf-8", errors="replace").strip()


def _ocr_cli_tesseract(
    pagina,
    executable: str,
    *,
    psm: int = 3,
    dpi: int = _OCR_DPI,
) -> str:
    """Ejecutar una pasada OCR con Tesseract CLI.

    Esta función se conserva como unidad reutilizable y testeable. La rutina
    multipasada renderiza una sola vez la página para evitar repetir un trabajo
    costoso en cada PSM.
    """
    import tempfile

    with tempfile.TemporaryDirectory(prefix="proyecto_facturas_ocr_") as temp_dir:
        image_path = Path(temp_dir) / "page.png"
        pixmap = pagina.get_pixmap(dpi=dpi, alpha=False)
        pixmap.save(str(image_path))
        return _ejecutar_tesseract_sobre_imagen(image_path, executable, psm=psm)


def _analizar_evidencia_ocr(texto: str):
    """Extraer cabecera fiscal e identidad validadas de una pasada OCR.

    La función mantiene los imports locales para evitar acoplar ``pdf_reader``
    con el dominio fiscal durante el arranque normal de la aplicación.
    """
    header = None
    identity = None
    try:
        from fiscal.parser import analizar_encabezado_fiscal

        header = analizar_encabezado_fiscal(texto or "")
    except Exception:
        pass
    try:
        from suppliers.issuer_identity import extraer_identidad_emisor

        identity = extraer_identidad_emisor(texto or "")
    except Exception:
        pass
    return header, identity


def _fusionar_evidencia_ocr(
    evaluados: list[tuple[str, str, int]],
) -> tuple[str, str, int] | None:
    """Fusionar campos *validados* recuperados por distintas pasadas OCR.

    Distintos PSM de Tesseract suelen leer bien regiones diferentes de una
    misma página. La lectura global con mejor puntaje puede conservar tipo,
    letra y número, mientras otra pasada recupera la razón social y el CUIT.

    La fusión es deliberadamente conservadora:

    * parte siempre de la mejor lectura global;
    * nunca reemplaza un campo fiscal ya detectado en esa lectura;
    * solo agrega una identidad si otra pasada logró construir un emisor con
      CUIT matemáticamente válido;
    * solo agrega tipo/letra/número/fecha cuando el campo está ausente;
    * no copia texto arbitrario entre pasadas, sino evidencia ya validada por
      los parsers del dominio.

    Esto evita convertir el OCR multipasada en una concatenación ruidosa que
    pueda mezclar el comprobante actual con referencias internas.
    """
    if not evaluados:
        return None

    evaluados_ordenados = sorted(
        evaluados,
        key=lambda item: (item[2], len(item[1])),
        reverse=True,
    )
    metodo_base, texto_base, puntaje_base = evaluados_ordenados[0]
    header_base, identity_base = _analizar_evidencia_ocr(texto_base)

    partes = [texto_base.strip()]
    metodos_usados = [metodo_base]
    changed = False

    # Los valores ya presentes en la mejor pasada son fuente prioritaria. Solo
    # completamos huecos con datos que otra pasada haya podido validar.
    document_type = getattr(header_base, "document_type", None)
    fiscal_letter = getattr(header_base, "fiscal_letter", None)
    document_number = getattr(header_base, "document_number", None)
    issue_date = getattr(header_base, "issue_date", None)

    for metodo, texto, _puntaje in evaluados_ordenados[1:]:
        header, identity = _analizar_evidencia_ocr(texto)
        complementos: list[str] = []

        if identity_base is None and identity is not None:
            complementos.extend(
                (
                    f"RAZON SOCIAL: {identity.legal_name}",
                    f"CUIT EMISOR: {identity.cuit}",
                )
            )
            identity_base = identity

        candidate_type = getattr(header, "document_type", None)
        candidate_letter = getattr(header, "fiscal_letter", None)
        candidate_number = getattr(header, "document_number", None)
        candidate_date = getattr(header, "issue_date", None)

        # Tipo y letra se agregan juntos cuando ambos faltan, o de manera
        # individual cuando la base ya fijó inequívocamente la otra mitad.
        if not document_type and candidate_type:
            if candidate_letter:
                complementos.append(f"{candidate_type} {candidate_letter}")
                fiscal_letter = fiscal_letter or candidate_letter
            else:
                complementos.append(candidate_type)
            document_type = candidate_type
        elif document_type and not fiscal_letter and candidate_letter:
            if candidate_type in (None, document_type):
                complementos.append(f"{document_type} {candidate_letter}")
                fiscal_letter = candidate_letter

        if not document_number and candidate_number:
            complementos.extend(("NUMERO DEL COMPROBANTE", candidate_number))
            document_number = candidate_number

        if not issue_date and candidate_date:
            complementos.append(f"FECHA DE EMISION: {candidate_date}")
            issue_date = candidate_date

        if complementos:
            partes.append("\n".join(complementos))
            metodos_usados.append(metodo)
            changed = True

        # Si ya reconstruimos todos los campos críticos y una identidad válida,
        # no necesitamos incorporar más evidencia secundaria.
        if all((document_type, fiscal_letter, document_number, issue_date, identity_base)):
            break

    if not changed:
        return None

    texto_fusionado = "\n\n".join(parte for parte in partes if parte).strip()
    puntaje_fusionado = _puntuar_calidad_ocr(texto_fusionado)

    # Una fusión que no mejora la evidencia total no desplaza a la pasada base.
    if puntaje_fusionado <= puntaje_base:
        return None

    metodos_unicos = list(dict.fromkeys(metodos_usados))
    metodo_fusion = "fusion_ocr[" + "+".join(metodos_unicos) + "]"
    return metodo_fusion, texto_fusionado, puntaje_fusionado


def _seleccionar_mejor_ocr(candidatos: list[tuple[str, str]]) -> tuple[str, str, int]:
    """Elegir o fusionar las lecturas con mayor evidencia fiscal validada."""
    disponibles = [(metodo, texto) for metodo, texto in candidatos if (texto or "").strip()]
    if not disponibles:
        return "sin_ocr", "", -10_000

    evaluados = [
        (metodo, texto, _puntuar_calidad_ocr(texto))
        for metodo, texto in disponibles
    ]
    evaluados.sort(key=lambda item: (item[2], len(item[1])), reverse=True)

    fusion = _fusionar_evidencia_ocr(evaluados)
    if fusion is not None:
        return fusion
    return evaluados[0]


def _ocr_tiene_evidencia_suficiente(texto: str) -> bool:
    """Decidir si una pasada ya es suficientemente fuerte para detenerse.

    No se usa un puntaje mágico. Para comprobantes fiscales exigimos los cuatro
    campos críticos y una identidad de emisor validada. Para un remito explícito
    exigimos además ``NO ES FACTURA``. Si falta cualquiera de esas piezas se
    prueban otras segmentaciones.
    """
    import re
    import unicodedata

    normalized = unicodedata.normalize("NFKD", texto or "")
    normalized = "".join(c for c in normalized if not unicodedata.combining(c)).upper()

    if "REMITO" in normalized and "NO ES FACTURA" in normalized:
        try:
            from suppliers.cuit import extraer_cuits
            return bool(extraer_cuits(texto or ""))
        except Exception:
            return False

    try:
        from fiscal.parser import analizar_encabezado_fiscal
        from suppliers.issuer_identity import extraer_identidad_emisor

        header = analizar_encabezado_fiscal(texto or "")
        complete = all(
            (
                header.document_type,
                header.fiscal_letter,
                header.document_number,
                header.issue_date,
            )
        )
        if not complete:
            return False
        return extraer_identidad_emisor(texto or "") is not None
    except Exception:
        return False


def _ocr_multapas_tesseract(pagina, executable: str) -> list[tuple[str, str]]:
    """Producir OCR adaptativo con segmentaciones y rotaciones complementarias.

    Primero se prueban PSM habituales sobre la página en orientación original.
    Si aun falta una identidad de emisor confiable, se renderizan versiones
    rotadas 90° y 270°. Estas pasadas sirven especialmente para encabezados o
    razones sociales impresas en barras laterales. Las rotaciones nunca
    reemplazan campos fiscales sólidos: solo aportan evidencia adicional que
    luego pasa por la fusión conservadora de OCR.
    """
    import tempfile

    candidatos: list[tuple[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="proyecto_facturas_ocr_multi_") as temp_dir:
        temp_path = Path(temp_dir)

        def ejecutar_sobre_raster(image_path: Path, prefijo: str, psms: tuple[int, ...]) -> bool:
            for psm in psms:
                try:
                    texto = _ejecutar_tesseract_sobre_imagen(image_path, executable, psm=psm)
                except Exception:
                    texto = ""
                if not texto:
                    continue
                candidatos.append((f"{prefijo}_psm{psm}", texto))

                # Corte rápido 1: una pasada individual ya reconstruyó toda
                # la evidencia fiscal necesaria.
                if _ocr_tiene_evidencia_suficiente(texto):
                    return True

                # Corte rápido 2: dos PSM pueden haber recuperado regiones
                # complementarias. Conservamos la fusión segura desarrollada
                # en los stress tests y evitamos seguir ejecutando Tesseract
                # cuando esa evidencia combinada ya es suficiente.
                if len(candidatos) > 1:
                    _metodo, texto_acumulado, _puntaje = _seleccionar_mejor_ocr(candidatos)
                    if _ocr_tiene_evidencia_suficiente(texto_acumulado):
                        return True
            return False

        image_path = temp_path / "page.png"
        pixmap = pagina.get_pixmap(dpi=_OCR_DPI, alpha=False)
        pixmap.save(str(image_path))

        suficiente = ejecutar_sobre_raster(
            image_path,
            "tesseract_cli",
            (3, 11, 4, 6, 12),
        )

        # Si la lectura horizontal ya reconstruyó documento + emisor, evitamos
        # trabajo extra. Si no, buscamos texto vertical con ambas rotaciones.
        if not suficiente:
            escala = _OCR_DPI / 72.0
            for angulo in (90, 270):
                rotated_path = temp_path / f"page_rot{angulo}.png"
                matriz = pymupdf.Matrix(escala, escala).prerotate(angulo)
                try:
                    rotated = pagina.get_pixmap(matrix=matriz, alpha=False)
                except TypeError:
                    # Compatibilidad con dobles de prueba / wrappers mínimos
                    # que solo implementan la firma histórica con ``dpi``.
                    continue
                rotated.save(str(rotated_path))
                suficiente_rotada = ejecutar_sobre_raster(
                    rotated_path,
                    f"tesseract_cli_rot{angulo}",
                    (6, 11, 3),
                )
                if suficiente_rotada:
                    break

    return candidatos

def _extraer_texto_ocr(ruta_pdf, cantidad_paginas: int) -> dict:
    """Intentar OCR y devolver tanto texto como diagnóstico explicable.

    El OCR es opcional. Un fallo nunca debe hacer caer el procesamiento, pero
    tampoco debe quedar oculto: el llamador recibe ``estado`` y ``error`` para
    poder mantener el PDF en ``_Pendientes`` en vez de clasificarlo a ciegas.
    """
    if pymupdf is None:
        return {
            "paginas": [],
            "estado": "pymupdf_no_disponible",
            "error": "PyMuPDF no está instalado; no se pudo intentar OCR.",
        }

    tessdata = _resolver_tessdata()
    if tessdata is None:
        return {
            "paginas": [],
            "estado": "tesseract_no_configurado",
            "error": (
                "El PDF no contiene texto y no se encontró la carpeta tessdata de "
                "Tesseract. Configure OCR_TESSDATA_PATH en .env o instale Tesseract OCR."
            ),
        }

    try:
        documento = pymupdf.open(str(validar_ruta_pdf(ruta_pdf)))
    except Exception as error:
        return {
            "paginas": [],
            "estado": "ocr_error",
            "error": f"No fue posible abrir el PDF con PyMuPDF para OCR: {error}",
        }

    paginas_ocr: list[dict] = []
    limite = min(len(documento), cantidad_paginas, _OCR_MAX_PAGES)

    for indice in range(limite):
        pagina = documento[indice]
        try:
            textpage = pagina.get_textpage_ocr(
                flags=0,
                dpi=_OCR_DPI,
                full=True,
                tessdata=tessdata,
                language="spa+eng",
            )
            texto_pymupdf = (pagina.get_text("text", textpage=textpage) or "").strip()
        except Exception as error:
            documento.close()
            return {
                "paginas": [],
                "estado": "ocr_error",
                "error": f"Tesseract OCR no pudo procesar el documento: {error}",
            }

        candidatos_ocr: list[tuple[str, str]] = [
            ("pymupdf_tesseract", texto_pymupdf),
        ]

        # PyMuPDF ya ejecutó una pasada OCR completa. Antes se lanzaban además
        # todas las pasadas CLI aunque esa primera lectura ya fuera suficiente.
        # Ahora las estrategias costosas quedan como fallback: si la evidencia
        # fiscal ya está completa, conservamos el resultado y evitamos trabajo
        # redundante; si falta algo, mantenemos intacto el arsenal multipasada,
        # scoring, fusión y rotaciones validado por los stress tests.
        if not _ocr_tiene_evidencia_suficiente(texto_pymupdf):
            executable = _resolver_tesseract_executable()
            if executable:
                candidatos_ocr.extend(_ocr_multapas_tesseract(pagina, executable))

        metodo_ocr, texto, puntaje_ocr = _seleccionar_mejor_ocr(candidatos_ocr)
        diagnostico_candidatos = [
            {
                "metodo": metodo,
                "puntaje": _puntuar_calidad_ocr(texto_candidato),
                "texto": texto_candidato,
            }
            for metodo, texto_candidato in candidatos_ocr
            if (texto_candidato or "").strip()
        ]
        diagnostico_candidatos.sort(
            key=lambda item: (item["puntaje"], len(item["texto"])),
            reverse=True,
        )

        paginas_ocr.append({
            "numero": indice + 1,
            "texto": texto,
            "origen_texto": "ocr",
            "metodo_ocr": metodo_ocr,
            "puntaje_ocr": puntaje_ocr,
            "ocr_candidatos": diagnostico_candidatos,
        })

    documento.close()
    if any(pagina["texto"] for pagina in paginas_ocr):
        return {"paginas": paginas_ocr, "estado": "ocr_ok", "error": None}

    return {
        "paginas": paginas_ocr,
        "estado": "ocr_sin_texto",
        "error": "El OCR se ejecutó, pero no recuperó texto utilizable.",
    }


def extraer_texto_ocr_forzado(ruta_pdf) -> dict:
    """Ejecutar OCR aun cuando el PDF ya tenga una capa de texto.

    Se usa como rescate semántico cuando la extracción digital existe pero
    omitió campos críticos (por ejemplo una razón social dibujada como imagen).
    No reemplaza automáticamente el texto digital: devuelve una segunda fuente
    para que el pipeline complete únicamente datos faltantes.
    """
    ruta_pdf = validar_ruta_pdf(ruta_pdf)
    try:
        lector = abrir_pdf(ruta_pdf)
        cantidad_paginas = len(lector.pages)
    except Exception:
        if pymupdf is None:
            return {"texto_completo": "", "estado": "pymupdf_no_disponible", "error": "PyMuPDF no está disponible."}
        documento = pymupdf.open(str(ruta_pdf))
        cantidad_paginas = len(documento)
        documento.close()

    resultado = _extraer_texto_ocr(ruta_pdf, cantidad_paginas)
    texto_completo = "\n\n".join(
        pagina.get("texto", "").strip()
        for pagina in resultado.get("paginas", [])
        if pagina.get("texto", "").strip()
    )
    return {
        "texto_completo": texto_completo,
        "estado": resultado.get("estado"),
        "error": resultado.get("error"),
        "paginas": resultado.get("paginas", []),
    }


# ==========================================================
# INICIO DE LA FUNCIÓN extraer_paginas_pdf()
# ==========================================================

def extraer_paginas_pdf(ruta_pdf, *, permitir_ocr=True):
    """
    Extraer por separado el texto de todas las páginas.

    Parámetros
    ----------
    ruta_pdf:

        Ruta del documento PDF.

    Retorna
    -------
    list

        Lista de diccionarios.

        Cada diccionario representa una página y posee esta
        estructura:

            {
                "numero": 1,
                "texto": "Contenido de la página"
            }

        Si una página no contiene texto extraíble, su valor
        "texto" será una cadena vacía.
    """

    try:
        lector = abrir_pdf(ruta_pdf)
    except PdfReadError:
        if pymupdf is None:
            raise
        # PyMuPDF tolera algunos PDFs que pypdf rechaza por tablas xref o
        # trailers no estándar. Es un respaldo textual, no OCR.
        documento = pymupdf.open(str(validar_ruta_pdf(ruta_pdf)))
        return [
            {"numero": indice + 1, "texto": (pagina.get_text("text") or "").strip()}
            for indice, pagina in enumerate(documento)
        ]

    paginas_extraidas = []

    for numero_pagina, pagina in enumerate(
        lector.pages,
        start=1
    ):

        try:

            texto_pagina = extraer_texto_pagina(
                pagina
            )

        except Exception as error:

            raise ValueError(
                "Se produjo un error al extraer el texto de "
                f"la página {numero_pagina}."
            ) from error

        informacion_pagina = {
            "numero": numero_pagina,
            "texto": texto_pagina
        }

        paginas_extraidas.append(
            informacion_pagina
        )

    # Si pypdf no obtuvo texto de ninguna página, intentamos OCR solo entonces
    # y únicamente si el llamador lo permite. El parser normal sigue siendo la
    # ruta por defecto; ``permitir_ocr=False`` existe para operaciones como la
    # auditoría histórica, donde preferimos omitir un escaneo antes que pagar
    # OCR o mover un archivo basándonos en una lectura secundaria.
    if (
        permitir_ocr
        and paginas_extraidas
        and not any(pagina["texto"] for pagina in paginas_extraidas)
    ):
        resultado_ocr = _extraer_texto_ocr(ruta_pdf, len(paginas_extraidas))
        paginas_ocr = resultado_ocr["paginas"]
        paginas_por_numero = {pagina["numero"]: pagina for pagina in paginas_ocr}
        for pagina in paginas_extraidas:
            recuperada = paginas_por_numero.get(pagina["numero"])
            if recuperada and recuperada.get("texto"):
                pagina["texto"] = recuperada["texto"]
                pagina["origen_texto"] = "ocr"
                pagina["metodo_ocr"] = recuperada.get("metodo_ocr")
                pagina["puntaje_ocr"] = recuperada.get("puntaje_ocr")
                pagina["ocr_candidatos"] = recuperada.get("ocr_candidatos", [])
            pagina["ocr_estado"] = resultado_ocr["estado"]
            pagina["ocr_error"] = resultado_ocr["error"]

    return paginas_extraidas

# ==========================================================
# FIN DE LA FUNCIÓN extraer_paginas_pdf()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN unir_texto_paginas()
# ==========================================================

def unir_texto_paginas(paginas):
    """
    Unir el texto extraído de todas las páginas.

    Parámetros
    ----------
    paginas:

        Lista de diccionarios generada por:

            extraer_paginas_pdf()

    Retorna
    -------
    str

        Texto completo del documento.

        Las páginas que contienen texto se separan mediante
        dos saltos de línea.

        Las páginas vacías no agregan espacios innecesarios.
    """

    textos_disponibles = []

    for pagina in paginas:

        texto_pagina = pagina.get(
            "texto",
            ""
        )

        if texto_pagina:

            textos_disponibles.append(
                texto_pagina
            )

    texto_completo = "\n\n".join(
        textos_disponibles
    )

    return texto_completo

# ==========================================================
# FIN DE LA FUNCIÓN unir_texto_paginas()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN leer_pdf()
# ==========================================================

def leer_pdf(ruta_pdf, *, permitir_ocr=True):
    """
    Leer un archivo PDF y devolver un resumen de su contenido.

    Parámetros
    ----------
    ruta_pdf:

        Ruta del archivo que deseamos procesar.

    Retorna
    -------
    dict

        Diccionario con la información obtenida.

        Su estructura es:

            {
                "ruta": Path(...),
                "nombre": "factura.pdf",
                "cantidad_paginas": 1,
                "paginas_con_texto": 1,
                "paginas_sin_texto": 0,
                "contiene_texto": True,
                "paginas": [...],
                "texto_completo": "..."
            }

    permitir_ocr:

        Si es ``True`` (valor por defecto), un PDF completamente sin texto
        digital puede recurrir a OCR. Si es ``False``, la función se limita a
        extracción digital y nunca invoca Tesseract.

    Importante
    ----------
    La función devuelve información estructurada.

    No imprime el resultado directamente porque la salida
    visual corresponde a console_output.py y main.py.
    """

    ruta_pdf = validar_ruta_pdf(
        ruta_pdf
    )

    paginas = extraer_paginas_pdf(
        ruta_pdf,
        permitir_ocr=permitir_ocr,
    )

    cantidad_paginas = len(
        paginas
    )

    paginas_con_texto = sum(
        1
        for pagina in paginas
        if pagina["texto"]
    )

    paginas_sin_texto = (
        cantidad_paginas
        -
        paginas_con_texto
    )

    texto_completo = unir_texto_paginas(
        paginas
    )

    ocr_utilizado = any(pagina.get("origen_texto") == "ocr" for pagina in paginas)
    ocr_estado = next(
        (pagina.get("ocr_estado") for pagina in paginas if pagina.get("ocr_estado")),
        "no_necesario" if texto_completo else "no_intentado",
    )
    ocr_error = next(
        (pagina.get("ocr_error") for pagina in paginas if pagina.get("ocr_error")),
        None,
    )
    ocr_metodo = next(
        (pagina.get("metodo_ocr") for pagina in paginas if pagina.get("metodo_ocr")),
        None,
    )
    ocr_puntaje = next(
        (pagina.get("puntaje_ocr") for pagina in paginas if pagina.get("puntaje_ocr") is not None),
        None,
    )
    ocr_candidatos = [
        candidato
        for pagina in paginas
        for candidato in pagina.get("ocr_candidatos", [])
    ]

    resultado = {
        "ruta": ruta_pdf,
        "nombre": ruta_pdf.name,
        "cantidad_paginas": cantidad_paginas,
        "paginas_con_texto": paginas_con_texto,
        "paginas_sin_texto": paginas_sin_texto,
        "contiene_texto": bool(texto_completo),
        "ocr_utilizado": ocr_utilizado,
        "ocr_estado": ocr_estado,
        "ocr_error": ocr_error,
        "ocr_metodo": ocr_metodo,
        "ocr_puntaje": ocr_puntaje,
        "ocr_candidatos": ocr_candidatos,
        "paginas": paginas,
        "texto_completo": texto_completo
    }

    return resultado

# ==========================================================
# FIN DE LA FUNCIÓN leer_pdf()
# ==========================================================




def describir_fallo_ocr(resultado_lectura: dict) -> str:
    """Construir un motivo claro cuando un PDF escaneado no pudo leerse."""
    estado = resultado_lectura.get("ocr_estado")
    error = resultado_lectura.get("ocr_error")

    if estado == "tesseract_no_configurado":
        return (
            "PDF sin capa de texto. OCR no disponible: no se encontró Tesseract/tessdata. "
            "El archivo se mantiene en _Pendientes por seguridad."
        )
    if estado == "pymupdf_no_disponible":
        return (
            "PDF sin capa de texto. PyMuPDF no está disponible para intentar OCR. "
            "El archivo se mantiene en _Pendientes por seguridad."
        )
    if estado in {"ocr_error", "ocr_sin_texto"}:
        detalle = f" Detalle técnico: {error}" if error else ""
        return (
            "PDF sin capa de texto y OCR sin resultado utilizable. "
            "El archivo se mantiene en _Pendientes por seguridad." + detalle
        )
    return (
        "El PDF no contiene texto utilizable. El archivo se mantiene en "
        "_Pendientes para revisión manual."
    )


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================