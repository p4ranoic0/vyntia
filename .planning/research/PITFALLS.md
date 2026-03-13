# Domain Pitfalls

**Domain:** Django HR system (Windows) — email, file uploads, Excel exports, payroll calculations
**Project:** Sistema de Gestión de RRHH — Intranet
**Researched:** 2026-03-13
**Source basis:** Direct codebase analysis (HIGH confidence) + Django/Python domain knowledge (MEDIUM confidence)

---

## Critical Pitfalls

Mistakes that cause rewrites, data loss, or silent production failures.

---

### Pitfall 1: Celery Dependency for Email — Silent Failure on Missing Broker

**What goes wrong:** `enviar_email_bienvenida` calls `send_email_html_task.delay()` (Celery async). If Redis/Celery is not running, `task.delay()` raises an exception that is caught by a bare `except Exception` block, which then falls back to synchronous SMTP. But if SMTP is also unconfigured (development uses `ConsoleEmailBackend`), the synchronous path silently swallows the error and returns `False`. The caller in `crear_onboarding_completo` does not check the return value. The employee is created, onboarding starts, but no email is sent — exactly the bug triggered by `ggarcia`.

**Why it happens:** Two layers of silent exception handling mask both the Celery failure and the SMTP failure. The `@transaction.atomic` block commits the employee record before the email attempt, so there is no rollback signal to the caller.

**Consequences:** Employee created successfully in DB, no welcome email sent, RRHH believes onboarding triggered, employee has no credentials. No log entry at ERROR level unless the synchronous fallback also fails.

**Warning signs:**
- Employee exists in DB but never received credentials
- Celery worker not running (`celery -A config.celery worker` never started)
- `EMAIL_BACKEND = console.EmailBackend` in active settings (emails go to terminal, not to recipient)
- `send_email_html_task.delay()` raises `kombu.exceptions.OperationalError` in logs

**Prevention:**
1. Check email delivery result in `crear_onboarding_completo` and raise or log at ERROR if `False`
2. Add a smoke test: after onboarding creation, verify email was queued (Celery task ID returned)
3. In development: use `django.core.mail.backends.filebased.EmailBackend` with a watched folder, not console — so emails are inspectable without a live SMTP server
4. Never silently swallow email failures in an HR system — at minimum write `logger.error()` with the employee ID and error detail

**Phase:** Email / Onboarding phase (immediate fix — this is the known bug for `ggarcia`)

---

### Pitfall 2: PDF Generation Falls Back to Stub — No Actual Document Content

**What goes wrong:** The PDF generation chain is xhtml2pdf → WeasyPrint → ReportLab. On Windows, WeasyPrint fails (GTK dependency absent) and xhtml2pdf frequently errors on complex HTML. ReportLab is the reliable fallback, but the current `_html_to_pdf_reportlab` implementation does NOT parse or render the HTML template — it outputs a hardcoded stub: `"DOCUMENTO GENERADO"` with a single placeholder paragraph. Contracts, certificates, and boletas saved to `DocumentosDigitales` contain useless content even though the record shows `formato_archivo='pdf'` and `estado_documento='activo'`.

**Why it happens:** Implementing a full HTML-to-PDF pipeline with ReportLab requires a custom HTML parser (not included). The stub was written as a placeholder but the fallback path is always hit on Windows, making the stub the de facto production behavior.

**Consequences:** All generated PDFs (contracts, certificates, boletas) are empty stubs. Employees download blank documents. RRHH cannot detect the failure because the API returns HTTP 200 and the document record looks valid.

**Warning signs:**
- Downloaded PDFs show "DOCUMENTO GENERADO" header only
- `WEASYPRINT_AVAILABLE = False` in logs from `obtener_configuracion_disponible()`
- xhtml2pdf silently errors on templates with CSS `@page` rules or non-ASCII characters
- `motor_preferido` always returns `'ReportLab'` from the config endpoint

