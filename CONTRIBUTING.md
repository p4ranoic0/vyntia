# Contributing to Intranet RRHH

¡Gracias por tu interés en contribuir a este proyecto! Esta guía te ayudará a entender cómo trabajar con nuestra codebase y cómo hacer que tus cambios sean aceptados rápidamente.

## 📋 Tabla de Contenidos

- [Configuración del Entorno](#configuración-del-entorno)
- [Flujo de Trabajo](#flujo-de-trabajo)
- [Estándares de Código](#estándares-de-código)
- [Testing](#testing)
- [Commits](#commits)
- [Pull Requests](#pull-requests)
- [Troubleshooting](#troubleshooting)

---

## 🛠️ Configuración del Entorno

### Requisitos Previos

- **Python 3.11+** (Backend)
- **Node.js 18.x** (Frontend)
- **PostgreSQL 15+**
- **Redis 7+**
- **Git**

### Setup Inicial

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-org/intranet-rrhh.git
cd intranet-rrhh

# 2. Backend Setup
cd back
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus credenciales locales

python manage.py migrate
python manage.py loaddata fixtures/*.json  # opcional: cargar datos demo
python manage.py runserver 8000

# 3. Frontend Setup (en otra terminal)
cd front
npm install
npm run dev  # Inicia Vite en puerto 5173
```

### Verificar Setup

```bash
# Backend
cd back
python manage.py check
python manage.py test tests/ -v 2

# Frontend
cd front
npm run build
npm run test -- --run
```

---

## 🔄 Flujo de Trabajo

### 1. Crear Nueva Branch

```bash
git checkout -b feature/descripcion-corta
# o para bugfixes:
git checkout -b bugfix/descripcion-corta
# o para hotfixes:
git checkout -b hotfix/descripcion-corta
```

**Convención de nombres:**
- `feature/` - Nuevas funcionalidades
- `bugfix/` - Corrección de bugs
- `hotfix/` - Urgentes, se hace directamente a main
- `refactor/` - Mejoras sin cambiar funcionalidad
- Usar kebab-case: `feature/generar-reporte-vacaciones`

### 2. Hacer Cambios

```bash
# Backend
cd back
# Editar archivos según necesidad
python manage.py makemigrations  # si cambias modelos
python manage.py migrate
python manage.py test tests/ -v 2  # ejecutar tests

# Frontend
cd front
# Editar archivos según necesidad
npm run lint
npm run test -- --run
npm run build
```

### 3. Commit

```bash
git add .
git commit -m "type: Descripción clara del cambio"
```

Ver sección [Commits](#commits) para formato específico.

### 4. Push y Pull Request

```bash
git push origin feature/descripcion-corta
```

Luego abre un PR en GitHub:
- Usa el template automático
- Llena sección "Changes" y "Testing"
- Solicita review a mínimo 1 person
- Asigna label apropiado (bug, enhancement, documentation, etc.)

### 5. Merge

Un PR puede mergearse cuando:
- ✅ Todos los CI/CD checks pasan
- ✅ Mínimo 1 aprobación
- ✅ Conversaciones resueltas
- ✅ Branch actualizado con main

---

## 💻 Estándares de Código

### Backend (Django/Python)

#### Formato

```bash
cd back

# Black (formatter)
black .

# isort (import organizer)
isort .

# Ambos juntos
black . && isort .
```

**Configuración:**
- Línea máxima: 100 caracteres
- Indentación: 4 espacios
- Strings: comillas dobles

#### Linting

```bash
cd back

# Flake8
flake8 . --exclude=migrations

# Bandit (security)
bandit -r . -ll
```

#### Reglas PEP 8

- Usa type hints cuando sea posible
- Docstrings para funciones públicas
- Máximo 10 argumentos por función
- Mantén funciones pequeñas (<50 líneas)

**Ejemplo:**

```python
from typing import Optional
from django.db.models import QuerySet

def get_empleados_activos_por_departamento(
    departamento_id: int,
    incluir_inactivos: bool = False,
) -> QuerySet:
    """
    Obtiene empleados de un departamento.
    
    Args:
        departamento_id: ID del departamento
        incluir_inactivos: Si incluir empleados inactivos
        
    Returns:
        QuerySet filtrado de empleados
    """
    queryset = Empleado.objects.filter(departamento_id=departamento_id)
    
    if not incluir_inactivos:
        queryset = queryset.filter(estado='activo')
    
    return queryset
```

### Frontend (React/TypeScript)

#### Formato y Linting

```bash
cd front

# ESLint fix
npm run lint -- --fix

# TypeScript check
npx tsc --noEmit

# Todo junto
npm run lint && npm run typecheck
```

**Configuración:**
- Línea máxima: 100 caracteres
- Indentación: 2 espacios
- Strings: comillas simples o backticks

#### Reglas TypeScript

- No usar `any`
- Exportar types/interfaces públicos
- Componentes como `const` con type explícito
- Usar arquivos .tsx para React componentes

**Ejemplo:**

```typescript
import React from 'react';
import { useQuery } from '@tanstack/react-query';

interface EmpleadoFormProps {
  empleadoId: number;
  onSuccess?: () => void;
}

const EmpleadoForm: React.FC<EmpleadoFormProps> = ({ 
  empleadoId, 
  onSuccess 
}) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['empleado', empleadoId],
    queryFn: () => fetchEmpleado(empleadoId),
  });

  if (isLoading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <form>
      {/* JSX aquí */}
    </form>
  );
};

export default EmpleadoForm;
```

---

## 🧪 Testing

### Backend

```bash
cd back

# Todos los tests
python manage.py test

# Tests específicos
python manage.py test app_rrhh.tests.test_model
python manage.py test tests/test_auth_api.py::LoginTest::test_login_success

# Con coverage
coverage run -m pytest tests/ -v
coverage report --include=app_rrhh,api,core
coverage html  # genera htmlcov/index.html

# Requirement
# ✅ Coverage mínimo: 80%
```

**Estructura de tests:**

```
tests/
├── test_auth_api.py       # Tests para auth endpoints
├── test_models.py         # Tests para modelos
└── test_services.py       # Tests para business logic
```

**Ejemplo de test:**

```python
from django.test import TestCase, APITestCase
from rest_framework import status
from rest_framework.test import APIClient

from app_rrhh.models import Empleado, Usuario

class EmpleadoListAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_empleados(self):
        """Test que lista empleados correctamente"""
        # Crear datos de prueba
        Empleado.objects.create(
            nombre='Juan',
            apellido='Pérez',
            email='juan@example.com'
        )
        
        # Hacer request
        response = self.client.get('/api/v1/empleados/')
        
        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
```

### Frontend

```bash
cd front

# Todos los tests
npm run test -- --run

# Tests específicos
npm run test -- --run LoginForm.test.tsx

# Con coverage
npm run test -- --run --coverage

# Watch mode
npm run test
```

**Estructura de tests:**

```
src/
├── components/
│   ├── LoginForm.tsx
│   └── LoginForm.test.tsx
└── features/
    └── empleados/
        ├── EmpleadoList.tsx
        └── EmpleadoList.test.tsx
```

**Ejemplo de test (Vitest):**

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import LoginForm from './LoginForm';

describe('LoginForm', () => {
  it('debería enviar datos cuando el form se submit', async () => {
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);
    
    const input = screen.getByPlaceholderText('Usuario');
    fireEvent.change(input, { target: { value: 'testuser' } });
    
    const button = screen.getByRole('button', { name: /iniciar/i });
    fireEvent.click(button);
    
    expect(onSubmit).toHaveBeenCalled();
  });
});
```

---

## 📝 Commits

Usa [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bug
- `docs:` - Cambios de documentación
- `style:` - Formato, sin cambios lógicos
- `refactor:` - Mejora de código existente
- `perf:` - Mejoras de performance
- `test:` - Tests agregados/modificados
- `chore:` - Dependencias, build, etc.

### Scopes (Backend)

- `auth` - Autenticación/autorización
- `empleados` - Módulo de empleados
- `vacaciones` - Módulo de vacaciones
- `permisos` - Sistema de permisos
- `api` - Configuración de API

### Scopes (Frontend)

- `login` - Componentes de login
- `empleados` - Módulo de empleados
- `vacaciones` - Módulo de vacaciones
- `ui` - Componentes reusables
- `hooks` - Hooks personalizados

### Ejemplos

```bash
# Bueno ✅
git commit -m "feat(empleados): agregar bulk import de empleados"
git commit -m "fix(auth): corregir token expiration en JWT"
git commit -m "docs: actualizar README con setup instructions"
git commit -m "refactor(api): simplificar permiso system"
git commit -m "test(empleados): agregar tests para EmpleadoViewSet"

# Malo ❌
git commit -m "fix stuff"
git commit -m "WIP"
git commit -m "asdf"
```

---

## 🔀 Pull Requests

### Template automático

Se rellenará automáticamente, completa todas las secciones:

```markdown
## 📝 Descripción
Describe brevemente qué cambios hace este PR

## 🎯 Tipo de cambio
- [ ] Nuevo feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Mejora de documentación

## 🧪 Testing
Describe cómo probaste los cambios:
- [ ] Tests unitarios pasarán
- [ ] Probé manualmente en navegador/postman
- [ ] Cobertura >80% (backend)

## ✅ Checklist
- [ ] Mi código sigue estándares de estilo
- [ ] He revisado mi propio código
- [ ] He actualizado documentación si es necesario
- [ ] Tests pasarán localmente

## 🔗 Related Issues
Closes #123
```

### Rules

1. **Título claro:**
   ```
   ✅ feat: Agregar reporte de vacaciones por empleado
   ❌ update stuff
   ```

2. **Descripción detallada:** Explica el "por qué", no solo el "qué"

3. **Tests incluidos:** Código nuevo sin tests no será aprobado

4. **No edites main:** Siempre usa una branch de feature

5. **Actualiza branch:** Antes del merge, actualiza con cambios en main

---

## 🆘 Troubleshooting

### Backend

#### ImportError en models

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Tests fallan localmente

```bash
# Limpiar
rm db.sqlite3
python manage.py migrate

# Ejecutar con verbosidad
python manage.py test tests/ -v 2 --keepdb
```

#### PostgreSQL connection error

```bash
# Verificar .env
# DATABASE_URL debe ser válida

# Resetear DB
dropdb intranet_rrhh
createdb intranet_rrhh
python manage.py migrate
```

### Frontend

#### Node modules corrupted

```bash
rm -rf node_modules package-lock.json
npm install
```

#### Vite cache issue

```bash
rm -rf .vite
npm run dev
```

#### Type errors

```bash
npx tsc --noEmit
npm run dev  # TypeScript se ejecuta en dev también
```

---

## 🚀 Deployment

### Staging

Los PRs mergeados a `develop` se despliegan automáticamente a staging.

### Production

Solo se despliega mergeando a `main`. Requiere:
- ✅ Todos los tests pasados
- ✅ Code review aprobado
- ✅ Commit message con `feat:` o `fix:` para bump automático de versión

---

## 📚 Resources

- [Backend README](back/README.md) - Setup específico del backend
- [Frontend README](front/README.md) - Setup específico del frontend
- [Backend Setup](back/SETUP.md) - Guía detallada de configuración
- [API Docs](https://localhost:8000/api/docs/) - Documentación interactiva (en desarrollo)
- [Django Best Practices](https://docs.djangoproject.com/en/4.2/)
- [React Best Practices](https://react.dev/learn)

---

## ❓ Questions?

- Abre una [Discussion](https://github.com/tu-org/intranet-rrhh/discussions)
- O pregunta en el Slack del equipo

---

**Gracias por contribuir! 🎉**
