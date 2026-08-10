## 0.44.0

- Agrega auditoría geométrica digital sin OCR para layouts en columnas.
- Evita ocultar fechas erróneas como estables por coincidencia con vencimientos.
- Informa cantidad de facturas digitales efectivamente verificadas.
- Mantiene OCR selectivo y opt-in.

# Versión 0.39.0 — auditoría conservadora y recuperación segura

- Separa la detección de fecha para auditoría del parser general: la auditoría ya no usa fallbacks amplios para decidir movimientos.
- Conserva la fecha actual si ya aparece en el PDF fuera de contextos secundarios como vencimiento, VTO, CAE, período facturado o inicio de actividades.
- Bloquea fechas futuras antes de cualquier movimiento automático.
- Mantiene la corrección DBA cuando la evidencia fuerte es `DD/MM/AAAA Fecha:` y la fecha histórica pertenece a `INICIO ACTIV.`.
- Agrega regresiones para el patrón observado de facturas C donde la fecha de vencimiento quedaba exactamente 10 días después de la emisión.
- Incluye un recuperador seguro y un plan generado desde el log del incidente v0.38.0 para revertir únicamente desplazamientos exactos de +10 días. La recuperación es vista previa por defecto y nunca sobrescribe archivos.
- Suite: 184 pruebas.

# Versión 0.38.0 — parser primero, OCR solo como rescate

- Refuerza la política parser-first: la evidencia digital, el nombre estructurado y la fecha semántica se agotan antes de ejecutar OCR forzado.
- `leer_pdf(..., permitir_ocr=False)` permite rutas explícitamente libres de OCR sin alterar el comportamiento seguro de los PDFs realmente escaneados.
- `--audit-organized-dates` ahora es digital-only y ya no dispara Tesseract al revisar archivos organizados.
- Corrige el layout DBA donde `06/08/2026 Fecha:` debe ganar sobre `INICIO ACTIV.: 01/04/2006`.
- Amplía la exclusión semántica para variantes abreviadas de `INICIO ACTIV.`.
- Elimina el fallback genérico de fechas sobre texto compactado, que perdía contexto y podía elegir fechas societarias o vencimientos.
- Conserva OCR multipasada, scoring fiscal, fusión conservadora, PSM alternativos y rotaciones como fallback para documentos realmente difíciles.

# Versión 0.37.0 — OCR adaptativo y rendimiento defensivo

- Convierte el OCR multipasada en fallback real: si la pasada inicial de PyMuPDF/Tesseract ya recuperó evidencia fiscal completa, no ejecuta PSM adicionales.
- Conserva PSM 3/11/4/6/12, fusión conservadora, scoring fiscal y rotaciones 90°/270° para documentos difíciles.
- Puede detener las pasadas cuando la evidencia combinada de varios PSM ya es suficiente.
- Reduce el timeout individual de Tesseract CLI a 25 segundos y trata cada timeout como una estrategia fallida, permitiendo continuar con el resto del lote.
- Detiene las rotaciones cuando una orientación ya reconstruyó evidencia suficiente.
- Muestra progreso por archivo durante `--reprocess-pending`, incluyendo el método OCR usado, para distinguir trabajo intensivo de un bloqueo.
- Agrega regresiones específicas para timeout y para evitar OCR multipasada redundante.

# Versión 0.36.1

- Implementa realmente OCR rotado 90°/270° para texto vertical.
- Expone `ocr_candidatos` con método, puntaje y texto de cada pasada.
- Mantiene fusión conservadora y validación estricta de CUIT.

# Versión 0.36

- Agrega diagnóstico de candidatos OCR.
- Prepara OCR rotado 90°/270° para rescatar texto vertical cuando falta proveedor.
- Mantiene validación estricta de CUIT y fusión conservadora de evidencia.

# Versión 0.35 — fusión conservadora de evidencia OCR

- Fusiona evidencia validada entre distintas pasadas OCR en vez de descartar todas salvo la de mayor puntaje global.
- Mantiene como base la lectura mejor puntuada y completa únicamente campos faltantes; nunca reemplaza tipo, letra, número o fecha ya detectados.
- Puede recuperar razón social y CUIT desde una pasada secundaria cuando otra segmentación conserva mejor la cabecera fiscal.
- La identidad complementaria solo se incorpora si el CUIT supera la validación matemática y el detector de emisor construye una identidad no ambigua.
- La fusión agrega evidencia canónica mínima, no concatena OCRs completos, para evitar mezclar facturas asociadas, receptores u otros textos internos.
- `ocr_metodo` expone las pasadas utilizadas con el formato `fusion_ocr[...]`, facilitando el diagnóstico.
- Agrega regresiones para fusionar cabecera + emisor, preservar campos fiscales confiables y rechazar CUIT OCR inválidos. La suite alcanza 168 pruebas.

