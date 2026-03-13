# CONTRIBUTING - Guía de Contribución Frontend

Guía para contribuir al proyecto Intranet RRHH - Frontend.

---

## 🎯 Antes de Empezar

### Pre-requisitos

- ✅ Node.js 18.x o superior
- ✅ npm 9.x o superior  
- ✅ Git configurado
- ✅ Acceso al repositorio
- ✅ Backend corriendo en `http://127.0.0.1:8000`

### Setup Inicial

```bash
# 1. Clonar repositorio
git clone [repository-url]
cd INTRANET/front

# 2. Instalar dependencias
npm install

# 3. Configurar entorno
cp .env.example .env

# 4. Verificar que todo funciona
npm run dev
npm run test
npm run lint
```

---

## 📋 Flujo de Trabajo

### 1. Crear Issue

Antes de empezar a trabajar, crea o asígnate un issue:

```
Título: [feat] Agregar filtro de búsqueda en empleados

Descripción:
Como usuario RRHH
Quiero poder buscar empleados por nombre, DNI o cargo
Para encontrar rápidamente la información que necesito

Criterios de aceptación:
- [ ] Input de búsqueda visible
- [ ] Búsqueda por nombre parcial
- [ ] Búsqueda por DNI completo
- [ ] Búsqueda por cargo
- [ ] Debounce de 300ms
- [ ] Tests unitarios
```

### 2. Crear Rama

Nomenclatura de ramas:

```bash
# Features
git checkout -b feature/employee-search-filter

# Fixes
git checkout -b fix/login-redirect-issue

# Refactoring
git checkout -b refactor/empleados-service

# Docs
git checkout -b docs/api-integration-guide
```

### 3. Desarrollar

