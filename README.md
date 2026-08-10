
## Etapa 5.3 — cierre de familias pendientes

- Proveedores recurrentes nuevos: Souverain/Buenos Ayres Vinos, Fratelli Branca y La Agrícola.
- Emisores ocasionales se reconocen desde el encabezado sin incorporarlos al catálogo JSON.
- Clasificación de ABL, instructivos, documentos operativos, consorcio, recibos y transferencias.
- Segundo lector PDF con PyMuPDF para estructuras que pypdf rechaza.
- Nuevas familias: El Nuevo Emporio FACA/NCB y FCVTA de Souverain.

# Proyecto Facturas

Automatiza la búsqueda de correos en Gmail, descarga archivos PDF, extrae su
texto e intenta identificar al proveedor.

## Preparación

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Copiá `.env.example` como `.env` y completá tus credenciales. El archivo `.env`
no debe subirse a GitHub.

## Ejecución

```bash
python main.py
```

## Arquitectura inicial

- `main.py`: inicia la aplicación.
- `app/runner.py`: coordina la ejecución completa.
- `app/email_selection.py`: selecciona los correos recientes.
- `app/email_processor.py`: procesa un correo individual.
- `app/pdf_pipeline.py`: lee PDFs y detecta proveedores.
- `app/presentation.py`: muestra información en la terminal.
- Los módulos de la raíz conservan por ahora la lógica especializada existente.

Esta es la primera etapa de la refactorización. Las siguientes etapas dividirán
Gmail, el parser de facturas y el catálogo de proveedores sin alterar el flujo
que ya funciona.

## Arquitectura de Gmail

Las tareas relacionadas con Gmail se encuentran separadas por responsabilidad:

```text
gmail/
├── connection.py    # abre la sesión IMAP
├── mailboxes.py     # localiza las carpetas de Gmail
├── messages.py      # busca y lee correos
└── attachments.py   # detecta archivos adjuntos
```

`gmail_client.py` se conserva como fachada temporal. Esto permite refactorizar
el proyecto en etapas sin romper los imports antiguos de una sola vez.

## Reprocesar archivos pendientes

Cuando se mejora el parser no es necesario volver a descargar los correos. Los
PDF que ya están en `_Pendientes` pueden analizarse con:

```powershell
python main.py --reprocess-pending
```

Las facturas completas se moverán a su carpeta final. Las listas de precios se
archivarán en `_OtrosDocumentos/Listas_de_precios`. Solo los documentos dudosos
permanecerán en `_Pendientes`.

## Motor de comprobantes fiscales

La detección fiscal está separada en el paquete `fiscal/`:

- `definitions.py`: fuente única de tipos, letras, prefijos y códigos AFIP/ARCA.
- `type_detector.py`: distingue factura, nota de crédito y nota de débito.
- `letter.py`: detecta las letras A, B y C únicamente con contexto fiscal.
- `number.py`: normaliza punto de venta y número como `00000-00000000`.
- `issue_date.py`: detecta y valida la fecha de emisión.
- `parser.py`: coordina los extractores y devuelve un `FiscalHeaderAnalysis`.
- `analysis_result.py`: modelo del resultado fiscal, código y advertencias.

El proyecto contempla explícitamente estas nueve combinaciones: FCA, FCB,
FCC, NCA, NCB, NCC, NDA, NDB y NDC. Las reglas no se repiten en cada módulo:
`FiscalDocument`, el constructor de nombres y la evidencia del nombre del PDF
consultan las mismas definiciones centrales. El contenido del PDF tiene
prioridad; el nombre del archivo solo completa datos ausentes.

### Razón social y nombre comercial

El proyecto distingue la identidad fiscal del proveedor de su nombre de
fantasía. La razón social se conserva en el nombre del PDF, mientras que la
carpeta puede usar el nombre comercial para resultar más fácil de reconocer.
Por ejemplo, `ALL ONLINE SOLUTIONS S. A. U.` se organiza dentro de la carpeta
`COLPPY`.

## Modelos de dominio

El proyecto utiliza modelos tipados dentro de `models/` para transportar datos
entre módulos sin depender de diccionarios con claves escritas manualmente.
La migración es progresiva: los adaptadores aceptan las estructuras históricas,
lo cual permite mejorar la arquitectura sin romper el flujo ya probado.

- `FiscalDocument`: datos fiscales y validación de campos obligatorios.
- `Supplier`: identidad fiscal y nombre comercial del proveedor.
- `ProcessingResult`: estado uniforme de una operación sobre un documento.

### Normalizar carpetas históricas de proveedores

Si versiones anteriores crearon dos carpetas para la misma empresa, ejecute:

