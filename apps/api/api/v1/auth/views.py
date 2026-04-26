"""Views for authentication API v1."""

from typing import Any, Dict

from app_rrhh.menu_service import MenuService
from app_rrhh.models import Modulos, Permiso, Rol, Usuario
from apps.core.decorators import (
    require_admin,
    require_authenticated,
    require_hr,
    require_manager,
    require_permissions,
)
from apps.core.permissions import IsAuthenticated
from apps.core.responses import APIResponse
from django.contrib.auth import login, logout
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
)


@extend_schema(
    tags=["Authentication"],
    summary="Iniciar sesión",
    description="Autentica un usuario y devuelve tokens JWT de acceso y actualización.",
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(
            description="Autenticación exitosa",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name="LoginExitoso",
                    value={
                        "success": True,
                        "message": "Inicio de sesion exitoso",
                        "data": {
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "user": {
                                "id": 1,
                                "username": "usuario",
                                "email": "usuario@example.com",
                            },
                        },
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(description="Payload inválido o credenciales incompletas"),
        401: OpenApiResponse(
            description="Credenciales inválidas o usuario no autorizado"
        ),
        429: OpenApiResponse(
            description="Demasiados intentos de autenticación (rate limit)"
        ),
    },
)
class LoginAPIView(TokenObtainPairView):
    """API view for user authentication."""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Authenticate user and return JWT tokens in JSON response only.

        Args:
            request: HTTP request
            *args: Additional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Response with user data and tokens in JSON format
        """
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            # Update last login
            user = serializer.user
            if hasattr(user, "ultimo_acceso"):
                user.ultimo_acceso = timezone.now()
                user.save(update_fields=["ultimo_acceso"])

            # Extract tokens and user data
            validated_data = serializer.validated_data

            return APIResponse.success(
                data=validated_data,
                message="Inicio de sesion exitoso",
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            return APIResponse.error(
                message="Error en el inicio de sesion",
                errors={"detail": str(e)},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )


@extend_schema(exclude=True)
class LogoutAPIView(APIView):
    """API view for user logout."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Logout user and blacklist refresh token.

        Args:
            request: HTTP request

        Returns:
            Response confirming logout
        """
        try:
            # Get refresh token from request body
            refresh_token = request.data.get("refresh_token")

            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception:
                    # Token might already be blacklisted or invalid
                    pass

            # Logout from Django session
            logout(request)

            # Return success response
            return APIResponse.success(
                message="Cierre de sesión exitoso", status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return APIResponse.error(
                message="Error al cerrar sesión",
                errors={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(exclude=True)
class UserProfileAPIView(APIView):
    """API view for user profile management."""

    permission_classes = [IsAuthenticated]

    @require_authenticated()
    def get(self, request: Request) -> Response:
        """Get user profile information."""
        try:
            usuario = Usuario.objects.select_related("empleado").get(pk=request.user.pk)
            serializer = UserProfileSerializer(usuario)

            return APIResponse.success(
                data=serializer.data,
                message="Perfil de usuario obtenido exitosamente",
                status_code=status.HTTP_200_OK,
            )

        except Usuario.DoesNotExist:
            return APIResponse.error(
                message="Usuario no encontrado",
                errors={"detail": "No se encontró el perfil del usuario"},
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return APIResponse.error(
                message="Error al obtener el perfil de usuario",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @require_authenticated()
    def put(self, request: Request) -> Response:
        """Update user profile information."""
        try:
            usuario = Usuario.objects.select_related("empleado").get(pk=request.user.pk)
            serializer = UserUpdateSerializer(usuario, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                profile_serializer = UserProfileSerializer(usuario)

                return APIResponse.success(
                    data=profile_serializer.data,
                    message="Perfil actualizado exitosamente",
                    status_code=status.HTTP_200_OK,
                )
            else:
                return APIResponse.error(
                    message="Error en los datos proporcionados",
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return APIResponse.error(
                message="Error al actualizar el perfil",
                errors={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"], url_path="permissions")
    @require_authenticated()
    def get_user_permissions(self, request: Request) -> Response:
        """Get user permissions and roles."""
        try:
            usuario = Usuario.objects.select_related("empleado").get(pk=request.user.pk)

            # Obtener roles activos
            roles_activos = usuario.roles_activos()
            roles_data = [
                {
                    "id": rol.rol_id,
                    "nombre": rol.nombre_rol,
                    "descripcion": rol.descripcion_rol,
                }
                for rol in roles_activos
            ]

            # Obtener permisos activos
            permisos = usuario.permisos_activos()
            if permisos == "*":
                permisos_data = [{"nombre": "*", "descripcion": "Acceso total"}]
            elif hasattr(permisos, "values"):
                permisos_data = [
                    {
                        "id": p.permiso_id,
                        "nombre": p.nombre_permiso,
                        "descripcion": p.descripcion_permiso,
                    }
                    for p in permisos
                ]
            else:
                permisos_data = []

            permissions_data = {
                "roles": roles_data,
                "permisos": permisos_data,
            }

            return APIResponse.success(
                data=permissions_data,
                message="Permisos obtenidos exitosamente",
                status_code=status.HTTP_200_OK,
            )

        except Usuario.DoesNotExist:
            return APIResponse.error(
                message="Usuario no encontrado", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return APIResponse.error(
                message="Error al obtener permisos",
                errors={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(
    tags=["Authentication"],
    summary="Cambiar contraseña",
    description="Permite al usuario autenticado cambiar su contraseña.",
    request=ChangePasswordSerializer,
    responses={
        200: {
            "description": "Contraseña cambiada exitosamente",
            "examples": {
                "application/json": {
                    "success": True,
                    "message": "Contraseña cambiada exitosamente",
                }
            },
        },
        400: {"description": "Error en los datos proporcionados"},
    },
)
class ChangePasswordAPIView(APIView):
    """API view para cambio de contraseña."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Cambiar contraseña del usuario autenticado.

        Args:
            request: HTTP request con datos de contraseña

        Returns:
            Response confirmando el cambio de contraseña
        """
        import logging

        logger = logging.getLogger(__name__)

        try:
            # Log de datos recibidos (sin mostrar contraseñas)
            logger.info(f"ChangePassword request from user: {request.user.username}")
            logger.info(f"Request data keys: {list(request.data.keys())}")

            serializer = ChangePasswordSerializer(
                data=request.data, context={"request": request}
            )

            if serializer.is_valid():
                serializer.save()

                return APIResponse.success(
                    message="Contraseña cambiada exitosamente",
                    status_code=status.HTTP_200_OK,
                )
            else:
                # Log detallado de errores de validación
                logger.error(f"ChangePassword validation errors: {serializer.errors}")
                return APIResponse.error(
                    message="Error al cambiar la contraseña",
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            logger.error(f"ChangePassword exception: {str(e)}")
            return APIResponse.error(
                message="Error al cambiar la contraseña",
                errors={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(
    tags=["Authentication"],
    summary="Solicitar recuperación de contraseña",
    description="Envía un email con un enlace para recuperar la contraseña.",
    request=ForgotPasswordSerializer,
    responses={
        200: {
            "description": "Email de recuperación enviado exitosamente",
            "examples": {
                "application/json": {
                    "success": True,
                    "message": "Se ha enviado un email con las instrucciones para recuperar tu contraseña.",
                    "data": {"email_sent": True},
                }
            },
        },
        400: {"description": "Email no encontrado o error en el envío"},
    },
)
class ForgotPasswordAPIView(APIView):
    """API view para solicitud de recuperación de contraseña."""

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        """Procesar solicitud de recuperación de contraseña.

        Args:
            request: HTTP request con email del usuario

        Returns:
            Response confirmando el envío del email
        """
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            try:
                result = serializer.save()

                if result["email_sent"]:
                    return APIResponse.success(
                        message=result["message"],
                        data={"email_sent": True},
                        status_code=status.HTTP_200_OK,
                    )
                else:
                    return APIResponse.error(
                        message=result["message"],
                        errors={"email": result.get("error", "Error desconocido")},
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

            except Exception as e:
                return APIResponse.error(
                    message="Error interno del servidor",
                    errors={"detail": str(e)},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return APIResponse.error(
            message="Datos inválidos",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(
    tags=["Authentication"],
    summary="Restablecer contraseña",
    description="Restablece la contraseña del usuario usando un token de recuperación.",
    request=ResetPasswordSerializer,
    responses={
        200: {
            "description": "Contraseña restablecida exitosamente",
            "examples": {
                "application/json": {
                    "success": True,
                    "message": "Contraseña restablecida exitosamente",
                    "data": {"password_reset": True},
                }
            },
        },
        400: {"description": "Token inválido o datos incorrectos"},
    },
)
class ResetPasswordAPIView(APIView):
    """API view para restablecer contraseña con token."""

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        """Procesar restablecimiento de contraseña.

        Args:
            request: HTTP request con token y nueva contraseña

        Returns:
            Response confirmando el restablecimiento
        """
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()

                return APIResponse.success(
                    message="Contraseña restablecida exitosamente",
                    data={"password_reset": True, "user_id": user.usuario_id},
                    status_code=status.HTTP_200_OK,
                )

            except Exception as e:
                return APIResponse.error(
                    message="Error al restablecer la contraseña",
                    errors={"detail": str(e)},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return APIResponse.error(
            message="Datos inválidos",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(exclude=True)
class MenuAPIView(APIView):
    """API view para obtener el menú del usuario filtrado por sus roles/permisos."""

    permission_classes = [IsAuthenticated]

    @require_authenticated()
    def get(self, request: Request) -> Response:
        """Retorna el menú del usuario construido dinámicamente desde la BD.

        Solo se incluyen los módulos cuyo ``permisos_requeridos`` contiene al
        menos uno de los permisos activos del usuario (o está vacío).
        Los submódulos se filtran de igual forma.
        Super Administrador recibe el árbol completo.
        """
        try:
            menu_items = MenuService.get_menu_for_user(request.user)

            return APIResponse.success(
                data={"menu": menu_items},
                message="Menú obtenido exitosamente",
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            return APIResponse.error(
                message="Error al obtener el menú",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(exclude=True)
class MenuStructureAPIView(APIView):
    """API view para obtener la estructura completa del menú sin filtrar por permisos."""

    permission_classes = [IsAuthenticated]

    @require_admin()
    def get(self, request: Request) -> Response:
        """Get complete menu structure.

        Args:
            request: HTTP request

        Returns:
            Response with complete menu structure
        """
        try:
            # Obtener módulos activos desde la base de datos
            modulos_activos = Modulos.objects.filter(estado_modulo="activo").order_by(
                "orden_visualizacion"
            )

            # Construir estructura completa del menú
            menu_items = []

            for modulo in modulos_activos:
                menu_item = {
                    "id": f"modulo-{modulo.modulo_id}",
                    "name": modulo.nombre_modulo,
                    "icon": modulo.icono_modulo or "dashboard",
                    "path": modulo.ruta_modulo or f"/{modulo.nombre_modulo.lower()}",
                    "order": modulo.orden_visualizacion,
                    "permissions": [],  # Permisos requeridos para ver este módulo
                    "roles": [],  # Roles que pueden ver este módulo
                    "children": [],  # Subelementos del menú
                }

                # Agregar submenús para módulos que los necesitan
                if modulo.nombre_modulo.lower() == "vacaciones":
                    menu_item["children"] = [
                        {
                            "id": "vacaciones-solicitudes",
                            "name": "Solicitudes",
                            "icon": "calendar",
                            "path": "/vacaciones/solicitudes",
                            "permissions": ["ver_solicitudes_vacaciones"],
                            "roles": [],
                        },
                        {
                            "id": "vacaciones-periodos",
                            "name": "Periodos",
                            "icon": "calendar-days",
                            "path": "/vacaciones/periodos",
                            "permissions": ["administrar_periodos_vacaciones"],
                            "roles": [],
                        },
                        {
                            "id": "vacaciones-configuracion",
                            "name": "Configuración",
                            "icon": "settings",
                            "path": "/vacaciones/configuracion",
                            "permissions": ["configurar_modulo_vacaciones"],
                            "roles": [],
                        },
                    ]
                elif modulo.nombre_modulo.lower() == "administración":
                    menu_item["children"] = [
                        {
                            "id": "admin-modulos",
                            "name": "Módulos",
                            "icon": "layout",
                            "path": "/admin/modulos",
                            "permissions": ["Gestionar Modulos"],
                            "roles": [],
                        },
                        {
                            "id": "admin-usuarios",
                            "name": "Usuarios",
                            "icon": "users",
                            "path": "/admin/usuarios",
                            "permissions": ["gestionar_usuarios"],
                            "roles": [],
                        },
                        {
                            "id": "admin-roles",
                            "name": "Roles",
                            "icon": "shield",
                            "path": "/admin/roles",
                            "permissions": ["gestionar_roles"],
                            "roles": [],
                        },
                    ]

                menu_items.append(menu_item)

            return APIResponse.success(
                message="Estructura del menú obtenida correctamente",
                data=menu_items,
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return APIResponse.error(
                message="Error al obtener la estructura del menú",
                errors={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(exclude=True)
class PermissionsStructureAPIView(APIView):
    """API view para obtener la estructura completa de permisos y roles."""

    permission_classes = [IsAuthenticated]

    @require_admin()
    def post(self, request: Request) -> Response:
        """Get permissions and roles structure.

        Args:
            request: HTTP request

        Returns:
            Response with permissions and roles structure
        """
        try:
            # Obtener todos los módulos
            modulos = Modulos.objects.all().order_by("nombre_modulo")

            # Obtener todos los permisos agrupados por módulo
            permisos_por_modulo = {}
            for modulo in modulos:
                permisos = Permiso.objects.filter(modulo=modulo).order_by(
                    "nombre_permiso"
                )
                permisos_por_modulo[modulo.nombre_modulo] = [
                    {
                        "id": permiso.permiso_id,
                        "name": permiso.nombre_permiso,
                        "description": permiso.descripcion_permiso,
                    }
                    for permiso in permisos
                ]

            # Obtener todos los roles con sus permisos
            roles = Rol.objects.all().order_by("nombre_rol")
            roles_data = []

            for rol in roles:
                permisos_rol = rol.permisos_asignados.all()
                roles_data.append(
                    {
                        "id": rol.rol_id,
                        "name": rol.nombre_rol,
                        "description": rol.descripcion_rol,
                        "permissions": [
                            {
                                "id": permiso.permiso.permiso_id,
                                "name": permiso.permiso.nombre_permiso,
                            }
                            for permiso in permisos_rol
                        ],
                    }
                )

            # Construir respuesta
            response_data = {
                "modules": [
                    {
                        "id": modulo.modulo_id,
                        "name": modulo.nombre_modulo,
                        "status": modulo.estado_modulo,
                        "permissions": permisos_por_modulo.get(
                            modulo.nombre_modulo, []
                        ),
                    }
                    for modulo in modulos
                ],
                "roles": roles_data,
            }

            return APIResponse.success(
                message="Estructura de permisos obtenida correctamente",
                data=response_data,
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return APIResponse.error(
                message="Error al obtener la estructura de permisos",
                errors={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
