from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from app_rrhh.models import (
    ConfiguracionVacaciones, PeriodoVacacional, 
    SolicitudVacaciones, GoceVacaciones
)
from app_rrhh.validators import VacacionesValidator, VacacionesBusinessRules


class VacacionesAPIValidator:
    """
    Validadores específicos para las APIs de vacaciones
    """
    
    @staticmethod
    def validate_solicitud_data(data, instance=None):
        """
        Valida los datos completos de una solicitud de vacaciones
        """
        errors = {}
        
        try:
            # Validar fechas básicas
            fecha_inicio = data.get('fecha_inicio_solicitud')
            fecha_fin = data.get('fecha_fin_solicitud')
            
            if fecha_inicio and fecha_fin:
                VacacionesValidator.validar_fechas_solicitud(fecha_inicio, fecha_fin)
            
            # Validar período vacacional
            periodo = data.get('periodo_vacacional')
            if periodo:
                VacacionesValidator.validar_periodo_vigente(periodo)
                
                # Validar vencimiento
                vencimiento_result = VacacionesValidator.validar_vencimiento_periodo(periodo)
                if vencimiento_result and 'warning' in vencimiento_result:
                    errors['warning'] = vencimiento_result['warning']
            
            # Validar tipo de solicitud y días
            tipo_solicitud = data.get('tipo_solicitud')
            dias_solicitados = data.get('dias_solicitados')
            
            if tipo_solicitud and dias_solicitados:
                VacacionesValidator.validar_fraccionamiento_maximo(dias_solicitados, tipo_solicitud)
            
            # Validar saldo disponible
            if periodo and dias_solicitados:
                VacacionesValidator.validar_saldo_disponible(periodo, dias_solicitados)
            
            # Validar solicitudes duplicadas
            empleado = data.get('empleado')
            if empleado and fecha_inicio and fecha_fin:
                VacacionesValidator.validar_solicitud_duplicada(
                    empleado, fecha_inicio, fecha_fin, instance
                )
            
            # Validar días hábiles si se proporcionan
            incluye_fines_semana = data.get('incluye_fines_semana', False)
            if fecha_inicio and fecha_fin:
                if incluye_fines_semana:
                    VacacionesValidator.validar_inclusion_fines_semana(
                        fecha_inicio, fecha_fin, incluye_fines_semana
                    )
                
                # Calcular y validar días hábiles
                if dias_solicitados:
                    dias_calculados = VacacionesBusinessRules.calcular_dias_habiles(
                        fecha_inicio, fecha_fin, incluye_fines_semana
                    )
                    VacacionesValidator.validar_dias_habiles(
                        fecha_inicio, fecha_fin, dias_calculados
                    )
        
        except DjangoValidationError as e:
            if hasattr(e, 'message_dict'):
                errors.update(e.message_dict)
            else:
                errors['non_field_errors'] = [str(e)]
        
        if errors and 'warning' not in errors:
            raise serializers.ValidationError(errors)
        
        return errors.get('warning')
    
    @staticmethod
    def validate_goce_data(data, instance=None):
        """
        Valida los datos de un goce de vacaciones
        """
        errors = {}
        
        try:
            solicitud = data.get('solicitud_vacaciones')
            fecha_inicio_goce = data.get('fecha_inicio_goce')
            fecha_fin_goce = data.get('fecha_fin_goce')
            dias_gozados = data.get('dias_gozados')
            
            if solicitud and fecha_inicio_goce and fecha_fin_goce and dias_gozados:
                VacacionesValidator.validar_goce_contra_solicitud(
                    solicitud, fecha_inicio_goce, fecha_fin_goce, dias_gozados
                )
            
            # Validar fechas básicas del goce
            if fecha_inicio_goce and fecha_fin_goce:
                if fecha_inicio_goce > fecha_fin_goce:
                    raise DjangoValidationError(
                        'La fecha de inicio del goce no puede ser posterior a la fecha de fin'
                    )
        
        except DjangoValidationError as e:
            if hasattr(e, 'message_dict'):
                errors.update(e.message_dict)
            else:
                errors['non_field_errors'] = [str(e)]
        
        if errors:
            raise serializers.ValidationError(errors)
    
    @staticmethod
    def validate_configuracion_data(data, instance=None):
        """
        Valida los datos de configuración de vacaciones
        """
        errors = {}
        
        try:
            parametro = data.get('parametro')
            valor = data.get('valor')
            tipo_dato = data.get('tipo_dato')
            
            if parametro and valor and tipo_dato:
                VacacionesValidator.validar_configuracion_parametro(
                    parametro, valor, tipo_dato
                )
        
        except DjangoValidationError as e:
            if hasattr(e, 'message_dict'):
                errors.update(e.message_dict)
            else:
                errors['non_field_errors'] = [str(e)]
        
        if errors:
            raise serializers.ValidationError(errors)
    
    @staticmethod
    def validate_periodo_data(data, instance=None):
        """
        Valida los datos de un período vacacional
        """
        errors = {}
        
        try:
            fecha_inicio = data.get('fecha_inicio_periodo')
            fecha_fin = data.get('fecha_fin_periodo')
            
            if fecha_inicio and fecha_fin:
                if fecha_inicio >= fecha_fin:
                    raise DjangoValidationError(
                        'La fecha de inicio del período debe ser anterior a la fecha de fin'
                    )
                
                # Validar que el período sea de aproximadamente un año
                diferencia_dias = (fecha_fin - fecha_inicio).days
                if diferencia_dias < 360 or diferencia_dias > 370:
                    errors['warning'] = (
                        f'El período tiene {diferencia_dias} días. '
                        'Se recomienda que sea de aproximadamente 365 días.'
                    )
        
        except DjangoValidationError as e:
            if hasattr(e, 'message_dict'):
                errors.update(e.message_dict)
            else:
                errors['non_field_errors'] = [str(e)]
        
        if errors and 'warning' not in errors:
            raise serializers.ValidationError(errors)
        
        return errors.get('warning')