```powershell
python main.py --normalize-supplier-folders
```

El comando conoce alias históricos, mueve los archivos a la carpeta canónica,
compara duplicados idénticos mediante SHA-256 y nunca sobrescribe un archivo
diferente: ante un conflicto agrega un sufijo como `_2`.

### Documentos administrativos y duplicados

El comando `python main.py --reprocess-pending` también reconoce listas de
precios, comprobantes de pago y órdenes de pago. Estos documentos se archivan
dentro de `_OtrosDocumentos`.

Antes de eliminar una copia de `_Pendientes`, el programa compara el contenido
mediante SHA-256. Un archivo solo se elimina cuando ya existe otra copia
idéntica. Si dos documentos tienen el mismo nombre pero contenido diferente,
ambos se conservan agregando un sufijo numérico.

### Limpiar facturas duplicadas

La búsqueda de duplicados funciona primero como **vista previa**:

```powershell
python main.py --deduplicate-invoices
```

El comando informa qué copia conservaría, pero no elimina archivos. Después de revisar el resultado, la limpieza se confirma de forma explícita:

```powershell
python main.py --deduplicate-invoices --apply
```

Solo se elimina una copia cuando ambas producen exactamente la misma huella SHA-256. Si dos archivos comparten número fiscal pero su contenido es diferente, el proyecto conserva ambos para revisión manual.

## Registro de actividad

El proyecto conserva un log diario en `logs/YYYY-MM-DD.log` de forma predeterminada.
El nivel y la ubicación pueden configurarse con `LOG_LEVEL` y `LOG_FOLDER` en `.env`.
La referencia completa de comandos está disponible en `COMMANDS.txt`.

## Historial incremental de Gmail

El proyecto guarda en SQLite una identidad estable por correo procesado. Gmail
expone `X-GM-MSGID`, que permanece estable aunque cambie la posición del mensaje
en el buzón. Gracias a este historial, la ejecución diaria no vuelve a abrir los
mismos correos una y otra vez.

Estados principales:

- `processed`: correo procesado con uno o más PDF.
- `no_pdf`: correo revisado sin adjuntos PDF.
- `error`: intento fallido que debe volver a intentarse.

La ejecución normal usa `EMAIL_PROCESSING_LIMIT` y omite los correos completados:

```powershell
python main.py
```

Para la primera reconstrucción completa:

```powershell
python main.py --full-scan
```

El progreso se confirma después de cada correo. Si la computadora se apaga o la
conexión falla, la siguiente ejecución continúa omitiendo lo ya completado.

Para consultar el estado local:

```powershell
python main.py --email-history
```

El reinicio del historial requiere una confirmación explícita:

```powershell
python main.py --reset-email-history
python main.py --reset-email-history --apply
```

Eliminar la carpeta `Facturas` no reinicia automáticamente el historial. Para
reconstruir todo desde Gmail deben reiniciarse ambas cosas de manera consciente.

## Clasificación ampliada de documentos pendientes

El comando:

```powershell
python main.py --reprocess-pending
```

clasifica primero cada PDF antes de intentar interpretarlo como factura. Los
documentos con evidencia suficiente pueden archivarse en:

```text
_OtrosDocumentos/
├── Listas_de_precios/
├── Ordenes_de_pago/
├── Comprobantes_de_pago/
├── Recursos_Humanos/
│   ├── Altas_y_Bajas/
│   ├── Liquidaciones/
│   └── Recibos_y_Legajos/
├── Retenciones_y_Transferencias/
├── Estados_de_cuenta/
├── Menus_y_Cartas/
├── Instructivos/
└── Administrativos/
```

La clasificación combina el nombre y el contenido del archivo. Solo se mueve un
documento cuando una categoría supera un umbral alto y se diferencia claramente
de las demás. Un caso ambiguo permanece en `_Pendientes` para revisión.

## Compatibilidad fiscal incorporada en la etapa 4.8

El motor reconoce también nombres de adjuntos generados por sistemas que usan
formatos como `FACA...`, `FACB...`, `factura_ARCA_A_...` y
`Comprobante-FCVTA-A-...`. La evidencia del nombre solo completa campos que no
pudieron recuperarse desde el contenido del PDF.

Algunos encabezados gráficos no son extraíbles con `pypdf`. Para esos casos se
incorporaron firmas muy específicas y comprobadas para IVINI/Cantine y para la
familia de adjuntos de Frigorífico Los Prados. Los PDF completamente escaneados recurren a OCR únicamente cuando no existe
texto digital utilizable. Las pasadas multipropósito, PSM alternativos y
rotaciones se reservan como fallback para documentos difíciles.


## Manejo de texto vertical y familias fiscales estructuradas