**Prevention:**
1. Commit to xhtml2pdf as the primary engine on Windows — it handles most HR document HTML if templates avoid advanced CSS. WeasyPrint stays as secondary only
2. Add an integration test that generates a real contract PDF and asserts `len(pdf_bytes) > 5000` and that specific employee name appears in raw bytes
3. Never deploy `_html_to_pdf_reportlab` as a production path — mark it explicitly as emergency stub only and add a health-check endpoint that reveals current PDF engine status
4. Django template gotcha applies here: all `{% %}` and `{{ }}` tags in PDF templates must open and close on the same line

**Phase:** PDF generation / Document generation phase

---

### Pitfall 3: Settings Mismatch — Development Uses PostgreSQL, Runtime Uses MySQL

**What goes wrong:** `development.py` sets `ENGINE: django.db.backends.postgresql` with postgres defaults. The actual running environment uses MySQL (`bd_rrhh_intranet`, `root`, localhost:3306). This mismatch means migrations run against a different engine in CI/testing than in production, schema differences (e.g., `AUTO_INCREMENT` vs `SERIAL`, JSON field behavior, case-sensitivity of queries) may not surface until production.

**Why it happens:** The settings file was copied from a PostgreSQL template and never updated to match the real MySQL environment. CLAUDE.md notes this explicitly: "The actual running environment uses MySQL."

**Consequences:** Queries that work in MySQL may fail in PostgreSQL tests, or vice versa. Custom PK field behavior differs. MySQL's case-insensitive string comparisons can mask bugs. `ATOMIC_REQUESTS=True` in development.py has different transaction semantics in MySQL InnoDB vs PostgreSQL.

**Warning signs:**
- `python manage.py migrate --settings=config.settings.development` fails with MySQL connection errors
- Tests pass in CI (PostgreSQL) but fail in dev (MySQL) or vice versa
- `unique_together = [['empleado', 'tipo_documento', 'numero_documento', 'version']]` on `DocumentosDigitales` — case sensitivity differs between engines

**Prevention:**
1. Align `development.py` DB settings to MySQL immediately — or create a `development_local.py` that overrides with MySQL config
2. Add a settings validation check that warns when `ENGINE` does not match the actual DB
3. Run migrations and tests against MySQL (the real engine), not PostgreSQL

**Phase:** Infrastructure / Settings cleanup (pre-requisite for all other phases)

---

### Pitfall 4: File Upload Without Size Enforcement at Django Layer

**What goes wrong:** `DocumentosDigitales.archivo` uses `FileExtensionValidator` only — no `MaxValueValidator` or custom validator for file size. Production settings set `DATA_UPLOAD_MAX_MEMORY_SIZE = 5MB` and `FILE_UPLOAD_MAX_MEMORY_SIZE = 5MB`, but this is a server-wide limit, not per-field. A user can upload a 4.9MB file for every document type without Django rejecting it. Over time, `media/documentos_empleados/` accumulates gigabytes with no per-employee or per-document-type quota.

**Why it happens:** Django's `FileField` does not natively support size limits — developers forget to add a custom validator or serializer-level check.

**Consequences:** Disk fills up on Windows server. Large file uploads block the Django request thread (no async file handling in standard DRF). PDF scans from employees (photos of documents) are commonly 5-15MB.

**Warning signs:**
- No `validate_file_size` function in serializers or models
- `upload_to='documentos_empleados/%Y/%m/'` accumulates files without cleanup
- No `DATA_UPLOAD_MAX_MEMORY_SIZE` override per view
- Media folder grows unboundedly

**Prevention:**
1. Add a `validate_file_size(max_mb=10)` validator to `DocumentosDigitales.archivo` — enforce at model level, not just nginx/settings
2. Add per-type limits in serializers: photos max 2MB (PNG/JPG), documents max 10MB (PDF)
3. Add frontend-side size check before upload to give immediate feedback
4. Implement file cleanup: when `crear_nueva_version` creates a new version, archive (or delete) the old physical file, not just the DB record

**Phase:** File uploads / Onboarding document phase

