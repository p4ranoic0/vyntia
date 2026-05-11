"""MPP (Manual de Perfiles de Puestos) rendering service.

Per Maestro Module 02 § 2.2 + Ley 30057, the MPP is the public-sector
job-description manual: per-Position profile (mission, functions, requirements,
salary tier) for every plaza in the institution's CPE.

Architecture decision (B.8): MPP is a *rendering* of an approved CPE
(PositionRegister with register_type='cpe') × PositionProfile — not a separate
model. This service produces HTML and delegates PDF generation to the existing
PDFGenerator infrastructure (xhtml2pdf → WeasyPrint → ReportLab fallback).
"""
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string


def _resolve_institution(tenant):
    """Build a small dict of institutional data for the MPP header."""
    if tenant is None:
        return {
            'name': '',
            'ruc': '',
            'slug': '',
        }
    return {
        'name': tenant.name,
        'ruc': tenant.ruc,
        'slug': tenant.slug,
    }


def render_mpp_html(*, register_id, tenant=None):
    """Render the Manual de Perfiles de Puestos as HTML.

    Args:
        register_id: UUID (or str) of a CPE PositionRegister.
        tenant: Tenant instance for institutional header data. Optional —
                if omitted the header renders without institutional data.

    Returns:
        HTML string ready to convert to PDF.

    Raises:
        ValidationError: if the register exists but isn't a CPE.
        PositionRegister.DoesNotExist: if the register does not exist.
    """
    from apps.organization.models import PositionRegister

    register = PositionRegister.objects.select_related('approved_by').get(pk=register_id)
    if register.register_type != 'cpe':
        raise ValidationError(
            "El MPP solo puede generarse a partir de un CPE (Ley 30057). "
            f"El registro {register_id} es de tipo {register.register_type}."
        )

    entries = register.entries.select_related(
        'position',
        'position__profile',
        'position__department',
        'position__occupational_category',
    ).prefetch_related(
        'position__functions',
        'position__requirements',
    ).order_by('sequence', 'plaza_code')

    return render_to_string('mpp/mpp.html', {
        'register': register,
        'entries': entries,
        'institucion': _resolve_institution(tenant),
    })


def render_mpp_pdf(*, register_id, tenant=None):
    """Convert MPP HTML to PDF via existing PDFGenerator infrastructure.

    Args:
        register_id: UUID (or str) of a CPE PositionRegister.
        tenant: Tenant instance for institutional header data.

    Returns:
        bytes: PDF content.
    """
    from apps.documents.services import PDFGenerator

    html = render_mpp_html(register_id=register_id, tenant=tenant)
    return PDFGenerator()._html_to_pdf(html)
