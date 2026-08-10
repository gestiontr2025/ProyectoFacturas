"""Regresiones del OCR adaptativo orientadas a evitar trabajo redundante."""

import subprocess

import pdf_reader


def test_tesseract_cli_timeout_devuelve_texto_vacio(monkeypatch, tmp_path):
    image = tmp_path / "page.png"
    image.write_bytes(b"fake")

    def fake_run(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd="tesseract", timeout=25)

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert pdf_reader._ejecutar_tesseract_sobre_imagen(
        image,
        "tesseract",
        psm=3,
    ) == ""


def test_ocr_no_lanza_multipasada_si_pymupdf_ya_es_suficiente(monkeypatch, tmp_path):
    pdf = tmp_path / "factura.pdf"
    pdf.write_bytes(b"%PDF-fake")

    texto_suficiente = (
        "FACTURA B\n"
        "ARCHERON HERMANAS S.R.L.\n"
        "CUIT EMISOR: 30-70998877-4\n"
        "FECHA: 06/08/2026\n"
        "00007-00001842"
    )

    class FakePage:
        def get_textpage_ocr(self, **_kwargs):
            return object()

        def get_text(self, _mode, *, textpage):
            assert textpage is not None
            return texto_suficiente

    class FakeDocument:
        def __len__(self):
            return 1

        def __getitem__(self, index):
            assert index == 0
            return FakePage()

        def close(self):
            return None

    monkeypatch.setattr(pdf_reader, "_resolver_tessdata", lambda: tmp_path)
    monkeypatch.setattr(pdf_reader.pymupdf, "open", lambda _path: FakeDocument())
    monkeypatch.setattr(
        pdf_reader,
        "_ocr_tiene_evidencia_suficiente",
        lambda text: text == texto_suficiente,
    )

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("El OCR multipasada no debía ejecutarse")

    monkeypatch.setattr(pdf_reader, "_ocr_multapas_tesseract", fail_if_called)

    result = pdf_reader._extraer_texto_ocr(pdf, 1)

    assert result["estado"] == "ocr_ok"
    assert result["paginas"][0]["texto"] == texto_suficiente
    assert result["paginas"][0]["metodo_ocr"] == "pymupdf_tesseract"
