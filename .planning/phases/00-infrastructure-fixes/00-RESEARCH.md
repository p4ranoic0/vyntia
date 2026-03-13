# Phase 0: Infrastructure Fixes - Research

**Researched:** 2026-03-13
**Domain:** Django settings, Python model properties, PDF generation on Windows, requirements.txt hygiene
**Confidence:** HIGH — all four bugs were verified by direct source file inspection

---

## Summary

Phase 0 is four surgical fixes to known, located bugs. No new libraries are needed. No new features
are added. The work is bounded: find the exact broken line, understand why it breaks, write the
correct version, add a test that would have caught it, done.

The bugs are independent of each other. They can be fixed in any order and by different plan
steps. None of the fixes requires a migration. None touches the frontend.

The highest-risk fix is INFRA-03 (PDF generation). The change is simple in principle — promote
xhtml2pdf to a reliable primary path, demote the ReportLab stub to never-used last resort — but
requires an integration test with a real HTML template to prove it works end-to-end on Windows.
The other three fixes (settings syntax error, requirements driver, property mutation) are
one-to-five line changes that are trivially verified.

**Primary recommendation:** Fix all four bugs in a single phase. Sequence: INFRA-01 and INFRA-02
first (no risk, immediate), INFRA-04 second (one-liner, pure correctness), INFRA-03 last (requires
test harness to validate on Windows).

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFRA-01 | Django starts in production without settings syntax error | production.py line 161 confirmed: duplicate ADMIN_URL assignment on same line — SyntaxError at import time |
| INFRA-02 | requirements.txt declares mysqlclient, not psycopg2 | requirements.txt line 10 confirmed: `psycopg2-binary>=2.9.0`; development.py lines 52-72 confirmed: PostgreSQL ENGINE; mysqlclient confirmed in use via logs |
| INFRA-03 | Generated PDFs contain real document content (xhtml2pdf as primary on Windows) | pdf_generator.py lines 207-229 confirmed: xhtml2pdf already first in chain; lines 324-364 confirmed: ReportLab path outputs hardcoded "DOCUMENTO GENERADO" stub; xhtml2pdf must be made reliable |
| INFRA-04 | tamano_archivo_legible does not mutate tamano_archivo in the database | documentos_digitales.py line 251 confirmed: `self.tamano_archivo /= 1024.0` — in-place mutation of instance field |
</phase_requirements>

---

## Bug Inventory (Direct Source Evidence)

### Bug 1 — INFRA-01: SyntaxError in production.py

**File:** `back/config/settings/production.py`, line 161

**Exact broken line:**
```python
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')
```

**What happens:** Python raises `SyntaxError` when this module is imported. Django cannot start in
production. Development is unaffected because `development.py` does not have this line.

**Fix:** Remove the duplicate. Keep one assignment:
```python
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')
```

**Scope:** One line deleted. No migration. No other file affected.

**Verification command:**
```bash
cd D:/INTRANET/back && D:/INTRANET/.venv/Scripts/python.exe -c "import config.settings.production"
```
Must exit 0 with no output.

---

### Bug 2 — INFRA-02: Wrong database driver in requirements.txt and development.py

**File 1:** `back/requirements.txt`, line 10
```
psycopg2-binary>=2.9.0   ← declares PostgreSQL driver
```

**File 2:** `back/config/settings/development.py`, lines 52-72
```python
"ENGINE": "django.db.backends.postgresql",   ← wrong engine
"USER": os.environ.get("DB_USER", "postgres"),
"PORT": os.environ.get("DB_PORT", "5432"),
```

**What happens on a fresh install:** `pip install -r requirements.txt` installs psycopg2, not
mysqlclient. Running `manage.py migrate --settings=config.settings.development` tries to connect to
PostgreSQL on port 5432, which does not exist. The actual database is MySQL on port 3306.

**Also broken in production.py:** `back/config/settings/production.py` lines 13-47 also declare
`django.db.backends.postgresql` with postgres defaults. Production is also misconfigured, though it
reads credentials from env vars which may override the defaults if set correctly.

**Fix — requirements.txt:**
```diff
- psycopg2-binary>=2.9.0
+ mysqlclient>=2.2.0
```