---

### Pitfall 5: Decimal Precision Loss in Payroll Calculations

**What goes wrong:** Payroll calculations use `Decimal` correctly in most places, but intermediate values pass through `float()` in the result dict: `"total_neto_pagar": float(planilla.total_neto_pagar)`. JSON serialization then loses precision. More critically, the AFP calculation uses `Decimal(str(detalle.dias_laborados)) / Decimal(str(dias_mes))` — if `dias_laborados` comes from the DB as a Python `int` or `float` (MySQL field type), converting to `str` first is correct, but many other places do `Decimal("10.00") / Decimal("100")` which is exact, while others may accidentally do `base_calculo * 10 / 100` (integer division risk) or mix `float` constants.

**Why it happens:** Python's `Decimal` arithmetic is safe but requires discipline. Mixing `float` and `Decimal` raises `TypeError` in Python 3, but `int` mixed with `Decimal` silently converts, which can cause scale issues in aggregated sums.

**Consequences:** Planilla totals off by centimos. AFP/ONP deductions differ from SUNAT's expected values. PDT-PLAME export fails SUNAT validation if amounts have wrong decimal scale. Discrepancies detected only during audit.

**Warning signs:**
- `float()` wrapping of Decimal values before JSON serialization
- `Sum("total_haberes")` returning `None` when planilla has no detalles (handled with `or Decimal("0.00")` — correct)
- AFP `vigencia_mes` lookup fails (no config for period) → falls back to hardcoded rates `1.47%` commission — these are outdated (AFP rates change annually)
- `_calcular_essalud` uses `modalidad in ["subsidio", "locacion", "consultoria"]` as CAS proxy — this mapping may not match the actual business rule for all contract types

**Prevention:**
1. Never use `float()` in payroll result serialization — use `str(value)` or format to 2 decimal places: `f"{value:.2f}"`
2. Validate AFP rates annually — `ConfiguracionAfp` table must be populated per period; add a pre-calculation check that raises if no `ConfiguracionAfp` exists for the target period
3. Add unit tests for each calculation method with known inputs and expected Peruvian law outputs
4. The `renta_quinta_categoria` field stores 4th-category retention but is named for 5th category — clarify naming to avoid applying the wrong rate

**Phase:** Remuneraciones / Payroll calculation phase

---

## Moderate Pitfalls

### Pitfall 6: Email Sent to `correo_personal` — Not Institutional Email

**What goes wrong:** `enviar_email_bienvenida` sends to `empleado.correo_personal`. For onboarding, the employee has not yet received institutional email credentials — sending to personal email is correct. But for other HR notifications (vacation approvals, document rejections), the code may inconsistently use `empleado.correo_personal` vs `usuario.email`. If the employee updates their personal email in the system and the two fields diverge, notification routing breaks.

**Prevention:** Establish a single canonical `get_notification_email(empleado)` helper that applies a priority rule (institutional email if set and active, else personal email). Use it everywhere.

**Phase:** Email / Notification phase

---

### Pitfall 7: Vacation Balance Uses `relativedelta` — Edge Cases with Contract Gaps

**What goes wrong:** `VacationCalculationService` uses `dateutil.relativedelta` for period calculations (correct for month-accurate accrual). But `obtener_contrato_activo` filters `estado='ACTIVO'` only — if a worker has a gap between contracts (e.g., ended one contract, started a new one 3 days later), the vacation period resets. For Peruvian public sector workers with consecutive CAS contracts, accumulated vacation is typically continuous, not reset per contract.

**Prevention:** Validate with legal/HR team whether vacation accrual is per-contract or continuous. The calculation service must handle the "linked contracts" case where total seniority spans multiple consecutive contract records.

**Phase:** Vacaciones / Vacation calculation phase

---

### Pitfall 8: `unique_together` on DocumentosDigitales Will Break Null `numero_documento`

