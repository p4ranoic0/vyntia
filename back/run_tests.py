#!/usr/bin/env python
"""
Script para ejecutar tests con diferentes opciones de visualización

Uso:
    python run_tests.py [opciones]
    
Opciones Básicas:
    --simple     : Ejecuta tests con Django (salida simple)
    --verbose    : Ejecuta tests con salida detallada
    --quick      : Tests rápidos con configuración optimizada
    
Tests Específicos:
    --models     : Ejecuta solo tests de modelos
    --api        : Ejecuta solo tests de API
    --auth       : Ejecuta solo tests de autenticación
    --usuario    : Ejecuta solo tests de usuario
    --area       : Ejecuta solo tests de área
    --fast       : Ejecuta solo tests rápidos (sin marcador 'slow')
    
Reportes:
    --coverage   : Ejecuta tests con reporte de cobertura
    --html       : Genera reporte HTML
    --watch      : Ejecuta tests en modo watch (requiere pytest-watch)
    
Utilidades:
    --clean      : Limpia archivos temporales
    --help       : Muestra esta ayuda
"""

import os
import sys
import subprocess
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

def run_command(cmd):
    """Ejecuta un comando y muestra la salida"""
    print(f"\n🚀 Ejecutando: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode

def show_help():
    """Muestra la ayuda del script"""
    print("""
🧪 Script de Testing - Ayuda

📋 Comandos Básicos:
  python run_tests.py                    - Tests con pytest (recomendado)
  python run_tests.py --simple           - Tests con Django (básico)
  python run_tests.py --verbose          - Tests detallados
  python run_tests.py --quick            - Tests rápidos optimizados

🎯 Tests Específicos:
  python run_tests.py --models           - Solo tests de modelos
  python run_tests.py --api              - Solo tests de API
  python run_tests.py --auth             - Solo tests de autenticación
  python run_tests.py --usuario          - Solo tests de usuario
  python run_tests.py --area             - Solo tests de área
  python run_tests.py --fast             - Solo tests rápidos (sin 'slow')

📊 Reportes:
  python run_tests.py --coverage         - Tests con cobertura
  python run_tests.py --html             - Tests con reporte HTML
  python run_tests.py --watch            - Tests en modo watch

🔧 Utilidades:
  python run_tests.py --clean            - Limpiar archivos temporales
  python run_tests.py --help             - Mostrar esta ayuda

💡 Ejemplos:
  python run_tests.py --models --coverage
  python run_tests.py --api --html
  python run_tests.py --quick
    """)

def clean_temp_files():
    """Limpia archivos temporales de testing"""
    import shutil
    
    print("🧹 Limpiando archivos temporales...")
    
    dirs_to_clean = ['__pycache__', '.pytest_cache', 'htmlcov', 'reports']
    files_to_clean = ['.coverage']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"  ✅ Eliminado: {dir_name}")
    
    for file_name in files_to_clean:
        if Path(file_name).exists():
            Path(file_name).unlink()
            print(f"  ✅ Eliminado: {file_name}")
    
    # Limpiar archivos .pyc recursivamente
    for pyc_file in Path('.').rglob('*.pyc'):
        pyc_file.unlink()
    
    # Limpiar directorios __pycache__ recursivamente
    for pycache_dir in Path('.').rglob('__pycache__'):
        if pycache_dir.is_dir():
            shutil.rmtree(pycache_dir)
    
    print("✅ Limpieza completada!")