**Fix — development.py** (replace the DATABASES block):
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME", "bd_rrhh_intranet"),
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "connect_timeout": int(os.environ.get("DB_CONNECT_TIMEOUT", "10")),
        },
        "CONN_MAX_AGE": DATABASE_CONNECTION_POOLING["CONN_MAX_AGE"],
        "CONN_HEALTH_CHECKS": True,
        "ATOMIC_REQUESTS": True,
        "TEST": {
            "NAME": os.environ.get("DB_TEST_NAME", "test_bd_rrhh_intranet"),
        },
    }
}
```

**Fix — production.py:** Same ENGINE change. Remove PostgreSQL-specific OPTIONS keys
(`sslmode`, `options: -c default_transaction_isolation=...`, `client_encoding`) which are not valid
for mysqlclient. The `read_replica` block must also be updated.

**MySQL OPTIONS note:** mysqlclient does not accept `sslmode` in OPTIONS. Valid MySQL OPTIONS keys
include `charset`, `connect_timeout`, `ssl_ca`, `ssl_cert`, `ssl_key`. Remove all PostgreSQL-only
keys to prevent Django raising `django.db.utils.OperationalError` at startup.

**Verification command:**
```bash
cd D:/INTRANET/back && D:/INTRANET/.venv/Scripts/python.exe manage.py migrate --settings=config.settings.development --run-syncdb 2>&1 | head -5
```
Must show "Running migrations" or "No migrations to apply", not a connection error.

---

### Bug 3 — INFRA-03: ReportLab stub outputs "DOCUMENTO GENERADO" placeholder

**File:** `back/app_rrhh/services/pdf_generator.py`

**Root cause analysis:**

The `_html_to_pdf()` method (lines 207-229) already has xhtml2pdf first in the chain:
```python
if XHTML2PDF_AVAILABLE:
    try:
        return self._html_to_pdf_xhtml2pdf(html_content)
    except Exception:
        pass   ← silently falls through on ANY error
```

The xhtml2pdf path (lines 231-245) calls:
```python
result = pisa.CreatePDF(html_content.encode('utf-8'), dest=buffer, encoding='utf-8')
if result.err:
    raise ValidationError(f"Error xhtml2pdf: {result.err}")
```

**The problem:** `pisa.CreatePDF` sets `result.err` to a non-zero value when it encounters CSS it
cannot parse (e.g., `@page` rules with `counter(pages)`, `flexbox`, gradients). When `result.err`
is truthy, `ValidationError` is raised, the `except Exception: pass` in `_html_to_pdf()` swallows
it, and execution falls through to WeasyPrint (fails on Windows — no GTK) then to the ReportLab
stub which outputs:

```python
story.append(Paragraph("DOCUMENTO GENERADO", title_style))
story.append(Paragraph("Contenido del documento generado desde plantilla.", normal_style))
```

The `obtener_configuracion_disponible()` method (line 516) still reports `motor_preferido` as
`'WeasyPrint'` even when WeasyPrint is unavailable, which is also wrong.

**Two-part fix:**

**Part A — Make xhtml2pdf succeed on HR templates**

xhtml2pdf on Windows handles basic HTML and inline CSS well. The failure is caused by unsupported
CSS in the templates. The fix is to strip or isolate advanced CSS before passing to pisa, or to
ensure the HTML templates use only xhtml2pdf-compatible CSS.

The reliable approach: wrap the HTML in a minimal CSS-safe envelope before sending to xhtml2pdf:

```python
def _html_to_pdf_xhtml2pdf(self, html_content: str) -> bytes:
    buffer = BytesIO()
    # xhtml2pdf does not support @page counter(pages) — strip if present
    # Pass source_path for relative resource resolution
    result = pisa.CreatePDF(
        html_content.encode('utf-8'),
        dest=buffer,
        encoding='utf-8',
        raise_exception=False,
    )
    if result.err:
        raise ValidationError(f"Error xhtml2pdf (err={result.err}): check template CSS")
    pdf_bytes = buffer.getvalue()
    if len(pdf_bytes) < 100:
        raise ValidationError("xhtml2pdf produced empty output")
    return pdf_bytes