# Versión 0.34 — OCR multipasada con scoring fiscal

- Agrega OCR multipasada con Tesseract CLI usando PSM 3, 4, 6, 11 y 12 para layouts de columnas, formularios y texto disperso.
- La selección entre lecturas OCR ya no depende solo de palabras clave: premia tipo, letra, número, fecha, CUIT válido e identidad de emisor realmente validada por los parsers del proyecto.
- Penaliza lecturas donde una etiqueta CUIT contiene once dígitos que no superan el dígito verificador, reduciendo errores OCR de un solo carácter.
- Mantiene intacta la política conservadora: no corrige ni inventa CUIT o letras; elige otra lectura únicamente cuando Tesseract la recuperó con mayor evidencia.
- Expone `ocr_puntaje` junto a `ocr_metodo` para diagnóstico.
- Las facturas digitales no pagan el costo multipasada: estas estrategias solo se ejecutan cuando el documento ya necesita OCR o rescate semántico.

# Versión 0.33 — rescate semántico y scoring conservador

- Agrega OCR de rescate aunque el PDF ya tenga capa de texto cuando faltan campos críticos.
- La lectura OCR secundaria completa únicamente huecos y nunca sobrescribe datos fiscales ya detectados.
- Refuerza la detección de emisores cuando la razón social está inmediatamente antes de un CUIT, con mayor peso para `CUIT emisor`.
- Descarta rótulos variables como CUIT, fecha, número, receptor o nombre de fantasía como candidatos de razón social.
- Normaliza formas jurídicas puntuadas (`S.A.`, `S.R.L.`, `S.A.S.`) para mejorar el scoring.
- Limpia prefijos documentales pegados por OCR, por ejemplo `NOTA DE CREDITO CONSTRUCCIONES KAISA S.A.`.
- Corrige Factura B con `Punto de venta ... Comprobante ...` sin rótulo `Nro`.
- Corrige NC/ND para no confundir fechas con números de comprobante y admite `Numero del comprobante` en otra línea.
- Mantiene la validación estricta de CUIT y el criterio de dejar en `_Pendientes` los casos realmente ambiguos.
- Agrega pruebas de regresión para Archeron, Kaisa, Eventos Manon y rescate OCR semántico. La suite alcanza 161 pruebas.

# Versión 0.32 — OCR semántico y comprobantes relacionados

- Agrega un segundo OCR de rescate con Tesseract CLI (`--psm 3`) para PDFs imagen y conserva automáticamente la lectura con mayor evidencia fiscal.
- Distingue el número propio de una Nota de Crédito/Débito del número de la factura o comprobante asociado.
- Impide que rótulos como `Comprobante asociado`, `Factura asociada` o `Referencia` sean candidatos a razón social.
- Recupera letras A/B/C que el OCR deja aisladas o pegadas al nombre del emisor, únicamente cuando existe numeración fiscal completa.
- Puede recuperar una Nota de Débito desde `TOTAL DEBITO` cuando el OCR pierde el título, exigiendo además número y evidencia fiscal.
- La frase `NO ES FACTURA` deja de ser evidencia de factura, evitando falsos positivos en remitos.
- Excluye CUIT ubicados en el bloque explícito de Madero Roof aunque el OCR haya alterado el CUIT canónico.
- Expone `ocr_metodo` para diagnosticar si ganó PyMuPDF/Tesseract o el OCR CLI de rescate.
- Agrega regresiones específicas para NC asociadas, ND degradadas por OCR, letras aisladas, remitos negados y receptor OCR.

# Versión 0.31 — OCR fiscal robusto para expensas y recibos

- Aumenta el OCR de respaldo de 250 a 300 DPI para recuperar mejor letras y campos pequeños en comprobantes escaneados.
- Reconoce liquidaciones fiscales de gastos comunes aun cuando no imprimen la palabra FACTURA, siempre que combinen numeración fiscal, CUIT e IVA discriminado.
- Recupera la letra A en liquidaciones escaneadas cuando aparece aislada o degradada por OCR dentro de una estructura fiscal confirmada.
- Los recibos explícitos conservan prioridad como recibos aunque mencionen facturas imputadas dentro de su detalle.
- Evita usar `Venc.` como fecha de emisión y repara años OCR incompatibles cuando la fecha de vencimiento aporta una referencia temporal inequívoca.
- Normaliza la razón social de consorcios para que numeraciones de domicilio como `703/787` no creen carpetas duplicadas.
- Agrega regresiones para liquidaciones sin la palabra factura, recibos con referencias fiscales, fechas OCR y nombres de consorcio.