def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Si no hay argumentos, usar configuración por defecto
    if not args:
        args = ['--default']
    
    base_cmd = ['pytest', 'tests/']
    
    # Procesar argumentos especiales primero
    if '--help' in args:
        show_help()
        return 0
    
    if '--clean' in args:
        clean_temp_files()
        return 0
    
    # Procesar comandos de testing
    if '--simple' in args:
        cmd = ['python', 'manage.py', 'test', 'tests/', '--verbosity=1']
        print("📋 Ejecutando tests con Django (salida simple)")
        
    elif '--verbose' in args:
        cmd = base_cmd + ['-v', '--tb=long', '--color=yes', '--durations=10', '--showlocals']
        print("📋 Ejecutando tests con pytest (salida detallada)")
        
    elif '--quick' in args:
        cmd = base_cmd + ['-v', '--tb=short', '--color=yes', '--durations=3', '--maxfail=3']
        print("⚡ Ejecutando tests rápidos optimizados")
        
    elif '--coverage' in args:
        cmd = base_cmd + [
            '--cov=app_rrhh',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
            '-v', '--color=yes'
        ]
        print("📊 Ejecutando tests con reporte de cobertura")
        
    elif '--html' in args:
        cmd = base_cmd + [
            '--html=reports/test_report.html',
            '--self-contained-html',
            '-v', '--color=yes'
        ]
        # Crear directorio de reportes si no existe
        Path('reports').mkdir(exist_ok=True)
        print("📄 Ejecutando tests con reporte HTML")
        
    elif '--watch' in args:
        cmd = base_cmd + ['-v', '--color=yes', '-f']
        print("👀 Ejecutando tests en modo watch")
        
    elif '--fast' in args:
        cmd = base_cmd + ['-v', '--color=yes', '-m', 'not slow', '--maxfail=3']
        print("⚡ Ejecutando solo tests rápidos (sin marcador 'slow')")
        
    elif '--models' in args:
        cmd = base_cmd + ['-v', '--color=yes', 'tests/test_usuario_model.py', 'tests/test_area_model.py']
        print("🏗️ Ejecutando tests de modelos")
        
    elif '--api' in args:
        cmd = base_cmd + ['-v', '--color=yes', 'tests/test_login_api.py']
        print("🌐 Ejecutando tests de API")
        
    elif '--auth' in args:
        cmd = base_cmd + ['-v', '--color=yes', 'tests/test_auth_system_integration.py']
        print("🔐 Ejecutando tests de autenticación")
        
    elif '--usuario' in args:
        cmd = base_cmd + ['-v', '--color=yes', 'tests/test_usuario_model.py', '--durations=3']
        print("👤 Ejecutando tests de usuario")
        
    elif '--area' in args:
        cmd = base_cmd + ['-v', '--color=yes', 'tests/test_area_model.py', '--durations=3']
        print("🏢 Ejecutando tests de área")
        
    elif '--default' in args:
        cmd = base_cmd + ['-v', '--tb=short', '--color=yes', '--durations=3']
        print("🚀 Ejecutando tests con pytest (configuración recomendada)")
        
    else:
        print("❓ Opción no reconocida. Usa --help para ver las opciones disponibles")
        show_help()
        return 1
    
    # Ejecutar comando
    exit_code = run_command(cmd)
    
    # Mostrar resultados
    print("\n" + "="*50)
    if exit_code == 0:
        print("✅ Todos los tests completados exitosamente!")
        
        # Mostrar información adicional según el tipo de test
        if '--coverage' in args:
            print("📊 Reporte de cobertura generado en: htmlcov/index.html")
            print("   Abre el archivo en tu navegador para ver el reporte detallado")
        
        if '--html' in args:
            print("📄 Reporte HTML generado en: reports/test_report.html")
            print("   Abre el archivo en tu navegador para ver el reporte detallado")
        
        if '--watch' in args:
            print("👀 Modo watch activado. Los tests se ejecutarán automáticamente al detectar cambios")
            
    else:
        print("❌ Algunos tests fallaron. Revisa la salida anterior.")
        print("💡 Consejos:")
        print("   - Usa --verbose para más detalles")
        print("   - Usa --quick para tests más rápidos durante desarrollo")
        print("   - Revisa los logs de error mostrados arriba")
    
    print("="*50)
    return exit_code

if __name__ == '__main__':
    sys.exit(main())