```

The key insight: `raise_exception=False` is already the default, but logging `result.err` value
(not just truthy check) helps diagnose template CSS issues. The minimum size check (`< 100 bytes`)
catches the case where xhtml2pdf produces a valid PDF header but no content.

**Part B — Fix the fallback indicator**

`obtener_configuracion_disponible()` must report truthfully. Change:
```python
'motor_preferido': 'xhtml2pdf' if XHTML2PDF_AVAILABLE else ('ReportLab' if REPORTLAB_AVAILABLE else 'none'),
```

Also add `'xhtml2pdf_disponible': XHTML2PDF_AVAILABLE` to the returned dict.

**What NOT to do:** Do not rewrite the ReportLab path to parse HTML. It is not the right tool for
HTML-to-PDF conversion and the work required is disproportionate. Keep it as an explicit emergency
stub with a clear warning log, but it should never be reached in normal operation on this server.

**Verification:** Integration test that generates a real contract PDF, asserts `len(pdf_bytes) >
5000`, and asserts the employee's `numero_documento` appears in the raw bytes. This is the only
reliable proof that real content was rendered.

---

### Bug 4 — INFRA-04: tamano_archivo_legible mutates tamano_archivo

**File:** `back/app_rrhh/models/documentos_digitales.py`, lines 243-252

**Exact broken code:**
```python
@property
def tamano_archivo_legible(self):
    """Retorna el tamaño del archivo en formato legible."""
    if not self.tamano_archivo:
        return "0 B"

    for unidad in ['B', 'KB', 'MB', 'GB']:
        if self.tamano_archivo < 1024.0:
            return f"{self.tamano_archivo:.1f} {unidad}"
        self.tamano_archivo /= 1024.0      ← MUTATES INSTANCE ATTRIBUTE
    return f"{self.tamano_archivo:.1f} TB"
```

**Why it corrupts data:** `self.tamano_archivo /= 1024.0` modifies the instance attribute in-place.
`tamano_archivo` is a `BigIntegerField`. After calling `tamano_archivo_legible` on an instance
whose file is 2MB (2,097,152 bytes):

- After 1st division: `self.tamano_archivo = 2048.0` (the value "KB")
- After 2nd division: `self.tamano_archivo = 2.0` (the value "MB")

If any subsequent code calls `instance.save()` — and `validar_documento()`, `rechazar_documento()`,
`crear_nueva_version()`, `marcar_como_vencido()`, `renovar_documento()`, `archivar_documento()`,
`cambiar_nivel_acceso()`, `agregar_palabras_clave()` all call `self.save()` — the corrupted value
`2.0` is written to `tamano_archivo` in the database. The field then reads as 2 bytes, not 2MB.

**Also:** calling `tamano_archivo_legible` twice on the same in-memory instance returns different
results (first call may return "2.0 MB", second call would advance to "0.002 GB").

**Fix:**
```python
@property
def tamano_archivo_legible(self):
    """Retorna el tamaño del archivo en formato legible."""
    if not self.tamano_archivo:
        return "0 B"

    size = float(self.tamano_archivo)   # local copy, never touch self
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unidad}"
        size /= 1024.0
    return f"{size:.1f} TB"
