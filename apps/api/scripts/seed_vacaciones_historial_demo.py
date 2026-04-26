"""
Seed demo data for vacation requests and history for a specific user.

Usage:
  .venv\\Scripts\\python.exe back\\scripts\\seed_vacaciones_historial_demo.py
"""

from datetime import date, timedelta
from decimal import Decimal
import os
import sys

import django

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vyntia.settings.development')
django.setup()

from django.utils import timezone

from app_rrhh.models import Area
from apps.identity.models import Usuario
from app_rrhh.models.contratos_adendas import ContratosAdendas
from app_rrhh.models.vacaciones import (
    ConfiguracionVacaciones,
    GoceVacaciones,
    HistorialSolicitudVacaciones,
    SolicitudVacaciones,
)
from app_rrhh.services.vacation_service import VacationService


def _get_configuracion(usuario):
    hoy = date.today()
    config = ConfiguracionVacaciones.objects.filter(
        tipo_configuracion='general',
        area__isnull=True,
        empleado__isnull=True,
        activo=True,
        fecha_inicio_vigencia__lte=hoy,
    ).filter(
        fecha_fin_vigencia__isnull=True
    ).first()

    if config:
        return config

    return ConfiguracionVacaciones.objects.create(
        tipo_configuracion='general',
        dias_por_ano=30,
        activo=True,
        fecha_inicio_vigencia=hoy - timedelta(days=365),
        creado_por=usuario,
    )


def _get_or_create_contrato(empleado, usuario):
    hoy = date.today()
    contrato = (
        ContratosAdendas.objects.filter(
            empleado=empleado,
            estado='ACTIVO',
            fecha_inicio__lte=hoy,
        )
        .filter(fecha_fin__isnull=True)
        .order_by('-fecha_inicio')
        .first()
    )
    if contrato:
        return contrato

    datos_laborales = getattr(empleado, 'datos_laborales_actuales', lambda: None)()
    area = datos_laborales.area if datos_laborales else Area.objects.first()
    if not area:
        raise RuntimeError("No se encontró un área para crear el contrato demo.")

    numero_contrato = f"DEMO-CON-{hoy.year}-{empleado.empleado_id}"
    return ContratosAdendas.objects.create(
        empleado=empleado,
        area=area,
        numero_contrato=numero_contrato,
        tipo_documento='CONTRATO_INDEFINIDO',
        fecha_inicio=hoy - timedelta(days=420),
        fecha_fin=None,
        salario_bruto=Decimal('3000.00'),
        cargo=getattr(datos_laborales, 'cargo_empleado', 'Analista'),
        estado='ACTIVO',
        creado_por=usuario,
    )


def _registrar_historial(solicitud, usuario, acciones):
    for accion in acciones:
        HistorialSolicitudVacaciones.objects.create(
            solicitud_vacaciones=solicitud,
            tipo_accion=accion['tipo'],
            descripcion_accion=accion['descripcion'],
            estado_anterior=accion.get('estado_anterior'),
            estado_nuevo=accion.get('estado_nuevo'),
            usuario_accion=usuario,
        )


