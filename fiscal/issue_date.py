"""Detección defensiva de la fecha de emisión fiscal.

Las expresiones regulares localizan candidatos, pero la selección final usa
contexto semántico. Una fecha de inicio de actividades o vencimiento nunca debe
reemplazar a la fecha de emisión.
"""

import re
from datetime import datetime
from typing import Optional

from fiscal.normalization import normalizar_para_busqueda
from fiscal.type_detector import detectar_tipo_comprobante

PATRON_FECHA = r"(\d{1,2}[./-]\d{1,2}[./-](?:\d{4}|\d{2}))"
_MESES = {
    "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4,
    "MAYO": 5, "JUNIO": 6, "JULIO": 7, "AGOSTO": 8,
    "SEPTIEMBRE": 9, "SETIEMBRE": 9, "OCTUBRE": 10,
    "NOVIEMBRE": 11, "DICIEMBRE": 12,
}
_EXCLUDED_DATE_CONTEXT = (
    "INICIO DE ACTIVIDADES",
    "INICIO ACTIVIDADES",
    "FECHA DE INICIO",
    "VENCIMIENTO",
    "VTO",
    "CAE",
    "ENTREGA",
    "PERIODO FACTURADO",
)


def _limpiar_fecha(valor: str) -> Optional[str]:
    """Validar una fecha y devolverla como ``DD/MM/AAAA``."""
    for formato in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(valor, formato).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return None


def _limpiar_fecha_textual(dia: str, mes: str, anio: str) -> Optional[str]:
    """Normalizar fechas como ``12 DE MAYO DE 2026``."""
    numero_mes = _MESES.get(mes.upper())
    if numero_mes is None:
        return None
    try:
        return datetime(int(anio), numero_mes, int(dia)).strftime("%d/%m/%Y")
    except ValueError:
        return None


def _contexto_excluido(texto: str, inicio: int) -> bool:
    """Indicar si una fecha está asociada a un campo secundario."""
    contexto = texto[max(0, inicio - 70):inicio].upper()
    # Si hay otra fecha dentro de la ventana, las etiquetas anteriores
    # pertenecen a esa fecha, no necesariamente al candidato actual.
    fechas_previas = list(re.finditer(PATRON_FECHA, contexto))
    if fechas_previas:
        contexto = contexto[fechas_previas[-1].end():]
    return any(etiqueta in contexto for etiqueta in _EXCLUDED_DATE_CONTEXT)


def _detectar_fecha_en_bloque_arca(texto: str) -> Optional[str]:
    patron = (
        r"PERIODO\s+FACTURADO\s+DESDE:.{0,80}?HASTA:.{0,80}?"
        r"FECHA\s+DE\s+VTO\.?\s+PARA\s+EL\s+PAGO:.{0,500}?"
        rf"{PATRON_FECHA}\s+{PATRON_FECHA}\s+{PATRON_FECHA}\s+{PATRON_FECHA}"
    )
    coincidencia = re.search(patron, texto)
    return _limpiar_fecha(coincidencia.group(4)) if coincidencia else None


