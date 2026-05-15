"""dossier_service — DigitalDossier build + consolidated PDF + attach (B.12).

Per maestro § 6.2 the legajo has 15 obligatory sections. `build_dossier_for_employee`
provisions them all atomically. `attach_document_to_section` connects a
DigitalDocument to a section based on its `tipo_documento` (via heuristic
mapping) — convenient for the upload flow. `render_consolidated_index_html`
produces a TOC-style view of the legajo, which `render_consolidated_pdf` turns
into a PDF via the project chain.
"""

from __future__ import annotations

from collections import defaultdict

from django.db import transaction
from django.template.loader import render_to_string

from apps.documents.models import (
    DigitalDocument,
    DigitalDossier,
    DossierSection,
)
from apps.documents.models.digital_dossier import SECTION_DEFAULTS
from apps.documents.services.pdf_generator import PDFGenerator


# Heuristic mapping from DigitalDocument.tipo_documento value → section.kind.
# Anything unrecognised falls back to 'datos_personales'.
TIPO_TO_SECTION = {
    # Identidad / personales
    'dni': 'identidad_cuspp',
    'pasaporte': 'identidad_cuspp',
    'ce': 'identidad_cuspp',
    'cuspp': 'identidad_cuspp',
    'foto': 'datos_personales',
    # Académicos
    'diploma': 'datos_academicos',
    'certificado_estudios': 'datos_academicos',
    'colegiatura': 'datos_academicos',
    'constancia_academica': 'datos_academicos',
    # Contratos
    'contrato_trabajo': 'contratos',
    'adenda_contrato': 'contratos',
    'contrato_inicial': 'contratos',
    # Declaraciones juradas
    'dj_no_parentesco': 'declaraciones_juradas',
    'dj_no_incompatibilidad': 'declaraciones_juradas',
    'dj_intereses': 'declaraciones_juradas',
    'dj_impedimentos': 'declaraciones_juradas',
    # Médicos
    'examen_medico': 'medicos',
    'certificado_medico': 'medicos',
    # Accidentes
    'accidente_trabajo': 'accidentes',
    # Cese
    'liquidacion': 'cese',
    'certificado_trabajo': 'cese',
    # Sanciones
    'sancion_disciplinaria': 'sanciones',
    # Licencias
    'licencia_otorgada': 'licencias',
    # Capacitaciones
    'certificado_capacitacion': 'capacitaciones',
    # Reconocimientos
    'reconocimiento': 'reconocimientos',
    # Evaluaciones
    'evaluacion_desempeno': 'evaluaciones',
}


@transaction.atomic
def build_dossier_for_employee(*, employee, tenant=None) -> DigitalDossier:
    """Create the dossier with 15 seeded sections; idempotent."""
    if tenant is None:
        tenant = getattr(employee, 'tenant', None)
    dossier, _ = DigitalDossier.objects.get_or_create(
        employee=employee, defaults={'tenant': tenant},
    )
    existing_kinds = set(dossier.sections.values_list('kind', flat=True))
    for order, (kind, label, pl) in enumerate(SECTION_DEFAULTS):
        if kind in existing_kinds:
            continue
        DossierSection.objects.create(
            dossier=dossier, kind=kind, label=label,
            permission_level=pl, order=order,
        )
    return dossier


def attach_document_to_section(
    *, document: DigitalDocument, dossier: DigitalDossier | None = None,
) -> DossierSection:
    """Look up the dossier for the document's employee, return the matching section.

    The dossier is auto-built when not provided. The section kind is inferred
    from `document.tipo_documento` via TIPO_TO_SECTION; unknown types fall
    back to 'datos_personales'.
    """
    if dossier is None:
        dossier = build_dossier_for_employee(employee=document.empleado)
    kind = TIPO_TO_SECTION.get(document.tipo_documento, 'datos_personales')
    return dossier.sections.get(kind=kind)


def render_consolidated_index_html(dossier_id) -> str:
    """Render a TOC-style HTML index of the dossier."""
    dossier = (
        DigitalDossier.objects
        .select_related('employee')
        .prefetch_related('sections')
        .get(pk=dossier_id)
    )
    sections = list(dossier.sections.order_by('order', 'kind'))
    # Count DigitalDocuments per section. Documents are pinned to the dossier
    # employee + section via the same heuristic.
    docs_by_section = defaultdict(list)
    for doc in DigitalDocument.objects.filter(
        empleado=dossier.employee_id,
        es_version_actual=True,
    ).order_by('-fecha_subida'):
        section_kind = TIPO_TO_SECTION.get(doc.tipo_documento, 'datos_personales')
        docs_by_section[section_kind].append(doc)

    employee = dossier.employee
    full_name = ' '.join(
        part for part in [
            getattr(employee, 'nombres_empleado', ''),
            getattr(employee, 'apellido_paterno', ''),
            getattr(employee, 'apellido_materno', ''),
        ] if part
    )
    # Pre-shape so the template can iterate cleanly without a custom filter.
    sections_with_docs = [
        (section, docs_by_section.get(section.kind, []))
        for section in sections
    ]
    return render_to_string('legajo/consolidated_index.html', {
        'dossier': dossier,
        'employee_full_name': full_name,
        'sections_with_docs': sections_with_docs,
    })


def render_consolidated_pdf(dossier_id) -> bytes:
    """Return the consolidated index as a PDF via PDFGenerator chain."""
    html = render_consolidated_index_html(dossier_id)
    return PDFGenerator()._html_to_pdf(html)
