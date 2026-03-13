"""
Direct Django shell test to diagnose permisos_activos() issue.
Run with: python manage.py shell < test_perms_direct.py
"""

from app_rrhh.models import Usuario

try:
    print("=" * 60)
    print("TEST: permisos_activos() method")
    print("=" * 60)

    # Get jgarcia
    user = Usuario.objects.filter(nombres_usuario__icontains="jgarcia").first()
    if not user:
        print("❌ User jgarcia not found")
        exit(1)

    print(f"\n✅ Usuario encontrado: {user.nombres_usuario}")
    print(f"   Usuario ID: {user.usuario_id}")

    # Test roles_activos()
    print("\n[1] Testing roles_activos()...")
    try:
        roles = user.roles_activos()
        print(f"✅ roles_activos() returned: {type(roles)}")
        roles_list = list(roles)
        print(f"   Roles: {[r.nombre_rol for r in roles_list]}")
    except Exception as e:
        print(f"❌ Error in roles_activos(): {e}")
        import traceback

        traceback.print_exc()
        exit(1)

    # Test permisos_activos()
    print("\n[2] Testing permisos_activos()...")
    try:
        permisos = user.permisos_activos()
        print(f"✅ permisos_activos() returned: {type(permisos)}")
        print(f"   Value: {permisos}")

        # Validate type
        if permisos == "*":
            print("   ✓ Admin access (wildcard)")
        elif isinstance(permisos, set):
            print(f"   ✓ Set of {len(permisos)} permissions: {permisos}")
        else:
            print(f"❌ Unexpected type: {type(permisos)}")

    except Exception as e:
        print(f"❌ Error in permisos_activos(): {e}")
        import traceback

        traceback.print_exc()
        exit(1)

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)

except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback

    traceback.print_exc()
    exit(1)
