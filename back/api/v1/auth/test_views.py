"""
Test endpoints to debug permisos_activos() issues
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def test_permisos_debug(request):
    """Test endpoint to debug permisos_activos()"""
    try:
        user = request.user

        # Test 1: User info
        result = {
            "username": user.nombres_usuario,
            "user_id": user.usuario_id,
            "authenticated": user.is_authenticated,
        }

        # Test 2: roles_activos()
        try:
            roles = user.roles_activos()
            result["roles"] = [r.nombre_rol for r in roles]
            result["roles_status"] = "OK"
        except Exception as e:
            result["roles_error"] = str(e)
            result["roles_status"] = "ERROR"

        # Test 3: permisos_activos()
        try:
            permisos = user.permisos_activos()
            result["permisos"] = str(permisos)
            result["permisos_type"] = type(permisos).__name__
            result["permisos_status"] = "OK"
        except Exception as e:
            result["permisos_error"] = str(e)
            result["permisos_status"] = "ERROR"

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": str(e), "type": type(e).__name__},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