```

**Scope:** Four lines changed. No migration (field definition unchanged). No other files affected.

**Verification:** Unit test that creates an instance with `tamano_archivo=2097152`, calls
`tamano_archivo_legible` twice, asserts both return `"2.0 MB"`, and asserts
`instance.tamano_archivo == 2097152` after both calls.

---

## Standard Stack

No new libraries are needed for Phase 0.

### What is already installed and used

| Component | Library | Version in requirements.txt | Status |
|-----------|---------|----------------------------|--------|
| PDF generation | xhtml2pdf | `>=0.2.17` | Installed, broken configuration |
| PDF fallback | reportlab | `>=4.0.0` | Installed, stub output only |
| PDF (Windows failure) | weasyprint | `>=60.0` | Installed, fails (no GTK) |
| DB driver (actual) | mysqlclient | not in requirements.txt | Installed in venv, not declared |
| DB driver (declared) | psycopg2-binary | `>=2.9.0` | Declared, wrong |
| Test framework | pytest + pytest-django | `>=7.0.0` | Installed, configured |

### Installation change required

```diff
# back/requirements.txt
- psycopg2-binary>=2.9.0
+ mysqlclient>=2.2.0
```

```bash
# After editing requirements.txt (from back/ directory with venv active):
pip install -r requirements.txt
```

mysqlclient is already installed in the venv; this makes the requirements file match reality.

---

## Architecture Patterns

### Settings layer structure

```
config/settings/
├── base.py          — shared config (DATABASE_CONNECTION_POOLING used in overrides)
├── development.py   — extends base, overrides DB, email, CORS
├── production.py    — extends base, reads from env vars
├── staging.py       — (not investigated, not in scope)
└── testing.py       — extends base, used by pytest (DJANGO_SETTINGS_MODULE)
```

Each settings override file does `from .base import *` then overrides specific keys. The
`DATABASE_CONNECTION_POOLING` dict is defined in `base.py` and referenced by `development.py` and
`production.py` when building the DATABASES dict. Do not remove it.

### Pattern: Python property without side effects

The canonical Python pattern for a computed display property:

```python
@property
def tamano_archivo_legible(self):
    size = float(self.tamano_archivo)   # local variable only
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unidad}"
        size /= 1024.0
    return f"{size:.1f} TB"
```

Rule: `@property` methods must never assign to `self.*` fields unless the explicit purpose is to
update the model. Display/format properties must operate on local variables.

### Pattern: xhtml2pdf reliable invocation

```python
from io import BytesIO
from xhtml2pdf import pisa

def _html_to_pdf_xhtml2pdf(self, html_content: str) -> bytes:
    buffer = BytesIO()
    result = pisa.CreatePDF(
        html_content.encode('utf-8'),
        dest=buffer,
        encoding='utf-8',
    )
    if result.err:
        raise ValidationError(
            f"xhtml2pdf conversion error (code={result.err}). "
            "Check template for unsupported CSS (@page counters, flexbox)."
        )
    pdf_bytes = buffer.getvalue()
    if len(pdf_bytes) < 100:
        raise ValidationError("xhtml2pdf produced empty or malformed PDF output.")
    return pdf_bytes