class VacacionesPermissionValidator:
    """
    Validadores de permisos para operaciones de vacaciones
    """
    
    @staticmethod
    def can_approve_solicitud(user, solicitud):
        """
        Valida si el usuario puede aprobar una solicitud
        """
        # El jefe directo puede aprobar
        if hasattr(user, 'empleado') and solicitud.empleado.jefe_directo == user.empleado:
            return True
        
        # Los usuarios de RRHH pueden aprobar
        if user.groups.filter(name='RRHH').exists():
            return True
        
        # Los administradores pueden aprobar
        if user.is_superuser:
            return True
        
        return False
    
    @staticmethod
    def can_cancel_solicitud(user, solicitud):
        """
        Valida si el usuario puede cancelar una solicitud
        """
        # El empleado puede cancelar su propia solicitud
        if hasattr(user, 'empleado') and solicitud.empleado == user.empleado:
            return True
        
        # Los usuarios de RRHH pueden cancelar
        if user.groups.filter(name='RRHH').exists():
            return True
        
        # Los administradores pueden cancelar
        if user.is_superuser:
            return True
        
        return False
    
    @staticmethod
    def can_modify_configuracion(user):
        """
        Valida si el usuario puede modificar configuraciones
        """
        # Solo RRHH y administradores
        return (
            user.groups.filter(name='RRHH').exists() or 
            user.is_superuser
        )
    
    @staticmethod
    def can_view_all_solicitudes(user):
        """
        Valida si el usuario puede ver todas las solicitudes
        """
        # RRHH y administradores pueden ver todas
        if user.groups.filter(name='RRHH').exists() or user.is_superuser:
            return True
        
        # Los jefes pueden ver las de sus subordinados
        if hasattr(user, 'empleado'):
            return user.empleado.subordinados.exists()
        
        return False


class VacacionesStateValidator:
    """
    Validadores de transiciones de estado
    """
    
    @staticmethod
    def validate_solicitud_state_change(solicitud, new_state, user):
        """
        Valida el cambio de estado de una solicitud
        """
        current_state = solicitud.estado_solicitud
        
        # Validar transición de estado
        VacacionesValidator.validar_estado_transicion(current_state, new_state)
        
        # Validar permisos según el nuevo estado
        if new_state in ['aprobada', 'rechazada']:
            if not VacacionesPermissionValidator.can_approve_solicitud(user, solicitud):
                raise serializers.ValidationError(
                    'No tiene permisos para aprobar/rechazar esta solicitud'
                )
        
        if new_state == 'cancelada':
            if not VacacionesPermissionValidator.can_cancel_solicitud(user, solicitud):
                raise serializers.ValidationError(
                    'No tiene permisos para cancelar esta solicitud'
                )
    
    @staticmethod
    def validate_goce_state_change(goce, new_state):
        """
        Valida el cambio de estado de un goce
        """
        current_state = goce.estado_goce
        
        valid_transitions = {
            'programado': ['en_curso', 'cancelado'],
            'en_curso': ['finalizado', 'interrumpido'],
            'interrumpido': ['en_curso', 'finalizado'],
            'finalizado': [],  # Estado final
            'cancelado': []   # Estado final
        }
        
        if new_state not in valid_transitions.get(current_state, []):
            raise serializers.ValidationError(
                f'No se puede cambiar el estado de "{current_state}" a "{new_state}"'
            )