from fiscal.number import detectar_numero_comprobante
from suppliers.issuer_identity import extraer_identidad_emisor


def test_archeron_detecta_emisor_inmediatamente_antes_de_cuit_emisor():
    text = """B
FACTURA B
Punto de venta 00007     Comprobante 00001842
RECEPTOR
MADERO ROOF TOP S.A.
CUIT 30-71583474-6
ARCHERON HERMANAS S.R.L.
CUIT emisor: 30-70998877-4
IVA Responsable Inscripto
"""
    identity = extraer_identidad_emisor(text)
    assert identity is not None
    assert identity.legal_name == "ARCHERON HERMANAS S.R.L"
    assert identity.cuit == "30-70998877-4"


def test_kaisa_no_incluye_prefijo_documental_en_razon_social():
    text = """NOTA DE CREDITO
A
NOTA DE CREDITO CONSTRUCCIONES KAISA S.A.
CUIT 30-71223344-9
IVA Responsable Inscripto
NUMERO DE ESTA NOTA DE CREDITO
00009-00000128
Fecha de emision: 08/08/2026
Cliente: MADERO ROOF TOP S.A. - CUIT 30-71583474-6
"""
    identity = extraer_identidad_emisor(text)
    assert identity is not None
    assert identity.legal_name == "CONSTRUCCIONES KAISA S.A"


def test_eventos_manon_detecta_nombre_antes_de_cuit_sin_etiqueta_razon_social():
    text = """EVENTOS MANON
CUIT 27-29887766-5
NOTA DE DEBITO
B
Fecha: 09/08/2026
Numero del comprobante
00015-00000333
RECEPTOR
MADERO ROOF TOP S.A. - 30-71583474-6
"""
    identity = extraer_identidad_emisor(text)
    assert identity is not None
    assert identity.legal_name == "EVENTOS MANON"
    assert identity.cuit == "27-29887766-5"


def test_numero_factura_con_punto_venta_y_comprobante_separados():
    text = "FACTURA B Punto de venta 00007 Comprobante 00001842"
    assert detectar_numero_comprobante(text) == "00007-00001842"


def test_numero_nota_debito_no_confunde_fecha_con_comprobante():
    text = """NOTA DE DEBITO
B
Fecha: 09/08/2026
Numero del comprobante
00015-00000333
"""
    assert detectar_numero_comprobante(text) == "00015-00000333"


def test_rescate_ocr_completa_proveedor_omitido_por_capa_digital(monkeypatch, tmp_path):
    import invoices.processor as processor
    import supplier_detector

    path = tmp_path / "kaisa_parcial.pdf"
    path.write_bytes(b"%PDF-1.4\n% synthetic placeholder\n")

    digital = """NOTA DE CREDITO
A
CUIT 30-71223344-9
NUMERO DE ESTA NOTA DE CREDITO
00009-00000128
Fecha de emision: 08/08/2026
Cliente: MADERO ROOF TOP S.A. - CUIT 30-71834746-3
IVA 21% 4.200,00
TOTAL CREDITO 24.200,00
"""
    ocr = """NOTA DE CREDITO A
CONSTRUCCIONES KAISA S.A.
CUIT 30-71223344-9
00009-00000128
Fecha de emision: 08/08/2026
Cliente: MADERO ROOF TOP S.A. - CUIT 30-71834746-3
"""

    monkeypatch.setattr(
        processor.pdf_reader,
        "extraer_texto_ocr_forzado",
        lambda _path: {"texto_completo": ocr, "estado": "ocr_ok", "error": None},
    )
    monkeypatch.setattr(
        processor,
        "mover_a_destino_final",
        lambda _origen, carpeta, nombre: carpeta / nombre,
    )
    monkeypatch.setattr(processor, "registrar_proveedor_ocasional", lambda **_kwargs: None)

    proveedor_inicial = supplier_detector.detectar_proveedor(digital)
    result = processor.procesar_factura(path, digital, proveedor_inicial, tmp_path / "Facturas")

    assert result.organizada is True
    assert result.proveedor is not None
    assert result.proveedor.legal_name == "CONSTRUCCIONES KAISA S.A"
    assert result.datos_factura.numero_comprobante == "00009-00000128"
