"""Infraestructura técnica compartida por toda la aplicación.

Los módulos de esta carpeta resuelven necesidades transversales, como el
registro de actividad. No contienen reglas para interpretar facturas ni para
detectar proveedores.
"""

from infrastructure.logging_setup import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger"]
