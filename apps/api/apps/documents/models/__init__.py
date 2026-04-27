"""Documents models — re-exports for backward-compatible imports."""

from .digital_document import DigitalDocument
from .document_template import DocumentTemplate

__all__ = [
    "DigitalDocument",
    "DocumentTemplate",
]
