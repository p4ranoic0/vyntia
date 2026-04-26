from django.db import models
from django.utils import timezone
from datetime import timedelta


class ContratosAdendasManager(models.Manager):
    """
    Manager personalizado para el modelo ContratosAdendas.
    
    Proporciona métodos de consulta optimizados y funcionalidades
    específicas para la gestión de contratos y adendas.
    """
    
    def get_queryset(self):
        """Optimiza las consultas por defecto con select_related."""
        return super().get_queryset().select_related(
            'empleado', 'empleado__area', 'creado_por', 'modificado_por'
        )
    
    def activos(self):
        """Retorna solo los contratos activos."""
        return self.filter(estado='ACTIVO')
    
    def vencidos(self):
        """Retorna solo los contratos vencidos."""
        return self.filter(estado='VENCIDO')
    
    def terminados(self):
        """Retorna solo los contratos terminados."""
        return self.filter(estado='TERMINADO')
    
    def contratos(self):
        """Retorna solo los documentos de tipo contrato."""
        return self.filter(
            tipo_documento__in=[
                'CONTRATO_INDEFINIDO',
                'CONTRATO_FIJO',
                'CONTRATO_OBRA',
                'CONTRATO_HONORARIOS',
                'CONTRATO_PRACTICA'
            ]
        )
    
    def adendas(self):
        """Retorna solo los documentos de tipo adenda."""
        return self.filter(
            tipo_documento__in=[
                'ADENDA_SALARIAL',
                'ADENDA_CARGO',
                'ADENDA_HORARIO',
                'ADENDA_EXTENSION'
            ]
        )
    
    def por_empleado(self, empleado_id):
        """Retorna contratos de un empleado específico."""
        return self.filter(empleado_id=empleado_id)
    
    def por_area(self, area_id):
        """Retorna contratos de un área específica."""
        return self.filter(empleado__area_id=area_id)
    
    def proximos_a_vencer(self, dias=30):
        """
        Retorna contratos activos próximos a vencer.
        
        Args:
            dias (int): Número de días de anticipación para la alerta
        """
        fecha_limite = timezone.now().date() + timedelta(days=dias)
        return self.activos().filter(
            fecha_fin__lte=fecha_limite,
            fecha_fin__gte=timezone.now().date()
        ).order_by('fecha_fin')
    
    def vencen_hoy(self):
        """Retorna contratos que vencen hoy."""
        return self.activos().filter(fecha_fin=timezone.now().date())
    
    def vencen_esta_semana(self):
        """Retorna contratos que vencen en los próximos 7 días."""
        return self.proximos_a_vencer(dias=7)
    
    def vencen_este_mes(self):
        """Retorna contratos que vencen en los próximos 30 días."""
        return self.proximos_a_vencer(dias=30)
    
    def por_periodo(self, fecha_inicio=None, fecha_fin=None):
        """
        Retorna contratos en un período específico.
        
        Args:
            fecha_inicio (date): Fecha de inicio del período
            fecha_fin (date): Fecha de fin del período
        """
        queryset = self.get_queryset()
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_inicio__gte=fecha_inicio)
        
        if fecha_fin:
            queryset = queryset.filter(fecha_fin__lte=fecha_fin)
        
        return queryset
    
    def con_salario_mayor_a(self, monto):
        """Retorna contratos con salario bruto mayor al monto especificado."""
        return self.filter(salario_bruto__gt=monto)
    
    def con_salario_entre(self, monto_min, monto_max):
        """Retorna contratos con salario bruto en un rango específico."""
        return self.filter(
            salario_bruto__gte=monto_min,
            salario_bruto__lte=monto_max
        )
    
    def creados_por_usuario(self, usuario_id):
        """Retorna contratos creados por un usuario específico."""
        return self.filter(creado_por_id=usuario_id)
    
    def modificados_recientemente(self, dias=7):
        """Retorna contratos modificados en los últimos días."""
        fecha_limite = timezone.now() - timedelta(days=dias)
        return self.filter(fecha_modificacion__gte=fecha_limite)
    
    def estadisticas_por_tipo(self):
        """
        Retorna estadísticas agrupadas por tipo de documento.
        
        Returns:
            QuerySet: Estadísticas con total, activos y valor total por tipo
        """
        from django.db.models import Count, Sum, Q
        
        return self.values('tipo_documento').annotate(
            total=Count('id'),
            activos=Count('id', filter=Q(estado='ACTIVO')),
            vencidos=Count('id', filter=Q(estado='VENCIDO')),
            terminados=Count('id', filter=Q(estado='TERMINADO')),
            valor_total=Sum('salario_bruto'),
            valor_activos=Sum('salario_bruto', filter=Q(estado='ACTIVO'))
        ).order_by('-total')
    
    def estadisticas_por_area(self):
        """
        Retorna estadísticas agrupadas por área.
        
        Returns:
            QuerySet: Estadísticas con total, activos y valor total por área
        """
        from django.db.models import Count, Sum, Q
        
        return self.values(
            'empleado__area__id',
            'empleado__area__nombre'
        ).annotate(
            total=Count('id'),
            activos=Count('id', filter=Q(estado='ACTIVO')),
            vencidos=Count('id', filter=Q(estado='VENCIDO')),
            terminados=Count('id', filter=Q(estado='TERMINADO')),
            valor_total=Sum('salario_bruto'),
            valor_activos=Sum('salario_bruto', filter=Q(estado='ACTIVO'))
        ).order_by('-total')
    
    def ultimo_contrato_empleado(self, empleado_id):
        """
        Retorna el último contrato (más reciente) de un empleado.
        
        Args:
            empleado_id (int): ID del empleado
            
        Returns:
            ContratosAdendas: Último contrato del empleado o None
        """
        return self.contratos().filter(
            empleado_id=empleado_id
        ).order_by('-fecha_inicio').first()
    
    def contratos_activos_empleado(self, empleado_id):
        """
        Retorna todos los contratos activos de un empleado.
        
        Args:
            empleado_id (int): ID del empleado
            
        Returns:
            QuerySet: Contratos activos del empleado
        """
        return self.contratos().activos().filter(empleado_id=empleado_id)
    
    def adendas_contrato(self, contrato_id):
        """
        Retorna todas las adendas relacionadas con un contrato específico.
        
        Args:
            contrato_id (int): ID del contrato base
            
        Returns:
            QuerySet: Adendas del contrato
        """
        # Nota: Esta funcionalidad requeriría un campo adicional para relacionar
        # las adendas con su contrato base. Por ahora, retornamos adendas del mismo empleado
        try:
            contrato = self.get(id=contrato_id)
            return self.adendas().filter(
                empleado=contrato.empleado,
                fecha_inicio__gte=contrato.fecha_inicio
            ).order_by('fecha_inicio')
        except self.model.DoesNotExist:
            return self.none()
    
    def buscar(self, termino):
        """
        Búsqueda general en contratos por término.
        
        Args:
            termino (str): Término de búsqueda
            
        Returns:
            QuerySet: Contratos que coinciden con el término
        """
        from django.db.models import Q
        
        return self.filter(
            Q(empleado__nombres__icontains=termino) |
            Q(empleado__apellidos__icontains=termino) |
            Q(empleado__rut__icontains=termino) |
            Q(cargo__icontains=termino) |
            Q(observaciones__icontains=termino) |
            Q(empleado__area__nombre__icontains=termino)
        ).distinct()