import pdf_reader


def test_scoring_ocr_prefiere_cuit_valido_y_cabecera_completa():
    bad = """FACTURA B
Punto de venta 00007 Comprobante 00001842
Fecha: 06/08/2026
ARCHERON HERMANAS S.R.L.
CUIT emisor: 30-70908877-4
"""
    good = """FACTURA B
Punto de venta 00007 Comprobante 00001842
Fecha: 06/08/2026
ARCHERON HERMANAS S.R.L.
CUIT emisor: 30-70998877-4
"""
    assert pdf_reader._puntuar_calidad_ocr(good) > pdf_reader._puntuar_calidad_ocr(bad)


def test_scoring_ocr_prefiere_nota_debito_con_letra_recuperada():
    without_letter = """NOTA DE DEBITO
EVENTOS MANON
CUIT 27-29887766-5
Fecha: 09/08/2026
Numero del comprobante
00015-00000333
"""
    with_letter = """EVENTOS MANON
CUIT 27-29887766-5
NOTA DE DEBITO B
Fecha: 09/08/2026
Numero del comprobante
00015-00000333
"""
    assert pdf_reader._puntuar_calidad_ocr(with_letter) > pdf_reader._puntuar_calidad_ocr(without_letter)


def test_selector_ocr_conserva_metodo_del_mejor_candidato():
    bad = "FACTURA B\nCUIT emisor: 30-70908877-4\n00007-00001842"
    good = "FACTURA B\nARCHERON HERMANAS S.R.L.\nCUIT emisor: 30-70998877-4\nFecha: 06/08/2026\n00007-00001842"
    method, text, score = pdf_reader._seleccionar_mejor_ocr([
        ("tesseract_cli_psm3", bad),
        ("tesseract_cli_psm11", good),
    ])
    assert method == "tesseract_cli_psm11"
    assert text == good
    assert score == pdf_reader._puntuar_calidad_ocr(good)


def test_multapas_declara_segmentaciones_complementarias(monkeypatch):
    seen = []

    class FakePixmap:
        def save(self, _path):
            return None

    class FakePage:
        def get_pixmap(self, *, dpi, alpha):
            assert dpi == 300
            assert alpha is False
            return FakePixmap()

    def fake(_image_path, _exe, *, psm):
        seen.append(psm)
        return f"ocr-{psm}"

    monkeypatch.setattr(pdf_reader, "_ejecutar_tesseract_sobre_imagen", fake)
    monkeypatch.setattr(pdf_reader, "_ocr_tiene_evidencia_suficiente", lambda _text: False)
    candidates = pdf_reader._ocr_multapas_tesseract(FakePage(), "tesseract")
    assert seen == [3, 11, 4, 6, 12]
    assert [method for method, _text in candidates] == [
        "tesseract_cli_psm3",
        "tesseract_cli_psm11",
        "tesseract_cli_psm4",
        "tesseract_cli_psm6",
        "tesseract_cli_psm12",
    ]
