"""Batch import de empleados desde CSV (backlog #130).

Onboarding masivo: el usuario sube un CSV multipart y se crean N empleados en
una sola operación. Diseño **validate-all, persist-none-on-error**: se valida
fila por fila SIN abortar al primer error; si hay al menos un error, no se
persiste nada (todo-o-nada) y se devuelven todos los errores con su fila.

La validación reutiliza `EmpleadoCreateSerializer` — el mismo serializer del
alta individual — para heredar las reglas tenant-aware (DNI/CE únicos por
tenant, edad mínima 18, formato de documento, área activa).

Columnas CSV requeridas:
    numero_documento, tipo_documento, nombres_empleado, apellido_paterno,
    apellido_materno, fecha_nacimiento, correo_personal, regimen_laboral,
    fecha_ingreso, sueldo_basico, area_id

Columnas opcionales (con default si faltan):
    cargo_empleado (→ "Por definir"), categoria (→ "profesional"),
    tipo_contrato (→ derivado del régimen), fecha_inicio_contrato (→ fecha_ingreso)

Nota: `tipo_documento` se usa para validar el documento (DNI 8 dígitos / CE
8-12) pero, como en el alta individual, el modelo persiste el default "DNI"
(el serializer de alta no expone el campo). D-Pay/onboarding lo extenderá si
necesita persistir CE.
"""
import csv
import io

from django.db import transaction

from api.v1.rrhh.serializers import EmpleadoCreateSerializer

REQUIRED_COLUMNS = [
    "numero_documento",
    "tipo_documento",
    "nombres_empleado",
    "apellido_paterno",
    "apellido_materno",
    "fecha_nacimiento",
    "correo_personal",
    "regimen_laboral",
    "fecha_ingreso",
    "sueldo_basico",
    "area_id",
]

# tipo_contrato derivado del régimen laboral cuando el CSV no lo trae.
_REGIMEN_TO_TIPO_CONTRATO = {
    "276": "indefinido",
    "728": "indefinido",
    "1057": "CAS",
    "locacion": "locacion",
    "consultoria": "consultoria",
    "practicas": "practicas",
}


def _clean(row, key, default=""):
    value = row.get(key)
    if value is None:
        return default
    value = value.strip()
    return value if value else default


def _row_to_payload(row):
    """Mapea una fila plana del CSV al shape anidado de EmpleadoCreateSerializer."""
    regimen = _clean(row, "regimen_laboral")
    fecha_ingreso = _clean(row, "fecha_ingreso")
    datos_laborales = {
        "regimen_laboral": regimen,
        "fecha_ingreso": fecha_ingreso,
        "fecha_inicio_contrato": _clean(row, "fecha_inicio_contrato", fecha_ingreso),
        "sueldo_basico": _clean(row, "sueldo_basico"),
        "cargo_empleado": _clean(row, "cargo_empleado", "Por definir"),
        "categoria": _clean(row, "categoria", "profesional"),
        "tipo_contrato": _clean(
            row, "tipo_contrato", _REGIMEN_TO_TIPO_CONTRATO.get(regimen, "indefinido")
        ),
    }
    return {
        "nombres_empleado": _clean(row, "nombres_empleado"),
        "apellido_paterno": _clean(row, "apellido_paterno"),
        "apellido_materno": _clean(row, "apellido_materno"),
        "numero_documento": _clean(row, "numero_documento"),
        "tipo_documento": _clean(row, "tipo_documento", "DNI").upper(),
        "fecha_nacimiento": _clean(row, "fecha_nacimiento"),
        "correo_personal": _clean(row, "correo_personal"),
        "area_inicial": _clean(row, "area_id"),
        "datos_laborales": datos_laborales,
    }


def import_employees_from_csv(file_obj, request):
    """Procesa un CSV de empleados. Devuelve {"created": N, "errors": [...]}.

    `errors` es una lista de {"row": <fila-en-planilla>, "errors": {...}}.
    La fila 1 es la cabecera; la primera fila de datos es la fila 2.
    Si `errors` no está vacío, `created` es 0 (no se persiste nada).
    """
    try:
        raw = file_obj.read()
    except Exception:
        return {"created": 0, "errors": [{"row": 0, "errors": {"file": ["No se pudo leer el archivo."]}}]}

    if isinstance(raw, bytes):
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            return {
                "created": 0,
                "errors": [{"row": 0, "errors": {"file": ["El archivo no está en UTF-8."]}}],
            }
    else:
        text = raw

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return {
            "created": 0,
            "errors": [{"row": 0, "errors": {"file": ["CSV vacío o sin cabecera."]}}],
        }

    present = {name.strip() for name in reader.fieldnames}
    missing = [c for c in REQUIRED_COLUMNS if c not in present]
    if missing:
        return {
            "created": 0,
            "errors": [
                {
                    "row": 1,
                    "errors": {"columns": [f"Faltan columnas requeridas: {', '.join(missing)}"]},
                }
            ],
        }

    errors = []
    valid_serializers = []
    seen_docs = {}
    row_num = 1  # la cabecera es la fila 1

    for row in reader:
        row_num += 1
        row_errors = {}

        payload = _row_to_payload(row)

        # Duplicado de documento DENTRO del archivo (el serializer solo mira la BD).
        doc = payload["numero_documento"]
        if doc:
            if doc in seen_docs:
                row_errors["numero_documento"] = [
                    f"Documento duplicado dentro del archivo (también en la fila {seen_docs[doc]})."
                ]
            else:
                seen_docs[doc] = row_num

        serializer = EmpleadoCreateSerializer(data=payload, context={"request": request})
        if not serializer.is_valid():
            for field, detail in serializer.errors.items():
                if field in row_errors and isinstance(row_errors[field], list) and isinstance(detail, list):
                    row_errors[field].extend(detail)
                else:
                    row_errors[field] = detail

        if row_errors:
            errors.append({"row": row_num, "errors": row_errors})
        else:
            valid_serializers.append(serializer)

    if errors:
        return {"created": 0, "errors": errors}

    tenant = getattr(request, "tenant", None)
    with transaction.atomic():
        for serializer in valid_serializers:
            if tenant is not None:
                serializer.save(tenant=tenant)
            else:
                serializer.save()

    return {"created": len(valid_serializers), "errors": []}