```

The `result.err` field is an integer: 0 means success. Non-zero means at least one rendering error
occurred. For HR documents, any rendering error should propagate (not be silently swallowed)
because the document is going to be read by a human.

### Anti-Patterns to Avoid

- **Silent `except Exception: pass` on all PDF engines:** This hides the actual error. The planner
  should change the fallback to log the error at WARNING level before falling through.
- **`self.field /= value` inside `@property`:** Never. Always use a local variable.
- **Settings declaring wrong ENGINE with PostgreSQL-only OPTIONS keys:** When changing ENGINE to
  MySQL, also audit and remove PostgreSQL-only OPTIONS (`sslmode`, `options: -c ...`,
  `client_encoding`) which cause `ImproperlyConfigured` on MySQL.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| HTML to PDF on Windows | Custom HTML parser + PDF writer | xhtml2pdf (already installed) |
| File size display | Custom unit conversion mutating state | Simple local-variable loop (5 lines) |
| Settings import validation | Custom CI check script | `python -c "import config.settings.production"` |

---

## Common Pitfalls

### Pitfall 1: production.py also uses PostgreSQL ENGINE
**What goes wrong:** Only fixing `development.py` leaves `production.py` pointing at PostgreSQL.
**How to avoid:** Fix both files in INFRA-02. The production DATABASES block (lines 13-47) and the
`read_replica` block both declare PostgreSQL ENGINE. Both must be changed to MySQL. The `read_replica`
entry should likely be removed or kept as a copy of default for now — it adds operational complexity.

### Pitfall 2: PostgreSQL-only OPTIONS keys break MySQL at startup
**What goes wrong:** `OPTIONS: {'sslmode': 'require', 'options': '-c default_transaction_isolation=...'}`
are psycopg2-specific. mysqlclient will raise `django.db.utils.OperationalError: (2003, "Can't
connect to MySQL server")` or `TypeError` when these keys are passed. They must be removed when
switching to MySQL ENGINE.
**How to avoid:** For MySQL, OPTIONS should only contain: `{'charset': 'utf8mb4', 'connect_timeout': N}`.

### Pitfall 3: xhtml2pdf silently produces valid (but near-empty) PDF
**What goes wrong:** xhtml2pdf returns `result.err = 0` but writes a 1KB PDF with only the PDF
header and no visible content, when the HTML references external CSS files that cannot be resolved.
**How to avoid:** Assert `len(pdf_bytes) > 5000` in the integration test. A real contract should
be several KB minimum.

### Pitfall 4: tamano_archivo_legible called via serializer before save
**What goes wrong:** If a serializer reads `tamano_archivo_legible` on a freshly-created instance
(e.g., for the API response after upload), the buggy property corrupts the in-memory value. If the
view then calls `documento.save()` to update any field, the corrupted size is written to the DB.
**How to avoid:** Fix the property first. The serializer usage is safe after the fix because the
local-variable version never modifies `self`.

### Pitfall 5: Testing settings use PostgreSQL too
**What goes wrong:** `testing.py` (loaded by pytest via `DJANGO_SETTINGS_MODULE`) may also declare
PostgreSQL. If not fixed, `make test` will fail to connect to MySQL.
**How to avoid:** Audit `testing.py` as part of INFRA-02 and align to MySQL. (Not yet read — the
planner should include reading `testing.py` as a step.)

---

## Code Examples

### INFRA-01: Correct production.py last line

```python
# Source: direct inspection, back/config/settings/production.py line 161
# Before (broken):
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')

# After (correct):
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')
```

### INFRA-02: Correct MySQL DATABASES for development.py

```python
# Source: Django 4.2 MySQL documentation
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME", "bd_rrhh_intranet"),
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "connect_timeout": int(os.environ.get("DB_CONNECT_TIMEOUT", "10")),
        },
        "CONN_MAX_AGE": DATABASE_CONNECTION_POOLING["CONN_MAX_AGE"],
        "CONN_HEALTH_CHECKS": True,
        "ATOMIC_REQUESTS": True,
        "TEST": {
            "NAME": os.environ.get("DB_TEST_NAME", "test_bd_rrhh_intranet"),
            "CHARSET": "utf8mb4",
            "COLLATION": "utf8mb4_unicode_ci",
        },
    }
}
```

### INFRA-03: Fixed tamano_archivo_legible property

```python
# Source: direct inspection, back/app_rrhh/models/documentos_digitales.py lines 243-252
@property
def tamano_archivo_legible(self):
    """Retorna el tamaño del archivo en formato legible (read-only)."""
    if not self.tamano_archivo:
        return "0 B"
    size = float(self.tamano_archivo)
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unidad}"
        size /= 1024.0
    return f"{size:.1f} TB"
```

### INFRA-03: PDF generation with logging

```python
# Source: xhtml2pdf documentation pattern
def _html_to_pdf(self, html_content: str) -> bytes:
    import logging
    logger = logging.getLogger(__name__)

    if XHTML2PDF_AVAILABLE:
        try:
            return self._html_to_pdf_xhtml2pdf(html_content)
        except Exception as e:
            logger.warning("xhtml2pdf failed: %s — trying fallback", e)
    if WEASYPRINT_AVAILABLE:
        try:
            return self._html_to_pdf_weasyprint(html_content)
        except Exception as e:
            logger.warning("WeasyPrint failed: %s — trying fallback", e)
    if REPORTLAB_AVAILABLE:
        logger.error(
            "Using ReportLab stub — PDF will NOT contain real document content. "
            "Fix xhtml2pdf template CSS."
        )
        return self._html_to_pdf_reportlab(html_content)
    raise ValidationError("No hay librerías disponibles para generar PDF")
```

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 7+ + pytest-django |
| Config file | `back/setup.cfg` — `[tool:pytest]` section |
| DJANGO_SETTINGS_MODULE | `config.settings.testing` |
| Quick run command | `cd D:/INTRANET/back && D:/INTRANET/.venv/Scripts/python.exe -m pytest tests/ -x -q` |
| Full suite command | `cd D:/INTRANET/back && D:/INTRANET/.venv/Scripts/python.exe -m pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFRA-01 | `import config.settings.production` exits 0 | smoke | `python -c "import config.settings.production"` | ❌ Wave 0 |
| INFRA-02 | `migrate --settings=development` connects to MySQL | smoke | `python manage.py migrate --settings=config.settings.development --check` | ❌ Wave 0 |
| INFRA-03 | Generated PDF bytes contain real employee content | integration | `pytest tests/test_pdf_generation.py -x` | ❌ Wave 0 |
| INFRA-04 | `tamano_archivo_legible` called twice returns same value and does not change `tamano_archivo` | unit | `pytest tests/test_documentos_model.py::test_tamano_legible_no_muta -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `cd D:/INTRANET/back && D:/INTRANET/.venv/Scripts/python.exe -m pytest tests/ -x -q -m "not slow"`
- **Per wave merge:** `cd D:/INTRANET/back && D:/INTRANET/.venv/Scripts/python.exe -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `back/tests/test_documentos_model.py` — covers INFRA-04 unit test
- [ ] `back/tests/test_pdf_generation.py` — covers INFRA-03 integration test (needs a minimal HTML fixture)
- [ ] `back/tests/test_settings_import.py` — covers INFRA-01 smoke test (or use pytest subprocess call)

Note: INFRA-02 is best verified by running migrate directly, not a pytest test, since it requires a
live MySQL connection. The plan should include a manual verification step.

---

## Open Questions

1. **testing.py DATABASE ENGINE**
   - What we know: `testing.py` is loaded by pytest. It was not read in this research session.
   - What's unclear: Whether it also declares PostgreSQL ENGINE, which would cause `make test` to fail.
   - Recommendation: Planner should include "read and fix testing.py" as a step in INFRA-02.

2. **production.py read_replica block**
   - What we know: There is a `read_replica` database config block in production.py that also uses PostgreSQL.
   - What's unclear: Whether any code uses `using('read_replica')` or `DATABASE_ROUTERS` that route to it.
   - Recommendation: Check for `using('read_replica')` in codebase. If not used, remove the block to reduce maintenance surface. If used, fix ENGINE to MySQL.

3. **xhtml2pdf and PDF template CSS compatibility**
   - What we know: xhtml2pdf fails on CSS it cannot parse (WeasyPrint-style `@page` with `counter(pages)`).
   - What's unclear: Which specific CSS rules in the existing PDF templates cause `result.err != 0`.
   - Recommendation: The integration test (Wave 0 gap) will reveal this. The template CSS may need minor adjustment.

---

## Sources

### Primary (HIGH confidence — direct source inspection)

- `D:/INTRANET/back/config/settings/production.py` — INFRA-01 confirmed line 161
- `D:/INTRANET/back/config/settings/development.py` — INFRA-02 confirmed PostgreSQL ENGINE lines 52-72
- `D:/INTRANET/back/requirements.txt` — INFRA-02 confirmed `psycopg2-binary>=2.9.0` line 10
- `D:/INTRANET/back/app_rrhh/services/pdf_generator.py` — INFRA-03 confirmed stub lines 324-364, silent swallow lines 220-221
- `D:/INTRANET/back/app_rrhh/models/documentos_digitales.py` — INFRA-04 confirmed mutation line 251
- `D:/INTRANET/.planning/research/PITFALLS.md` — corroborates all four bugs
- `D:/INTRANET/.planning/research/STACK.md` — corroborates driver mismatch and PDF approach

### Secondary (MEDIUM confidence)

- Django 4.2 MySQL docs: valid OPTIONS keys for mysqlclient (`charset`, `connect_timeout`)
- xhtml2pdf pisa API: `result.err` semantics, `raise_exception` param

---

## Metadata

**Confidence breakdown:**
- Bug locations: HIGH — all four bugs found and read in source files
- Fixes: HIGH — all fixes are minimal, well-understood Python/Django patterns
- Integration test for PDF: MEDIUM — depends on which template CSS causes xhtml2pdf failures (requires runtime verification)
- MySQL OPTIONS keys: MEDIUM — training data confirms; Django docs not fetched during this session

**Research date:** 2026-03-13
**Valid until:** 2026-06-13 (stable domain — bugs don't change; 90 days is generous)
