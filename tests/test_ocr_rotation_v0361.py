from pathlib import Path

import pdf_reader


def test_rotated_passes_are_added_when_horizontal_ocr_is_insufficient(monkeypatch):
    seen_paths = []

    class FakePixmap:
        def save(self, path):
            Path(path).write_bytes(b"fake")

    class FakePage:
        def get_pixmap(self, **kwargs):
            return FakePixmap()

    def fake_tesseract(image_path, _exe, *, psm):
        seen_paths.append((Path(image_path).name, psm))
        if "rot90" in Path(image_path).name and psm == 6:
            return "EVENTOS MANON\nCUIT 27-29887766-5"
        return "NOTA DE DEBITO B\n00015-00000333"

    monkeypatch.setattr(pdf_reader, "_ejecutar_tesseract_sobre_imagen", fake_tesseract)
    monkeypatch.setattr(pdf_reader, "_ocr_tiene_evidencia_suficiente", lambda _text: False)

    candidates = pdf_reader._ocr_multapas_tesseract(FakePage(), "tesseract")
    methods = [method for method, _ in candidates]

    assert "tesseract_cli_rot90_psm6" in methods
    assert any(name == "page_rot270.png" for name, _ in seen_paths)


def test_diagnostic_candidates_include_method_score_and_text(monkeypatch, tmp_path):
    # Exercise the serialization shape independently from Tesseract itself.
    sample = [("m1", "FACTURA A\n00001-00000001"), ("m2", "PROVEEDOR SA\nCUIT 30-12345678-3")]
    evaluated = [
        {"metodo": method, "puntaje": pdf_reader._puntuar_calidad_ocr(text), "texto": text}
        for method, text in sample
    ]
    assert all(set(item) == {"metodo", "puntaje", "texto"} for item in evaluated)
