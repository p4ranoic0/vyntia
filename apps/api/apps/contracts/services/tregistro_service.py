"""tregistro_service — SUNAT T-Registro Anexo 3 generation + PVS validation (B.10).

The real SUNAT PVS validator and submission API are out-of-scope for B.10. This
module captures the rules we know about (header format, field-level validations)
behind a service boundary so that swapping in a real client later is a single
seam. `submit_declaration` is currently an in-process state transition (no HTTP
call); production deployment will replace it with a real SUNAT call.

References:
- Module 03.2 § 3.4 docs/modulos/03_gestion_empleo.md
- SUNAT Tabla 2 (doc type), Tabla 8 (modalidad), Tabla 24 (CIUO-08)
- ROADMAP-B.md backlog #111
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction

from apps.contracts.models import TRegistroDeclaration


_KNOWN_DOC_TYPES = {'01', '04', '07'}  # DNI, CE, Pasaporte
_DOC_LEN_RULES = {
    '01': (8, 8),   # DNI 8 digits
    '04': (9, 12),  # CE 9-12
    '07': (6, 12),  # Pasaporte 6-12
}

_KNOWN_REGIMEN = {'728', '1057', '276', '1024', '1153', '30057'}
_KNOWN_MODALIDAD = {
    # Subset of SUNAT Tabla 8 — codes commonly used. Real spec has more.
    'SBT',  # Sujeto a modalidad - inicio o lanzamiento de nueva actividad
    'IND',  # Indeterminado
    'OBR',  # Obra determinada
    'TPC',  # Trabajo parcial
    'SUP',  # Suplencia
    'OCS',  # Ocasional
    'EMR',  # Emergencia
    'TMP',  # Temporada
    'INT',  # Intermitente
    'EXT',  # Extranjero
    'CAS',  # CAS
}


# --------------------------------------------------------------------------- #
# Anexo 3 plain-text generation                                               #
# --------------------------------------------------------------------------- #

def build_anexo3_txt(declaration: TRegistroDeclaration) -> str:
    """Return the Anexo 3 plain-text payload for the declaration.

    Layout (pipe-separated, one record per line):
        H | TRREG | <ruc> | <razon_social> | <declaration_type> | <created_iso>
        W | <doc_type> | <doc_number> | <ap_paterno> | <ap_materno> | <nombres>
          | <birth_date YYYYMMDD> | <gender> | <nationality_code> | <address>
        C | <start_date YYYYMMDD> | <end_date YYYYMMDD or 99999999>
          | <modality_code> | <regimen_laboral> | <occupation_code>
        R | <regimen_pension> | <pension_provider> | <cuspp>
          | <regimen_salud> | <eps_code>
        S | <remuneracion_basica> | <jornada_horas_semanales>
        T | COUNT | 1
    """
    end_date_field = (
        declaration.contract_end_date.strftime('%Y%m%d')
        if declaration.contract_end_date else '99999999'
    )
    created_iso = (
        declaration.created_at.isoformat()
        if declaration.created_at else ''
    )

    rows = [
        '|'.join([
            'H', 'TRREG', declaration.employer_ruc,
            declaration.employer_razon_social, declaration.declaration_type,
            created_iso,
        ]),
        '|'.join([
            'W', declaration.worker_doc_type, declaration.worker_doc_number,
            declaration.worker_apellido_paterno,
            declaration.worker_apellido_materno,
            declaration.worker_nombres,
            declaration.worker_birth_date.strftime('%Y%m%d'),
            declaration.worker_gender,
            declaration.worker_nationality_code,
            declaration.worker_address,
        ]),
        '|'.join([
            'C', declaration.contract_start_date.strftime('%Y%m%d'),
            end_date_field, declaration.work_modality_code,
            declaration.regimen_laboral_code, declaration.occupation_code,
        ]),
        '|'.join([
            'R', declaration.regimen_pensionario,
            declaration.pension_provider_code, declaration.cuspp,
            declaration.regimen_salud, declaration.eps_code,
        ]),
        '|'.join([
            'S', f'{declaration.remuneracion_basica:.2f}',
            str(declaration.jornada_horas_semanales),
        ]),
        '|'.join(['T', 'COUNT', '1']),
    ]
    return '\n'.join(rows)


# --------------------------------------------------------------------------- #
# PVS-style validation                                                        #
# --------------------------------------------------------------------------- #

def validate_pvs(declaration: TRegistroDeclaration) -> list[str]:
    """Run local PVS-style rules and return a list of error messages.

    Empty list means the declaration is valid.
    """
    errors: list[str] = []

    if not declaration.employer_ruc.isdigit() or len(declaration.employer_ruc) != 11:
        errors.append('employer_ruc must be 11 digits')

    if declaration.worker_doc_type not in _KNOWN_DOC_TYPES:
        errors.append(
            f'worker_doc_type {declaration.worker_doc_type} not in '
            f'known SUNAT Tabla 2 set'
        )
    else:
        min_len, max_len = _DOC_LEN_RULES[declaration.worker_doc_type]
        doc = declaration.worker_doc_number
        if not (min_len <= len(doc) <= max_len):
            errors.append(
                f'worker_doc_number length {len(doc)} out of range '
                f'{min_len}-{max_len} for doc_type {declaration.worker_doc_type}'
            )

    if not declaration.worker_apellido_paterno:
        errors.append('worker_apellido_paterno is required')
    if not declaration.worker_nombres:
        errors.append('worker_nombres is required')

    today = date.today()
    age_at_start = (
        declaration.contract_start_date.year - declaration.worker_birth_date.year
        - (
            (
                declaration.contract_start_date.month,
                declaration.contract_start_date.day,
            )
            < (
                declaration.worker_birth_date.month,
                declaration.worker_birth_date.day,
            )
        )
    )
    if age_at_start < 18:
        errors.append('worker must be ≥18 years at contract_start_date')

    if declaration.contract_start_date > today + timedelta(days=30):
        errors.append('contract_start_date is more than 30 days in the future')

    if (
        declaration.contract_end_date
        and declaration.contract_end_date <= declaration.contract_start_date
    ):
        errors.append('contract_end_date must be after contract_start_date')

    if declaration.work_modality_code not in _KNOWN_MODALIDAD:
        errors.append(
            f'work_modality_code {declaration.work_modality_code} '
            f'not in known SUNAT Tabla 8 set'
        )

    if declaration.regimen_laboral_code not in _KNOWN_REGIMEN:
        errors.append(
            f'regimen_laboral_code {declaration.regimen_laboral_code} '
            f'not in known set'
        )

    if declaration.regimen_pensionario == 'spp':
        if not declaration.pension_provider_code:
            errors.append('SPP régimen requires pension_provider_code')
        if not declaration.cuspp:
            errors.append('SPP régimen requires cuspp')

    if declaration.regimen_salud == 'eps':
        if not declaration.eps_code:
            errors.append('EPS régimen requires eps_code')

    if declaration.remuneracion_basica is None:
        errors.append('remuneracion_basica is required')
    elif Decimal(declaration.remuneracion_basica) <= 0:
        errors.append('remuneracion_basica must be > 0')

    return errors


# --------------------------------------------------------------------------- #
# Lifecycle convenience                                                       #
# --------------------------------------------------------------------------- #

@transaction.atomic
def validate_and_persist(declaration_id) -> TRegistroDeclaration:
    """Re-validate, persist txt + errors. If clean: status='validated'."""
    declaration = TRegistroDeclaration.objects.select_for_update().get(pk=declaration_id)
    errors = validate_pvs(declaration)
    declaration.anexo3_txt = build_anexo3_txt(declaration)
    declaration.pvs_errors = errors
    if errors:
        # Stay in draft; surface errors.
        declaration.status = 'draft'
        declaration.save(update_fields=[
            'anexo3_txt', 'pvs_errors', 'status', 'updated_at',
        ])
    else:
        declaration.save(update_fields=[
            'anexo3_txt', 'pvs_errors', 'updated_at',
        ])
        declaration.mark_validated()
    return declaration


@transaction.atomic
def submit_declaration(declaration_id, *, user, reference: str = '') -> TRegistroDeclaration:
    """Re-validate, build txt, then transition to submitted.

    Out-of-scope: real SUNAT API call. A future implementation replaces this
    method's body with HTTP submission and persists the SUNAT reference.
    """
    declaration = validate_and_persist(declaration_id)
    if declaration.pvs_errors:
        return declaration  # Cannot submit; caller checks pvs_errors.
    declaration.mark_submitted(user=user, reference=reference)
    return declaration
