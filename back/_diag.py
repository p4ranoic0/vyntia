import os, sys, django, traceback
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE']='config.settings.development'
django.setup()

print('=== DB Connection charset ===')
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SHOW VARIABLES LIKE "character_set%%"')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]}')

print()
print('=== ConfiguracionEmpresa table check ===')
try:
    with connection.cursor() as cursor:
        cursor.execute('SHOW CREATE TABLE configuracion_empresa')
        result = cursor.fetchone()
        print(result[1] if result else 'Table not found')
except Exception as e:
    print(f'Table check error: {e}')

print()
print('=== ConfiguracionEmpresa data ===')
try:
    from app_rrhh.models.configuracion_empresa import ConfiguracionEmpresa
    cfg = ConfiguracionEmpresa.get_config()
    print(f'nombre: {repr(cfg.nombre)}')
    print(f'representante_legal: {repr(cfg.representante_legal)}')
    print(f'cargo_representante: {repr(cfg.cargo_representante)}')
    print(f'direccion: {repr(cfg.direccion)}')
except Exception as e:
    traceback.print_exc()

print()
print('=== Full template render test ===')
try:
    from app_rrhh.services.template_service import TemplateService
    ts = TemplateService()
    ctx = ts._obtener_datos_institucion()
    print(f'institucion context OK: nombre={ctx["nombre"]}')
except Exception as e:
    traceback.print_exc()
