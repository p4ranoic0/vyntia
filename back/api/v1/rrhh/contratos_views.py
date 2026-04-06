from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.decorators import (
    require_authenticated, require_hr, require_permissions,
    require_manager, require_admin
)

from app_rrhh.models import ContratosAdendas, Empleado, Area
from .contratos_serializers import (
    ContratosAdendasSerializer, ContratosAdendasCreateSerializer,
    ContratosAdendasUpdateSerializer, ContratosAdendasListSerializer,
    ContratoReporteSerializer, AlertaVencimientoSerializer
)
from core.responses import APIResponse
from core.pagination import StandardResultsSetPagination


class ContratosAdendasViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de contratos y adendas.
    
    Proporciona operaciones CRUD completas y funcionalidades específicas
    como alertas de vencimiento, reportes por área y estadísticas.
    """
    queryset = ContratosAdendas.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar contratos y adendas - requiere autenticación."""
        return super().list(request, *args, **kwargs)
    
    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        """Obtener contrato específico - requiere autenticación."""
        return super().retrieve(request, *args, **kwargs)
    
    @require_hr()
    def create(self, request, *args, **kwargs):
        """Crear contrato o adenda - requiere rol RRHH."""
        return super().create(request, *args, **kwargs)
    
    @require_hr()
    def update(self, request, *args, **kwargs):
        """Actualizar contrato o adenda - requiere rol RRHH."""
        return super().update(request, *args, **kwargs)
    
    @require_hr()
    def partial_update(self, request, *args, **kwargs):
        """Actualizar contrato parcialmente - requiere rol RRHH."""
        return super().partial_update(request, *args, **kwargs)
    
    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar contrato o adenda - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == 'create':
            return ContratosAdendasCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ContratosAdendasUpdateSerializer
        elif self.action == 'list':
            return ContratosAdendasListSerializer
        return ContratosAdendasSerializer
    
    def get_queryset(self):
        """Optimiza las consultas con select_related y prefetch_related."""
        queryset = ContratosAdendas.objects.select_related(
            'empleado', 'area', 'creado_por', 'modificado_por'
        ).order_by('-fecha_creacion')
        
        # Filtros por parámetros de consulta
        empleado_id = self.request.query_params.get('empleado_id')
        area_id = self.request.query_params.get('area_id')
        tipo_documento = self.request.query_params.get('tipo_documento')
        estado = self.request.query_params.get('estado')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if empleado_id:
            queryset = queryset.filter(empleado_id=empleado_id)
        
        if area_id:
            queryset = queryset.filter(area_id=area_id)
        
        if tipo_documento:
            queryset = queryset.filter(tipo_documento=tipo_documento)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_inicio__gte=fecha_inicio)
            except ValueError:
                pass
        
        if fecha_fin:
            try:
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_fin__lte=fecha_fin)
            except ValueError:
                pass
        
        return queryset
    
    # @extend_schema(
    #     description="Obtiene contratos próximos a vencer",
    #     parameters=[
    #         OpenApiParameter('dias', int, description="Días de anticipación para la alerta (default: 30)"),
    #         OpenApiParameter('area_id', int, description="Filtrar por área específica")
    #     ],
    #     responses=AlertaVencimientoSerializer(many=True)
    # )
    @require_hr()
    @action(detail=False, methods=['get'])
    def alertas_vencimiento(self, request):
        """Obtiene contratos próximos a vencer."""
        try:
            dias = int(request.query_params.get('dias', 30))
            area_id = request.query_params.get('area_id')
            
            fecha_limite = timezone.now().date() + timedelta(days=dias)
            
            # Filtrar contratos activos próximos a vencer
            queryset = self.get_queryset().filter(
                estado='ACTIVO',
                fecha_fin__lte=fecha_limite,
                fecha_fin__gte=timezone.now().date()
            )
            
            if area_id:
                queryset = queryset.filter(area_id=area_id)
            
            # Calcular días restantes
            contratos_vencimiento = []
            for contrato in queryset:
                dias_restantes = (contrato.fecha_fin - timezone.now().date()).days
                contratos_vencimiento.append({
                    'contrato': contrato,
                    'dias_restantes': dias_restantes
                })
            
            # Ordenar por días restantes (más urgentes primero)
            contratos_vencimiento.sort(key=lambda x: x['dias_restantes'])
            
            serializer = AlertaVencimientoSerializer(
                [item['contrato'] for item in contratos_vencimiento],
                many=True,
                context={'request': request}
            )
            
            return APIResponse.success(
                data=serializer.data,
                message=f"Se encontraron {len(contratos_vencimiento)} contratos próximos a vencer"
            )
            
        except Exception as e:
            return APIResponse.error(
                message="Error al obtener alertas de vencimiento",
                errors={'detail': str(e)}
            )
    
    # @extend_schema(
    #     description="Genera reporte de contratos por área y período",
    #     parameters=[
    #         OpenApiParameter('area_id', int, description="ID del área (opcional)"),
    #         OpenApiParameter('fecha_inicio', str, description="Fecha de inicio del período (YYYY-MM-DD)"),
    #         OpenApiParameter('fecha_fin', str, description="Fecha de fin del período (YYYY-MM-DD)"),
    #         OpenApiParameter('tipo_documento', str, description="Tipo de documento a incluir")
    #     ]
    # )
    @require_hr()
    @action(detail=False, methods=['get'])
    def reporte_contratos(self, request):
        """Genera reporte estadístico de contratos."""
        try:
            area_id = request.query_params.get('area_id')
            fecha_inicio = request.query_params.get('fecha_inicio')
            fecha_fin = request.query_params.get('fecha_fin')
            tipo_documento = request.query_params.get('tipo_documento')
            
            queryset = self.get_queryset()
            
            # Aplicar filtros adicionales
            if area_id:
                queryset = queryset.filter(area_id=area_id)
            
            if fecha_inicio:
                try:
                    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                    queryset = queryset.filter(fecha_inicio__gte=fecha_inicio)
                except ValueError:
                    pass
            
            if fecha_fin:
                try:
                    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                    queryset = queryset.filter(fecha_fin__lte=fecha_fin)
                except ValueError:
                    pass
            
            if tipo_documento:
                queryset = queryset.filter(tipo_documento=tipo_documento)
            
            # Estadísticas generales
            total_contratos = queryset.count()
            contratos_activos = queryset.filter(estado='ACTIVO').count()
            contratos_vencidos = queryset.filter(estado='VENCIDO').count()
            contratos_terminados = queryset.filter(estado='TERMINADO').count()
            
            # Estadísticas por tipo
            stats_por_tipo = queryset.values('tipo_documento').annotate(
                total=Count('contrato_id'),
                activos=Count('contrato_id', filter=Q(estado='ACTIVO')),
                valor_total=Sum('salario_bruto')
            )

            # Estadísticas por área
            stats_por_area = queryset.values(
                'area__siglas_area', 'area__nombre_unidad_organica'
            ).annotate(
                total=Count('contrato_id'),
                activos=Count('contrato_id', filter=Q(estado='ACTIVO')),
                valor_total=Sum('salario_bruto')
            )
            
            # Salario promedio
            salario_promedio = queryset.aggregate(
                promedio=Avg('salario_bruto')
            )['promedio'] or 0
            
            # Valor total de contratos activos
            valor_total_activos = queryset.filter(
                estado='ACTIVO'
            ).aggregate(
                total=Sum('salario_bruto')
            )['total'] or 0
            
            reporte_data = {
                'resumen': {
                    'total_contratos': total_contratos,
                    'contratos_activos': contratos_activos,
                    'contratos_vencidos': contratos_vencidos,
                    'contratos_terminados': contratos_terminados,
                    'salario_promedio': float(salario_promedio),
                    'valor_total_activos': float(valor_total_activos)
                },
                'por_tipo': list(stats_por_tipo),
                'por_area': list(stats_por_area),
                'filtros_aplicados': {
                    'area_id': area_id,
                    'fecha_inicio': fecha_inicio.isoformat() if fecha_inicio else None,
                    'fecha_fin': fecha_fin.isoformat() if fecha_fin else None,
                    'tipo_documento': tipo_documento
                },
                'fecha_generacion': timezone.now().isoformat()
            }
            
            return APIResponse.success(
                data=reporte_data,
                message="Reporte generado exitosamente"
            )
            
        except Exception as e:
            return APIResponse.error(
                message="Error al generar reporte",
                errors={'detail': str(e)}
            )
    
    # @extend_schema(description="Obtiene estadísticas generales de contratos")
    @require_hr()
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas generales del sistema de contratos."""
        try:
            # Estadísticas básicas
            total_contratos = ContratosAdendas.objects.count()
            contratos_activos = ContratosAdendas.objects.filter(estado='ACTIVO').count()
            
            # Contratos por vencer en los próximos 30 días
            fecha_limite = timezone.now().date() + timedelta(days=30)
            contratos_por_vencer = ContratosAdendas.objects.filter(
                estado='ACTIVO',
                fecha_fin__lte=fecha_limite,
                fecha_fin__gte=timezone.now().date()
            ).count()
            
            # Distribución por tipo de documento
            distribucion_tipos = ContratosAdendas.objects.values(
                'tipo_documento'
            ).annotate(
                total=Count('contrato_id')
            ).order_by('-total')

            # Empleados con contratos activos
            empleados_con_contratos = ContratosAdendas.objects.filter(
                estado='ACTIVO'
            ).values('empleado').distinct().count()

            # Áreas con más contratos
            areas_top = ContratosAdendas.objects.values(
                'area__siglas_area', 'area__nombre_unidad_organica'
            ).annotate(
                total=Count('contrato_id')
            ).order_by('-total')[:5]
            
            estadisticas_data = {
                'resumen_general': {
                    'total_contratos': total_contratos,
                    'contratos_activos': contratos_activos,
                    'contratos_por_vencer': contratos_por_vencer,
                    'empleados_con_contratos': empleados_con_contratos
                },
                'distribucion_tipos': list(distribucion_tipos),
                'areas_top': list(areas_top),
                'fecha_consulta': timezone.now().isoformat()
            }
            
            return APIResponse.success(
                data=estadisticas_data,
                message="Estadísticas obtenidas exitosamente"
            )
            
        except Exception as e:
            return APIResponse.error(
                message="Error al obtener estadísticas",
                errors={'detail': str(e)}
            )
    
    # @extend_schema(
    #     description="Renueva un contrato creando uno nuevo",
    #     request={
    #         'fecha_inicio': str,
    #         'fecha_fin': str,
    #         'salario_bruto': float,
    #         'observaciones': str
    #     }
    # )
    @require_hr()
    @action(detail=True, methods=['post'])
    def renovar_contrato(self, request, pk=None):
        """Renueva un contrato existente creando uno nuevo."""
        try:
            contrato_original = self.get_object()
            
            # Validar que el contrato se pueda renovar
            if contrato_original.estado not in ['ACTIVO', 'VENCIDO']:
                return APIResponse.error(
                    message="Solo se pueden renovar contratos activos o vencidos",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Datos para el nuevo contrato (heredar campos del original)
            nuevo_contrato_data = {
                'empleado': contrato_original.empleado_id,
                'area': contrato_original.area_id,
                'tipo_documento': contrato_original.tipo_documento,
                'fecha_inicio': request.data.get('fecha_inicio'),
                'fecha_fin': request.data.get('fecha_fin'),
                'salario_bruto': request.data.get('salario_bruto', contrato_original.salario_bruto),
                'cargo': contrato_original.cargo,
                'jornada_laboral': contrato_original.jornada_laboral,
                'funciones': contrato_original.funciones,
                'lugar_trabajo': contrato_original.lugar_trabajo,
                'horario_trabajo': contrato_original.horario_trabajo,
                'observaciones': request.data.get('observaciones', f'Renovación del contrato {contrato_original.contrato_id}'),
            }
            
            # Crear el nuevo contrato
            serializer = ContratosAdendasCreateSerializer(
                data=nuevo_contrato_data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                nuevo_contrato = serializer.save(creado_por=request.user)
                
                # Activar el nuevo contrato
                nuevo_contrato.estado = 'ACTIVO'
                nuevo_contrato.save(update_fields=['estado'])
                
                # Marcar el contrato original como terminado
                contrato_original.estado = 'TERMINADO'
                obs_anterior = contrato_original.observaciones or ''
                contrato_original.observaciones = f'{obs_anterior} - Renovado con contrato {nuevo_contrato.contrato_id}'.strip(' -')
                contrato_original.save(update_fields=['estado', 'observaciones'])
                
                return APIResponse.success(
                    data=ContratosAdendasSerializer(nuevo_contrato, context={'request': request}).data,
                    message="Contrato renovado exitosamente",
                    status_code=status.HTTP_201_CREATED
                )
            else:
                return APIResponse.error(
                    message="Error en los datos del nuevo contrato",
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return APIResponse.error(
                message="Error al renovar contrato",
                errors={'detail': str(e)}
            )