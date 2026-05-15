"""Documents models — re-exports for backward-compatible imports."""

from .digital_document import DigitalDocument
from .digital_dossier import DigitalDossier, DossierSection
from .document_signature import DocumentSignature
from .document_template import DocumentTemplate
from .hiring_bundle import HiringBundleItem, HiringDocumentBundle

__all__ = [
    "DigitalDocument",
    "DigitalDossier",
    "DocumentSignature",
    "DocumentTemplate",
    "DossierSection",
    "HiringBundleItem",
    "HiringDocumentBundle",
]