La versión 0.20 reconoce comprobantes cuyo PDF conserva los datos, pero extrae cada carácter en una línea distinta. El programa solo aplica la compactación como respaldo cuando el nombre del archivo ya confirmó de forma inequívoca el tipo, la letra y el número fiscal. Esto evita usar una fecha aislada en documentos desconocidos.

También se distinguen documentos comerciales no fiscales (`INV-*` con `Recibo X`) y comunicaciones institucionales, que se archivan fuera de `_Pendientes`.


## Auditoría defensiva de fechas organizadas

Una factura puede haberse guardado históricamente con una fecha secundaria,
como el inicio de actividades o el vencimiento del CAE. El comando siguiente
revisa las facturas ya organizadas sin modificar archivos:

```powershell
python main.py --audit-organized-dates
```

Después de revisar la vista previa, las correcciones se aplican con:

```powershell
python main.py --audit-organized-dates --apply
```

El auditor no sobrescribe destinos existentes y excluye `_Pendientes` y
`_OtrosDocumentos`. Además trabaja deliberadamente en modo digital-only: no
dispara OCR/Tesseract durante una auditoría masiva de archivos ya organizados.


## Bandeja manual de entrada

Además de los adjuntos descargados desde Gmail, se puede copiar cualquier PDF
directamente en `Facturas/_Pendientes` y ejecutar:

```powershell
python main.py --reprocess-pending
```

El archivo será leído, clasificado y organizado con el mismo flujo. Esto permite
incorporar documentos descargados desde WhatsApp, Google Drive u otros medios.

## Proveedores ocasionales

Los emisores detectados desde una factura válida pueden organizarse aunque no
formen parte del catálogo recurrente. Sus apariciones se guardan localmente en
`data/supplier_candidates.json`. El archivo es auxiliar: no modifica
`suppliers/data/supplier_catalog.json` y evita promover automáticamente compras
únicas. A partir de tres comprobantes distintos se marca al emisor como candidato
para revisión manual.

## Exportar el perfil impositivo de proveedores

```powershell
python main.py --export-supplier-tax-profile
```

El comando analiza las facturas organizadas y crea en el Escritorio un Excel
con una única fila por CUIT. Para cada proveedor indica si se observó alguna
vez IVA 27%, IVA 21%, IVA 10,5%, percepción de IVA, percepción de IIBB CABA,
percepción de IIBB Buenos Aires o impuestos internos. No exporta importes.

## Integración con Google Drive

Google Drive funciona como una fuente de entrada adicional. El módulo **no**
interpreta facturas ni decide su destino final: descarga los PDF completos a
`Facturas/_Pendientes` y reutiliza el pipeline existente.

Arquitectura:

```text
drive/
├── connection.py   # OAuth, token y cliente Drive v3
├── files.py        # listado paginado de una carpeta
└── downloads.py    # descarga segura .part -> PDF

app/drive_workflow.py   # coordina las fuentes configuradas
state/drive_history.py  # historial SQLite por fileId de Google Drive
```

La carpeta `_Pendientes` se crea automáticamente si no existe. Las descargas
incompletas permanecen con extensión `.part` dentro de una subcarpeta temporal
y nunca son entregadas al reprocesador.

### Configuración

1. Habilitá Google Drive API y creá un cliente OAuth de tipo **Desktop app**.
2. Guardá el JSON privado como `credentials.json` en la raíz del proyecto.
3. Configurá en `.env` al menos una fuente:

```text
DRIVE_PROVIDER_FOLDER_ID=ID_DE_LA_CARPETA_DEL_PROVEEDOR
DRIVE_SCAN_FOLDER_ID=
```

`DRIVE_SCAN_FOLDER_ID` es opcional y puede agregarse más adelante para la
carpeta donde se carguen facturas físicas escaneadas.

La primera autorización crea `token.json`. Tanto `credentials.json` como
`token.json` están ignorados por Git.

### Descargar desde Drive

```powershell
python main.py --download-drive
```

El comando:

- revisa todas las páginas de cada carpeta configurada;
- ignora elementos que no sean PDF;
- omite `fileId` ya completados;
- descarga primero como `.part`;
- nunca sobrescribe silenciosamente un PDF local distinto;
- registra éxito/error en `data/project_state.sqlite3`.

Después, el procesamiento continúa con el comando ya existente:

```powershell
python main.py --reprocess-pending
```

### Migración desde `drive_test.py`

Si existe `data/drive_downloaded.json`, los IDs del prototipo se importan de
forma idempotente a SQLite. De esta forma los documentos ya descargados durante
las pruebas no vuelven a bajarse. El JSON queda únicamente como archivo legado.
