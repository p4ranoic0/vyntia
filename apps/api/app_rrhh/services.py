"""Business logic services for app_rrhh."""

from django.db import transaction
from django.db.models import Q, Count, Avg, Sum, F
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal

from .models import (
    Area, Empleado, DatosLaborales, DatosFamiliares,
    DatosAcademicos, HistorialUbicaciones, Usuario, Rol, Permiso
)
from apps.core.exceptions import (
    BusinessLogicError, ResourceNotFoundError,
    DuplicateResourceError, InvalidOperationError
)


class EmpleadoService:
    """Service for employee-related business logic."""
    
    @staticmethod
    def crear_empleado_completo(
        datos_personales: Dict[str, Any],
        datos_laborales: Dict[str, Any],
        area_id: int,
        datos_familiares: List[Dict[str, Any]] = None,
        datos_academicos: List[Dict[str, Any]] = None
    ) -> Empleado:
        """Create a complete employee record with all related data.
        
        Args:
            datos_personales: Personal data dictionary
            datos_laborales: Labor data dictionary
            area_id: Area ID for initial location
            datos_familiares: Optional family data list
            datos_academicos: Optional academic data list
            
        Returns:
            Empleado: Created employee instance
            
        Raises:
            DuplicateResourceError: If DNI already exists
            ResourceNotFoundError: If area doesn't exist
            BusinessLogicError: For validation errors
        """
        # Validate DNI uniqueness
        dni = datos_personales.get('dni')
        if dni and Empleado.objects.filter(dni=dni).exists():
            raise DuplicateResourceError(f"Ya existe un empleado con DNI {dni}")
        
        # Validate area exists
        try:
            area = Area.objects.get(area_id=area_id, estado_area='activo')
        except Area.DoesNotExist:
            raise ResourceNotFoundError(f"Área con ID {area_id} no encontrada o inactiva")
        
        with transaction.atomic():
            # Create employee
            empleado = Empleado.objects.create(**datos_personales)
            
            # Create labor data
            DatosLaborales.objects.create(
                empleado=empleado,
                **datos_laborales
            )
            
            # Create initial location
            HistorialUbicaciones.objects.create(
                empleado=empleado,
                area=area,
                fecha_inicio=datos_laborales.get('fecha_ingreso', timezone.now().date()),
                estado=True
            )
            
            # Create family data if provided
            if datos_familiares:
                for familiar in datos_familiares:
                    DatosFamiliares.objects.create(
                        empleado=empleado,
                        **familiar
                    )
            
            # Create academic data if provided
            if datos_academicos:
                for academico in datos_academicos:
                    DatosAcademicos.objects.create(
                        empleado=empleado,
                        **academico
                    )
        
        return empleado
    
    @staticmethod
    def transferir_empleado(empleado_id: int, nueva_area_id: int, fecha_inicio: datetime.date = None) -> HistorialUbicaciones:
        """Transfer employee to new area.
        
        Args:
            empleado_id: Employee ID
            nueva_area_id: New area ID
            fecha_inicio: Transfer start date
            
        Returns:
            HistorialUbicaciones: New location record
            
        Raises:
            ResourceNotFoundError: If employee or area not found
            InvalidOperationError: If employee is inactive
        """
        try:
            empleado = Empleado.objects.get(id=empleado_id)
        except Empleado.DoesNotExist:
            raise ResourceNotFoundError(f"Empleado con ID {empleado_id} no encontrado")
        
        if not empleado.es_activo:
            raise InvalidOperationError("No se puede transferir un empleado inactivo")
        
        try:
            nueva_area = Area.objects.get(area_id=nueva_area_id, estado_area='activo')
        except Area.DoesNotExist:
            raise ResourceNotFoundError(f"Área con ID {nueva_area_id} no encontrada o inactiva")
        
        fecha_inicio = fecha_inicio or timezone.now().date()
        
        with transaction.atomic():
            # Close current location
            ubicacion_actual = empleado.ubicacion_actual()
            if ubicacion_actual:
                ubicacion_actual.fecha_termino = fecha_inicio
                ubicacion_actual.estado = False
                ubicacion_actual.save()
            
            # Create new location
            nueva_ubicacion = HistorialUbicaciones.objects.create(
                empleado=empleado,
                area=nueva_area,
                fecha_inicio=fecha_inicio,
                estado=True
            )
        
        return nueva_ubicacion
    
    @staticmethod
    def obtener_empleados_por_criterios(
        area_id: int = None,
        estado: bool = None,
        genero: bool = None,
        edad_min: int = None,
        edad_max: int = None,
        regimen_laboral: str = None,
        busqueda: str = None
    ) -> List[Empleado]:
        """Get employees by multiple criteria.
        
        Args:
            area_id: Filter by area
            estado: Filter by status
            genero: Filter by gender
            edad_min: Minimum age
            edad_max: Maximum age
            regimen_laboral: Labor regime
            busqueda: Search term
            
        Returns:
            List[Empleado]: Filtered employees
        """
        queryset = Empleado.objects.con_datos_completos()
        
        if estado is not None:
            queryset = queryset.filter(estado=estado)
        
        if genero is not None:
            queryset = queryset.filter(genero_empleado=genero)
        
        if area_id:
            queryset = queryset.filter(
                historialubicaciones__area_destino_id=area_id,
            historialubicaciones__estado=True,
            historialubicaciones__fecha_termino__isnull=True
            )
        
        if edad_min or edad_max:
            queryset = queryset.por_edad(edad_min, edad_max)
        
        if regimen_laboral:
            queryset = queryset.filter(
                datoslaborales__reg_laboral__icontains=regimen_laboral,
                datoslaborales__estado=True
            )
        
        if busqueda:
            queryset = queryset.buscar(busqueda)
        
        return queryset.distinct()
    
    @staticmethod
    def obtener_estadisticas_empleados() -> Dict[str, Any]:
        """Get comprehensive employee statistics.
        
        Returns:
            Dict[str, Any]: Statistics dictionary
        """
        empleados_activos = Empleado.objects.activos()
        
        # Basic demographics
        demograficas = empleados_activos.estadisticas_demograficas()
        
        # By area
        por_area = empleados_activos.values(
            'historialubicaciones__area_destino__siglas_area',
            'historialubicaciones__area_destino__unidad_organica'
        ).filter(
            historialubicaciones__estado=True,
            historialubicaciones__fecha_termino__isnull=True
        ).annotate(
            total=Count('id')
        ).order_by('-total')
        
        # By labor regime
        por_regimen = empleados_activos.values(
            'datoslaborales__reg_laboral'
        ).filter(
            datoslaborales__estado=True
        ).annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Salary statistics
        estadisticas_salariales = DatosLaborales.objects.vigentes().estadisticas_salariales()
        
        return {
            'demograficas': demograficas,
            'por_area': list(por_area),
            'por_regimen': list(por_regimen),
            'salariales': estadisticas_salariales,
            'total_activos': empleados_activos.count(),
            'total_inactivos': Empleado.objects.inactivos().count()
        }