def main():
    usuario = Usuario.objects.filter(username='jgarcia').first()
    if not usuario or not usuario.empleado:
        raise RuntimeError("No se encontró el usuario jgarcia con empleado asociado.")

    empleado = usuario.empleado
    jefe_usuario = Usuario.objects.filter(tipo_usuario='jefe').exclude(pk=usuario.pk).first()
    rrhh_usuario = Usuario.objects.filter(tipo_usuario__in=['rrhh', 'administrador']).first()

    _get_configuracion(usuario)
    contrato = _get_or_create_contrato(empleado, usuario)

    # Crear/obtener periodos por aniversario
    periodo_actual = VacationService.obtener_o_crear_periodo(empleado, date.today())
    periodo_anterior = VacationService.obtener_o_crear_periodo(empleado, date.today() - timedelta(days=370))

    # Limpiar datos demo previos
    SolicitudVacaciones.objects.filter(
        empleado=empleado,
        motivo_solicitud__icontains='[DEMO]'
    ).delete()

    # Solicitud finalizada (periodo anterior)
    inicio_1 = periodo_anterior.fecha_inicio_periodo + timedelta(days=30)
    fin_1 = inicio_1 + timedelta(days=4)
    s1 = SolicitudVacaciones.objects.create(
        empleado=empleado,
        periodo_vacacional=periodo_anterior,
        tipo_solicitud='vacaciones',
        fecha_inicio=inicio_1,
        fecha_fin=fin_1,
        dias_solicitados=Decimal('5.0'),
        medio_dia=False,
        motivo_solicitud='[DEMO] Vacaciones del periodo anterior',
        observaciones_empleado='',
        estado_solicitud='finalizada',
        fecha_envio=timezone.now(),
        aprobado_por_jefe=True,
        jefe_aprobador=jefe_usuario.empleado if jefe_usuario and jefe_usuario.empleado else None,
        fecha_aprobacion_jefe=timezone.now(),
        aprobado_por_rrhh=True,
        rrhh_aprobador=rrhh_usuario,
        fecha_aprobacion_rrhh=timezone.now(),
    )
    GoceVacaciones.objects.create(
        solicitud_vacaciones=s1,
        empleado=empleado,
        periodo_vacacional=periodo_anterior,
        fecha_inicio_real=inicio_1,
        fecha_fin_real=fin_1,
        dias_gozados=Decimal('5.0'),
        estado_goce='finalizado',
        registrado_por=rrhh_usuario or usuario,
    )
    VacationService.descontar_dias_periodo(periodo_anterior, Decimal('5.0'))
    _registrar_historial(
        s1,
        usuario,
        [
            {'tipo': 'creacion', 'descripcion': 'Creación de solicitud demo', 'estado_nuevo': 'borrador'},
            {'tipo': 'envio', 'descripcion': 'Solicitud enviada', 'estado_anterior': 'borrador', 'estado_nuevo': 'en_revision'},
            {'tipo': 'aprobacion_jefe', 'descripcion': 'Aprobación por jefe', 'estado_anterior': 'en_revision', 'estado_nuevo': 'aprobada_jefe'},
            {'tipo': 'aprobacion_rrhh', 'descripcion': 'Aprobación por RRHH', 'estado_anterior': 'aprobada_jefe', 'estado_nuevo': 'aprobada'},
            {'tipo': 'inicio_goce', 'descripcion': 'Inicio de goce', 'estado_anterior': 'aprobada', 'estado_nuevo': 'en_goce'},
            {'tipo': 'fin_goce', 'descripcion': 'Fin de goce', 'estado_anterior': 'en_goce', 'estado_nuevo': 'finalizada'},
        ],
    )

    # Solicitud en revisión (periodo actual)
    inicio_2 = date.today() + timedelta(days=15)
    fin_2 = inicio_2 + timedelta(days=2)
    s2 = SolicitudVacaciones.objects.create(
        empleado=empleado,
        periodo_vacacional=periodo_actual,
        tipo_solicitud='vacaciones',
        fecha_inicio=inicio_2,
        fecha_fin=fin_2,
        dias_solicitados=Decimal('3.0'),
        medio_dia=False,
        motivo_solicitud='[DEMO] Solicitud pendiente de aprobación',
        observaciones_empleado='',
        estado_solicitud='en_revision',
        fecha_envio=timezone.now(),
        jefe_aprobador=jefe_usuario.empleado if jefe_usuario and jefe_usuario.empleado else None,
    )
    _registrar_historial(
        s2,
        usuario,
        [
            {'tipo': 'creacion', 'descripcion': 'Creación de solicitud demo', 'estado_nuevo': 'borrador'},
            {'tipo': 'envio', 'descripcion': 'Solicitud enviada', 'estado_anterior': 'borrador', 'estado_nuevo': 'en_revision'},
        ],
    )

    # Solicitud borrador con medio día
    inicio_3 = date.today() + timedelta(days=45)
    s3 = SolicitudVacaciones.objects.create(
        empleado=empleado,
        periodo_vacacional=periodo_actual,
        tipo_solicitud='vacaciones',
        fecha_inicio=inicio_3,
        fecha_fin=inicio_3,
        dias_solicitados=Decimal('0.5'),
        medio_dia=True,
        motivo_solicitud='[DEMO] Borrador medio día',
        observaciones_empleado='',
        estado_solicitud='borrador',
    )
    _registrar_historial(
        s3,
        usuario,
        [
            {'tipo': 'creacion', 'descripcion': 'Creación de solicitud demo', 'estado_nuevo': 'borrador'},
        ],
    )

    print("Demo de vacaciones creado para jgarcia.")
    print(f"Contrato usado: {contrato.numero_contrato}")
    print(f"Solicitudes: {SolicitudVacaciones.objects.filter(empleado=empleado, motivo_solicitud__icontains='[DEMO]').count()}")


if __name__ == '__main__':
    main()
