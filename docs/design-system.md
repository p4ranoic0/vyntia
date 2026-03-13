# Design System - Intranet RRHH

Sistema de diseño unificado para la aplicación de Intranet de Recursos Humanos.

## 📐 Principios de Diseño

1. **Consistencia**: Todos los componentes siguen patrones visuales y de interacción uniformes
2. **Accesibilidad**: Cumplimiento con WCAG 2.1 AA
3. **Modularidad**: Componentes reutilizables y composables
4. **Escalabilidad**: Sistema preparado para crecer con nuevas funcionalidades

---

## 🎨 Paleta de Colores

### Colores Principales

```css
--primary: hsl(222.2, 47.4%, 11.2%)     /* Azul oscuro */
--primary-foreground: hsl(210, 40%, 98%) /* Blanco */
--secondary: hsl(210, 40%, 96.1%)       /* Gris claro */
--secondary-foreground: hsl(222.2, 47.4%, 11.2%)
```

### Estados de Empleado

- **Activo**: `hsl(142, 76%, 36%)` (Verde)
- **Inactivo**: `hsl(0, 0%, 45%)` (Gris)
- **Suspendido**: `hsl(25, 95%, 53%)` (Naranja)
- **Cesado**: `hsl(0, 72%, 51%)` (Rojo)

### Estados de Solicitudes

- **Pendiente**: `hsl(48, 96%, 53%)` (Amarillo)
- **Aprobado**: `hsl(142, 76%, 36%)` (Verde)
- **Rechazado**: `hsl(0, 72%, 51%)` (Rojo)
- **En Proceso**: `hsl(217, 91%, 60%)` (Azul)

### Estados de Documentos

- **Vigente**: Verde
- **Vencido**: Rojo
- **Por Vencer**: Naranja
- **No Presenta**: Gris

---

## 📝 Tipografía

### Tamaños de Fuente

```typescript
xs: 0.75rem    // 12px - Labels pequeños
sm: 0.875rem   // 14px - Texto secundario
base: 1rem     // 16px - Texto principal
lg: 1.125rem   // 18px - Subtítulos
xl: 1.25rem    // 20px - Títulos de secciones
2xl: 1.5rem    // 24px - Títulos de página
3xl: 1.875rem  // 30px - Títulos principales
```

### Pesos de Fuente

- **Normal**: 400 - Texto regular
- **Medium**: 500 - Énfasis sutil
- **Semibold**: 600 - Subtítulos
- **Bold**: 700 - Títulos importantes

---

## 📏 Espaciado

Sistema de espaciado basado en múltiplos de 4px:

```typescript
xs: 0.25rem   // 4px
sm: 0.5rem    // 8px
md: 1rem      // 16px
lg: 1.5rem    // 24px
xl: 2rem      // 32px
2xl: 3rem     // 48px
3xl: 4rem     // 64px
```

---

## 🧩 Componentes

### Componentes Base (shadcn/ui)

Ubicación: `src/components/ui/`

- `button` - Botones con múltiples variantes
- `card` - Contenedores de contenido
- `badge` - Indicadores de estado
- `dialog` - Modales
- `table` - Tablas de datos
- `input` - Campos de entrada
- `select` - Selectores
- `avatar` - Avatares de usuario
- `tooltip` - Tooltips informativos
- Y más...

### Componentes del Dominio

Ubicación: `src/shared/components/`

#### EmpleadoCard

Tarjeta para mostrar información de empleado.

**Variantes:**
- `compact` - Vista compacta para listas
- `default` - Vista estándar
- `detailed` - Vista completa con todos los datos

```tsx
import { EmpleadoCard } from '@/shared/components';

<EmpleadoCard
  empleado={{
    nombres_empleado: "Juan",
    apellido_paterno: "Pérez",
    apellido_materno: "García",
    cargo: "Desarrollador",
    estado: "activo"
  }}
  variant="detailed"
  onClick={() => navigate(`/empleados/${id}`)}
/>
```

#### EstadoBadge

Badge para mostrar estados con iconos y colores consistentes.

**Estados soportados:**
- Empleados: `activo`, `inactivo`, `suspendido`, `cesado`
- Solicitudes: `pendiente`, `aprobado`, `rechazado`, `proceso`
- Documentos: `vigente`, `vencido`, `por_vencer`

```tsx
import { EstadoBadge } from '@/shared/components';

<EstadoBadge 
  estado="activo" 
  showIcon={true}
  size="default"
/>
```

#### DocumentStatus

Indicador visual del estado de documentos.

```tsx
import { DocumentStatus } from '@/shared/components';

<DocumentStatus
  status="por_vencer"
  documentName="DNI"
  expirationDate="2024-12-31"
  size="md"
  showLabel={true}
/>
```

#### StatCard

Tarjeta para mostrar estadísticas y métricas.

