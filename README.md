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
