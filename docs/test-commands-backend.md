# 🧪 Comandos de Testing - Guía Rápida

## Comandos Básicos

### 🚀 Ejecución Simple (Django)
```bash
# Salida básica con Django
python manage.py test tests/ --verbosity=1

# Salida detallada con Django
python manage.py test tests/ --verbosity=2
```

### ⚡ Ejecución con Pytest (Más Amigable)
```bash
# Salida básica con pytest
python -m pytest tests/ -v

# Salida detallada y colorida
python -m pytest tests/ -v --tb=short --color=yes --durations=5

# Salida compacta con líneas de error
python -m pytest tests/ -v --tb=line --color=yes --no-header

# Solo mostrar fallos
python -m pytest tests/ -v --tb=short --color=yes -x
```

## 🎯 Tests Específicos

### Por Archivo
```bash
# Solo tests de modelos
python -m pytest tests/test_usuario_model.py -v --color=yes

# Solo tests de API
python -m pytest tests/test_login_api.py -v --color=yes
```

### Por Clase o Método
```bash
# Una clase específica
python -m pytest tests/test_usuario_model.py::UsuarioModelTest -v

# Un método específico
python -m pytest tests/test_usuario_model.py::UsuarioModelTest::test_creacion_usuario -v
```

## 📊 Reportes y Cobertura

### Reporte de Cobertura
```bash
# Cobertura en terminal
python -m pytest tests/ --cov=app_rrhh --cov-report=term-missing -v

# Cobertura HTML
python -m pytest tests/ --cov=app_rrhh --cov-report=html:htmlcov -v
```

### Reporte HTML
```bash
# Generar reporte HTML de tests
python -m pytest tests/ --html=reports/test_report.html --self-contained-html -v
```

## 🔧 Opciones Útiles

### Filtros y Marcadores
```bash
# Solo tests rápidos (si están marcados)
python -m pytest tests/ -v -m "not slow"

# Solo tests de integración
python -m pytest tests/ -v -m "integration"

# Excluir tests específicos
python -m pytest tests/ -v -k "not test_login_django_admin"
```

### Debugging
```bash
# Parar en el primer fallo
python -m pytest tests/ -v -x

# Mostrar variables locales en fallos
python -m pytest tests/ -v --tb=long -l

# Modo verbose máximo
python -m pytest tests/ -vv --tb=long --color=yes
```

## 🎨 Script Personalizado

```bash
# Usar el script personalizado
python run_tests.py --verbose    # Salida detallada
python run_tests.py --simple     # Salida simple
python run_tests.py --coverage   # Con cobertura
python run_tests.py --html       # Reporte HTML
python run_tests.py --models     # Solo modelos
python run_tests.py --api        # Solo API
```

## 💡 Tips

1. **Colores**: Usa `--color=yes` para salida colorida
2. **Velocidad**: Usa `--durations=N` para ver los N tests más lentos
3. **Fallos**: Usa `--tb=short` para trazas de error más compactas
4. **Progreso**: Usa `-v` para ver cada test individualmente
5. **Filtros**: Usa `-k "palabra"` para filtrar tests por nombre

## 🚨 Solución de Problemas

Si pytest no funciona:
```bash
# Usar Django directamente
python manage.py test tests/ --verbosity=2

# Verificar configuración
python -m pytest --collect-only
```