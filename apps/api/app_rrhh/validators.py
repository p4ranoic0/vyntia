from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal


class VacacionesValidator:
    """
    Validadores para el módulo de vacaciones
    """
    
    @staticmethod
    def validar_fraccionamiento_maximo(dias_solicitados, tipo_solicitud):
        """
        Valida que las vacaciones fraccionadas no excedan 7 días
        """
        if tipo_solicitud == 'fraccionada' and dias_solicitados > 7:
            raise ValidationError(
                'Las vacaciones fraccionadas no pueden exceder 7 días. '
                f'Días solicitados: {dias_solicitados}'
            )
    
    @staticmethod
    def validar_saldo_disponible(periodo, dias_solicitados):
        """
        Valida que el empleado tenga saldo suficiente para la solicitud
        """
        if periodo.dias_pendientes < dias_solicitados:
            raise ValidationError(
                f'Saldo insuficiente. Días disponibles: {periodo.dias_pendientes}, '
                f'días solicitados: {dias_solicitados}'
            )
    
    @staticmethod
    def validar_periodo_vigente(periodo):
        """
        Valida que el período vacacional esté vigente
        """
        if periodo.estado_periodo != 'vigente':
            raise ValidationError(
                f'El período vacacional {periodo.anio_periodo} no está vigente. '
                f'Estado actual: {periodo.estado_periodo}'
            )
    
    @staticmethod
    def validar_fechas_solicitud(fecha_inicio, fecha_fin):
        """
        Valida que las fechas de la solicitud sean coherentes
        """
        if fecha_inicio > fecha_fin:
            raise ValidationError(
                'La fecha de inicio no puede ser posterior a la fecha de fin'
            )
        
        if fecha_inicio < timezone.now().date():
            raise ValidationError(
                'La fecha de inicio no puede ser anterior a la fecha actual'
            )
    
    @staticmethod
    def validar_dias_habiles(fecha_inicio, fecha_fin, dias_habiles_calculados):
        """
        Valida que los días hábiles calculados sean correctos
        """
        # Calcular días hábiles manualmente para validar
        dias_totales = (fecha_fin - fecha_inicio).days + 1
        
        # Contar fines de semana
        fines_semana = 0
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            if fecha_actual.weekday() >= 5:  # Sábado (5) y Domingo (6)
                fines_semana += 1
            fecha_actual += timedelta(days=1)
        
        dias_habiles_esperados = dias_totales - fines_semana
        
        if dias_habiles_calculados != dias_habiles_esperados:
            raise ValidationError(
                f'Error en el cálculo de días hábiles. '
                f'Esperados: {dias_habiles_esperados}, '
                f'calculados: {dias_habiles_calculados}'
            )
    
    @staticmethod
    def validar_inclusion_fines_semana(fecha_inicio, fecha_fin, incluye_fines_semana):
        """
        Valida la configuración de inclusión de fines de semana
        """
        # Verificar si hay fines de semana en el rango
        tiene_fines_semana = False
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            if fecha_actual.weekday() >= 5:  # Sábado (5) y Domingo (6)
                tiene_fines_semana = True
                break
            fecha_actual += timedelta(days=1)
        
        if tiene_fines_semana and not incluye_fines_semana:
            raise ValidationError(
                'El rango de fechas incluye fines de semana. '
                'Debe marcar la opción "Incluye fines de semana"'
            )
    
    @staticmethod
    def validar_vencimiento_periodo(periodo, fecha_solicitud=None):
        """
        Valida que el período no esté próximo a vencer
        """
        if fecha_solicitud is None:
            fecha_solicitud = timezone.now().date()
        
        dias_para_vencer = (periodo.fecha_vencimiento - fecha_solicitud).days
        
        if dias_para_vencer < 0:
            raise ValidationError(
                f'El período vacacional {periodo.anio_periodo} ya venció '
                f'el {periodo.fecha_vencimiento}'
            )
        
        if dias_para_vencer <= 30:
            # Advertencia, no error
            return {
                'warning': f'El período vacacional vence en {dias_para_vencer} días '
                          f'({periodo.fecha_vencimiento})'
            }
    
    @staticmethod
    def validar_configuracion_parametro(parametro, valor, tipo_dato):
        """
        Valida que el valor de configuración sea del tipo correcto
        """
        try:
            if tipo_dato == 'entero':
                int(valor)
            elif tipo_dato == 'decimal':
                Decimal(valor)
            elif tipo_dato == 'booleano':
                if valor.lower() not in ['true', 'false', '1', '0', 'si', 'no']:
                    raise ValueError()
            elif tipo_dato == 'fecha':
                datetime.strptime(valor, '%Y-%m-%d')
            # 'texto' no necesita validación especial
        except (ValueError, TypeError):
            raise ValidationError(
                f'El valor "{valor}" no es válido para el tipo de dato "{tipo_dato}" '
                f'del parámetro "{parametro}"'
            )
    
    @staticmethod
    def validar_solicitud_duplicada(empleado, fecha_inicio, fecha_fin, solicitud_actual=None):
        """
        Valida que no exista una solicitud duplicada en las mismas fechas
        """
        from .models import SolicitudVacaciones
        
        # Buscar solicitudes que se solapen con las fechas
        solicitudes_existentes = SolicitudVacaciones.objects.filter(
            empleado=empleado,
            fecha_inicio_solicitud__lte=fecha_fin,
            fecha_fin_solicitud__gte=fecha_inicio,
            estado_solicitud__in=['enviada', 'en_revision', 'aprobada']
        )
        
        # Excluir la solicitud actual si se está editando
        if solicitud_actual:
            solicitudes_existentes = solicitudes_existentes.exclude(
                solicitud_id=solicitud_actual.solicitud_id
            )
        
        if solicitudes_existentes.exists():
            solicitud_conflicto = solicitudes_existentes.first()
            raise ValidationError(
                f'Ya existe una solicitud de vacaciones en fechas que se solapan. '
                f'Solicitud #{solicitud_conflicto.numero_solicitud} '
                f'del {solicitud_conflicto.fecha_inicio_solicitud} '
                f'al {solicitud_conflicto.fecha_fin_solicitud}'
            )
    
    @staticmethod
    def validar_goce_contra_solicitud(solicitud, fecha_inicio_goce, fecha_fin_goce, dias_gozados):
        """
        Valida que el goce esté dentro de los parámetros de la solicitud
        """
        if fecha_inicio_goce < solicitud.fecha_inicio_solicitud:
            raise ValidationError(
                'La fecha de inicio del goce no puede ser anterior '
                'a la fecha de inicio de la solicitud'
            )
        
        if fecha_fin_goce > solicitud.fecha_fin_solicitud:
            raise ValidationError(
                'La fecha de fin del goce no puede ser posterior '
                'a la fecha de fin de la solicitud'
            )
        
        if dias_gozados > solicitud.dias_solicitados:
            raise ValidationError(
                f'Los días gozados ({dias_gozados}) no pueden exceder '
                f'los días solicitados ({solicitud.dias_solicitados})'
            )
    
    @staticmethod
    def validar_estado_transicion(estado_actual, estado_nuevo):
        """
        Valida que la transición de estado sea válida
        """
        transiciones_validas = {
            'borrador': ['enviada', 'cancelada'],
            'enviada': ['en_revision', 'cancelada'],
            'en_revision': ['aprobada', 'rechazada', 'cancelada'],
            'aprobada': ['cancelada'],  # Solo se puede cancelar si no se ha gozado
            'rechazada': ['enviada'],  # Se puede reenviar después de correcciones
            'cancelada': []  # Estado final
        }
        
        if estado_nuevo not in transiciones_validas.get(estado_actual, []):
            raise ValidationError(
                f'No se puede cambiar el estado de "{estado_actual}" a "{estado_nuevo}"'
            )


