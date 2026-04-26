"""Seed demo data for vacation report visualization.

Run with:
  python manage.py shell < back/scripts/seed_vacaciones_reporte_demo.py
"""

from datetime import date, timedelta

from apps.employees.models import Empleado
from apps.organization.models import Area
from apps.identity.models import Usuario
from apps.contracts.models import ContratosAdendas, DatosLaborales
from apps.time_off.models import ConfiguracionVacaciones, PeriodoVacacional, SolicitudVacaciones, GoceVacaciones


def seed():
    area, _ = Area.objects.get_or_create(
        siglas_area="TI",
        defaults={
            "nombre_organo": "Gerencia",
            "nombre_unidad_organica": "Tecnología",
            "descripcion_area": "Área de TI",
            "estado_area": "activo",
        },
    )

    empleado, _ = Empleado.objects.get_or_create(
        numero_documento="99999999",
        defaults={
            "tipo_documento": "DNI",
            "nombres_empleado": "María",
            "apellido_paterno": "García",
            "apellido_materno": "Ramos",
            "genero_empleado": "femenino",
            "fecha_nacimiento": date(1992, 5, 10),
            "telefono_celular": "999111222",
            "correo_personal": "maria.demo@empresa.com",
            "estado_civil": "soltero",
            "direccion_domicilio": "Av. Demo 123",
            "distrito_domicilio": "Lima",
            "provincia_domicilio": "Lima",
            "departamento_domicilio": "Lima",
            "entidad_bancaria": "Banco Demo",
            "numero_cuenta_bancaria": "001-000000-0-00",
            "numero_cci": "00000000000000000000",
            "estado_empleado": "activo",
        },
    )

    jefe, _ = Empleado.objects.get_or_create(
        numero_documento="88888888",
        defaults={
            "tipo_documento": "DNI",
            "nombres_empleado": "Carlos",
            "apellido_paterno": "Lopez",
            "apellido_materno": "Diaz",
            "genero_empleado": "masculino",
            "fecha_nacimiento": date(1985, 3, 2),
            "telefono_celular": "999222333",
            "correo_personal": "carlos.jefe@empresa.com",
            "estado_civil": "casado",
            "direccion_domicilio": "Av. Jefe 456",
            "distrito_domicilio": "Lima",
            "provincia_domicilio": "Lima",
            "departamento_domicilio": "Lima",
            "entidad_bancaria": "Banco Demo",
            "numero_cuenta_bancaria": "001-000000-0-01",
            "numero_cci": "00000000000000000001",
            "estado_empleado": "activo",
        },
    )

    DatosLaborales.objects.get_or_create(
        empleado=empleado,
        fecha_inicio_contrato=date(2025, 1, 10),
        defaults={
            "area": area,
            "cargo_empleado": "Analista de Sistemas",
            "categoria": "profesional",
            "tipo_contrato": "indefinido",
            "regimen_laboral": "728",
            "modalidad_trabajo": "presencial",
            "jornada_laboral": "completa",
            "fecha_ingreso": date(2025, 1, 10),
            "fecha_fin_contrato": None,
            "sueldo_basico": 3500,
            "jefe_directo": jefe,
            "estado_datos": "activo",
        },
    )

    DatosLaborales.objects.get_or_create(
        empleado=jefe,
        fecha_inicio_contrato=date(2020, 1, 5),
        defaults={
            "area": area,
            "cargo_empleado": "Jefe de Área",
            "categoria": "funcionario",
            "tipo_contrato": "indefinido",
            "regimen_laboral": "728",
            "modalidad_trabajo": "presencial",
            "jornada_laboral": "completa",
            "fecha_ingreso": date(2020, 1, 5),
            "fecha_fin_contrato": None,
            "sueldo_basico": 6500,
            "estado_datos": "activo",
        },
    )

    usuario_jefe, created = Usuario.objects.get_or_create(
        username="jefe.demo",
        defaults={
            "email": "jefe.demo@empresa.com",
            "nombres_usuario": "Carlos",
            "apellidos_usuario": "Lopez Diaz",
            "tipo_usuario": "jefe",
            "nivel_acceso": "departamental",
            "is_staff": True,
            "empleado": jefe,
        },
    )
    if created:
        usuario_jefe.set_password("Demo12345")
        usuario_jefe.save(update_fields=["password"])

    usuario_empleado, created = Usuario.objects.get_or_create(
        username="maria.demo",
        defaults={
            "email": "maria.demo@empresa.com",
            "nombres_usuario": "María",
            "apellidos_usuario": "García Ramos",
            "tipo_usuario": "empleado",
            "nivel_acceso": "personal",
            "is_staff": False,
            "empleado": empleado,
        },
    )
    if created:
        usuario_empleado.set_password("Demo12345")
        usuario_empleado.save(update_fields=["password"])

    config, _ = ConfiguracionVacaciones.objects.get_or_create(
        tipo_configuracion="general",
        area=None,
        empleado=None,
        fecha_inicio_vigencia=date(2024, 1, 1),
        defaults={
            "dias_por_ano": 30,
            "dias_minimos_solicitud": 1,
            "dias_maximos_solicitud": 30,
            "dias_anticipacion_minima": 10,
            "incluye_feriados": False,
            "incluye_fines_semana": False,
            "requiere_aprobacion_jefe": True,
            "requiere_aprobacion_rrhh": False,
            "permite_fraccionamiento": True,
            "min_dias_por_fraccion": 1,
            "max_fracciones_por_ano": 5,
            "activo": True,
        },
    )

    contrato_old, _ = ContratosAdendas.objects.get_or_create(
        empleado=empleado,
        numero_contrato="CON-2023-0001",
        defaults={
            "area": area,
            "tipo_documento": "CONTRATO_FIJO",
            "fecha_inicio": date(2023, 1, 10),
            "fecha_fin": date(2024, 1, 9),
            "salario_bruto": 3000,
            "cargo": "Analista Junior",
            "estado": "TERMINADO",
        },
    )

    contrato_activo, _ = ContratosAdendas.objects.get_or_create(
        empleado=empleado,
        numero_contrato="CON-2025-0001",
        defaults={
            "area": area,
            "tipo_documento": "CONTRATO_INDEFINIDO",
            "fecha_inicio": date(2025, 1, 10),
            "fecha_fin": None,
            "salario_bruto": 3500,
            "cargo": "Analista de Sistemas",
            "estado": "ACTIVO",
        },
    )

    periodo_old, _ = PeriodoVacacional.objects.get_or_create(
        empleado=empleado,
        contrato=contrato_old,
        ano_periodo=2023,
        defaults={
            "fecha_inicio_periodo": date(2023, 1, 10),
            "fecha_fin_periodo": date(2024, 1, 9),
            "fecha_vencimiento": date(2025, 1, 9),
            "dias_correspondientes": 30,
            "dias_adicionales": 0,
            "dias_totales": 30,
            "dias_gozados": 20,
            "dias_pendientes": 10,
            "dias_vencidos": 0,
            "estado_periodo": "cerrado",
            "configuracion": config,
        },
    )

    periodo_activo, _ = PeriodoVacacional.objects.get_or_create(
        empleado=empleado,
        contrato=contrato_activo,
        ano_periodo=2025,
        defaults={
            "fecha_inicio_periodo": date(2025, 1, 10),
            "fecha_fin_periodo": date(2026, 1, 9),
            "fecha_vencimiento": date(2027, 1, 9),
            "dias_correspondientes": 30,
            "dias_adicionales": 0,
            "dias_totales": 30,
            "dias_gozados": 5,
            "dias_pendientes": 25,
            "dias_vencidos": 0,
            "estado_periodo": "activo",
            "configuracion": config,
        },
    )

    solicitud, _ = SolicitudVacaciones.objects.get_or_create(
        empleado=empleado,
        periodo_vacacional=periodo_activo,
        fecha_inicio=date(2025, 6, 20),  # Viernes
        fecha_fin=date(2025, 6, 24),
        defaults={
            "tipo_solicitud": "vacaciones",
            "dias_solicitados": 7,
            "motivo_solicitud": "Descanso anual",
            "observaciones_empleado": "Vacaciones de prueba",
            "estado_solicitud": "aprobada",
            "aprobado_por_jefe": True,
            "jefe_aprobador": jefe,
        },
    )

    GoceVacaciones.objects.get_or_create(
        solicitud_vacaciones=solicitud,
        empleado=empleado,
        periodo_vacacional=periodo_activo,
        defaults={
            "fecha_inicio_real": solicitud.fecha_inicio,
            "fecha_fin_real": solicitud.fecha_fin,
            "dias_gozados": solicitud.dias_solicitados,
            "estado_goce": "finalizado",
        },
    )

    print("Demo vacaciones: OK")


if __name__ == "__main__":
    seed()
