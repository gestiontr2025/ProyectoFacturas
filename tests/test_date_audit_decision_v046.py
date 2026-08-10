"""Regresiones de la política única de decisión de fechas v0.46."""

from fiscal.issue_date import DateAuditCandidate, resolver_candidatos_fecha


def c(fecha, score, reason):
    return DateAuditCandidate(fecha, score, reason, 0)


def test_coincidencia_media_con_fecha_actual_no_es_manual_review():
    result = resolver_candidatos_fecha(
        [c("09/02/2026", 91, "geometría: etiqueta Fecha dentro de cabecera fiscal")],
        fecha_actual="09/02/2026",
    )
    assert result.issue_date == "09/02/2026"
    assert result.confidence == "stable"


def test_fecha_actual_no_recibe_puntos_por_existir_en_nombre():
    result = resolver_candidatos_fecha(
        [c("05/08/2026", 100, "geometría: fecha en la misma fila que etiqueta explícita de emisión")],
        fecha_actual="03/08/2026",
    )
    assert result.issue_date == "05/08/2026"
    assert result.confidence == "high"


def test_evidencia_media_distinta_no_mueve_automaticamente():
    result = resolver_candidatos_fecha(
        [c("12/03/2026", 91, "geometría: etiqueta Fecha dentro de cabecera fiscal")],
        fecha_actual="02/03/2026",
    )
    assert result.issue_date == "12/03/2026"
    assert result.confidence == "medium"


def test_conflicto_real_entre_fechas_medias_queda_ambiguo():
    result = resolver_candidatos_fecha(
        [
            c("02/03/2026", 91, "geometría: etiqueta Fecha dentro de cabecera fiscal"),
            c("03/03/2026", 90, "otra evidencia geométrica comparable"),
        ],
        fecha_actual="02/03/2026",
    )
    assert result.issue_date is None
    assert result.confidence == "ambiguous"
