
## 0.28 - Detección de emisores por evidencia ponderada

- El detector de proveedores nuevos recorre todo el documento, sin asumir que el emisor está en el encabezado.
- Los nombres candidatos se asocian al CUIT mediante distancia, etiquetas explícitas y señales fiscales.
- Cada decisión conserva el puntaje y la evidencia que la justifica.
- Se rechazan empates ambiguos y documentos con varios CUIT de terceros.
- Se agregaron regresiones para emisor al final del PDF y para CUIT/razón social separados.


## 0.27 - Detección genérica de proveedores nuevos

- Valida CUIT argentinos mediante su dígito verificador.
- Excluye automáticamente el CUIT de Madero Roof.
- Extrae una razón social confiable del encabezado fiscal de facturas ARCA.
- Organiza proveedores nuevos sin agregarlos manualmente al catálogo.
- Registra la identidad aprendida en el archivo auxiliar de candidatos.
- Mantiene pendientes los documentos ambiguos con varios CUIT de terceros.

## 0.26 - 2026-08-04

- Se agregó soporte general para comprobantes compactos como `A00013-00024717`, incluso cuando el número aparece antes de la etiqueta `Número:`.
- Se incorporó una regresión basada en la familia real de facturas de GOODIES S.A.
- La regla sigue exigiendo una estructura fiscal completa y no acepta letras aisladas.

## Etapa 5.8

- Corregida la auditoría de fechas para PDF cuyo texto expone un carácter por línea.
- La fecha compacta inmediatamente posterior a la identidad fiscal ahora tiene prioridad sobre F.VTO/CAE.
- Agregada prueba de regresión basada en la extracción real de Herrajes San Martín.

## 0.21 — Etapa 5.4: cierre defensivo de pendientes

- Se dio precedencia a documentos no fiscales explícitos antes del parser de facturas.
- Los recibos X `RDRC`, transferencias, instructivos y listas verticales se archivan correctamente.
- Se agregó soporte para nombres SAP `FACT_A002600360215`.
- Las fechas textuales, como `12 DE MAYO DE 2026`, se normalizan como emisión.
- Se excluyen fechas de inicio de actividades, vencimiento, CAE y entrega.
- Los códigos `TIPO 01/06/11` pueden aportar la letra fiscal cuando el tipo ya fue confirmado.
- Se incorporó `--audit-organized-dates` para detectar y reparar fechas históricas incorrectas de forma segura.
- Suite validada con 116 pruebas automatizadas.


## Etapa 5.3 — cierre de familias pendientes

- Proveedores recurrentes nuevos: Souverain/Buenos Ayres Vinos, Fratelli Branca y La Agrícola.
- Emisores ocasionales se reconocen desde el encabezado sin incorporarlos al catálogo JSON.
- Clasificación de ABL, instructivos, documentos operativos, consorcio, recibos y transferencias.
- Segundo lector PDF con PyMuPDF para estructuras que pypdf rechaza.
- Nuevas familias: El Nuevo Emporio FACA/NCB y FCVTA de Souverain.

# Changelog

## 0.20 — Etapa 5.1

- Se agregó recuperación defensiva de fechas en PDF cuya capa de texto separa cada carácter por saltos de línea.
- Los nombres fiscales estructurados ahora pueden corregir falsos positivos de tipo, letra y número detectados en texto degradado.
- Se incorporó soporte para las familias FACA de GIFEL, FACB de El Nuevo Emporio y CA de Frigorífico Los Prados.
- Se agregó GIFEL S.R.L. al catálogo JSON como proveedor recurrente validado.
- Los documentos `INV-*` con `Recibo X` se archivan como remitos/recibos no fiscales.
- Las comunicaciones institucionales se archivan en `_OtrosDocumentos/Comunicaciones`.
- Se reforzó la detección de altas ARCA con varios empleados.
- Se eliminaron patrones demasiado amplios de `N C` y `N D` que podían generar falsos positivos en texto vertical.
- Suite validada con 95 pruebas automatizadas.

# Historial de cambios

## Etapa 5.0 — Definiciones fiscales y coordinador único

