import json

from suppliers.ad_hoc import detectar_emisor_no_recurrente
from suppliers.candidates import registrar_proveedor_ocasional


def test_ceamse_se_detecta_por_cuit_aunque_el_nombre_sea_dificil():
    result = detectar_emisor_no_recurrente(
        "FACTURA A 0155-00048850",
        "30-57720719-0",
    )
    assert result is not None
    assert result["razon_social_canonica"].startswith("COORDINACION ECOLOGICA")


def test_herrajes_san_martin_se_detecta_por_encabezado():
    result = detectar_emisor_no_recurrente(
        "HERRAJES SAN MARTIN FACTURA B 00021-00001477",
        "30-51561183-1",
    )
    assert result is not None
    assert result["cuit_canonico"] == "30-51561183-1"


def test_registro_de_candidato_no_cuenta_dos_veces_el_mismo_documento(tmp_path):
    path = tmp_path / "candidates.json"
    first = registrar_proveedor_ocasional(
        cuit="30-51561183-1",
        business_name="HERRAJES SAN MARTIN",
        document_key="08/07/2025|FACTURA|B|00021-00001477",
        folder_name="HERRAJES_SAN_MARTIN",
        path=path,
    )
    second = registrar_proveedor_ocasional(
        cuit="30-51561183-1",
        business_name="HERRAJES SAN MARTIN",
        document_key="08/07/2025|FACTURA|B|00021-00001477",
        folder_name="HERRAJES_SAN_MARTIN",
        path=path,
    )
    data = json.loads(path.read_text(encoding="utf-8"))
    assert first["registered"] is True
    assert second["reason"] == "already_registered"
    assert data["candidates"]["30515611831"]["occurrences"] == 1


def test_tercera_aparicion_sugiere_revision_del_catalogo(tmp_path):
    path = tmp_path / "candidates.json"
    for number in ("1", "2", "3"):
        result = registrar_proveedor_ocasional(
            cuit="30-51561183-1",
            business_name="HERRAJES SAN MARTIN",
            document_key=number,
            folder_name="HERRAJES_SAN_MARTIN",
            path=path,
        )
    assert result["record"]["occurrences"] == 3
    assert result["record"]["suggest_catalog_review"] is True


def test_herrajes_se_detecta_por_nombre_validado_si_el_pdf_pierde_el_encabezado():
    result = detectar_emisor_no_recurrente(
        "FACTURA B 00021-00001477",
        "0",
        "#1026 FACB0002100001477.pdf",
    )
    assert result is not None
    assert result["razon_social_canonica"] == "HERRAJES SAN MARTIN"


def test_fecha_espaciada_del_comprobante_antiguo_tiene_prioridad_sobre_vencimiento():
    from fiscal.issue_date import detectar_fecha_emision

    # Reproduce la capa de texto real de Herrajes San Martín. La fecha de
    # emisión no trae etiqueta; aparece inmediatamente después de la identidad
    # fiscal. El 18/07/2025 es solamente el vencimiento del CAE.
    text = (
        "F A C T U R A B 00021-00001477 08 07 25 006 "
        "SANTIAGO SCAVUZZO CAE 75271643145619 F.VTO: 18/07/2025"
    )
    assert detectar_fecha_emision(text, contexto_fiscal_confirmado=True) == "08/07/2025"


def test_fecha_validada_del_archivo_herrajes():
    from invoices.validated_file_overrides import get_validated_issue_date
    assert get_validated_issue_date("#1026 FACB0002100001477.pdf") == "08/07/2025"


def test_ceamse_se_detecta_aunque_el_parser_haya_tomado_el_cuit_del_receptor():
    texto = (
        "MADERO ROOF TOP S.A. CUIT 30-71834746-3 "
        "FACTURA A 0155-00048850 CUIT 30-57720719-0 "
        "CHEQUES A ORDEN: COORDINACION ECOLOGICA AREA METROPOLITANA S.E."
    )
    result = detectar_emisor_no_recurrente(
        texto,
        "30-71834746-3",
        "48850 (2).pdf",
    )
    assert result is not None
    assert result["cuit_canonico"] == "30-57720719-0"
    assert result["razon_social_canonica"] == (
        "COORDINACION ECOLOGICA AREA METROPOLITANA S.E."
    )
