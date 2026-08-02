"""Configuración centralizada del sistema de logging.

¿Por qué usar logging en lugar de escribir todo con ``print``?

``print`` resulta útil para mostrar información inmediata al usuario, pero no
conserva un historial. ``logging`` permite registrar qué ocurrió, cuándo y con
qué nivel de importancia. Esto facilita investigar errores que aparecieron en
una ejecución anterior sin volver a reproducirlos.

La consola detallada actual se conserva durante esta transición. El objetivo
de este módulo es añadir trazabilidad sin modificar de golpe toda la interfaz.
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path


_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _normalize_level(level_name: str) -> int:
    """Convertir un nombre de nivel en una constante válida de ``logging``.

    Se rechazan valores desconocidos en lugar de usar silenciosamente otro
    nivel. Esta validación defensiva evita que un error de escritura en ``.env``
    deje el proyecto sin los registros esperados.
    """

    normalized = level_name.strip().upper()
    level = logging.getLevelNamesMapping().get(normalized)

    if not isinstance(level, int):
        valid_levels = "DEBUG, INFO, WARNING, ERROR, CRITICAL"
        raise ValueError(
            f"LOG_LEVEL={level_name!r} no es válido. Usá uno de: {valid_levels}."
        )

    return level


def configure_logging(log_folder: Path, level_name: str = "INFO") -> Path:
    """Configurar el registro general y devolver el archivo utilizado.

    Cada día utiliza un archivo independiente, por ejemplo::

        logs/2026-08-01.log

    La función elimina y cierra manejadores anteriores antes de configurar los
    nuevos. Esto es importante en pruebas automáticas y ejecuciones repetidas,
    porque evita que cada mensaje se escriba dos o más veces.
    """

    level = _normalize_level(level_name)
    folder = Path(log_folder).expanduser().resolve()
    folder.mkdir(parents=True, exist_ok=True)
    log_file = folder / f"{date.today().isoformat()}.log"

    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        handler.close()

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))

    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)

    # Evitamos que bibliotecas externas muy verbosas llenen el registro con
    # mensajes internos que no ayudan a comprender el flujo del proyecto.
    logging.getLogger("pypdf").setLevel(max(level, logging.WARNING))

    return log_file


def get_logger(name: str) -> logging.Logger:
    """Obtener un logger con el nombre del módulo que lo solicita."""

    return logging.getLogger(name)
