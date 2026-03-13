# Frontend - Sistema de Recursos Humanos Intranet

> Aplicación moderna de intranet para gestión de RRHH construida con React 18, TypeScript, TanStack Query y shadcn/ui.

[![React](https://img.shields.io/badge/React-18.3-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF.svg)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)](https://tailwindcss.com/)

---

## 📑 Tabla de Contenidos

- [Características](#-características)
- [Stack Tecnológico](#️-stack-tecnológico)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Inicio Rápido](#-inicio-rápido)
- [Scripts Disponibles](#-scripts-disponibles)
- [Desarrollo](#-desarrollo)
- [Testing](#-testing)
- [Build y Deploy](#-build-y-deploy)
- [Documentación Adicional](#-documentación-adicional)

---

## 🚀 Características

### Funcionalidades Core
- ✅ **Autenticación JWT** con refresh automático y manejo de sesiones
- ✅ **Dashboard profesional** con métricas en tiempo real y actividad reciente
- ✅ **Gestión de empleados** con CRUD completo, búsqueda y filtros avanzados
- ✅ **Módulos especializados** para áreas, vacaciones, contratos, boletas, capacitaciones
- ✅ **Sistema de roles y permisos** con control de acceso granular
- ✅ **Gestión de documentos** con versionado y seguimiento de vencimientos

### UX/UI
- 🎨 **Design System unificado** con tokens de diseño consistentes
- 🌓 **Modo oscuro/claro** con persistencia de preferencias
- 📱 **Diseño responsive** optimizado para móvil, tablet y desktop
- ♿ **Accesibilidad** cumpliendo estándares WCAG 2.1 AA
- 🔔 **Sistema de notificaciones** con toast messages y alertas
- 📊 **Tablas avanzadas** con paginación, ordenamiento, filtros y exportación

### Arquitectura
- 🏗️ **Arquitectura modular** basada en features
- 🔄 **State management** con TanStack Query (React Query)
- 🔌 **API integration** con tipos TypeScript generados desde OpenAPI
- 🧪 **Testing** con Vitest, Cypress y Playwright
- 📦 **Code splitting** automático y lazy loading
- 🚀 **CI/CD** con GitHub Actions

---

## 🛠️ Stack Tecnológico

### Core
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **React** | 18.3 | Librería UI |
| **TypeScript** | 5.5 | Tipado estático |
| **Vite** | 5.4 | Build tool y dev server |

### UI & Styling
| Tecnología | Uso |
|------------|-----|
| **shadcn/ui** | Componentes base (Radix UI) |
| **Tailwind CSS** | Utility-first CSS |
| **Lucide React** | Iconografía |
| **CVA** | Variantes de componentes |

### State & Data
| Tecnología | Uso |
|------------|-----|
| **TanStack Query** | Server state management |
| **React Hook Form** | Gestión de formularios |
| **Zod** | Validación de schemas |

### Routing & Navigation
| Tecnología | Uso |
|------------|-----|
| **React Router DOM** | Enrutamiento SPA |

### Testing
| Tecnología | Uso |
|------------|-----|
| **Vitest** | Unit & integration testing |
| **Testing Library** | Testing de React components |
| **Cypress** | E2E testing |
| **Playwright** | E2E testing alternativo |
| **MSW** | API mocking |

---

## 📁 Estructura del Proyecto

```
front/
├── public/                      # Archivos estáticos
├── src/
│   ├── components/             # Componentes organizados por tipo
│   │   ├── ui/                # shadcn/ui base components (25+)
│   │   ├── layout/            # Layout (Header, Sidebar, Footer)
│   │   ├── auth/              # Login, ProtectedRoute, etc.
│   │   ├── common/            # DataTable, DocumentViewer, Loading
│   │   ├── modals/            # Modales reutilizables
│   │   ├── notifications/     # Sistema de notificaciones
│   │   ├── areas/             # Componentes de áreas
│   │   ├── users/             # Componentes de usuarios
│   │   └── vacaciones/        # Componentes de vacaciones
│   │
│   ├── features/              # Módulos por funcionalidad
│   │   ├── auth/             # Feature de autenticación
│   │   ├── empleados/        # Feature de empleados
│   │   └── vacaciones/       # Feature de vacaciones
│   │
│   ├── shared/               # Recursos compartidos
│   │   ├── components/       # EmpleadoCard, EstadoBadge, etc.
│   │   ├── hooks/            # useDebounce, useLocalStorage, etc.
│   │   └── utils/            # Utilidades compartidas
│   │
│   ├── services/             # Capa de servicios API
│   │   ├── api/             # Cliente API base
│   │   ├── empleados/       # Servicio de empleados
│   │   ├── areas/           # Servicio de áreas
│   │   ├── auth/            # Servicio de autenticación
│   │   └── vacaciones/      # Servicio de vacaciones
│   │
│   ├── generated/            # Tipos TypeScript auto-generados
│   │   ├── models/          # Tipos de modelos del backend
│   │   └── services/        # Servicios generados desde OpenAPI
│   │
│   ├── pages/               # Páginas/Rutas principales
│   │   ├── Dashboard.tsx
│   │   ├── EmpleadosPage.tsx
│   │   ├── VacacionesPage.tsx
│   │   └── ...
│   │
│   ├── context/             # React Context providers
│   │   ├── AuthContext.tsx
│   │   └── ThemeContext.tsx
│   │
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useDebounce.ts
│   │   └── useLocalStorage.ts
│   │
│   ├── lib/                 # Configuración y utilidades
│   │   ├── api.ts          # Cliente HTTP con interceptores
│   │   ├── utils.ts        # cn(), getInitials(), etc.
│   │   └── design-tokens.ts # Sistema de diseño
│   │
│   ├── mocks/              # Mock Service Worker handlers
│   │   ├── handlers/
│   │   └── browser.ts
│   │
│   ├── test/               # Utilidades de testing
│   │   ├── setup.ts
│   │   └── utils.tsx
│   │
│   ├── utils/              # Utilidades globales
│   │
│   ├── App.tsx             # Componente raíz
│   ├── main.tsx            # Entry point
│   └── index.css           # Estilos globales + Tailwind
│
├── tests/                  # Tests E2E organizados
│   ├── e2e/               # Playwright tests
│   └── integration/       # Cypress tests
│
├── scripts/               # Scripts de desarrollo
│   ├── generate-api-types.mjs
│   ├── generate-api-types.bat
│   └── generate-api-types.sh
│
├── .github/               # CI/CD workflows
│   └── workflows/
│       └── frontend-ci.yml
│
├── cypress.config.js      # Configuración Cypress
├── playwright.config.js   # Configuración Playwright
├── vitest.config.js       # Configuración Vitest
├── vite.config.ts         # Configuración Vite
├── tailwind.config.js     # Configuración Tailwind
├── tsconfig.json          # Configuración TypeScript
└── package.json           # Dependencias y scripts
```

---

## 🚀 Inicio Rápido

### Prerequisitos

- **Node.js**: 18.x o superior
- **npm**: 9.x o superior
- **Backend Django**: Ejecutándose en `http://127.0.0.1:8000`

### Instalación

```bash
# 1. Navegar a la carpeta del frontend
cd front

# 2. Instalar dependencias
npm install

# 3. Configurar variables de entorno
cp .env.example .env

# 4. Iniciar servidor de desarrollo
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

### Variables de Entorno

Crear archivo `.env` en la raíz de `front/`:

```env
# URL base del backend API
VITE_API_BASE_URL=http://127.0.0.1:8000

# Modo de desarrollo (opcional)
VITE_ENV=development
```

---

## 📜 Scripts Disponibles

### Desarrollo

```bash
# Iniciar servidor de desarrollo (puerto 5173)
npm run dev

# Build de producción
npm run build

# Preview del build de producción
npm run preview

# Linting con ESLint
npm run lint
```

### Testing

```bash
# Tests unitarios con Vitest
npm run test              # Modo watch
npm run test:ui          # UI de Vitest
npm run test:coverage    # Con cobertura

# E2E con Cypress
npm run cypress          # Interfaz interactiva
npm run cypress:run      # Headless

# E2E con Playwright
npm run playwright       # Headless
npm run playwright:ui    # UI mode
```

### Generación de Tipos

```bash
# Generar tipos TypeScript desde OpenAPI schema
npm run generate:api        # Linux/Mac/Git Bash
npm run generate:api:win    # Windows CMD
npm run generate:api:unix   # Unix Shell

# El script automáticamente:
# 1. Genera schema OpenAPI desde Django
# 2. Crea tipos TypeScript en src/generated/
```

---

## 💻 Desarrollo

### Flujo de Trabajo

1. **Crear rama de feature**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

2. **Desarrollar con tipos actualizados**
   ```bash
   # Si cambiaste modelos del backend
   npm run generate:api
   ```

3. **Escribir tests**
   ```bash
   # Tests unitarios
   npm run test
   
   # Tests E2E
   npm run cypress
   ```

4. **Validar código**
   ```bash
   npm run lint
   npm run build  # Verificar que compila
   ```

5. **Commit y push**
   ```bash
   git add .
   git commit -m "feat: nueva funcionalidad"
   git push origin feature/nueva-funcionalidad
   ```

### Convenciones de Código

#### Nomenclatura

- **Componentes**: PascalCase (`EmpleadoCard.tsx`)
- **Hooks**: camelCase con prefijo `use` (`useAuth.ts`)
- **Servicios**: camelCase (`empleadosService.ts`)
- **Utilidades**: camelCase (`formatDate.ts`)
- **Constantes**: UPPER_SNAKE_CASE (`API_BASE_URL`)

#### Estructura de Componentes

```tsx
// EmpleadoCard.tsx
import React from 'react';
import { cn } from '@/lib/utils';

interface EmpleadoCardProps {
  empleado: Empleado;
  variant?: 'default' | 'compact' | 'detailed';
  className?: string;
  onClick?: () => void;
}

export const EmpleadoCard: React.FC<EmpleadoCardProps> = ({
  empleado,
  variant = 'default',
  className,
  onClick
}) => {
  return (
    <div className={cn('rounded-lg border p-4', className)}>
      {/* Contenido */}
    </div>
  );
};
```

#### Servicios API

```typescript
// src/services/empleados/empleadosService.ts
import { apiClient } from '@/services/api/apiClient';
import type { Empleado } from '@/generated/models';

export const empleadosService = {
  getAll: async (): Promise<Empleado[]> => {
    const response = await apiClient.get('/api/v1/empleados/');
    return response.data;
  },
  
  getById: async (id: number): Promise<Empleado> => {
    const response = await apiClient.get(`/api/v1/empleados/${id}/`);
    return response.data;
  },
  
  // ... más métodos
};
```

#### React Query Hooks

```typescript
// src/features/empleados/hooks/useEmpleados.ts
import { useQuery } from '@tanstack/react-query';
import { empleadosService } from '@/services/empleados';

export const useEmpleados = () => {
  return useQuery({
    queryKey: ['empleados'],
    queryFn: empleadosService.getAll,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};
```

### Agregar Nuevo Módulo

1. **Crear estructura de carpetas**
   ```
   src/
   ├── features/mi-modulo/
   │   ├── components/
   │   ├── hooks/
   │   ├── services/
   │   └── index.ts
   ├── services/mi-modulo/
   └── pages/MiModuloPage.tsx
   ```

2. **Crear servicio API**
   ```typescript
   // src/services/mi-modulo/miModuloService.ts
   ```

3. **Crear hooks con React Query**
   ```typescript
   // src/features/mi-modulo/hooks/useMiModulo.ts
   ```

4. **Crear componentes**
   ```typescript
   // src/features/mi-modulo/components/MiModuloCard.tsx
   ```

5. **Crear página**
   ```typescript
   // src/pages/MiModuloPage.tsx
   ```

6. **Agregar ruta**
   ```typescript
   // src/App.tsx
   <Route path="/mi-modulo" element={<MiModuloPage />} />
   ```

---

## 🧪 Testing

### Estrategia de Testing

- **Unit Tests**: Componentes, hooks, utilidades (Vitest)
- **Integration Tests**: Flujos de usuario (Vitest + Testing Library)
- **E2E Tests**: Casos de uso completos (Cypress/Playwright)

### Escribir Tests

#### Unit Test - Componente

```typescript
// EmpleadoCard.test.tsx
import { render, screen } from '@/test/utils';
import { EmpleadoCard } from './EmpleadoCard';

describe('EmpleadoCard', () => {
  const empleado = {
    id: 1,
    nombres_empleado: 'Juan',
    apellido_paterno: 'Pérez',
    cargo: 'Desarrollador',
    estado: 'activo'
  };

  it('renderiza información del empleado', () => {
    render(<EmpleadoCard empleado={empleado} />);
    
    expect(screen.getByText('Juan Pérez')).toBeInTheDocument();
    expect(screen.getByText('Desarrollador')).toBeInTheDocument();
  });
});
```

#### Integration Test - Hook

```typescript
// useEmpleados.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { createWrapper } from '@/test/utils';
import { useEmpleados } from './useEmpleados';

describe('useEmpleados', () => {
  it('obtiene lista de empleados', async () => {
    const { result } = renderHook(() => useEmpleados(), {
      wrapper: createWrapper()
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    
    expect(result.current.data).toHaveLength(3);
  });
});
```

#### E2E Test - Cypress

```typescript
// cypress/e2e/empleados.cy.ts
describe('Gestión de Empleados', () => {
  beforeEach(() => {
    cy.login('admin', 'password');
    cy.visit('/empleados');
  });

  it('lista todos los empleados', () => {
    cy.get('[data-testid="empleado-row"]').should('have.length.gt', 0);
  });

  it('crea nuevo empleado', () => {
    cy.get('[data-testid="btn-nuevo-empleado"]').click();
    cy.get('input[name="nombres_empleado"]').type('Juan');
    cy.get('input[name="apellido_paterno"]').type('Pérez');
    cy.get('button[type="submit"]').click();
    
    cy.contains('Empleado creado exitosamente').should('be.visible');
  });
});
```

### Cobertura de Testing

Objetivo: **≥ 80%** de cobertura

```bash
npm run test:coverage

# Ver reporte HTML
open coverage/index.html
```

---

## 🏗️ Build y Deploy

### Build de Producción

```bash
# Generar build optimizado
npm run build

# Output: dist/
# - HTML, CSS, JS minificados
# - Assets optimizados
# - Source maps
```

### Preview Local

```bash
npm run preview
# Servidor en http://localhost:4173
```

### Despliegue

#### Opción 1: Netlify

```bash
# netlify.toml (ya configurado)
npm run build
netlify deploy --prod
```

#### Opción 2: Vercel

```bash
vercel --prod
```

#### Opción 3: Servidor Propio

```bash
# Copiar carpeta dist/ al servidor
scp -r dist/ user@server:/var/www/intranet/
```

### Variables de Entorno en Producción

Configurar en plataforma de hosting:

```env
VITE_API_BASE_URL=https://api.produccion.com
VITE_ENV=production
```

### CI/CD

El proyecto incluye GitHub Actions para:

- ✅ **Linting** automático
- ✅ **Tests unitarios** con cobertura
- ✅ **Build** de producción
- ✅ **Deploy** automático (opcional)

Ver [CI/CD.md](../docs/CI-CD.md) para más detalles.

---

## 📚 Documentación Adicional

### Documentos del Proyecto

- **[Design System](../docs/design-system.md)** - Guía de diseño y componentes
- **[CI/CD Guide](../docs/CI-CD.md)** - Configuración de pipelines
- **[API Integration](../docs/api-integration.md)** - Integración con backend
- **[Testing Guide](../docs/testing-backend.md)** - Estrategias de testing

### Recursos Externos

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [TanStack Query](https://tanstack.com/query/latest)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vite Guide](https://vitejs.dev/guide/)

---

## 🤝 Contribución

### Proceso de Contribución

1. **Fork** del repositorio
2. **Crear rama** de feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** cambios (`git commit -m 'feat: Add AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abrir Pull Request**

### Conventional Commits

Seguimos la especificación de [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: nueva funcionalidad
fix: corrección de bug
docs: cambios en documentación
style: cambios de formato (no afectan código)
refactor: refactorización de código
test: agregar o actualizar tests
chore: tareas de mantenimiento
```

### Code Review

Todos los PRs requieren:
- ✅ Tests pasando
- ✅ Linting sin errores
- ✅ Revisión de al menos 1 desarrollador
- ✅ Build exitoso

---

## 📝 Licencia

Este proyecto es privado y de uso interno.

---

## 👥 Equipo

**Departamento de TI - RRHH**

Para soporte o consultas: ti@empresa.com

---

**Última actualización**: 8 de marzo de 2026
2. Modificar `tailwind.config.js` para ajustar la configuración de Tailwind
3. Los colores se adaptan automáticamente al modo oscuro/claro

## 📱 Características Responsive

- **Mobile First**: Diseño optimizado para dispositivos móviles
- **Touch Friendly**: Elementos táctiles de tamaño adecuado
- **Sidebar Colapsable**: Se adapta automáticamente en pantallas pequeñas
- **Tablas Responsivas**: Scroll horizontal en dispositivos móviles
- **Breakpoints**: Optimizado para móvil (<768px), tablet (768-1024px), y desktop (>1024px)

## 🔐 Seguridad

- **JWT Tokens**: Almacenados en cookies HttpOnly seguras
- **Refresh Automático**: Los tokens se renuevan automáticamente
- **Rutas Protegidas**: Acceso controlado basado en autenticación
- **CORS**: Configuración adecuada para peticiones cross-origin
- **Validación**: Validación de formularios con Zod

## 🚀 Funcionalidades Avanzadas

### Gestión de Estado
- Cache inteligente con TanStack Query
- Invalidación automática de datos
- Estados de carga y error manejados globalmente

### UX/UI Mejorada
- Animaciones suaves y micro-interacciones
- Feedback visual inmediato
- Skeleton loaders durante la carga
- Toast notifications para acciones del usuario

### Manejo de Errores
- Interceptores para errores HTTP
- Mensajes de error amigables al usuario
- Retry automático para peticiones fallidas
- Fallbacks para estados de error

## 📊 Módulos Implementados

### ✅ Completados
- **Dashboard**: Métricas generales y actividad reciente
- **Empleados**: CRUD completo con tabla avanzada
- **Áreas**: Gestión de áreas organizacionales
- **Boletas**: Visualización y descarga de boletas de pago

### 🚧 En Desarrollo
- **Usuarios**: Gestión de usuarios del sistema
- **Roles**: Administración de roles y permisos
- **Datos Académicos**: Información educativa de empleados
- **Datos Laborales**: Historial laboral
- **Datos Familiares**: Información familiar
- **Ubicaciones**: Gestión de ubicaciones

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas sobre el sistema, contactar al equipo de desarrollo.

---

**Desarrollado con ❤️ para la gestión moderna de recursos humanos**