**What goes wrong:** `unique_together = [['empleado', 'tipo_documento', 'numero_documento', 'version']]` includes `numero_documento` which is `null=True, blank=True`. In MySQL, `NULL != NULL` in unique constraints, so multiple rows with `numero_documento=NULL` for the same employee and document type are allowed. This is actually correct behavior for MySQL, but if the project ever migrates to PostgreSQL, `NULL` comparisons in unique constraints differ and multiple nulls would still be allowed (PostgreSQL also allows multiple NULLs in unique constraints since NULLs are considered distinct).

**Prevention:** This is currently safe in MySQL. Document this known behavior. If employees upload multiple DNI copies without a `numero_documento`, duplicates will accumulate. Add application-level deduplication: before creating a new document, check if an active version already exists for the same `(empleado, tipo_documento)` combination and prompt for replacement.

**Phase:** File uploads / Legajo digital phase

---

### Pitfall 9: Excel Export Column Mapping for AFP Net / PDT-PLAME

**What goes wrong:** AFP Net and PDT-PLAME have strict column layouts defined by SUNAT/AFP regulations that change periodically. Hardcoding column positions or using generic `openpyxl` row writes without a schema validation step will produce files that fail SUNAT's validator. The PDT-PLAME format requires specific cell formats (text for DNI with leading zeros, dates as `DD/MM/YYYY` string, not Excel date serial).

**Warning signs:**
- DNI `07654321` exported as integer `7654321` (loses leading zero)
- Date cells exported as Excel serial numbers instead of formatted strings
- AFP Net requires specific sheet names, header rows, and field order

**Prevention:**
1. Build Excel export as a mapping from internal model fields to a validated schema object — not direct row writes
2. DNI and RUC fields: always export as `str` with zero-padding, not numeric
3. Date fields: use explicit format strings, not Excel date type
4. Add a post-export validator that reads back the file and checks key fields before allowing download

**Phase:** Excel export / Remuneraciones phase

---

### Pitfall 10: Windows Path Separators in `upload_to` and Template Paths

**What goes wrong:** Django's `FileField(upload_to='documentos_empleados/%Y/%m/')` uses forward slashes which Django normalizes correctly on Windows. But custom file path logic that concatenates with `os.path.join` on Windows produces backslash paths (`documentos_empleados\2026\03\file.pdf`) that may not match what the web server (nginx/IIS) expects for `MEDIA_URL` serving.

The `pdf_generator.py` stores files using `ContentFile` + Django's ORM (safe), but any code that builds paths manually using string concatenation or `os.path.join` on Windows will produce backslash paths.

**Prevention:**
1. Always use `pathlib.Path` for path construction and convert to forward slashes with `.as_posix()` when building URLs
2. Avoid `os.path.join` for paths that become URL components
3. Use Django's `default_storage.url(name)` to get the URL for a stored file — never build the URL manually from `MEDIA_ROOT + filename`

**Phase:** File uploads / Storage phase

---

### Pitfall 11: `APIResponse.error()` Defaults to 400 — Payroll Errors Look Like Validation Errors

**What goes wrong:** `APIResponse.error()` defaults to HTTP 400. In `PlanillaCalculoService`, exceptions are caught and re-raised as `RuntimeError`. If the view catches this and calls `APIResponse.error()` without specifying `status_code=500`, a calculation failure (server bug) looks like a bad request (client error). Frontend shows a validation error toast instead of a system error banner.

**Prevention:** In payroll and calculation views, always use explicit status codes: `APIResponse.error(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)` for server-side calculation failures. Reserve 400 for user input validation errors.

**Phase:** All backend phases — apply consistently

---

## Minor Pitfalls

### Pitfall 12: `production.py` Syntax Error at EOF

**What goes wrong:** `production.py` ends with a duplicate line: `ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')` — this is a syntax error that will crash Django startup in production. Development uses `development.py` which does not have this issue, so it goes undetected until a production deploy.

**Prevention:** Fix immediately. Run `python -c "import config.settings.production"` as part of CI to catch syntax errors in all settings files.