class AreaService:
    """Service for area-related business logic."""
    
    @staticmethod
    def obtener_areas_con_estadisticas() -> List[Dict[str, Any]]:
        """Get areas with employee statistics.
        
        Returns:
            List[Dict[str, Any]]: Areas with statistics
        """
        areas = Area.objects.activas().con_estadisticas()
        
        resultado = []
        for area in areas:
            resultado.append({
                'id': area.area_id,
                'siglas': area.siglas,
                'unidad_organica': area.unidad_organica,
                'organo': area.organo,
                'total_empleados': area.total_empleados_activos or 0,
                'promedio_remuneracion': float(area.promedio_remuneracion or 0)
            })
        
        return resultado
    
    @staticmethod
    def reasignar_empleados_area(area_origen_id: int, area_destino_id: int) -> int:
        """Reassign all employees from one area to another.
        
        Args:
            area_origen_id: Source area ID
            area_destino_id: Destination area ID
            
        Returns:
            int: Number of employees reassigned
            
        Raises:
            ResourceNotFoundError: If areas not found
            InvalidOperationError: If areas are the same
        """
        if area_origen_id == area_destino_id:
            raise InvalidOperationError("Las áreas de origen y destino no pueden ser iguales")
        
        try:
            area_origen = Area.objects.get(area_id=area_origen_id)
            area_destino = Area.objects.get(area_id=area_destino_id, estado_area='activo')
        except Area.DoesNotExist:
            raise ResourceNotFoundError("Una o ambas áreas no fueron encontradas")
        
        empleados_activos = area_origen.empleados_activos()
        fecha_transferencia = timezone.now().date()
        
        with transaction.atomic():
            # Close current locations
            HistorialUbicaciones.objects.filter(
                area=area_origen,
                estado=True,
                fecha_termino__isnull=True
            ).update(
                fecha_termino=fecha_transferencia,
                estado=False
            )
            
            # Create new locations
            nuevas_ubicaciones = [
                HistorialUbicaciones(
                    empleado_id=ubicacion.empleado_id,
                    area=area_destino,
                    fecha_inicio=fecha_transferencia,
                    estado=True
                )
                for ubicacion in empleados_activos
            ]
            
            HistorialUbicaciones.objects.bulk_create(nuevas_ubicaciones)
        
        return len(nuevas_ubicaciones)


