"""displacement_service — resolution generation for B.13 Module 03.6.

Workflow lives on the Displacement model itself (submit / approve_X /
activate / complete / cancel) — this service handles the side-products:
the administrative resolution HTML / PDF generation that gets stored on
the Displacement.resolution_pdf field once `approved`.
"""

from __future__ import annotations

from django.template.loader import render_to_string
from django.utils import timezone

from apps.documents.services.pdf_generator import PDFGenerator
from apps.organization.models import Displacement


def render_resolution_html(displacement_id) -> str:
    """Render the administrative resolution HTML for an approved displacement."""
    d = (
        Displacement.objects
        .select_related(
            'employee', 'origen_department', 'destino_department',
            'origen_position', 'destino_position',
            'approved_by_supervisor', 'approved_by_hr', 'approved_by_titular',
        )
        .get(pk=displacement_id)
    )
    employee = d.employee
    full_name = ' '.join(
        part for part in [
            getattr(employee, 'nombres_empleado', ''),
            getattr(employee, 'apellido_paterno', ''),
            getattr(employee, 'apellido_materno', ''),
        ] if part
    )
    return render_to_string('desplazamiento/resolucion.html', {
        'displacement': d,
        'employee_full_name': full_name,
        'issued_at': timezone.now(),
    })


def render_resolution_pdf(displacement_id) -> bytes:
    html = render_resolution_html(displacement_id)
    return PDFGenerator()._html_to_pdf(html)


def extend_displacement(
    *,
    displacement_id,
    new_end_date,
    reason: str,
    granted_by,
    resolution_number: str = '',
):
    """Create a DisplacementExtension for an active displacement."""
    from apps.organization.models import DisplacementExtension
    d = Displacement.objects.get(pk=displacement_id)
    if d.status != 'active':
        from django.core.exceptions import ValidationError
        raise ValidationError(
            f'Cannot extend displacement in status={d.status}'
        )
    previous_end = d.end_date
    ext = DisplacementExtension(
        displacement=d,
        previous_end_date=previous_end,
        new_end_date=new_end_date,
        reason=reason,
        granted_by=granted_by,
        resolution_number=resolution_number,
    )
    ext.full_clean()
    ext.save()
    # Update the displacement's end_date to reflect the new horizon.
    d.end_date = new_end_date
    d.save(update_fields=['end_date', 'updated_at'])
    return ext
