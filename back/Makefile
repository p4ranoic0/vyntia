# Makefile para comandos de testing más directos
# Uso: make test, make test-models, make test-api, etc.

# Variables
PYTHON = python
PYTEST = python -m pytest
MANAGE = python manage.py
TEST_DIR = tests/

# Colores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

# Comandos principales de testing
.PHONY: help test test-simple test-verbose test-models test-api test-integration test-coverage test-html test-fast

help:
	@echo "$(YELLOW)🧪 Comandos de Testing Disponibles:$(NC)"
	@echo ""
	@echo "$(GREEN)Comandos Básicos:$(NC)"
	@echo "  make test          - Tests con pytest (recomendado)"
	@echo "  make test-simple   - Tests con Django (básico)"
	@echo "  make test-verbose  - Tests detallados con pytest"
	@echo ""
	@echo "$(GREEN)Tests Específicos:$(NC)"
	@echo "  make test-models   - Solo tests de modelos"
	@echo "  make test-api      - Solo tests de API"
	@echo "  make test-auth     - Solo tests de autenticación"
	@echo "  make test-fast     - Solo tests rápidos"
	@echo ""
	@echo "$(GREEN)Reportes:$(NC)"
	@echo "  make test-coverage - Tests con cobertura"
	@echo "  make test-html     - Tests con reporte HTML"
	@echo ""
	@echo "$(GREEN)Utilidades:$(NC)"
	@echo "  make clean         - Limpiar archivos temporales"
	@echo "  make install       - Instalar dependencias"

# Comando principal (más amigable)
test:
	@echo "$(GREEN)🚀 Ejecutando tests con pytest...$(NC)"
	$(PYTEST) $(TEST_DIR) -v --tb=short --color=yes --durations=3

# Tests simples con Django
test-simple:
	@echo "$(GREEN)📋 Ejecutando tests con Django...$(NC)"
	$(MANAGE) test $(TEST_DIR) --verbosity=1

# Tests detallados
test-verbose:
	@echo "$(GREEN)📋 Ejecutando tests detallados...$(NC)"
	$(PYTEST) $(TEST_DIR) -v --tb=long --color=yes --durations=10 --showlocals

# Tests específicos por tipo
test-models:
	@echo "$(GREEN)🏗️ Ejecutando tests de modelos...$(NC)"
	$(PYTEST) $(TEST_DIR)test_usuario_model.py $(TEST_DIR)test_area_model.py -v --tb=short --color=yes

test-api:
	@echo "$(GREEN)🌐 Ejecutando tests de API...$(NC)"
	$(PYTEST) $(TEST_DIR)test_login_api.py -v --tb=short --color=yes

test-auth:
	@echo "$(GREEN)🔐 Ejecutando tests de autenticación...$(NC)"
	$(PYTEST) $(TEST_DIR)test_auth_system_integration.py -v --tb=short --color=yes

# Tests rápidos
test-fast:
	@echo "$(GREEN)⚡ Ejecutando tests rápidos...$(NC)"
	$(PYTEST) $(TEST_DIR) -v --color=yes -m "not slow" --maxfail=3

# Tests con cobertura
test-coverage:
	@echo "$(GREEN)📊 Ejecutando tests con cobertura...$(NC)"
	$(PYTEST) $(TEST_DIR) --cov=app_rrhh --cov-report=term-missing --cov-report=html:htmlcov -v --color=yes
	@echo "$(YELLOW)📊 Reporte de cobertura generado en: htmlcov/index.html$(NC)"

# Tests con reporte HTML
test-html:
	@echo "$(GREEN)📄 Ejecutando tests con reporte HTML...$(NC)"
	@mkdir -p reports
	$(PYTEST) $(TEST_DIR) --html=reports/test_report.html --self-contained-html -v --color=yes
	@echo "$(YELLOW)📄 Reporte HTML generado en: reports/test_report.html$(NC)"

# Comandos de utilidad
clean:
	@echo "$(GREEN)🧹 Limpiando archivos temporales...$(NC)"
	@rm -rf __pycache__ .pytest_cache htmlcov reports .coverage
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true

install:
	@echo "$(GREEN)📦 Instalando dependencias...$(NC)"
	pip install -r requirements.txt

# Comandos adicionales para desarrollo
.PHONY: dev-setup test-watch test-debug

dev-setup: install
	@echo "$(GREEN)🔧 Configurando entorno de desarrollo...$(NC)"
	$(MANAGE) migrate
	$(MANAGE) collectstatic --noinput

test-watch:
	@echo "$(GREEN)👀 Ejecutando tests en modo watch...$(NC)"
	$(PYTEST) $(TEST_DIR) -v --color=yes -f

test-debug:
	@echo "$(GREEN)🐛 Ejecutando tests en modo debug...$(NC)"
	$(PYTEST) $(TEST_DIR) -v --tb=long --color=yes --pdb --showlocals

# Comandos específicos por archivo
test-usuario:
	@echo "$(GREEN)👤 Ejecutando tests de usuario...$(NC)"
	$(PYTEST) $(TEST_DIR)test_usuario_model.py -v --tb=short --color=yes --durations=3

test-area:
	@echo "$(GREEN)🏢 Ejecutando tests de área...$(NC)"
	$(PYTEST) $(TEST_DIR)test_area_model.py -v --tb=short --color=yes --durations=3

test-login:
	@echo "$(GREEN)🔑 Ejecutando tests de login...$(NC)"
	$(PYTEST) $(TEST_DIR)test_login_api.py -v --tb=short --color=yes --durations=3