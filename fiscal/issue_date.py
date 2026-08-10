"""Detección defensiva de la fecha de emisión fiscal.

Las expresiones regulares localizan candidatos, pero la selección final usa
contexto semántico. Una fecha de inicio de actividades o vencimiento nunca debe
reemplazar a la fecha de emisión.
"""

import re
from dataclasses import dataclass
from datetime import date, datetime
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
    "INICIO ACTIV",
    "INICIO DE ACTIV",
    "FECHA DE INICIO",
    "VENCIMIENTO",
    "VENC",
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


def _reparar_anio_por_vencimiento(fecha: str, texto: str) -> str:
    """Corregir un año OCR claramente incompatible con el vencimiento.

    En formularios escaneados un ``6`` puede leerse como ``8`` o ``0``. Si la
    fecha de emisión detectada tiene un año distinto al vencimiento, probamos
    el mismo día y mes con el año del vencimiento. Solo se corrige cuando esa
    alternativa queda entre 0 y 62 días antes del vencimiento. Así evitamos
    usar el año actual o una heurística dependiente del reloj del equipo.
    """
    try:
        issue = datetime.strptime(fecha, "%d/%m/%Y")
    except ValueError:
        return fecha

    due_match = re.search(
        r"\b(?:VENC(?:IMIENTO)?|VTO)\.?\s*[:;.-]?\s*(\d{1,2}[./-]\d{1,2}[./-](?:\d{4}|\d{2}))",
        texto,
    )
    if not due_match:
        return fecha

    due_text = _limpiar_fecha(due_match.group(1))
    if not due_text:
        return fecha
    due = datetime.strptime(due_text, "%d/%m/%Y")
    if issue.year == due.year:
        return fecha

    try:
        repaired = issue.replace(year=due.year)
    except ValueError:
        return fecha

    delta = (due - repaired).days
    if 0 <= delta <= 62:
        return repaired.strftime("%d/%m/%Y")
    return fecha


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



@dataclass(frozen=True)
class DateAuditCandidate:
    """Candidato de fecha con evidencia explicable para una auditoría."""

    issue_date: str
    score: int
    reason: str
    position: int


@dataclass(frozen=True)
class DateAuditAnalysis:
    """Resultado explicable del análisis estricto de fecha de emisión."""

    issue_date: Optional[str]
    confidence: str
    reason: str
    candidates: tuple[DateAuditCandidate, ...]


def _fecha_a_date(valor: str) -> Optional[date]:
    try:
        return datetime.strptime(valor, "%d/%m/%Y").date()
    except (TypeError, ValueError):
        return None


def _contexto_secundario_alrededor(texto: str, inicio: int, fin: int) -> bool:
    """Detectar si una fecha pertenece a un campo que no es emisión.

    Se inspecciona contexto anterior y posterior porque algunos PDF extraen el
    valor antes de la etiqueta visual (``16/08/2026 Fecha Vencimiento CAE``).
    """

    antes = texto[max(0, inicio - 90):inicio].upper()
    despues = texto[fin:min(len(texto), fin + 70)].upper()

    # Cuando existe otra fecha previa, ignoramos etiquetas anteriores a ella:
    # suelen pertenecer al candidato anterior en layouts de columnas.
    previas = list(re.finditer(PATRON_FECHA, antes))
    if previas:
        antes = antes[previas[-1].end():]

    etiquetas_antes = (
        "INICIO DE ACTIVIDADES",
        "INICIO ACTIVIDADES",
        "INICIO ACTIV",
        "INICIO DE ACTIV",
        "FECHA DE INICIO",
        "VENCIMIENTO",
        "VENC",
        "VTO",
        "CAE",
        "ENTREGA",
        "PERIODO FACTURADO",
        "PERIODO DESDE",
        "PERIODO HASTA",
    )
    # Para el texto posterior solo consideramos etiquetas que estén pegadas al
    # valor. Una factura DBA puede extraerse como ``06/08/2026 Fecha: ...
    # INICIO ACTIV.: 01/04/2006``; la etiqueta del campo siguiente no debe
    # contaminar la fecha anterior.
    despues_cercano = despues[:40].lstrip(" :;.-")
    secundario_despues = bool(
        re.match(
            r"^(?:FECHA\s+)?(?:DE\s+)?(?:VTO|VENC|VENCIMIENTO|CAE|"
            r"INICIO\s+(?:DE\s+)?ACTIV|ENTREGA)\b",
            despues_cercano,
        )
    )

    return any(x in antes for x in etiquetas_antes) or secundario_despues


