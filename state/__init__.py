"""Persistencia del estado local del Proyecto Facturas.

El paquete ``state`` guarda información que debe sobrevivir entre ejecuciones.
Actualmente registra qué correos ya fueron revisados para que la ejecución
diaria no vuelva a procesar el mismo mensaje una y otra vez.
"""

from state.email_history import EmailHistory, EmailIdentity, EmailRecord

__all__ = ["EmailHistory", "EmailIdentity", "EmailRecord"]
