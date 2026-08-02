"""Fachada de compatibilidad para las funciones de Gmail.

Antes de la refactorización, todas las funciones estaban definidas en este
archivo. Ahora viven dentro del paquete ``gmail``, separadas por
responsabilidad.

Este archivo se conserva temporalmente para que los módulos existentes puedan
seguir haciendo ``import gmail_client`` sin romperse. En una etapa posterior
podremos actualizar esos imports y retirar esta fachada.
"""

from gmail import (
    buscar_todos_los_correos,
    conectar,
    encontrar_carpeta_todos,
    leer_correo,
    obtener_identidad_correo,
    obtener_adjuntos,
    obtener_datos_correo,
)

__all__ = [
    "conectar",
    "encontrar_carpeta_todos",
    "buscar_todos_los_correos",
    "leer_correo",
    "obtener_identidad_correo",
    "obtener_datos_correo",
    "obtener_adjuntos",
]
