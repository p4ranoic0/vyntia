# 🧪 Guía de Testing - Sistema RRHH Intranet

Esta guía explica cómo ejecutar tests en el proyecto de manera eficiente y amigable.

## 📋 Opciones Disponibles

### 1. Script Python Mejorado (Recomendado)

El script `run_tests.py` proporciona comandos directos y amigables:

```bash
# Comando por defecto (recomendado)
python run_tests.py

# Ver todas las opciones disponibles
python run_tests.py --help
```

#### Comandos Básicos
```bash
# Tests con configuración optimizada (por defecto)
python run_tests.py

# Tests con Django (básico)
python run_tests.py --simple

# Tests detallados con más información
python run_tests.py --verbose

# Tests rápidos optimizados
python run_tests.py --quick
```

#### Tests Específicos
```bash
# Solo tests de modelos
python run_tests.py --models

# Solo tests de API
python run_tests.py --api

# Solo tests de autenticación
python run_tests.py --auth

# Solo tests de usuario
python run_tests.py --usuario

# Solo tests de área
python run_tests.py --area

# Solo tests rápidos (sin marcador 'slow')
python run_tests.py --fast
```

#### Reportes
```bash
# Tests con reporte de cobertura
python run_tests.py --coverage

# Tests con reporte HTML
python run_tests.py --html

# Tests en modo watch (requiere pytest-watch)
python run_tests.py --watch
```

#### Utilidades
```bash
# Limpiar archivos temporales
python run_tests.py --clean

# Mostrar ayuda
python run_tests.py --help
```

### 2. Comandos Directos con pytest

Para usuarios avanzados que prefieren comandos directos:

```bash
# Comando básico recomendado
pytest tests/ -v --tb=short --color=yes --durations=3

# Tests específicos
pytest tests/test_usuario_model.py -v --tb=short --color=yes --durations=3
pytest tests/test_area_model.py -v --tb=short --color=yes --durations=3

# Con cobertura
pytest tests/ --cov=app_rrhh --cov-report=term-missing --cov-report=html:htmlcov -v --color=yes

# Solo tests rápidos
pytest tests/ -v --color=yes -m "not slow" --maxfail=3
```

### 3. Comandos con Django

```bash
# Comando básico de Django
python manage.py test tests --verbosity=1

# Tests específicos con Django
python manage.py test tests.test_usuario_model --verbosity=2
```

### 4. Scripts de Conveniencia (Windows)

#### PowerShell Script
```powershell
# Ejecutar script de PowerShell
.\test.ps1
.\test.ps1 models
.\test.ps1 coverage
```

#### Batch Script
```cmd
# Ejecutar script batch
test.bat
test.bat models
test.bat coverage
```

#### Makefile (si tienes make instalado)
```bash
# Comandos con make
make test
make test-models
make test-coverage
```

## 🎯 Casos de Uso Recomendados

### Durante Desarrollo
```bash
# Para desarrollo rápido
python run_tests.py --quick

# Para tests específicos mientras desarrollas
python run_tests.py --usuario
python run_tests.py --models
```

### Antes de Commit
```bash
# Ejecutar todos los tests
python run_tests.py

# Con reporte de cobertura
python run_tests.py --coverage
```

### Para Debugging
```bash
# Tests detallados con más información
python run_tests.py --verbose

# Tests específicos con información detallada
pytest tests/test_usuario_model.py -v --tb=long --showlocals
```

### Para CI/CD
```bash
# Tests con reporte HTML para CI
python run_tests.py --html

# Tests con cobertura para CI
python run_tests.py --coverage
```

## 📊 Interpretación de Resultados

### Símbolos de Estado
- ✅ `PASSED` - Test exitoso
- ❌ `FAILED` - Test falló
- ⚠️ `SKIPPED` - Test omitido
- 🔄 `XFAIL` - Fallo esperado
- ⭐ `XPASS` - Éxito inesperado

### Información de Duración
- `--durations=3` muestra los 3 tests más lentos
- Útil para identificar tests que necesitan optimización

### Reportes de Cobertura
- **Terminal**: Muestra porcentaje de cobertura por archivo
- **HTML**: Genera reporte detallado en `htmlcov/index.html`
- **Missing**: Muestra líneas no cubiertas por tests

## 🔧 Configuración

### pytest.ini
El archivo `pytest.ini` contiene la configuración optimizada:
```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = config.settings.development
addopts = 
    --verbose
    --tb=short
    --color=yes
    --durations=10
    --strict-markers
    --strict-config
    --disable-warnings
    --reuse-db
    --failed-first
    --maxfail=5
    -ra
```

### Dependencias de Testing
Asegúrate de tener instaladas las dependencias:
```bash
pip install pytest pytest-django pytest-cov pytest-html pytest-xdist factory-boy faker
```

## 🚀 Tips y Mejores Prácticas

1. **Usa `--quick` durante desarrollo** para feedback rápido
2. **Ejecuta `--coverage` antes de commits** para mantener cobertura
3. **Usa `--verbose` para debugging** cuando tests fallan
4. **Limpia archivos temporales** regularmente con `--clean`
5. **Revisa reportes HTML** para análisis detallado de cobertura

## 🐛 Solución de Problemas

### Error: "No module named pytest"
```bash
# Instalar pytest
pip install pytest pytest-django

# Verificar instalación
pytest --version
```

### Error: "Table doesn't exist"
```bash
# Ejecutar migraciones
python manage.py migrate

# O usar base de datos en memoria para tests
# (configurado automáticamente en settings de test)
```

### Tests lentos
```bash
# Usar tests paralelos
pytest tests/ -n auto

# O solo tests rápidos
python run_tests.py --fast
```

## 📝 Ejemplos Prácticos

```bash
# Desarrollo diario
python run_tests.py --quick

# Antes de push
python run_tests.py --coverage

# Debugging específico
python run_tests.py --usuario --verbose

# Reporte para revisión
python run_tests.py --html

# Limpieza
python run_tests.py --clean
```

---

**💡 Tip**: Usa `python run_tests.py --help` para ver todas las opciones disponibles en cualquier momento.