**Variantes:**
- `default` - Neutral
- `primary` - Principal
- `success` - Positivo (verde)
- `warning` - Advertencia (naranja)
- `danger` - Error/Crítico (rojo)

```tsx
import { StatCard } from '@/shared/components';
import { Users } from 'lucide-react';

<StatCard
  title="Empleados Activos"
  value={245}
  description="Total de empleados actualmente trabajando"
  icon={Users}
  trend={{
    value: 12,
    label: "vs. mes anterior",
    isPositive: true
  }}
  variant="success"
/>
```

---

## 🎭 Iconos

Librería: **Lucide React**

Tamaños estándar:
```typescript
xs: 12px   // Iconos muy pequeños
sm: 16px   // Iconos inline con texto
base: 20px // Iconos estándar
lg: 24px   // Iconos destacados
xl: 32px   // Iconos grandes
2xl: 48px  // Iconos hero
```

Uso:
```tsx
import { User, Mail, Phone } from 'lucide-react';

<User className="h-5 w-5" />
```

---

## 🔧 Utilidades

### cn() - Class Name Merger

Combina clases de Tailwind evitando conflictos:

```tsx
import { cn } from '@/lib/utils';

<div className={cn(
  'base-class',
  isActive && 'active-class',
  className
)} />
```

### getInitials()

Genera iniciales de nombres:

```tsx
import { getInitials } from '@/lib/utils';

const initials = getInitials('Juan', 'Pérez'); // "JP"
```

---

## 🎯 Design Tokens

Todos los tokens de diseño están centralizados en:

**Archivo**: `src/lib/design-tokens.ts`

```tsx
import { colors, spacing, typography } from '@/lib/design-tokens';

// Usar colores consistentes
const empleadoColor = colors.empleado.activo;

// Espaciado consistente
const padding = spacing.lg;
```

---

## ♿ Accesibilidad

### Contraste de Color

Todos los colores cumplen con WCAG 2.1 AA:
- Texto normal: Ratio mínimo 4.5:1
- Texto grande: Ratio mínimo 3:1
- Elementos UI: Ratio mínimo 3:1

### Navegación por Teclado

Todos los componentes interactivos son accesibles por teclado:
- `Tab` - Navegar entre elementos
- `Enter/Space` - Activar botones
- `Esc` - Cerrar modales/diálogos
- `Arrow keys` - Navegar en listas/menús

### Screen Readers

- Uso de etiquetas ARIA apropiadas
- Texto alternativo en imágenes
- Mensajes de estado anunciados
- Navegación por landmarks

---

## 📱 Responsive Design

### Breakpoints

```typescript
sm: 640px   // Tablets pequeñas
md: 768px   // Tablets
lg: 1024px  // Laptops
xl: 1280px  // Desktops
2xl: 1536px // Pantallas grandes
```

### Ejemplo de Uso

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Contenido responsive */}
</div>
```

---

## 🌙 Dark Mode

Activar dark mode:

```tsx
// Layout o App.tsx
<div className="dark">
  {/* App content */}
</div>
```

Todos los componentes soportan automáticamente dark mode usando las variables CSS definidas.

---

## 🚀 Best Practices

### 1. Usa Componentes Compartidos

❌ **No hacer:**
```tsx
<div className="flex items-center gap-2 bg-green-100 text-green-800">
  Activo
</div>
```

✅ **Hacer:**
```tsx
<EstadoBadge estado="activo" />
```

### 2. Sigue las Convenciones de Nomenclatura

- Componentes: PascalCase (`EmpleadoCard`)
- Archivos: PascalCase (`EmpleadoCard.tsx`)
- Props: camelCase (`showIcon`)
- CSS classes: kebab-case (via Tailwind)

### 3. Mantén la Consistencia Visual

Usa siempre los design tokens en lugar de valores hardcodeados:

❌ **No hacer:**
```tsx
<div style={{ padding: '24px', color: '#22c55e' }}>
```

✅ **Hacer:**
```tsx
import { spacing, colors } from '@/lib/design-tokens';

<div style={{ padding: spacing.lg, color: colors.empleado.activo }}>
```

### 4. Documenta Nuevos Componentes

Al crear componentes nuevos:
- Añade comentarios JSDoc
- Exporta tipos/interfaces
- Incluye ejemplos de uso
- Actualiza este documento

---

## 📚 Recursos

- [Radix UI Documentation](https://www.radix-ui.com/)
- [shadcn/ui Components](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Lucide Icons](https://lucide.dev/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

## 🔄 Actualización del Design System

Este documento debe actualizarse cuando:
- Se agreguen nuevos componentes
- Se modifiquen colores o tokens
- Se cambien patrones de diseño
- Se agreguen nuevas utilidades

**Última actualización**: 8 de marzo de 2026