# Versión 0.30

- Migra PyMuPDF desde la API obsoleta `fitz` a `pymupdf`.
- Agrega diagnóstico explícito del OCR (`ocr_estado` y `ocr_error`).
- Busca `tessdata` mediante `OCR_TESSDATA_PATH`, `TESSDATA_PREFIX` o rutas estándar de Windows.
- Un PDF sin capa de texto y sin OCR ya no puede archivarse automáticamente por nombre: permanece en `_Pendientes`.
- El mismo fail-safe se aplica tanto al reprocesamiento local como al pipeline normal de PDFs.
- Mejora los mensajes de diagnóstico para instalaciones sin Tesseract OCR.

## 0.29 - Prioridad fiscal y OCR selectivo

- La evidencia fiscal estructural fuerte tiene prioridad sobre categorías auxiliares como consorcio o comprobante de pago.
- Se evita interpretar la frase `NO ES COMPROBANTE DE PAGO` como un comprobante de pago real.
- Se incorporó soporte para numeración legacy `FACTURA 0056 - 00562701` y `FA "A" 0001-00005591`.
- Las fechas legacy separadas por espacios se recuperan cuando están vinculadas a una identidad fiscal.
- Los PDF completamente escaneados usan OCR selectivo de PyMuPDF como último recurso, sin penalizar los PDF digitales.
- El scoring de emisores evita asociar CUIT embebidos en códigos de barras y mejora denominaciones de consorcios.



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

# Integración Google Drive modularizada

- Reemplaza el prototipo monolítico `drive_test.py` por el paquete `drive/`.
- Separa OAuth (`drive/connection.py`), listado paginado (`drive/files.py`) y descarga defensiva (`drive/downloads.py`).
- Agrega `app/drive_workflow.py` como coordinador de fuentes Drive.
- Incorpora `--download-drive` al runner principal; Drive descarga a `_Pendientes` y no interpreta facturas.
- Agrega soporte opcional para una segunda carpeta de escaneos mediante `DRIVE_SCAN_FOLDER_ID`.
- Migra automáticamente los IDs de `data/drive_downloaded.json` a la base SQLite compartida del proyecto.
- Evita sobrescrituras: archivos locales idénticos se reutilizan y colisiones con contenido distinto reciben sufijo numérico.
- Las descargas usan archivos temporales `.part`; un PDF solo aparece en `_Pendientes` después de completarse.
- Agrega las dependencias oficiales de Google Drive al `requirements.txt` y pruebas del historial persistente.

## 0.43.0
- La auditoría de fechas valida la ruta canónica completa: proveedor/año/mes/nombre.
- Corrige nombres con fecha antigua aunque la carpeta ya sea correcta.
- Corrige carpeta año/mes aunque el nombre ya tenga la fecha correcta.
- Si carpeta y nombre están mal, los corrige juntos en una única operación de movimiento.
- La vista previa informa ubicación actual y ubicación canónica esperada.
- Se mantienen las defensas parser-first, OCR selectivo y bloqueo de fechas ambiguas.


## 0.46.0 — Motor único de decisión de fechas

- Se centralizó la decisión de fecha en `fiscal.issue_date.resolver_candidatos_fecha`.
- La geometría ya no actúa como un segundo parser: aporta evidencia al mismo motor que evalúa el texto.
- Se eliminó la evidencia circular que sumaba puntos a una fecha solo por aparecer en el nombre actual.
- Un bloque ARCA aplanado ya no se considera evidencia fuerte por posición: su orden textual puede variar entre generadores PDF.
- Una fecha geométrica explícitamente asociada a `Fecha de Emisión` prevalece sobre el orden lineal ambiguo.
- `manual_review` queda reservado a contradicciones reales entre fechas plausibles. Una coincidencia media con el nombre se considera estable y no genera cientos de falsos positivos.
- Los documentos sin evidencia suficiente ahora se contabilizan como `unresolved_date` en lugar de desaparecer silenciosamente del resumen.
- Se agregaron regresiones específicas para la nueva política de decisión.
- Validación sobre el conjunto real suministrado: 515 facturas organizadas contabilizadas, 380 verificadas, 46 correcciones digitales detectadas, 1 conflicto real, 73 sin evidencia suficiente y 15 escaneadas omitidas en modo sin OCR.