def _agregar_candidato(
    candidatos: list[DateAuditCandidate],
    texto: str,
    valor: str,
    *,
    score: int,
    reason: str,
    position: int,
    end_position: Optional[int] = None,
    reject_secondary: bool = True,
) -> None:
    fecha = _limpiar_fecha(valor)
    if not fecha:
        return

    fin = end_position if end_position is not None else position + len(valor)
    if reject_secondary and _contexto_secundario_alrededor(texto, position, fin):
        return

    candidatos.append(
        DateAuditCandidate(
            issue_date=fecha,
            score=score,
            reason=reason,
            position=position,
        )
    )


def _consolidar_candidatos(
    candidatos: list[DateAuditCandidate],
) -> tuple[DateAuditCandidate, ...]:
    """Combinar evidencias de la misma fecha sin sumar puntos sin límite."""

    agrupados: dict[str, list[DateAuditCandidate]] = {}
    for candidato in candidatos:
        agrupados.setdefault(candidato.issue_date, []).append(candidato)

    consolidados: list[DateAuditCandidate] = []
    for fecha, evidencias in agrupados.items():
        evidencias = sorted(evidencias, key=lambda c: c.score, reverse=True)
        mejor = evidencias[0]
        # Una segunda evidencia independiente refuerza levemente, pero nunca
        # convierte una señal débil en una señal inequívoca por repetición.
        bonus = min(8, max(0, len({e.reason for e in evidencias}) - 1) * 4)
        razones = "; ".join(dict.fromkeys(e.reason for e in evidencias))
        consolidados.append(
            DateAuditCandidate(
                issue_date=fecha,
                score=min(100, mejor.score + bonus),
                reason=razones,
                position=min(e.position for e in evidencias),
            )
        )

    return tuple(
        sorted(consolidados, key=lambda c: (-c.score, c.position, c.issue_date))
    )


