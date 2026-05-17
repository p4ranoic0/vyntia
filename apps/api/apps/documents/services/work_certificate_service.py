"""work_certificate_service — Art. 45 LPCL Constancia de Trabajo (B.14).

Pipeline:
1. Build context snapshot (employee + contract + termination details).
2. Render `cese/constancia_trabajo.html` to HTML.
3. Run through PDFGenerator chain (xhtml2pdf → WeasyPrint → ReportLab).
4. Persist WorkCertificate row with snapshot fields + PDF.

See Module 03.7 of docs/modulos/03_gestion_empleo.md and BACKLOG #125.
"""
from __future__ import annotations

from datetime import date

from django.core.files.base import ContentFile
from django.db import transaction
from django.template.loader import render_to_string

from apps.documents.models import WorkCertificate
from apps.documents.services.pdf_generator import PDFGenerator


def _next_certificate_number(tenant) -> str:
    año = date.today().year
    qs = WorkCertificate.objects.filter(
        numero_constancia__startswith=f'CTR-{año}-',
    )
    if tenant is not None:
        qs = qs.filter(tenant=tenant)
    seq = qs.count() + 1
    return f'CTR-{año}-{seq:04d}'


def _build_context(termination, employee, contract) -> dict:
    full_name = ' '.join(
        part for part in [
            getattr(employee, 'apellido_paterno', ''),
            getattr(employee, 'apellido_materno', ''),
            getattr(employee, 'nombres_empleado', ''),
        ] if part
    )
    motivo_textual = termination.motivo or termination.get_causal_display()
    return {
        'numero_constancia': '',  # filled after save (TBD); template tolerates blank
        'fecha_emision': date.today(),
        'employee_full_name': full_name,
        'employee_doc_number': getattr(employee, 'numero_documento', ''),
        'cargo': getattr(contract, 'cargo', '') or '',
        'area_nombre': getattr(getattr(contract, 'area', None), 'nombre_unidad_organica', '') or '',
        'fecha_inicio': contract.fecha_inicio,
        'fecha_fin': termination.fecha_cese,
        'sueldo': contract.salario_bruto,
        'motivo_cese': motivo_textual,
        'causal_code': termination.causal,
    }


def render_certificate_html(termination) -> str:
    contract = termination.contract
    employee = termination.employee
    context = _build_context(termination, employee, contract)
    return render_to_string('cese/constancia_trabajo.html', context)


def render_certificate_pdf(termination) -> bytes:
    html = render_certificate_html(termination)
    return PDFGenerator()._html_to_pdf(html)


@transaction.atomic
def generate_certificate(
    termination, *, user=None, attach_to_employee=False,
) -> WorkCertificate:
    """Render PDF + persist WorkCertificate row.

    Idempotente: si ya existe, regenera el PDF y refresca snapshots.
    """
    contract = termination.contract
    employee = termination.employee
    tenant = termination.tenant

    cert, created = WorkCertificate.objects.get_or_create(
        termination=termination,
        defaults={
            'tenant': tenant,
            'employee': employee,
            'contract': contract,
            'numero_constancia': _next_certificate_number(tenant),
            'fecha_emision': date.today(),
            'cargo_snapshot': getattr(contract, 'cargo', '') or '',
            'area_snapshot': getattr(
                getattr(contract, 'area', None),
                'nombre_unidad_organica',
                '',
            ) or '',
            'fecha_inicio_snapshot': contract.fecha_inicio,
            'fecha_fin_snapshot': termination.fecha_cese,
            'sueldo_snapshot': contract.salario_bruto,
            'motivo_cese_textual': termination.motivo or termination.get_causal_display(),
            'signed_by': user,
        },
    )
    if not created:
        cert.cargo_snapshot = getattr(contract, 'cargo', '') or ''
        cert.fecha_inicio_snapshot = contract.fecha_inicio
        cert.fecha_fin_snapshot = termination.fecha_cese
        cert.sueldo_snapshot = contract.salario_bruto
        cert.motivo_cese_textual = termination.motivo or termination.get_causal_display()
        if user:
            cert.signed_by = user

    pdf_bytes = render_certificate_pdf(termination)
    filename = (
        f'constancia_{cert.numero_constancia}.pdf'
    )
    cert.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
    cert.save()
    return cert
