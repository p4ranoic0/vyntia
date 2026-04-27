"""AppConfig for the `apps.documents` Django app — VYNTIA digital documents.

Owns the document-management entities of the HR system:
- DigitalDocument (digital file storage for employee records — DNI scans,
  diplomas, certificates, contracts as PDF, etc., with versioning, validation
  state, access control levels, and metadata for SUNAT/legal compliance)
- DocumentTemplate (Word .docx templates with {{PLACEHOLDER}} markers used
  to generate certificates, constancias, contracts, and adendas)

Owned services (PDF/Word generation engines):
- pdf_generator.py — chain xhtml2pdf → WeasyPrint → ReportLab fallback
- template_service.py — HTML template rendering for PDF output
- word_template_service.py — python-docx based .docx generation

Bounded context boundary: documents owns the legajo digital and template
engines. Personal data lives in `apps.employees`. Contract data lives in
`apps.contracts`. Compensation data lives in `apps.payroll` (L3.7).

Future rename (deferred to L3.10):
- DigitalDocument → DigitalDocument
- DocumentTemplate → DocumentTemplate
"""

from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    name = "apps.documents"
    label = "documents"
    verbose_name = "VYNTIA Documents"
