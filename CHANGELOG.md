# Historial de cambios

## Etapa 2 — Modularización de Gmail

- Se dividió `gmail_client.py` en cuatro módulos especializados.
- Se mantuvo `gmail_client.py` como fachada de compatibilidad.
- Se agregaron anotaciones de tipos y docstrings didácticos.
- Se corrigió la interpretación de carpetas con espacios, como `All Mail`.
- Se estandarizó `SAVE_FOLDER` mediante `.env` y `Path.home()`.

## Etapa 3.1 — Corrección del organizador

- Se corrigió la incompatibilidad entre la normalización de `Nº` a `No` y los patrones del parser.
- Se agregó reconocimiento de números con espacios alrededor del guion.
- Se agregó soporte para títulos extraídos como `FA C T U R A`.
- Se agregó un respaldo defensivo para fechas sin etiqueta en documentos claramente identificados como facturas.
- El detector de proveedores ahora puede usar el nombre original del adjunto como evidencia secundaria.
- Se agregó el alias comercial `FRIGORIFICO LOS PRADOS`.
- Se añadieron pruebas de regresión para HORECA, Frigorífico Los Prados y listas de precios.

## Etapa 3.2

- Se corrigió la detección de letras fiscales cuando aparecen antes del número.
- Se agregó `documents/` para clasificar facturas y listas de precios.
- Las listas se archivan en `_OtrosDocumentos/Listas_de_precios`.
- Se agregó `python main.py --reprocess-pending` para reprocesar archivos locales.
- Se añadieron pruebas de regresión para Frigorífico Los Prados y listas comerciales.

## Etapa 3.3

- Se agregó evidencia secundaria basada en nombres de archivo estructurados.
- Se reconocen formatos `FC A 0003-...`, `FA-A 00040-...` y nombres con código AFIP.
- El código AFIP `011` se interpreta como Factura C.
- Los datos del nombre solo completan campos faltantes; nunca reemplazan datos detectados dentro del PDF.
- Se agregaron pruebas de regresión para archivos de ARTA y otros formatos reales.

## Etapa 3.4 - Motor fiscal modular

- Se creó el paquete `fiscal/` para separar detección de tipo, letra, número y fecha.
- `invoice_parser.py` conserva su API pública y delega al nuevo motor.
- Se agregó soporte probado para FCA, FCB, FCC, NCA, NCB, NCC, NDA, NDB y NDC.
- La evidencia del nombre de archivo ahora reconoce tipo, letra y número.
- Se incorporó la tabla de códigos AFIP 001/002/003, 006/007/008 y 011/012/013.
- Se agregaron pruebas de regresión; la suite alcanza 22 pruebas exitosas.
