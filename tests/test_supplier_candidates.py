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


def test_proveedor_nuevo_se_detecta_genericamente_por_cuit_y_encabezado():
    texto = """
    Fecha de Emisión:
    ORIGINAL
    CORVALAN ARIEL ANDRES
    Olleros 1363 - La Tablada, Buenos Aires
    CUIT:
    03/08/2026
    20290392781
    30718347463 MADERO ROOF TOP S. A.
    Punto de Venta: Comp. Nro:00001 00002165
    Razón Social:
    ESTABLECIMIENTOS CORVALAN
    FACTURA A COD. 01
    IVA Responsable Inscripto
    20-29039278-1
    Código Producto / Servicio Cantidad U. medida
    """
    result = detectar_emisor_no_recurrente(texto, "20-29039278-1")
    assert result is not None
    assert result["razon_social_canonica"] == "CORVALAN ARIEL ANDRES"
    assert result["cuit_canonico"] == "20-29039278-1"
    assert result["metodo_deteccion"] == "encabezado_fiscal_generico_no_persistente"


def test_detector_generico_no_confunde_al_receptor_con_proveedor():
    texto = """
    ORIGINAL
    MADERO ROOF TOP S. A.
    CUIT 30-71834746-3
    FACTURA A 00001-00000001
    """
    assert detectar_emisor_no_recurrente(texto, "30-71834746-3") is None


def test_detector_generico_rechaza_varios_cuits_terceros_ambiguos():
    texto = """
    ORIGINAL
    PROVEEDOR SIN IDENTIDAD CLARA
    CUIT 20-29039278-1
    CUIT 30-63779923-8
    MADERO ROOF TOP S. A. CUIT 30-71834746-3
    FACTURA A 00001-00000001
    """
    assert detectar_emisor_no_recurrente(texto, None) is None


def test_proveedor_nuevo_puede_aparecer_despues_del_cliente_y_del_detalle():
    texto = """
    ORIGINAL
    CLIENTE
    Razón Social: MADERO ROOF TOP S. A.
    CUIT: 30-71834746-3
    Descripción Cantidad Precio unit. Subtotal
    SERVICIO DE PRUEBA BETA 1.00 42000.00 42000.00
    SERVICIOS BETA DE MARTIN PEREZ
    Razón Social: PEREZ MARTIN ALEJANDRO
    Nombre de fantasía: SERVICIOS BETA
    CUIT: 20-34567890-6
    FACTURA B
    Punto de Venta: 00007
    Comp. Nro: 00000321
    Fecha de Emisión: 06/08/2026
    IVA 21%: 9450.00
    """
    result = detectar_emisor_no_recurrente(texto, None)
    assert result is not None
    assert result["razon_social_canonica"] == "PEREZ MARTIN ALEJANDRO"
    assert result["cuit_canonico"] == "20-34567890-6"
    assert "razon_social_explicita_en_misma_linea" in result["evidencias"]


def test_proveedor_nuevo_vincula_cuit_y_razon_social_separados():
    texto = """
    ORIGINAL
    FACTURA A
    Fecha de Emisión: 07/08/2026
    Punto de Venta: 00023
    Comp. Nro: 00004567
    Receptor CUIT: 30-71834746-3
    Receptor: MADERO ROOF TOP S. A.
    Descripción Cantidad Precio unit. Subtotal
    PRODUCTO GAMMA TEST 3.00 8500.00 25500.00
    CUIT emisor: 33-76543210-9
    Ingresos Brutos: 33-76543210-9
    Inicio de actividades: 01/01/2020
    INSUMOS GAMMA S.A.S.
    Razón Social: INSUMOS GAMMA S.A.S.
    Domicilio Comercial: Avenida Simulada 456 - Buenos Aires
    IVA 21%: 5880.00
    """
    result = detectar_emisor_no_recurrente(texto, None)
    assert result is not None
    assert result["razon_social_canonica"] == "INSUMOS GAMMA S.A.S"
    assert result["cuit_canonico"] == "33-76543210-9"
    assert "cuit_etiquetado_como_emisor" in result["evidencias"]


def test_scoring_conserva_evidencias_que_explican_la_decision():
    texto = """
    ORIGINAL
    PROVEEDOR PRUEBA ALFA S.R.L.
    Razón Social: PROVEEDOR PRUEBA ALFA S.R.L.
    CUIT: 30-71234567-1
    Domicilio Comercial: Calle Ficticia 100 - CABA
    A FACTURA COD. 01
    Punto de Venta: 00011
    Comp. Nro: 00000001
    Fecha de Emisión: 05/08/2026
    CUIT receptor: 30-71834746-3
    MADERO ROOF TOP S. A.
    """
    result = detectar_emisor_no_recurrente(texto, None)
    assert result is not None
    assert result["puntaje"] >= 18
    assert "cuit_valido_distinto_del_receptor" in result["evidencias"]
    assert "inmediatamente_despues_de_marca_de_copia" in result["evidencias"]
