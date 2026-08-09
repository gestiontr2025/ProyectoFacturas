"""Regresiones para PDFs escaneados cuando el OCR no está disponible."""

from pathlib import Path

import config
import pdf_reader
from app.pending_reprocessor import reprocesar_pendientes


def test_describir_fallo_ocr_tesseract_no_configurado():
    mensaje = pdf_reader.describir_fallo_ocr({
        "ocr_estado": "tesseract_no_configurado",
        "ocr_error": "sin tessdata",
    })
    assert "OCR no disponible" in mensaje
    assert "_Pendientes" in mensaje


def test_reprocesador_no_archiva_pdf_sin_texto_si_ocr_falla(tmp_path, monkeypatch):
    pending = tmp_path / "_Pendientes"
    pending.mkdir()
    pdf = pending / "CCF_000480.pdf"
    pdf.write_bytes(b"fake scanned pdf")

    monkeypatch.setattr(config, "SAVE_FOLDER", tmp_path)
    monkeypatch.setattr(
        pdf_reader,
        "leer_pdf",
        lambda ruta: {
            "ruta": Path(ruta),
            "nombre": Path(ruta).name,
            "contiene_texto": False,
            "texto_completo": "",
            "ocr_utilizado": False,
            "ocr_estado": "tesseract_no_configurado",
            "ocr_error": "No se encontró tessdata",
        },
    )

    resultados = reprocesar_pendientes()

    assert len(resultados) == 1
    assert resultados[0]["estado"] == "pendiente"
    assert resultados[0]["categoria"] == "desconocido"
    assert resultados[0]["ruta_final"] == pdf
    assert pdf.exists()
    assert not (tmp_path / "_OtrosDocumentos").exists()