**Phase:** Immediate fix — pre-requisite for production deploy

---

### Pitfall 13: Celery/Redis Not Running — Email and Async Tasks Silently Fall Back

**What goes wrong:** `base.py` configures Celery with Redis (`redis://127.0.0.1:6379/1`) but Redis is not guaranteed to be running on the Windows development machine. `send_email_html_task.delay()` will fail silently (caught exception), rate limiting and other commented-out Celery tasks will never run, and any future async work will have the same silent-failure pattern.

**Prevention:** Add a startup check or management command that verifies Celery worker connectivity. In development, document that `redis-server` and `celery -A config.celery worker --loglevel=info` must be running. Consider `django-celery-results` to track task status in DB so failures are visible.

**Phase:** Email / Infrastructure phase

---

### Pitfall 14: `tamano_archivo_legible` Property Mutates `self.tamano_archivo`

**What goes wrong:** In `DocumentosDigitales`, the property `tamano_archivo_legible` divides `self.tamano_archivo` in-place (`self.tamano_archivo /= 1024.0`) during the loop. This mutates the instance attribute, so calling `tamano_archivo_legible` twice on the same instance returns different (wrong) values, and any subsequent `self.save()` call will persist the corrupted `tamano_archivo` to the database.

**Prevention:** Fix to use a local variable: `size = self.tamano_archivo` and operate on `size` only.

**Phase:** Immediate fix — data integrity bug

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Email / Onboarding | Celery not running → silent no-send (ggarcia bug) | Validate email delivery; use sync fallback with explicit error |
| Email / Onboarding | `ConsoleEmailBackend` in dev swallows emails | Switch to `FileBasedEmailBackend` in dev; SMTP in staging |
| File uploads | No per-file size validation | Add `validate_file_size` validator to `DocumentosDigitales` |
| File uploads | Windows path backslash in media URLs | Use `pathlib.Path.as_posix()` for all URL construction |
| File uploads | `tamano_archivo_legible` mutates DB field | Fix property bug before bulk document upload goes live |
| PDF generation | ReportLab fallback is a stub, not real render | Use xhtml2pdf as primary; test with real document content |
| PDF generation | Django template tags multi-line → parse error | All `{% %}` and `{{ }}` on single line in PDF templates |
| Excel export (AFP Net) | DNI as integer loses leading zero | Serialize DNI/RUC as zero-padded string |
| Excel export (PDT-PLAME) | Date as Excel serial number fails SUNAT | Explicit string date format `DD/MM/YYYY` |
| Payroll calculations | AFP rates hardcoded as fallback (outdated) | Require `ConfiguracionAfp` record per period; no silent fallback |
| Payroll calculations | `float()` in result serialization loses precision | Use `str()` or `Decimal.quantize()` before JSON |
| Payroll calculations | 4th vs 5th category field naming confusion | Clarify: `renta_quinta_categoria` stores 4th-category retention |
| Vacation approval | Consecutive contracts reset accrual | Confirm with HR: is accrual per-contract or continuous? |
| Settings | `development.py` points to PostgreSQL, runtime is MySQL | Align DB settings immediately |
| Settings | `production.py` has syntax error at EOF | Fix and add CI settings import check |
| All views | `APIResponse.error()` defaults to 400 | Explicitly pass `status_code=500` for server-side failures |

---

## Sources

- Direct codebase analysis: `D:\INTRANET\back\app_rrhh\services\` (HIGH confidence)
- Direct codebase analysis: `D:\INTRANET\back\config\settings\` (HIGH confidence)
- Direct codebase analysis: `D:\INTRANET\back\app_rrhh\models\documentos_digitales.py` (HIGH confidence)
- Django documentation: file upload validators, email backends, Decimal handling (HIGH confidence)
- Peruvian labor law context from PROJECT.md: AFP/ONP/PDT-PLAME requirements (MEDIUM confidence — legislative details need HR validation)
- CLAUDE.md project instructions: known pitfalls for this codebase (HIGH confidence)