def resolver_candidatos_fecha(
    candidatos: list[DateAuditCandidate] | tuple[DateAuditCandidate, ...],
    *,
    fecha_actual: Optional[str] = None,
    hoy: Optional[date] = None,
) -> DateAuditAnalysis:
    """Resolver candidatos de emisión con una política única y explicable.

    Esta función es el punto central de decisión para parser estricto y
    auditoría. Los números de ``score`` ordenan evidencia; no se interpretan
    como probabilidades ni se usan con umbrales arbitrarios de un punto.

    Política:
    - evidencia fuerte (>=96) puede corregir;
    - evidencia media que coincide con la fecha actual puede confirmarla;
    - una evidencia media que contradice el nombre nunca mueve por sí sola;
    - ``manual_review`` solo representa un conflicto real entre fechas
      plausibles, no la ausencia de una segunda confirmación;
    - la fecha actual nunca suma puntos por el hecho de estar en el nombre.
    """

    consolidados = _consolidar_candidatos(list(candidatos))
    if not consolidados:
        return DateAuditAnalysis(
            None,
            "none",
            "No se encontró evidencia estructurada de fecha de emisión.",
            (),
        )

    hoy = hoy or date.today()
    viables: list[DateAuditCandidate] = []
    for candidato in consolidados:
        parsed = _fecha_a_date(candidato.issue_date)
        if parsed is None or parsed > hoy:
            continue
        viables.append(candidato)

    if not viables:
        return DateAuditAnalysis(
            None,
            "none",
            "Los únicos candidatos encontrados son fechas futuras o inválidas.",
            consolidados,
        )

    actual = _limpiar_fecha(fecha_actual) if fecha_actual else None

    def es_fuerte(c: DateAuditCandidate) -> bool:
        # La fuerza depende del TIPO de evidencia, no de cruzar un umbral
        # numérico arbitrario. Algunas cabeceras digitales fiables (por
        # ejemplo DBA) producen score 94 porque la etiqueta queda después del
        # valor al aplanar el PDF, pero la relación Fecha + Nro + cabecera
        # fiscal sigue siendo estructuralmente fuerte.
        if c.score >= 96:
            return True
        return c.score >= 94 and (
            "cabecera fiscal" in c.reason.lower()
            or "identidad fiscal" in c.reason.lower()
        )

    fuertes = [c for c in viables if es_fuerte(c)]

    if fuertes:
        mejor = fuertes[0]
        rivales = [c for c in fuertes[1:] if c.issue_date != mejor.issue_date]
        if rivales and mejor.score - rivales[0].score < 5:
            return DateAuditAnalysis(
                None,
                "ambiguous",
                (
                    "Hay evidencia fuerte incompatible para más de una fecha "
                    "de emisión."
                ),
                consolidados,
            )
        return DateAuditAnalysis(
            mejor.issue_date,
            "high",
            f"{mejor.reason}; score {mejor.score}",
            consolidados,
        )

    # Sin evidencia fuerte, una coincidencia independiente con el nombre es
    # suficiente para DEJAR el archivo quieto. No necesitamos dos fuentes
    # independientes para probar que algo que no contradice al PDF está mal.
    if actual:
        actuales = [c for c in viables if c.issue_date == actual and c.score >= 66]
        if actuales:
            mejor_actual = actuales[0]
            rivales = [c for c in viables if c.issue_date != actual]
            rival = rivales[0] if rivales else None

            # Solo existe conflicto real si otra fecha independiente tiene una
            # fuerza comparable o superior. Una señal débil no transforma una
            # coincidencia válida en revisión manual.
            if rival is None or rival.score + 8 < mejor_actual.score:
                return DateAuditAnalysis(
                    actual,
                    "stable",
                    (
                        "La evidencia del PDF coincide con la fecha actual "
                        f"({mejor_actual.reason}; score {mejor_actual.score})."
                    ),
                    consolidados,
                )
            if rival.score < 88:
                return DateAuditAnalysis(
                    actual,
                    "stable",
                    (
                        "La fecha actual coincide con la mejor evidencia útil; "
                        "los candidatos alternativos son débiles."
                    ),
                    consolidados,
                )

            return DateAuditAnalysis(
                None,
                "ambiguous",
                (
                    f"Conflicto real: la fecha actual {actual} tiene evidencia "
                    f"score {mejor_actual.score}, pero {rival.issue_date} tiene "
                    f"score {rival.score}."
                ),
                consolidados,
            )

    # Una fecha media distinta de la actual no tiene autoridad para mover un
    # archivo organizado. Se expone como ambigua únicamente si realmente hay
    # una alternativa plausible; de lo contrario queda como evidencia
    # insuficiente sin generar una falsa alarma masiva.
    mejor = viables[0]
    segundo = next((c for c in viables[1:] if c.issue_date != mejor.issue_date), None)
    if segundo and segundo.score >= 80 and mejor.score - segundo.score < 10:
        return DateAuditAnalysis(
            None,
            "ambiguous",
            (
                f"Candidatos de fuerza similar: {mejor.issue_date} score "
                f"{mejor.score} y {segundo.issue_date} score {segundo.score}."
            ),
            consolidados,
        )

    return DateAuditAnalysis(
        mejor.issue_date,
        "medium",
        (
            f"Candidato probable {mejor.issue_date} ({mejor.reason}; score "
            f"{mejor.score}), insuficiente para corregir automáticamente."
        ),
        consolidados,
    )