def detectar_fecha_emision(texto: str, *, contexto_fiscal_confirmado: bool = False) -> Optional[str]:
    """Buscar la fecha de emisión de mayor a menor evidencia contextual."""
    texto = normalizar_para_busqueda(texto)
    if not texto:
        return None

    # Fechas textuales utilizadas por sistemas SAP/legacy. Se priorizan cuando
    # aparecen junto al encabezado del comprobante.
    textual = re.search(
        r"(?:FACTURA.{0,80}?|BS[.]?AS[.]?,?\s*)(\d{1,2})\s+DE\s+"
        r"(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|"
        r"SEPTIEMBRE|SETIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE)\s+DE\s+(\d{4})",
        texto,
    )
    if textual:
        fecha = _limpiar_fecha_textual(*textual.groups())
        if fecha:
            return fecha

    # Algunos comprobantes antiguos separan día, mes y año únicamente con
    # espacios (por ejemplo ``FECHA: 08 07 25``). Esta variante se admite solo
    # junto a la etiqueta FECHA para no convertir importes o códigos en fechas.
    fecha_espaciada = re.search(
        r"\bFECHA\b\s*[:\-]?\s*(\d{1,2})\s+(\d{1,2})\s+(\d{2}|\d{4})\b",
        texto,
    )
    if fecha_espaciada:
        dia, mes, anio = fecha_espaciada.groups()
        valor = f"{dia}/{mes}/{anio}"
        fecha = _limpiar_fecha(valor)
        if fecha:
            return fecha

    # Algunos comprobantes legacy imprimen la fecha sin etiqueta, pero justo
    # después de la identidad fiscal completa. Ejemplo real:
    #
    #     B 00021-00001477 08 07 25
    #
    # La combinación letra + punto de venta + número aporta contexto suficiente
    # para interpretar los tres grupos siguientes como fecha de emisión. Esta
    # regla se evalúa antes de cualquier búsqueda genérica para que un campo
    # posterior como ``F.VTO: 18/07/2025`` nunca gane por aparecer con barras.
    fecha_despues_identidad = re.search(
        r"\b[ABC]\s*\d{4,5}\s*[- ]\s*\d{8}\s+"
        r"(\d{1,2})\s+(\d{1,2})\s+(\d{2}|\d{4})\b",
        texto,
    )
    if fecha_despues_identidad:
        dia, mes, anio = fecha_despues_identidad.groups()
        fecha = _limpiar_fecha(f"{dia}/{mes}/{anio}")
        if fecha:
            return fecha

    # Algunos PDF antiguos no exponen palabras ni números como bloques: cada
    # carácter aparece en una línea independiente. Después de normalizar los
    # espacios, una fecha como ``08 07 25`` continúa separada y la expresión
    # anterior no puede relacionarla con el número fiscal. Para este caso se
    # construye una vista compacta *solo para una regla estructural fuerte*:
    # letra + punto de venta + número de ocho dígitos + fecha de seis u ocho
    # dígitos. No se usa la vista compacta para buscar cualquier fecha, porque
    # eso podría confundir importes, CAE o vencimientos.
    texto_sin_espacios = re.sub(r"\s+", "", texto)
    fecha_compacta_despues_identidad = re.search(
        r"[ABC]\d{4,5}-\d{8}(\d{6}|\d{8})",
        texto_sin_espacios,
    )
    if fecha_compacta_despues_identidad:
        valor_compacto = fecha_compacta_despues_identidad.group(1)
        if len(valor_compacto) == 6:
            dia, mes, anio = (
                valor_compacto[0:2],
                valor_compacto[2:4],
                valor_compacto[4:6],
            )
        else:
            dia, mes, anio = (
                valor_compacto[0:2],
                valor_compacto[2:4],
                valor_compacto[4:8],
            )
        fecha = _limpiar_fecha(f"{dia}/{mes}/{anio}")
        if fecha:
            return fecha

    # Etiquetas inequívocas tienen prioridad absoluta.
    for etiqueta in (r"FECHA\s+DE\s+EMISION", r"FECHA\s+EMISION", r"FECHA\s+DEL\s+COMPROBANTE"):
        coincidencia = re.search(rf"\b{etiqueta}\b\s*[:\-]?\s*{PATRON_FECHA}", texto)
        if coincidencia:
            fecha = _limpiar_fecha(coincidencia.group(1))
            if fecha:
                return fecha

    fecha_arca = _detectar_fecha_en_bloque_arca(texto)
    if fecha_arca:
        return fecha_arca

    # Algunos diseños imprimen la fecha inmediatamente antes del título
    # FACTURA. Esta regla resuelve layouts visuales cuyo orden textual queda
    # invertido, como DF Megafrío/TurboBlender.
    for antes_del_tipo in re.finditer(
        rf"{PATRON_FECHA}(?=.{{0,80}}?\b(?:FACTURA|NOTA\s+DE\s+(?:CREDITO|DEBITO))\b)",
        texto,
    ):
        if _contexto_excluido(texto, antes_del_tipo.start(1)):
            continue
        fecha = _limpiar_fecha(antes_del_tipo.group(1))
        if fecha:
            return fecha

    # ``Fecha:`` es ambiguo. Solo se acepta si el contexto inmediato no habla
    # de vencimiento, CAE, entrega o inicio de actividades.
    for coincidencia in re.finditer(rf"\bFECHA\b\s*[:\-]?\s*{PATRON_FECHA}", texto):
        if _contexto_excluido(texto, coincidencia.start(1)):
            continue
        fecha = _limpiar_fecha(coincidencia.group(1))
        if fecha:
            return fecha

    if contexto_fiscal_confirmado or detectar_tipo_comprobante(texto):
        for coincidencia in re.finditer(PATRON_FECHA, texto):
            if _contexto_excluido(texto, coincidencia.start(1)):
                continue
            fecha = _limpiar_fecha(coincidencia.group(1))
            if fecha:
                return fecha

        texto_compacto = re.sub(r"\s+", "", texto)
        for valor in re.findall(PATRON_FECHA, texto_compacto):
            fecha = _limpiar_fecha(valor)
            if fecha:
                return fecha
    return None
