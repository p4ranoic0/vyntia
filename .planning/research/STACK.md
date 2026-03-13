# Technology Stack

**Project:** Sistema de Gestión de RRHH — Intranet
**Researched:** 2026-03-13
**Scope:** Additions to existing Django 4.2 + DRF + React 18 + TypeScript + Vite + MySQL stack

---

## What Already Exists (Do Not Reinstall)

The `back/requirements.txt` already declares these libraries. They are **in the stack** — gaps are
in configuration, not installation:

| Library | Version Pinned | Status |
|---------|---------------|--------|
| `reportlab` | `>=4.0.0` | Installed, used in `pdf_generator.py` |
| `xhtml2pdf` | `>=0.2.17` | Installed, tried first in fallback chain |
| `weasyprint` | `>=60.0` | Installed, fails on Windows (GTK missing) |
| `openpyxl` | `>=3.1.0` | Installed, not yet used in any service |
| `pillow` | `>=9.0.0` | Installed, required by Django `ImageField` |
| `celery` | `>=5.2.0` | Installed + configured, `tasks.py` exists |
| `redis` | `>=4.5.0` | Installed, configured as Celery broker |
| `django-storages[s3]` | `>=1.14.0` | Installed, not yet configured in `INSTALLED_APPS` |
| `boto3` | `>=1.28.0` | Installed (S3 support) |
| `jinja2` | `>=3.1.0` | Installed |
| `mysqlclient` | not in requirements.txt | Installed in venv (confirmed via logs) |

**Key gap:** `requirements.txt` declares `psycopg2-binary` (PostgreSQL) but the running venv has
`mysqlclient`. The requirements file does not reflect the actual MySQL database driver in use.

---

## Recommended Stack Additions

### Email — No New Libraries Needed

**Decision: Use Django's built-in email system. Do not add django-anymail.**

Django 4.2 provides `EmailMultiAlternatives` + `render_to_string()` which is exactly what the
codebase already uses in `onboarding_service.py` and `tasks.py`. The email infrastructure is
complete: Celery task (`send_email_html_task`), HTML/text templates
(`templates/emails/bienvenida.html`, `bienvenida.txt`), and a synchronous fallback.

The only gap is **settings configuration** — `development.py` uses `console.EmailBackend`, and
there is no production settings block defining SMTP credentials. Nothing to install.

**Required settings additions (production/staging):**

```python
# config/settings/production.py
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.office365.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@intranet.gob.pe")
```

**Why not django-anymail:** The system sends transactional email from a single address to known
recipients. It does not need bounce tracking, event webhooks, or multi-provider routing. A
government intranet typically routes through an institutional SMTP relay (Office 365 or similar) —
plain SMTP is correct. django-anymail adds value only when integrating with Mailgun, SendGrid, or
similar ESPs, which is out of scope.

**Confidence: HIGH** — Verified against Django 4.2 docs. Code already implements the full pattern.

---

### File Upload — No New Libraries Needed

**Decision: Use Django's built-in `FileField`/`ImageField` + `FileExtensionValidator`. Already wired.**

The `DocumentosDigitales` model already has:
- `FileField` with `upload_to='documentos_empleados/%Y/%m/'`
- `FileExtensionValidator` for pdf, jpg, jpeg, png, doc, docx, xls, xlsx, txt, zip, rar
- `MEDIA_ROOT = BASE_DIR / "media"` and `MEDIA_URL = "media/"` in `base.py`
- `MultiPartParser` and `FormParser` in `REST_FRAMEWORK.DEFAULT_PARSER_CLASSES`

The only thing missing is a **photo/profile-picture field on `Empleado`**. This should use
`ImageField` (requires Pillow, already installed) — not a new `DocumentosDigitales` entry, because
profile photos need direct access without document workflow overhead.

**Required additions:**

1. Add `foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)` to
   `Empleado` model. Pillow is already installed.

2. Add `DATA_UPLOAD_MAX_MEMORY_SIZE` and `FILE_UPLOAD_MAX_MEMORY_SIZE` to settings for PDFs up to
   10MB:
   ```python
   FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB
   DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB
   ```

