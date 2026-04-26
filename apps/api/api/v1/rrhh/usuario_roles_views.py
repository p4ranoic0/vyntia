from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from apps.identity.models import UsuarioRoles, Usuario, Rol
from apps.core.responses import APIResponse
from apps.core.permissions import IsAuthenticated
from apps.core.decorators import (
    require_authenticated, require_hr, require_permissions,
    require_manager, require_admin
)
from .usuario_roles_serializers import (
    UsuarioRolesSerializer, UsuarioRolesCreateSerializer, 
    UsuarioRolesListSerializer, AsignarRolSerializer
)
from .permissions import RRHHPermission


class UsuarioRolesViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las asignaciones de roles a usuarios
    """
    queryset = UsuarioRoles.objects.all()
    serializer_class = UsuarioRolesSerializer
    permission_classes = [IsAuthenticated, RRHHPermission]
    
    @require_admin()
    def list(self, request, *args, **kwargs):
        """Listar asignaciones de roles - requiere rol administrador."""
        return super().list(request, *args, **kwargs)
    
    @require_admin()
    def retrieve(self, request, *args, **kwargs):
        """Obtener asignación específica - requiere rol administrador."""
        return super().retrieve(request, *args, **kwargs)
    
    @require_admin()
    def update(self, request, *args, **kwargs):
        """Actualizar asignación - requiere rol administrador."""
        return super().update(request, *args, **kwargs)
    
    @require_admin()
    def partial_update(self, request, *args, **kwargs):
        """Actualizar asignación parcialmente - requiere rol administrador."""
        return super().partial_update(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """
        Retorna la clase de serializer apropiada según la acción
        """
        if self.action == 'create':
            return UsuarioRolesCreateSerializer
        elif self.action == 'list':
            return UsuarioRolesListSerializer
        return UsuarioRolesSerializer
    
    def get_queryset(self):
        """
        Filtra el queryset según los parámetros de consulta
        """
        queryset = UsuarioRoles.objects.select_related('usuario', 'rol', 'asignado_por_usuario')
        
        # Filtrar por usuario
        usuario_id = self.request.query_params.get('usuario_id')
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)
        
        # Filtrar por rol
        rol_id = self.request.query_params.get('rol_id')
        if rol_id:
            queryset = queryset.filter(rol_id=rol_id)
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', 'activo')
        if estado:
            queryset = queryset.filter(estado_asignacion=estado)
        
        return queryset.order_by('-fecha_asignacion')
    
    @require_admin()
    def create(self, request, *args, **kwargs):
        """
        Crea una nueva asignación de rol a usuario - requiere rol administrador.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                # Verificar si ya existe una asignación activa
                usuario_id = serializer.validated_data['usuario'].usuario_id
                rol_id = serializer.validated_data['rol'].rol_id
                
                asignacion_existente = UsuarioRoles.objects.filter(
                    usuario_id=usuario_id,
                    rol_id=rol_id,
                    estado_asignacion='activo'
                ).first()
                
                if asignacion_existente:
                    return APIResponse.error(
                        message="El usuario ya tiene este rol asignado",
                        errors={"rol": ["Ya existe una asignación activa para este rol"]}
                    )
                
                # Crear la asignación
                usuario_rol = serializer.save(
                    asignado_por_usuario=request.user,
                    fecha_asignacion=timezone.now(),
                    estado_asignacion='activo'
                )
                
                response_serializer = UsuarioRolesSerializer(usuario_rol)
                return APIResponse.success(
                    data=response_serializer.data,
                    message="Rol asignado exitosamente al usuario"
                )
            else:
                return APIResponse.error(
                    message="Datos inválidos para asignar rol",
                    errors=serializer.errors
                )
        except Exception as e:
            return APIResponse.error(
                message="Error al asignar rol al usuario",
                errors={"detail": str(e)}
            )
    
    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """
        Marca una asignación como inactiva en lugar de eliminarla - requiere rol administrador.
        """
        try:
            instance = self.get_object()
            
            if instance.estado_asignacion == 'inactivo':
                return APIResponse.error(
                    message="Esta asignación ya está inactiva",
                    errors={"estado": ["La asignación ya fue removida"]}
                )
            
            # Marcar como inactivo
            instance.estado_asignacion = 'inactivo'
            instance.fecha_expiracion = timezone.now()
            instance.save()
            
            return APIResponse.success(
                message="Asignación de rol removida exitosamente"
            )
        except Exception as e:
            return APIResponse.error(
                message="Error al remover asignación de rol",
                errors={"detail": str(e)}
            )
    
    @require_authenticated()
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """
        Obtiene todas las asignaciones de roles activas
        """
        try:
            asignaciones = self.get_queryset().filter(estado_asignacion='activo')
            serializer = UsuarioRolesListSerializer(asignaciones, many=True)
            
            return APIResponse.success(
                data=serializer.data,
                message="Asignaciones activas obtenidas exitosamente"
            )
        except Exception as e:
            return APIResponse.error(
                message="Error al obtener asignaciones activas",
                errors={"detail": str(e)}
            )
    
    @require_admin()
    @action(detail=False, methods=['get'])
    def por_usuario(self, request):
        """
        Obtiene las asignaciones de roles para un usuario específico
        """
        try:
            usuario_id = request.query_params.get('usuario_id')
            if not usuario_id:
                return APIResponse.error(
                    message="ID del usuario es requerido",
                    errors={"usuario_id": ["Este parámetro es requerido"]}
                )
            
            asignaciones = self.get_queryset().filter(
                usuario_id=usuario_id,
                estado_asignacion='activo'
            )
            
            serializer = UsuarioRolesListSerializer(asignaciones, many=True)
            return APIResponse.success(
                data=serializer.data,
                message=f"Roles del usuario obtenidos exitosamente"
            )
        except Exception as e:
            return APIResponse.error(
                message="Error al obtener roles del usuario",
                errors={"detail": str(e)}
            )
    
    @require_admin()
    @action(detail=False, methods=['get'])
    def por_rol(self, request):
        """
        Obtiene los usuarios que tienen un rol específico
        """
        try:
            rol_id = request.query_params.get('rol_id')
            if not rol_id:
                return APIResponse.error(
                    message="ID del rol es requerido",
                    errors={"rol_id": ["Este parámetro es requerido"]}
                )
            
            asignaciones = self.get_queryset().filter(
                rol_id=rol_id,
                estado_asignacion='activo'
            )
            
            serializer = UsuarioRolesListSerializer(asignaciones, many=True)
            return APIResponse.success(
                data=serializer.data,
                message=f"Usuarios con el rol obtenidos exitosamente"
            )
        except Exception as e:
            return APIResponse.error(
                message="Error al obtener usuarios con el rol",
                errors={"detail": str(e)}
            )
    
    @require_admin()
    @action(detail=False, methods=['post'])
    def asignar_multiple(self, request):
        """
        Asigna múltiples roles a un usuario o un rol a múltiples usuarios
        """
        try:
            usuario_ids = request.data.get('usuario_ids', [])
            rol_ids = request.data.get('rol_ids', [])
            fecha_expiracion = request.data.get('fecha_expiracion')
            
            if not usuario_ids or not rol_ids:
                return APIResponse.error(
                    message="Se requieren IDs de usuarios y roles",
                    errors={
                        "usuario_ids": ["Este campo es requerido"] if not usuario_ids else [],
                        "rol_ids": ["Este campo es requerido"] if not rol_ids else []
                    }
                )
            
            asignaciones_creadas = []
            errores = []
            
            for usuario_id in usuario_ids:
                for rol_id in rol_ids:
                    # Verificar si ya existe
                    if UsuarioRoles.objects.filter(
                        usuario_id=usuario_id,
                        rol_id=rol_id,
                        estado_asignacion='activo'
                    ).exists():
                        errores.append(f"Usuario {usuario_id} ya tiene el rol {rol_id}")
                        continue
                    
                    # Crear asignación
                    try:
                        usuario_rol = UsuarioRoles.objects.create(
                            usuario_id=usuario_id,
                            rol_id=rol_id,
                            fecha_asignacion=timezone.now(),
                            fecha_expiracion=fecha_expiracion,
                            estado_asignacion='activo',
                            asignado_por_usuario=request.user
                        )
                        asignaciones_creadas.append(usuario_rol)
                    except Exception as e:
                        errores.append(f"Error asignando rol {rol_id} a usuario {usuario_id}: {str(e)}")
            
            if asignaciones_creadas:
                serializer = UsuarioRolesSerializer(asignaciones_creadas, many=True)
                response_data = {
                    "asignaciones": serializer.data,
                    "total_creadas": len(asignaciones_creadas),
                    "errores": errores
                }
                return APIResponse.success(
                    data=response_data,
                    message=f"Se crearon {len(asignaciones_creadas)} asignaciones exitosamente"
                )
            else:
                return APIResponse.error(
                    message="No se pudo crear ninguna asignación",
                    errors={"detail": errores}
                )
        except Exception as e:
            return APIResponse.error(
                message="Error en asignación múltiple",
                errors={"detail": str(e)}
            )
    
    @require_hr()
    @action(detail=False, methods=['get'])
    def buscar_usuarios_por_roles(self, request):
        """
        Busca usuarios que tienen roles específicos asignados
        Parámetros de consulta:
        - rol_ids: Lista de IDs de roles separados por coma
        - nombres: Filtro por nombres de usuario (búsqueda parcial)
        - estado: Estado de la asignación (activo, inactivo, expirado)
        - operador: 'AND' o 'OR' para múltiples roles (por defecto 'OR')
        """
        try:
            # Obtener parámetros de consulta
            rol_ids_param = request.query_params.get('rol_ids', '')
            nombres_filtro = request.query_params.get('nombres', '')
            estado_asignacion = request.query_params.get('estado', 'activo')
            operador = request.query_params.get('operador', 'OR').upper()
            
            if not rol_ids_param:
                return APIResponse.error(
                    message="Se requiere al menos un ID de rol",
                    errors={"rol_ids": ["Este parámetro es requerido"]}
                )
            
            # Convertir rol_ids a lista de enteros
            try:
                rol_ids = [int(id.strip()) for id in rol_ids_param.split(',') if id.strip()]
            except ValueError:
                return APIResponse.error(
                    message="IDs de roles inválidos",
                    errors={"rol_ids": ["Deben ser números enteros separados por coma"]}
                )
            
            # Construir consulta base
            queryset = Usuario.objects.select_related('empleado').prefetch_related(
                'roles_asignados__rol'
            )
            
            # Filtrar por nombres si se proporciona
            if nombres_filtro:
                queryset = queryset.filter(
                    Q(nombres_usuario__icontains=nombres_filtro) |
                    Q(empleado__nombres_empleado__icontains=nombres_filtro) |
                    Q(empleado__apellido_paterno__icontains=nombres_filtro) |
                    Q(empleado__apellido_materno__icontains=nombres_filtro)
                )
            
            # Filtrar por roles asignados
            if operador == 'AND':
                # Usuario debe tener TODOS los roles especificados
                for rol_id in rol_ids:
                    queryset = queryset.filter(
                        roles_asignados__rol_id=rol_id,
                        roles_asignados__estado_asignacion=estado_asignacion
                    )
            else:
                # Usuario debe tener AL MENOS UNO de los roles especificados
                queryset = queryset.filter(
                    roles_asignados__rol_id__in=rol_ids,
                    roles_asignados__estado_asignacion=estado_asignacion
                ).distinct()
            
            # Serializar resultados
            usuarios_data = []
            for usuario in queryset:
                # Obtener roles activos del usuario
                roles_activos = UsuarioRoles.objects.filter(
                    usuario=usuario,
                    estado_asignacion=estado_asignacion
                ).select_related('rol')
                
                usuario_data = {
                    'usuario_id': usuario.usuario_id,
                    'nombres_usuario': usuario.nombres_usuario,
                    'correo_institucional': usuario.correo_institucional,
                    'empleado': {
                        'nombres_empleado': usuario.empleado.nombres_empleado if usuario.empleado else None,
                        'apellido_paterno': usuario.empleado.apellido_paterno if usuario.empleado else None,
                        'apellido_materno': usuario.empleado.apellido_materno if usuario.empleado else None,
                    } if usuario.empleado else None,
                    'roles_asignados': [
                        {
                            'rol_id': ur.rol.rol_id,
                            'nombre_rol': ur.rol.nombre_rol,
                            'descripcion_rol': ur.rol.descripcion_rol,
                            'fecha_asignacion': ur.fecha_asignacion,
                            'fecha_expiracion': ur.fecha_expiracion,
                            'estado_asignacion': ur.estado_asignacion
                        }
                        for ur in roles_activos
                    ]
                }
                usuarios_data.append(usuario_data)
            
            # Información adicional
            total_usuarios = len(usuarios_data)
            roles_info = Rol.objects.filter(rol_id__in=rol_ids).values('rol_id', 'nombre_rol')
            
            response_data = {
                'usuarios': usuarios_data,
                'total_usuarios': total_usuarios,
                'filtros_aplicados': {
                    'rol_ids': rol_ids,
                    'roles_nombres': list(roles_info),
                    'nombres_filtro': nombres_filtro,
                    'estado_asignacion': estado_asignacion,
                    'operador': operador
                }
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Se encontraron {total_usuarios} usuarios con los roles especificados"
            )
            
        except Exception as e:
            return APIResponse.error(
                message="Error al buscar usuarios por roles",
                errors={"detail": str(e)}
            )