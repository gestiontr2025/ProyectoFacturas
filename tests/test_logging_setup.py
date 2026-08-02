"""Pruebas del sistema de logging.

Estas pruebas verifican comportamiento observable: creación del archivo,
escritura UTF-8 y rechazo de configuraciones inválidas.
"""

import logging

import pytest

from infrastructure.logging_setup import configure_logging


def test_configure_logging_creates_daily_file(tmp_path):
    log_file = configure_logging(tmp_path, "INFO")

    logging.getLogger("tests").info("Factura organizada correctamente")
    logging.shutdown()

    assert log_file.exists()
    assert "Factura organizada correctamente" in log_file.read_text(encoding="utf-8")


def test_configure_logging_rejects_unknown_level(tmp_path):
    with pytest.raises(ValueError, match="LOG_LEVEL"):
        configure_logging(tmp_path, "MUCHO_DETALLE")