3. Add MEDIA serving to `config/urls.py` for development:
   ```python
   from django.conf import settings
   from django.conf.urls.static import static
   if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```

**Why not django-storages for local deployment:** `django-storages[s3]` is already installed for
production cloud storage, but for development and the current deployment context (Windows server,
local filesystem), `FileSystemStorage` (Django's default) is correct. Enable S3 backend only when
moving to cloud production by adding `DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'`
to production settings.

**Confidence: HIGH** — Verified against Django 4.2 docs. Model and parsers confirmed in code.

---

### Excel Generation — openpyxl, Already Installed

**Decision: Use `openpyxl` exclusively. Do not add `xlsxwriter`.**

`openpyxl >= 3.1.0` is already in `requirements.txt`. It supports both reading and writing `.xlsx`
files, which is required because AFP Net and PDT-PLAME exports may need to populate a template
spreadsheet (not just write to a blank workbook). xlsxwriter is write-only and cannot open
existing Excel templates.

**openpyxl capabilities (MEDIUM confidence — training data, docs access restricted):**
- Write `.xlsx` files from scratch
- Open and modify existing `.xlsx` templates
- Cell formatting: fonts, colors, borders, number formats
- Write-only mode for large exports (memory efficient)
- Freeze panes, column widths, row heights
- Formula support

**What needs to be built (no new library required):**

```python
# Pattern for AFP Net export in a new service
# back/app_rrhh/services/excel_service.py
import openpyxl
from io import BytesIO

class ExcelService:
    def generar_afp_net(self, periodo, empleados):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "AFP Net"
        # ... column headers and data rows per AFP Net format
        buffer = BytesIO()
        wb.save(buffer)
        return buffer.getvalue()
```

**AFP Net and PDT-PLAME format notes:**
- AFP Net: Fixed-column text format or Excel — confirm with actual AFP Net documentation from
  the AFP (AFP Integra, Prima, Profuturo, Habitat). MEDIUM confidence on exact format.
- PDT-PLAME: SUNAT's PDT 601 uses a fixed-format text file (`.txt`) historically, though recent
  versions accept Excel uploads. Use openpyxl for Excel; use Python's built-in `io.StringIO` for
  text format. LOW confidence — verify against current SUNAT PDT 601 specification.

**Why not xlsxwriter:** Cannot read existing Excel files. openpyxl covers all use cases here.
**Why not pandas:** Heavy dependency for a task that is simply row/column writing. openpyxl is
leaner and already installed.

**Confidence: HIGH (openpyxl choice), MEDIUM (AFP Net/PDT-PLAME format specifics)**

---

### PDF Generation — Fix Existing Chain, No New Libraries

**Decision: Invert the fallback order in `pdf_generator.py`. ReportLab first on Windows.**

The current `_html_to_pdf()` tries xhtml2pdf → WeasyPrint → ReportLab. On Windows:
- xhtml2pdf may partially work but has UTF-8 issues with Spanish characters and limited CSS
- WeasyPrint always fails (GTK dependency not available on Windows without extra setup)
- ReportLab always works but current implementation is a stub (outputs placeholder text, not the
  actual HTML content)

**Two-track approach:**

**Track 1: xhtml2pdf for HTML-rendered documents (certificates, contracts)**

xhtml2pdf is a pure-Python HTML-to-PDF converter that works on Windows without system dependencies.
It supports basic CSS and UTF-8. The Django template chain already renders HTML — xhtml2pdf
consumes it. For documents where layout fidelity matters less than content completeness, xhtml2pdf
is the right tool. It is already installed.

**Track 2: ReportLab Platypus for structured payroll documents (boletas, planillas)**

ReportLab's Platypus layout engine (already imported in `pdf_generator.py`) can build
highly-structured tabular documents programmatically. For payroll slips and salary reports,
structured layout code produces better results than HTML-to-PDF conversion.

The existing ReportLab fallback is a stub that outputs "DOCUMENTO GENERADO" as placeholder text.
It must be replaced with actual Platypus document construction that reads the data and formats it
properly.

**No new libraries needed. Specific action items:**

1. In `_html_to_pdf()`, change order to: xhtml2pdf first, skip WeasyPrint on Windows (detect via
   `sys.platform == 'win32'`), ReportLab last.
2. Build a proper `_html_to_pdf_reportlab()` that parses structured data (not raw HTML) using
   Platypus `Table`, `Paragraph`, and `SimpleDocTemplate`.
3. For boletas: build a dedicated `generar_boleta_pdf(planilla_id)` method using Platypus directly
   — bypassing the HTML-to-PDF chain entirely.

**Why not add a new library (e.g., pdfkit/wkhtmltopdf):** wkhtmltopdf requires a system binary
and is not maintained. PyMuPDF (fitz) is for reading/manipulating existing PDFs, not generating
from data. The existing three-library chain with corrected priority order is sufficient.

**Confidence: HIGH (Windows constraint), HIGH (ReportLab capability), MEDIUM (xhtml2pdf CSS
fidelity for complex layouts)**

---

### MySQL Driver — Needs Requirements.txt Fix

**Decision: Add `mysqlclient` to `requirements.txt`. Remove `psycopg2-binary`.**

The venv has `mysqlclient` (confirmed via `django.db.backends.mysql` in logs) but
`requirements.txt` declares `psycopg2-binary` (PostgreSQL). `development.py` also configures
PostgreSQL. This is a documentation/configuration mismatch that will cause failures on fresh
installs.

```
# requirements.txt change:
# Remove: psycopg2-binary>=2.9.0
# Add:    mysqlclient>=2.2.0
```

Also: `development.py` DATABASE ENGINE must be changed to `django.db.backends.mysql`.

**Confidence: HIGH** — Confirmed by Django log file showing mysql backend in use.

---

### Frontend File Upload — react-dropzone

**Decision: Add `react-dropzone` for the file upload UI component.**

The current frontend has no file upload component. `react-dropzone` is the standard React library
for drag-and-drop file inputs. It integrates with `react-hook-form` (already in use) via the
`useController` pattern, and it is lightweight (~15KB) with no heavy dependencies.

```bash
npm install react-dropzone
```

**Why react-dropzone over alternatives:**
- Native `<input type="file">`: no drag-and-drop, no visual feedback, bad UX for legajo upload
- `filepond`: feature-rich but large, requires server plugin configuration
- `uppy`: even larger, designed for direct-to-S3 uploads — overkill for proxied multipart uploads

The upload flow is: browser → Vite proxy → Django DRF `MultiPartParser` → `DocumentosDigitales`.
This does not need a dedicated upload library with chunked upload support. `react-dropzone`
handles the drag-drop UX; `axios` (already installed) sends the `FormData`.

**Usage pattern with react-hook-form:**

```typescript
// In onboarding upload component
import { useDropzone } from 'react-dropzone'
import { useController } from 'react-hook-form'

function DocumentUploadField({ name, control, accept }) {
  const { field } = useController({ name, control })
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept,
    maxSize: 10 * 1024 * 1024, // 10MB
    onDrop: (files) => field.onChange(files[0])
  })
  // ...
}
```

**Confidence: HIGH** — Well-established library, clear integration path with existing stack.

---

### Frontend PDF Viewer

**Decision: `react-pdf` is already installed (`^10.3.0`). No addition needed.**

`react-pdf` (by wojtekmaj, based on PDF.js) is already in `package.json`. Use it for the legajo
digital document preview panel. The only work needed is building the component.

---

## Complete Addition Summary

### Backend — Requirements.txt Changes

```diff
- psycopg2-binary>=2.9.0
+ mysqlclient>=2.2.0
```

Everything else (`reportlab`, `xhtml2pdf`, `openpyxl`, `pillow`, `celery`, `redis`,
`django-storages`, `boto3`) is already declared and installed.

### Frontend — New Package

```bash
npm install react-dropzone
# Current version: ^14.x (verify at install time)
```

Everything else (`react-pdf`, `react-hook-form`, `axios`, `@tanstack/react-query`, `zod`,
`sonner`) is already installed and covers all new feature requirements.

---

## Configuration Work Required (No New Libraries)

| Area | What to Configure | Where |
|------|------------------|-------|
| Email SMTP | `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, credentials | `production.py` / `.env` |
| Email dev test | Switch from `console` to `locmem` backend for automated tests | `testing.py` |
| File upload limits | `FILE_UPLOAD_MAX_MEMORY_SIZE = 10MB` | `base.py` |
| Media URL serving | `static(MEDIA_URL, ...)` in `urlpatterns` | `config/urls.py` |
| MySQL driver | Change ENGINE to `django.db.backends.mysql` | `development.py` |
| Django-storages | Add `'storages'` to `INSTALLED_APPS` for S3 (production) | `production.py` |
| Celery broker | Verify Redis is running; Celery config is complete in `base.py` | Infrastructure |
| ReportLab stub | Replace placeholder text output with real Platypus layout | `pdf_generator.py` |

---

## What NOT to Use

| Library | Why Not |
|---------|---------|
| `django-anymail` | No ESP integration needed; plain SMTP to institutional relay is correct |
| `xlsxwriter` | Write-only; openpyxl can read and write; one library is enough |
| `pandas` | Heavyweight for simple row/column Excel writing; openpyxl is sufficient |
| `pdfkit` / `wkhtmltopdf` | Requires unmaintained system binary; worse than xhtml2pdf on Windows |
| `WeasyPrint` (as primary) | GTK dependency unavailable on Windows; already in fallback chain, keep there |
| `filepond` / `uppy` (React) | Overengineered for server-proxied multipart uploads; react-dropzone is enough |
| `react-query-file-upload` | Not a real package; axios + FormData is the correct pattern |
| `celery-beat` | Not needed for v1; scheduled tasks (contract expiry alerts) can wait |

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Email | Django built-in SMTP | django-anymail | No ESP needed; SMTP relay is sufficient |
| Excel | openpyxl (existing) | xlsxwriter | Cannot read templates; openpyxl does both |
| Excel | openpyxl (existing) | pandas | Overkill; 10x more dependency weight |
| PDF (Windows) | xhtml2pdf + ReportLab | WeasyPrint | GTK missing on Windows |
| File upload UI | react-dropzone | filepond | Simpler; no server plugin needed |
| File storage | FileSystemStorage (local) + S3 (prod) | MinIO | S3-compatible already supported |
| MySQL driver | mysqlclient | PyMySQL | mysqlclient already installed; faster |

---

## Sources

- Django 4.2 email documentation: https://docs.djangoproject.com/en/4.2/topics/email/ (HIGH)
- Django 4.2 file upload documentation: https://docs.djangoproject.com/en/4.2/ref/files/uploads/ (HIGH)
- Django 4.2 file settings: https://docs.djangoproject.com/en/4.2/ref/settings/#file-upload-settings (HIGH)
- Django 4.2 validators: https://docs.djangoproject.com/en/4.2/ref/validators/ (HIGH)
- Django 4.2 static/media files: https://docs.djangoproject.com/en/4.2/howto/static-files/ (HIGH)
- Project requirements.txt: D:/INTRANET/back/requirements.txt (HIGH — primary source)
- Project settings base.py: D:/INTRANET/back/config/settings/base.py (HIGH — primary source)
- Project onboarding_service.py: D:/INTRANET/back/app_rrhh/services/onboarding_service.py (HIGH)
- Project pdf_generator.py: D:/INTRANET/back/app_rrhh/services/pdf_generator.py (HIGH)
- Django logs confirming MySQL backend: D:/INTRANET/back/logs/django.log (HIGH)
- openpyxl capabilities: MEDIUM confidence (training data; official docs access restricted in session)
- AFP Net / PDT-PLAME format: LOW confidence (verify against current SUNAT/AFP documentation)