def analizar_fecha_emision_para_auditoria(
    texto: str,
    *,
    fecha_actual: Optional[str] = None,
    hoy: Optional[date] = None,
) -> DateAuditAnalysis:
    """Analizar la fecha de emisión con evidencia y nivel de confianza.

    La auditoría es deliberadamente más estricta que el parser de ingreso.
    Reúne candidatos, descarta contextos secundarios y solo propone un cambio
    cuando existe evidencia fuerte e independiente de la fecha escrita en el
    nombre del archivo.

    Principios importantes
    ----------------------
    - ``FECHA DE EMISION`` explícita tiene prioridad máxima.
    - En el bloque ARCA aplanado se interpreta la semántica completa del
      bloque; nunca se toma ``FECHA DE VTO. PARA EL PAGO`` como emisión.
    - Una etiqueta genérica ``Fecha`` es evidencia media, no suficiente por sí
      sola para mover una factura ya organizada.
    - La fecha actual del nombre solo aporta estabilidad; nunca se usa como
      prueba de que una fecha alternativa es incorrecta.
    - Las fechas futuras quedan visibles para diagnóstico, pero jamás provocan
      una reparación automática.
    """

    texto = normalizar_para_busqueda(texto)
    if not texto:
        return DateAuditAnalysis(None, "none", "PDF sin texto digital utilizable.", ())

    candidatos: list[DateAuditCandidate] = []

    # 1) Etiquetas explícitas de emisión: evidencia inequívoca.
    for etiqueta in (
        r"FECHA\s+DE\s+EMISION",
        r"FECHA\s+EMISION",
        r"FECHA\s+DEL\s+COMPROBANTE",
        r"FECHA\s+DEL\s+DOCUMENTO",
    ):
        for m in re.finditer(rf"\b{etiqueta}\b\s*[:\-]?\s*{PATRON_FECHA}", texto):
            _agregar_candidato(
                candidatos,
                texto,
                m.group(1),
                score=100,
                reason="etiqueta explícita de fecha de emisión",
                position=m.start(1),
                end_position=m.end(1),
                reject_secondary=False,
            )

    # 1b) Escaneos / layouts legacy: OCR puede separar día, mes y año con
    # espacios. Solo se acepta cuando la etiqueta FECHA está explícitamente
    # pegada al valor; vencimientos siguen vetados por contexto.
    for m in re.finditer(
        r"\bFECHA\b\s*[:;,.-]?\s*(\d{1,2})\s+(\d{1,2})\s+(\d{2}|\d{4})\b",
        texto,
    ):
        valor = "/".join(m.groups())
        _agregar_candidato(
            candidatos,
            texto,
            valor,
            score=98,
            reason="etiqueta Fecha explícita con fecha espaciada (OCR/legacy)",
            position=m.start(1),
            end_position=m.end(3),
            reject_secondary=False,
        )

    # 2) ARCA / comprobantes electrónicos: al extraer columnas, pypdf suele
    # producir primero todas las etiquetas y luego los cuatro valores:
    #
    #   FECHA DE EMISION: ORIGINAL
    #   PERIODO FACTURADO DESDE: HASTA: FECHA DE VTO. PARA EL PAGO:
    #   emision desde hasta vencimiento
    #
    # La versión histórica elegía por posición genérica y llegó a confundir el
    # cuarto valor (vencimiento) con la fecha de emisión. Aquí se reconoce el
    # bloque completo y se toma exclusivamente el primer valor como emisión.
    patron_arca = (
        r"FECHA\s+DE\s+EMISION\s*:\s*ORIGINAL.{0,260}?"
        r"PERIODO\s+FACTURADO\s+DESDE\s*:.{0,120}?"
        r"HASTA\s*:.{0,120}?"
        r"FECHA\s+DE\s+VTO\.?\s+PARA\s+EL\s+PAGO\s*:.{0,600}?"
        rf"{PATRON_FECHA}\s+{PATRON_FECHA}\s+{PATRON_FECHA}\s+{PATRON_FECHA}"
    )
    for m in re.finditer(patron_arca, texto):
        _agregar_candidato(
            candidatos,
            texto,
            m.group(1),
            score=80,
            reason="bloque ARCA aplanado: orden textual no confiable sin geometría",
            position=m.start(1),
            end_position=m.end(1),
            reject_secondary=False,
        )

    # 3) Cabecera ARCA/ERP con código de comprobante, fecha y número. DBA y
    # otros emisores exponen la cabecera digital como:
    #
    #   COD. 01 06/08/2026 FECHA: NRO: 00013-00189814
    #
    # La combinación de código + fecha + etiqueta + número es mucho más fuerte
    # que una fecha aislada cercana al título FACTURA.
    for m in re.finditer(
        rf"\bCOD\.?\s*\d{{1,3}}\s+{PATRON_FECHA}\s+FECHA\s*:\s*"
        r"(?:NRO|NUMERO|COMP\.?\s*NRO)\.?\s*:\s*\d{1,5}\s*[-/]\s*\d{1,8}\b",
        texto,
    ):
        _agregar_candidato(
            candidatos,
            texto,
            m.group(1),
            score=100,
            reason="cabecera fiscal COD + Fecha + Nro de comprobante",
            position=m.start(1),
            end_position=m.end(1),
            reject_secondary=False,
        )

    # 4) Identidad fiscal completa seguida por una fecha espaciada. Esta forma
    # aparece en layouts legacy y constituye una relación estructural fuerte.
    for m in re.finditer(
        r"\b[ABC]\s*\d{4,5}\s*[- ]\s*\d{8}\s+"
        r"(\d{1,2})\s+(\d{1,2})\s+(\d{2}|\d{4})\b",
        texto,
    ):
        fecha = _limpiar_fecha("/".join(m.groups()))
        if fecha:
            candidatos.append(
                DateAuditCandidate(
                    issue_date=fecha,
                    score=96,
                    reason="fecha estructural después de identidad fiscal",
                    position=m.start(1),
                )
            )

    # 4) Algunos PDF (DBA entre ellos) extraen el valor antes de ``Fecha:``.
    # Una etiqueta genérica no basta para mover. Solo se vuelve evidencia alta
    # si en la misma ventana de cabecera existe estructura fiscal principal.
    for m in re.finditer(
        rf"{PATRON_FECHA}(?=.{{0,35}}?\bFECHA\b(?!\s*(?:DE\s+)?(?:VTO|VENC|VENCIMIENTO|CAE)))",
        texto,
    ):
        inicio = m.start(1)
        fin = m.end(1)
        if _contexto_secundario_alrededor(texto, inicio, fin):
            continue
        ventana = texto[max(0, inicio - 180):min(len(texto), fin + 240)]
        soporte_fiscal = bool(
            re.search(r"\b(?:FACTURA|NOTA\s+DE\s+(?:CREDITO|DEBITO))\b", ventana)
            or re.search(r"\b(?:NRO|NUMERO|COMP\.?\s*NRO)\.?\s*[:\-]?\s*\d{1,5}\s*[-/]\s*\d{1,8}\b", ventana)
            or re.search(r"\b[ABC]\s*\d{1,5}\s*[-/]\s*\d{1,8}\b", ventana)
        )
        _agregar_candidato(
            candidatos,
            texto,
            m.group(1),
            score=94 if soporte_fiscal else 70,
            reason=(
                "fecha antes de etiqueta Fecha dentro de cabecera fiscal"
                if soporte_fiscal
                else "fecha antes de etiqueta genérica Fecha"
            ),
            position=inicio,
            end_position=fin,
        )

    # 5) ``Fecha: valor`` es deliberadamente media. Puede representar emisión,
    # vencimiento u otro dato según el emisor. Solo sube de peso cuando la
    # cabecera fiscal principal está inmediatamente alrededor.
    for m in re.finditer(rf"\bFECHA\b\s*[:\-]?\s*{PATRON_FECHA}", texto):
        inicio = m.start(1)
        fin = m.end(1)
        if _contexto_secundario_alrededor(texto, inicio, fin):
            continue
        ventana = texto[max(0, m.start() - 160):min(len(texto), fin + 180)]
        soporte_fiscal = bool(
            re.search(r"\b(?:FACTURA|NOTA\s+DE\s+(?:CREDITO|DEBITO))\b", ventana)
            and re.search(r"\b\d{1,5}\s*[-/]\s*\d{1,8}\b", ventana)
        )
        _agregar_candidato(
            candidatos,
            texto,
            m.group(1),
            score=88 if soporte_fiscal else 66,
            reason=(
                "etiqueta Fecha dentro de cabecera fiscal"
                if soporte_fiscal
                else "etiqueta genérica Fecha"
            ),
            position=inicio,
            end_position=fin,
        )

    # 6) Fecha inmediatamente antes del título fiscal: señal útil pero no
    # inequívoca, por lo que no basta sola para una reparación automática.
    for m in re.finditer(
        rf"{PATRON_FECHA}(?=.{{0,70}}?\b(?:FACTURA|NOTA\s+DE\s+(?:CREDITO|DEBITO))\b)",
        texto,
    ):
        _agregar_candidato(
            candidatos,
            texto,
            m.group(1),
            score=84,
            reason="fecha próxima al título fiscal",
            position=m.start(1),
            end_position=m.end(1),
        )

    # La fecha escrita en el nombre NO se agrega como candidato. Hacerlo
    # convertiría el estado actual del archivo en evidencia circular. La fecha
    # del nombre se usa únicamente al final para comparar contra la evidencia
    # extraída independientemente del PDF.
    return resolver_candidatos_fecha(
        candidatos,
        fecha_actual=fecha_actual,
        hoy=hoy,
    )