Sigue las [Guías de Estilo](#-guías-de-estilo) y [Best Practices](#-best-practices).

### 4. Escribir Tests

```bash
# Unit tests
npm run test

# Cobertura
npm run test:coverage

# E2E (opcional para features grandes)
npm run cypress
```

### 5. Validar Código

```bash
# Linting
npm run lint

# Build
npm run build

# Preview
npm run preview
```

### 6. Commit

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Formato
<type>(<scope>): <subject>

# Ejemplos
git commit -m "feat(empleados): agregar filtro de búsqueda"
git commit -m "fix(auth): corregir redirección después de login"
git commit -m "refactor(services): simplificar empleadosService"
git commit -m "docs(readme): actualizar instrucciones de instalación"
git commit -m "test(empleados): agregar tests para filtro de búsqueda"
git commit -m "chore(deps): actualizar dependencias"
```

**Types**:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `refactor`: Refactorización (no cambia funcionalidad)
- `docs`: Documentación
- `test`: Tests
- `style`: Formato (no afecta código)
- `chore`: Tareas de mantenimiento
- `perf`: Mejoras de performance

**Scopes** (opcional):
- `empleados`, `areas`, `vacaciones`, `auth`, `ui`, `services`, etc.

### 7. Push y Pull Request

```bash
# Push
git push origin feature/employee-search-filter

# Crear PR en GitHub
# Título: feat: Agregar filtro de búsqueda en empleados
# Descripción: Cierra #123
```

**Template de PR**:
```markdown
## Descripción
Breve descripción del cambio

## Tipo de cambio
- [ ] Nueva funcionalidad (feature)
- [ ] Corrección de bug (fix)
- [ ] Refactorización (refactor)
- [ ] Documentación (docs)

## Checklist
- [ ] Tests pasando
- [ ] Lint sin errores
- [ ] Tipos TypeScript correctos
- [ ] Documentación actualizada
- [ ] Self-review completado

## Screenshots (si aplica)
[Agregar capturas]

## Relacionado
Cierra #123
```

### 8. Code Review

Todos los PRs requieren:
- ✅ Aprobación de al menos 1 reviewer
- ✅ CI/CD pasando (tests, lint, build)
- ✅ Conflictos resueltos
- ✅ Comentarios de review atendidos

### 9. Merge

Después de aprobación:
```bash
# Squash merge (preferido)
git merge --squash feature/employee-search-filter

# O merge directo si los commits son limpios
git merge feature/employee-search-filter
```

---

## 📐 Guías de Estilo

### TypeScript

**Naming Conventions**:

```typescript
// Componentes: PascalCase
export const EmpleadoCard: React.FC<Props> = () => {};

// Hooks: camelCase con prefijo 'use'
export const useEmpleados = () => {};

// Servicios: camelCase
export const empleadosService = {};

// Constantes: UPPER_SNAKE_CASE
export const API_BASE_URL = 'http://...';

// Tipos/Interfaces: PascalCase
interface EmpleadoCardProps {}
type EstadoType = 'activo' | 'inactivo';

// Funciones normales: camelCase
function formatDate(date: Date): string {}
```

**Imports Order**:

```typescript
// 1. External libraries
import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';

// 2. Internal aliases
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { empleadosService } from '@/services/empleados';

// 3. Types
import type { Empleado } from '@/generated/models';

// 4. Relative imports
import { EmpleadoCard } from './EmpleadoCard';
import styles from './EmpleadoPage.module.css';
```

**Type Annotations**:

```typescript
// ✅ Explícito en parámetros y retornos de funciones
function getEmpleado(id: number): Promise<Empleado> {
  return empleadosService.getById(id);
}

// ✅ Implícito en variables cuando es obvio
const empleados = await empleadosService.getAll(); // Type: Empleado[]

// ✅ Explícito en props de componentes
interface EmpleadoCardProps {
  empleado: Empleado;
  onClick?: () => void;
}

// ❌ No usar 'any'
const data: any = await fetch(); // MAL

// ✅ Usar 'unknown' y type guards
const data: unknown = await fetch();
if (isEmpleado(data)) {
  // data es Empleado aquí
}
```

---

### React Components

**Estructura de Archivo**:

```typescript
// EmpleadoCard.tsx

// 1. Imports
import React from 'react';
import { cn } from '@/lib/utils';
import type { Empleado } from '@/generated/models';

// 2. Types/Interfaces
interface EmpleadoCardProps {
  empleado: Empleado;
  variant?: 'default' | 'compact';
  className?: string;
  onClick?: () => void;
}

// 3. Constants (si hay)
const VARIANTS = {
  default: 'p-4',
  compact: 'p-2'
} as const;

// 4. Component
export const EmpleadoCard: React.FC<EmpleadoCardProps> = ({
  empleado,
  variant = 'default',
  className,
  onClick
}) => {
  // Hooks
  const [isHovered, setIsHovered] = useState(false);

  // Event handlers
  const handleClick = () => {
    onClick?.();
  };

  // Render helpers (si hay)
  const renderHeader = () => (
    <div className="header">
      {/* ... */}
    </div>
  );

  // Main render
  return (
    <div 
      className={cn(VARIANTS[variant], className)}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {renderHeader()}
      {/* ... */}
    </div>
  );
};
```

**Component Patterns**:

```typescript
// ✅ Functional components con TypeScript
export const MyComponent: React.FC<Props> = (props) => {};

// ✅ Props destructuring
export const MyComponent: React.FC<Props> = ({ 
  title, 
  onClick,
  children 
}) => {};

// ✅ Default props con destructuring
export const MyComponent: React.FC<Props> = ({ 
  variant = 'default',
  size = 'md'
}) => {};

// ❌ No usar default props object (deprecated)
MyComponent.defaultProps = { variant: 'default' }; // MAL
```

---

### CSS / Tailwind

**Tailwind Classes**:

```typescript
// ✅ Usar cn() para composición
<div className={cn(
  'base-classes',
  variant === 'primary' && 'variant-classes',
  isActive && 'active-classes',
  className
)} />

// ✅ Ordenar clases por categoría
<div className={cn(
  // Layout
  'flex items-center justify-between',
  // Spacing
  'p-4 gap-2',
  // Sizing
  'w-full h-auto',
  // Typography
  'text-sm font-medium',
  // Colors
  'bg-gray-100 text-gray-900',
  // Effects
  'rounded-lg shadow-sm hover:shadow-md',
  // Transitions
  'transition-all duration-200'
)} />

// ❌ No hardcodear colores en hex
<div className="bg-[#ff0000]" /> // MAL

// ✅ Usar tokens de diseño
<div className="bg-destructive" />
```

**Responsive Design**:

```typescript
<div className={cn(
  // Mobile first
  'flex-col gap-2',
  // Tablet
  'md:flex-row md:gap-4',
  // Desktop
  'lg:gap-6'
)} />
```

---

## 🧪 Testing

### Unit Tests

**Nombrar tests**:

```typescript
// EmpleadoCard.test.tsx
describe('EmpleadoCard', () => {
  describe('rendering', () => {
    it('renderiza nombre completo del empleado', () => {});
    it('muestra badge de estado correcto', () => {});
  });

  describe('interactions', () => {
    it('llama onClick cuando se hace click', () => {});
    it('muestra tooltip al hover', () => {});
  });

  describe('variants', () => {
    it('aplica clases correctas para variant compact', () => {});
    it('aplica clases correctas para variant detailed', () => {});
  });
});
```

**Testing patterns**:

```typescript
// ✅ Usar Testing Library query priorities
// 1. getByRole
screen.getByRole('button', { name: /guardar/i });

// 2. getByLabelText
screen.getByLabelText(/nombre completo/i);

// 3. getByPlaceholderText
screen.getByPlaceholderText(/buscar empleado/i);

// 4. getByText
screen.getByText(/empleados activos/i);

// 5. getByTestId (último recurso)
screen.getByTestId('empleado-card');

// ❌ No usar querySelector
container.querySelector('.empleado-card'); // MAL
```

**Mocking**:

```typescript
// Mock de servicio
vi.mock('@/services/empleados', () => ({
  empleadosService: {
    getAll: vi.fn(() => Promise.resolve(mockEmpleados)),
    getById: vi.fn((id) => Promise.resolve(mockEmpleado)),
  }
}));

// Mock de React Query
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};
```

---

### E2E Tests

**Cypress patterns**:

```typescript
// empleados.cy.ts
describe('Gestión de Empleados', () => {
  beforeEach(() => {
    cy.login('admin', 'password');
    cy.visit('/empleados');
  });

  it('lista todos los empleados', () => {
    cy.get('[data-testid="empleado-row"]')
      .should('have.length.gt', 0);
  });

  it('crea nuevo empleado', () => {
    // Arrange
    cy.get('[data-testid="btn-nuevo-empleado"]').click();

    // Act
    cy.get('input[name="nombres_empleado"]').type('Juan');
    cy.get('input[name="apellido_paterno"]').type('Pérez');
    cy.get('button[type="submit"]').click();

    // Assert
    cy.contains('Empleado creado exitosamente')
      .should('be.visible');
    cy.url().should('include', '/empleados');
  });
});
```

---

## ✅ Best Practices

### Performance

```typescript
// ✅ Memoizar componentes pesados
export const EmpleadoList = React.memo(({ empleados }) => {
  // ...
});