class VacacionesBusinessRules:
    """
    Reglas de negocio específicas para vacaciones
    """
    
    @staticmethod
    def calcular_dias_habiles(fecha_inicio, fecha_fin, incluye_fines_semana=False):
        """
        Calcula los días hábiles entre dos fechas
        """
        dias_totales = (fecha_fin - fecha_inicio).days + 1
        
        if incluye_fines_semana:
            return dias_totales
        
        # Contar solo días hábiles (lunes a viernes)
        dias_habiles = 0
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            if fecha_actual.weekday() < 5:  # Lunes (0) a Viernes (4)
                dias_habiles += 1
            fecha_actual += timedelta(days=1)
        
        return dias_habiles
    
    @staticmethod
    def generar_numero_solicitud(empleado, anio=None):
        """
        Genera un número único para la solicitud
        """
        if anio is None:
            anio = timezone.now().year
        
        from .models import SolicitudVacaciones
        
        # Contar solicitudes del empleado en el año
        count = SolicitudVacaciones.objects.filter(
            empleado=empleado,
            fecha_registro__year=anio
        ).count() + 1
        
        return f"VAC-{empleado.numero_documento}-{anio}-{count:03d}"
    
    @staticmethod
    def calcular_fecha_vencimiento(fecha_inicio_periodo):
        """
        Calcula la fecha de vencimiento del período (1 año después)
        """
        return fecha_inicio_periodo.replace(year=fecha_inicio_periodo.year + 1)
    
    @staticmethod
    def puede_fraccionar_vacaciones(empleado, configuracion=None):
        """
        Determina si el empleado puede fraccionar sus vacaciones
        """
        # Por defecto, todos pueden fraccionar
        # Aquí se pueden agregar reglas específicas según el tipo de empleado
        return True
    
    @staticmethod
    def obtener_dias_vacaciones_por_anio(empleado, anio):
        """
        Obtiene los días de vacaciones que corresponden al empleado por año
        """
        # Por defecto 30 días, pero puede variar según el régimen laboral
        dias_base = 30
        
        # Aquí se pueden agregar reglas específicas según:
        # - Régimen laboral
        # - Años de servicio
        # - Tipo de contrato
        
        return dias_base