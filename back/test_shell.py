from app_rrhh.models import Usuario

# Get jgarcia user
user = Usuario.objects.get(nombres_usuario__icontains="jgarcia")
print(f"Usuario: {user.nombres_usuario}")

# Test roles_activos()
roles = user.roles_activos()
print(f"Roles: {[r.nombre_rol for r in roles]}")

# Test permisos_activos()
permisos = user.permisos_activos()
print(f"Permisos: {permisos}")
print(f"Tipo: {type(permisos)}")
