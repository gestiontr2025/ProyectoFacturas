"""Integración modular con Google Drive.

Los submódulos se importan de forma explícita desde la capa de aplicación. Esto
mantiene el paquete liviano y evita cargar las dependencias de Google cuando se
ejecutan comandos que solo trabajan con Gmail o archivos locales.
"""
