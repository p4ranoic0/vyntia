"""Documents services — re-exports for backward-compatible imports.

PDF/Word generation engines for the HR document workflow.
"""

from . import access_service, bundle_service, dossier_service, signature_service
from .pdf_generator import PDFGenerator
from .template_service import TemplateService
from .word_template_service import WordTemplateService

__all__ = [
    "PDFGenerator",
    "TemplateService",
    "WordTemplateService",
    "access_service",
    "bundle_service",
    "dossier_service",
    "signature_service",
]