def detectar_fecha_emision_para_auditoria(
    texto: str,
    *,
    fecha_actual: Optional[str] = None,
) -> Optional[str]:
    """Compatibilidad: devolver solo fechas de auditoría confiables/estables."""

    analisis = analizar_fecha_emision_para_auditoria(
        texto,
        fecha_actual=fecha_actual,
    )
    return analisis.issue_date


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
            return _reparar_anio_por_vencimiento(fecha, texto)

    # ERP legacy: la capa de texto puede omitir la palabra FECHA y dejar el
    # valor inmediatamente después de ``FACTURA 0056 - 00562701``. La
    # numeración fiscal aporta el contexto necesario para interpretar esos tres
    # grupos como día, mes y año.
    legacy_factura = re.search(
        r"\bFACTURA\s+\d{1,5}\s*[-/]\s*\d{1,8}.{0,80}?"
        r"(\d{1,2})\s+(\d{1,2})\s+(\d{4})\b",
        texto,
    )
    if legacy_factura:
        fecha = _limpiar_fecha("/".join(legacy_factura.groups()))
        if fecha:
            return _reparar_anio_por_vencimiento(fecha, texto)

    # Algunos PDF digitales (incluido el layout de DBA) exponen el valor antes
    # de la etiqueta visual, por ejemplo ``06/08/2026 Fecha:``. Esta evidencia
    # es más fuerte que una fecha genérica posterior como ``INICIO ACTIV.:
    # 01/04/2006`` y por eso se evalúa antes de los fallbacks amplios.
    before_fecha_formateada = re.search(
        rf"{PATRON_FECHA}(?=.{{0,40}}?\bFECHA\b)",
        texto,
    )
    if before_fecha_formateada and not _contexto_excluido(
        texto, before_fecha_formateada.start(1)
    ):
        fecha = _limpiar_fecha(before_fecha_formateada.group(1))
        if fecha:
            return _reparar_anio_por_vencimiento(fecha, texto)

    # En OCR de comprobantes escaneados el orden visual puede invertirse y la
    # fecha quedar inmediatamente antes de la etiqueta FECHA. Se admite solo
    # una fecha válida dentro de una ventana pequeña.
    before_fecha = re.search(
        r"(\d{1,2})\s+(\d{1,2})\s+(\d{4})(?=.{0,40}?\bFECHA\b)",
        texto,
    )
    if before_fecha:
        fecha = _limpiar_fecha("/".join(before_fecha.groups()))
        if fecha:
            return _reparar_anio_por_vencimiento(fecha, texto)

    # Algunos comprobantes antiguos separan día, mes y año únicamente con
    # espacios (por ejemplo ``FECHA: 08 07 25``). Esta variante se admite solo
    # junto a la etiqueta FECHA para no convertir importes o códigos en fechas.
    fecha_espaciada = re.search(
        r"\bFECHA\b\s*[:;,.\-]?\s*(\d{1,2})\s+(\d{1,2})\s+(\d{2}|\d{4})\b",
        texto,
    )
    if fecha_espaciada:
        dia, mes, anio = fecha_espaciada.groups()
        valor = f"{dia}/{mes}/{anio}"
        fecha = _limpiar_fecha(valor)
        if fecha:
            return _reparar_anio_por_vencimiento(fecha, texto)

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
            return _reparar_anio_por_vencimiento(fecha, texto)

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
            return _reparar_anio_por_vencimiento(fecha, texto)

    # Etiquetas inequívocas tienen prioridad absoluta.
    for etiqueta in (r"FECHA\s+DE\s+EMISION", r"FECHA\s+EMISION", r"FECHA\s+DEL\s+COMPROBANTE"):
        coincidencia = re.search(rf"\b{etiqueta}\b\s*[:\-]?\s*{PATRON_FECHA}", texto)
        if coincidencia:
            fecha = _limpiar_fecha(coincidencia.group(1))
            if fecha:
                return _reparar_anio_por_vencimiento(fecha, texto)

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
            return _reparar_anio_por_vencimiento(fecha, texto)

    # ``Fecha:`` es ambiguo. Solo se acepta si el contexto inmediato no habla
    # de vencimiento, CAE, entrega o inicio de actividades.
    for coincidencia in re.finditer(rf"\bFECHA\b\s*[:\-]?\s*{PATRON_FECHA}", texto):
        if _contexto_excluido(texto, coincidencia.start(1)):
            continue
        fecha = _limpiar_fecha(coincidencia.group(1))
        if fecha:
            return _reparar_anio_por_vencimiento(fecha, texto)

    if contexto_fiscal_confirmado or detectar_tipo_comprobante(texto):
        for coincidencia in re.finditer(PATRON_FECHA, texto):
            if _contexto_excluido(texto, coincidencia.start(1)):
                continue
            fecha = _limpiar_fecha(coincidencia.group(1))
            if fecha:
                return _reparar_anio_por_vencimiento(fecha, texto)

        # No hacemos una búsqueda genérica sobre una copia sin espacios.
        # Al compactar se pierde el contexto semántico que permite distinguir
        # fecha de emisión de Inicio de Actividad, vencimiento o CAE. Los
        # layouts carácter-por-caracter ya están cubiertos arriba por la regla
        # estructural fuerte de identidad fiscal + fecha.
    return None
