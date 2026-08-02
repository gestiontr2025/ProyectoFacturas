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

- `type_detector.py`: distingue factura, nota de crédito y nota de débito.
- `letter.py`: detecta las letras A, B y C con contexto fiscal.
- `number.py`: normaliza punto de venta y número como `00000-00000000`.
- `issue_date.py`: detecta y valida la fecha de emisión.

El proyecto contempla estas combinaciones: FCA, FCB, FCC, NCA, NCB, NCC,
NDA, NDB y NDC. El contenido del PDF tiene prioridad; el nombre del archivo
solo funciona como evidencia secundaria cuando faltan datos.

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