- Se centralizaron las nueve combinaciones prioritarias: FCA, FCB, FCC, NCA, NCB, NCC, NDA, NDB y NDC.
- Se creó `fiscal/definitions.py` como fuente única de letras, tipos, prefijos y códigos AFIP/ARCA.
- Se incorporó `FiscalHeaderAnalysis`, que reúne tipo, letra, número, fecha, código fiscal y advertencias.
- `invoice_parser.py` utiliza ahora un coordinador fiscal único en vez de ejecutar cuatro detectores desconectados.
- `FiscalDocument`, `filename_builder.py` y la evidencia por nombre comparten las mismas definiciones centrales.
- Se reforzó el reconocimiento de abreviaturas compactas como FCA, FCB, FCC, NCA, NCB y NDC.
- Se mantuvieron las fachadas históricas para evitar romper imports existentes.
- La suite alcanza 88 pruebas automáticas exitosas.

## Etapa 4.5 - Logging y documentación operativa

- Se agregó logging diario configurable mediante `LOG_LEVEL` y `LOG_FOLDER`.
- Se incorporó `COMMANDS.txt` con comandos, efectos y precauciones.
- Se separaron dependencias de desarrollo en `requirements-dev.txt`.
- Se agregó `pytest.ini` y pruebas para la configuración del logger.
- Los paquetes de entrega ya no incluyen cachés generadas por Python o pytest.

## Etapa 3.5 - Formatos ARCA/Colppy y nombres comerciales

- Se reconocen letras ubicadas antes del tipo, como `C FACTURA`.
- Se interpretan códigos ARCA/AFIP (`COD 01`, `COD 011`) como evidencia fiscal.
- Se detectan números separados como `Punto de Venta ... Comp. Nro ...`.
- Se separa la razón social fiscal del nombre usado para la carpeta.
- All Online Solutions S. A. U. se archiva bajo la carpeta comercial `COLPPY`.
- Se agregan regresiones para diseños reales de ARCA y Colppy.
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

## Etapa 4.1 - Modelos de dominio tipados

- Se incorporaron `FiscalDocument`, `Supplier` y `ProcessingResult`.
- El organizador adapta progresivamente las estructuras históricas a modelos tipados.
- Se mantiene compatibilidad con las APIs anteriores para reducir el riesgo de regresiones.
- Se agregaron pruebas de validación, adaptación y estados de procesamiento.

## Etapa 4.2 - Identidad canónica de carpetas

- Se centralizó el nombre físico de carpeta por identificador de proveedor.
- ARTA utiliza siempre `ARTA_VERDULEROS`.
- El Criollo utiliza siempre `EL_CRIOLLO`.
- Colppy utiliza siempre `COLPPY`.
- Se agregó `--normalize-supplier-folders` para migrar carpetas históricas sin sobrescribir archivos.

## Etapa 4.3

- Se agregaron categorías para comprobantes y órdenes de pago.
- El reprocesamiento elimina copias redundantes solo después de verificar SHA-256.
- Los archivos con igual nombre y contenido diferente se conservan con sufijo.
- La lógica de duplicados se centralizó en el paquete `storage`.

## Etapa 4.4 — Deduplicación de facturas organizadas

- Se evita crear una nueva copia cuando una factura idéntica ya existe en la carpeta del proveedor.
- Se compara el contenido mediante SHA-256 antes de eliminar la copia temporal.
- Si la identidad fiscal coincide pero el contenido es diferente, se conservan ambas versiones y se informa un conflicto.
- Se agregó `python main.py --deduplicate-invoices` como vista previa segura.
- La eliminación real requiere confirmación explícita con `--apply`.

## Etapa 4.6 — Historial incremental de Gmail

- Se incorporó SQLite para recordar correos procesados entre ejecuciones.
- Gmail usa `X-GM-MSGID` como identidad persistente y `Message-ID` como respaldo.
- La ejecución normal omite correos ya completados.
- Los correos que fallan quedan en estado `error` y pueden reintentarse.
- Se agregó `--full-scan` para recorrer todo el buzón de forma reanudable.
- Se agregó `--email-history` para consultar el estado local.
- Se agregó `--reset-email-history` con confirmación obligatoria mediante `--apply`.
- Los comandos locales pueden ejecutarse aunque las credenciales Gmail todavía no estén configuradas.