# Clase BoletaService removida - funcionalidad migrada a DocumentosDigitalesService con tipo_documento='BOLETA_PAGO'


class UsuarioService:
    """Service for user-related business logic."""
    
    @staticmethod
    def crear_usuario_empleado(
        empleado_id: int,
        username: str,
        password: str,
        roles: List[str] = None
    ) -> Usuario:
        """Create user account for employee.
        
        Args:
            empleado_id: Employee ID
            username: Username
            password: Password
            roles: List of role names
            
        Returns:
            Usuario: Created user
            
        Raises:
            ResourceNotFoundError: If employee not found
            DuplicateResourceError: If username exists
        """
        try:
            empleado = Empleado.objects.get(id=empleado_id, estado=True)
        except Empleado.DoesNotExist:
            raise ResourceNotFoundError(f"Empleado con ID {empleado_id} no encontrado")
        
        if Usuario.objects.filter(username=username).exists():
            raise DuplicateResourceError(f"El username {username} ya existe")
        
        with transaction.atomic():
            usuario = Usuario.objects.create_user(
                username=username,
                password=password,
                empleado=empleado,
                email=empleado.email or '',
                first_name=empleado.nombres or '',
                last_name=f"{empleado.ape_paterno} {empleado.ape_materno}".strip()
            )
            
            # Assign roles if provided
            if roles:
                roles_obj = Rol.objects.filter(nombre__in=roles, estado=True)
                usuario.rol_set.set(roles_obj)
        
        return usuario
    
    @staticmethod
    def verificar_permisos_usuario(usuario_id: int, permiso_nombre: str) -> bool:
        """Check if user has specific permission.
        
        Args:
            usuario_id: User ID
            permiso_nombre: Permission name
            
        Returns:
            bool: True if user has permission
        """
        try:
            usuario = Usuario.objects.get(id=usuario_id, estado=True)
            return usuario.permisos_usuario().filter(
                nombre__icontains=permiso_nombre
            ).exists()
        except Usuario.DoesNotExist:
            return False
    
    @staticmethod
    def obtener_usuarios_sin_login_reciente(dias: int = 90) -> List[Usuario]:
        """Get users without recent login.
        
        Args:
            dias: Number of days
            
        Returns:
            List[Usuario]: Users without recent login
        """
        fecha_limite = timezone.now() - timedelta(days=dias)
        
        return Usuario.objects.filter(
            Q(fecha_ult_login__lt=fecha_limite) | Q(fecha_ult_login__isnull=True),
            estado=True
        ).select_related('empleado')