// ✅ useMemo para cálculos costosos
const empleadosActivos = useMemo(
  () => empleados.filter(e => e.estado === 'activo'),
  [empleados]
);

// ✅ useCallback para funciones en deps
const handleSearch = useCallback((query: string) => {
  // ...
}, []);

// ✅ Lazy loading de rutas
const EmpleadosPage = lazy(() => import('./pages/EmpleadosPage'));

// ✅ Code splitting
<Route 
  path="/empleados" 
  element={
    <Suspense fallback={<Loading />}>
      <EmpleadosPage />
    </Suspense>
  } 
/>
```

### Accessibility

```typescript
// ✅ Semantic HTML
<button type="button" onClick={handleClick}>
  Guardar
</button>

// ✅ ARIA labels cuando sea necesario
<div role="alert" aria-live="polite">
  {errorMessage}
</div>

// ✅ Keyboard navigation
<div
  tabIndex={0}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  Clickeable div
</div>

// ✅ Focus management
const inputRef = useRef<HTMLInputElement>(null);

useEffect(() => {
  inputRef.current?.focus();
}, []);
```

### State Management

```typescript
// ✅ React Query para server state
const { data: empleados } = useEmpleados();

// ✅ useState para UI state local
const [isOpen, setIsOpen] = useState(false);

// ✅ Context para estado global (auth, theme)
const { user, logout } = useAuth();

// ❌ No usar Context para server state
// Usar React Query en su lugar
```

### Error Handling

```typescript
// ✅ Error boundaries para errores de React
<ErrorBoundary fallback={<ErrorPage />}>
  <YourApp />
</ErrorBoundary>

// ✅ Try-catch en async functions
const handleSubmit = async (data) => {
  try {
    await empleadosService.create(data);
    toast.success('Empleado creado');
  } catch (error) {
    toast.error('Error al crear empleado');
    console.error(error);
  }
};

// ✅ React Query maneja errores automáticamente
const { data, error, isError } = useEmpleados();

if (isError) {
  return <ErrorMessage error={error} />;
}
```

---

## 🚫 Anti-Patterns

### ❌ No Hacer

```typescript
// ❌ Mutar state directamente
const [items, setItems] = useState([]);
items.push(newItem); // MAL

// ✅ Crear nuevo array
setItems([...items, newItem]);

// ❌ Fetch en useEffect
useEffect(() => {
  fetch('/api/empleados').then(res => setEmpleados(res));
}, []);

// ✅ Usar React Query
const { data: empleados } = useEmpleados();

// ❌ Lógica de negocio en componentes
const EmpleadoPage = () => {
  const calculateVacaciones = (empleado) => {
    // Lógica compleja aquí
  };
};

// ✅ Extraer a servicios/utilidades
// src/services/vacaciones/vacacionesCalculation.ts
export const calculateVacaciones = (empleado) => {};

// ❌ Props drilling excesivo
<ComponentA>
  <ComponentB data={data}>
    <ComponentC data={data}>
      <ComponentD data={data} />
    </ComponentC>
  </ComponentB>
</ComponentA>

// ✅ Context o React Query
const { data } = useEmpleados();

// ❌ Concatenar strings para clases
className={'button ' + (isActive ? 'active' : '')}

// ✅ Usar cn()
className={cn('button', isActive && 'active')}
```

---

## 📚 Recursos

### Documentación Oficial
- [React Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Testing Library](https://testing-library.com/)

### Guías Internas
- [Design System](../docs/design-system.md)
- [API Integration](../docs/api-integration.md)
- [Frontend README](./README.md)

### Herramientas
- [ESLint](https://eslint.org/)
- [Prettier](https://prettier.io/)
- [Vitest](https://vitest.dev/)
- [Cypress](https://www.cypress.io/)

---

## 🆘 Soporte

**¿Tienes dudas?**
- 💬 Slack: #frontend-dev
- 📧 Email: dev-team@empresa.com
- 📝 Issues: [GitHub Issues](https://github.com/...)

**Reportar bugs**
1. Verificar que no exista issue similar
2. Incluir pasos para reproducir
3. Agregar screenshots/logs
4. Especificar versión de Node/navegador

---

**Última actualización**: 8 de marzo de 2026