## Etapa 4.7 — Clasificación documental ampliada

- El clasificador se dividió en reglas modulares para Recursos Humanos, documentos comerciales y administrativos.
- Se agregaron categorías para altas y bajas, liquidaciones, recibos/legajos, retenciones, estados de cuenta, menús/cartas, instructivos y documentos administrativos.
- Las decisiones automáticas usan puntajes, umbral mínimo y margen de separación para evitar clasificaciones ambiguas.
- `_Pendientes` queda reservado para facturas incompletas, documentos desconocidos y errores reales.
- `--reprocess-pending` muestra ahora un resumen agrupado por resultado.
- La suite alcanza 62 pruebas automáticas.


## Etapa 4.8 — Nuevas familias fiscales reales

- Se agregaron proveedores Bartoszuk Gonzalo Andrés y Establecimiento Don Pacho 2024.
- Se corrigió el CUIT canónico de Cantine S.R.L. según una factura real y se agregó el alias IVINI.
- Se incorporaron patrones para FACA, FACB, factura ARCA, FCVTA y notas de débito/crédito descriptivas.
- Se agregó evidencia modular por nombre para la familia de adjuntos de Frigorífico Los Prados cuyo encabezado no es extraíble.
- El OCR de documentos escaneados continúa como fallback futuro; no se introdujo una dependencia externa en esta etapa.
- Se añadieron pruebas de regresión basadas en las familias encontradas durante el escaneo completo.

## Etapa 5.5 — Bandeja manual y proveedores ocasionales

- Se completó la detección de CEAMSE y Herrajes San Martín como emisores ocasionales.
- `_Pendientes` continúa funcionando como bandeja manual: cualquier PDF copiado allí puede reprocesarse sin haber pasado por Gmail.
- Se agregó un registro local de candidatos en `data/supplier_candidates.json`.
- El registro evita contar dos veces el mismo comprobante y sugiere revisión al alcanzar tres apariciones.
- Los candidatos no se incorporan automáticamente a `supplier_catalog.json`.
- Se añadieron pruebas defensivas para CUIT, encabezados y conteo idempotente.


## Etapa 5.6 — Corrección final de CEAMSE

- La detección de proveedores ocasionales ahora busca el CUIT canónico en todo el texto del PDF.
- Se corrige el caso en que el parser fiscal invierte emisor y receptor porque el diseño imprime primero los datos del cliente.
- CEAMSE se reconoce por CUIT exacto o razón social normalizada aunque `cuit_emisor` contenga temporalmente el CUIT de Madero Roof.
- Se agregó una prueba de regresión basada en el recorrido real de `48850 (2).pdf`.


## Etapa 5.7 — Auditoría conservadora de fechas

- Se corrigió la lectura de comprobantes legacy cuya fecha de emisión aparece sin etiqueta inmediatamente después de la identidad fiscal.
- El patrón `B 00021-00001477 08 07 25` se interpreta como emisión 08/07/2025.
- Las fechas asociadas a `F.VTO`, vencimiento o CAE permanecen excluidas.
- Parser y auditor continúan usando el mismo extractor compartido.
- Se agregaron pruebas de regresión con el caso real de Herrajes San Martín.

## Etapa 5.9 — Perfil impositivo de proveedores

- Se agregó `--export-supplier-tax-profile` para generar un Excel en el Escritorio.
- El archivo contiene una sola fila por CUIT, sin duplicar proveedores.
- Las alícuotas IVA 27%, 21% y 10,5% se acumulan de manera independiente entre todas las facturas del proveedor.
- Se detecta presencia de percepción IVA, IIBB CABA, IIBB Buenos Aires e impuestos internos.
- El reporte no suma ni expone importes: solo indica `Sí` o `No` para cada concepto observado.
- La extracción tributaria se aisló en el paquete `taxes` y se agregaron pruebas de regresión.
