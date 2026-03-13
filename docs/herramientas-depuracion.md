# Herramientas de Depuración

## Descripción General

Este documento describe las herramientas de depuración implementadas en la Intranet para facilitar el desarrollo, pruebas y resolución de problemas relacionados con la autenticación, autorización y navegación.

## Panel de Depuración (DebugPanel)

El Panel de Depuración es un componente que proporciona una interfaz unificada para acceder a todas las herramientas de depuración. Este panel:

- Solo es visible en entorno de desarrollo (process.env.NODE_ENV === 'development')
- Se puede mostrar/ocultar mediante un botón flotante
- Organiza las herramientas en pestañas para facilitar la navegación

### Ubicación

```
src/components/debug/DebugPanel.tsx
```

### Uso

El panel se integra automáticamente en la aplicación en modo desarrollo. Para utilizarlo:

1. Ejecutar la aplicación en modo desarrollo
2. Hacer clic en el botón flotante de depuración (esquina inferior derecha)
3. Navegar entre las pestañas para acceder a las diferentes herramientas

## Herramientas Disponibles

### MenuDebug

**Descripción**: Muestra información detallada sobre el estado actual del menú.

**Ubicación**: `src/components/debug/MenuDebug.tsx`

**Información mostrada**:
- Estado de autenticación del usuario
- Estado de carga del menú
- Errores en la carga del menú
- Lista completa de elementos del menú con detalles:
  - Nombre
  - ID
  - Icono
  - Ruta
  - Número de hijos

### UserPermissionsDebug

**Descripción**: Muestra información detallada sobre los permisos y roles del usuario actual.

**Ubicación**: `src/components/debug/UserPermissionsDebug.tsx`

**Información mostrada**:
- Estado de autenticación
- Nombre de usuario
- Roles asignados
- Lista completa de permisos
- Funciones de verificación de permisos y roles

### MenuPermissionsDebug

**Descripción**: Analiza y muestra información sobre el acceso a elementos del menú según los permisos del usuario.

**Ubicación**: `src/components/debug/MenuPermissionsDebug.tsx`

**Información mostrada**:
- Elementos visibles para el usuario actual
- Elementos ocultos por falta de permisos
- Requisitos de permisos y roles por elemento
- Análisis de acceso (por qué un elemento es visible u oculto)

### PermissionsStructureDebug

**Descripción**: Muestra la estructura completa de permisos y roles del sistema.

**Ubicación**: `src/components/debug/PermissionsStructureDebug.tsx`

**Información mostrada**:
- Módulos disponibles en el sistema
- Permisos agrupados por módulo
- Roles definidos en el sistema
- Permisos asignados a cada rol

### MenuStructureDebug

**Descripción**: Muestra la estructura completa del menú, incluyendo elementos visibles y no visibles para el usuario actual.

**Ubicación**: `src/components/debug/MenuStructureDebug.tsx`

**Información mostrada**:
- Jerarquía completa de elementos del menú
- Detalles de cada elemento:
  - Nombre
  - Ruta
  - Icono
  - Permisos requeridos
  - Roles requeridos
- Subelementos (estructura recursiva)

### MenuDebugInline

**Descripción**: Versión simplificada de MenuDebug que se puede integrar directamente en otros componentes.

**Ubicación**: `src/components/debug/MenuDebugInline.tsx`

**Información mostrada**:
- Estado de carga del menú
- Errores en la carga del menú
- Lista básica de elementos del menú

## Integración en la Aplicación

El Panel de Depuración se integra en la aplicación a través del componente principal App.tsx. La integración se realiza de la siguiente manera:

```tsx
// En App.tsx
import DebugPanel from '@/components/debug/DebugPanel'

function App() {
  return (
    <Router>
      {/* ... otros componentes ... */}
      {process.env.NODE_ENV === 'development' && <DebugPanel />}
    </Router>
  )
}
```

## Casos de Uso

### Depuración de Permisos

1. Acceder al panel de depuración
2. Navegar a la pestaña "Permisos de Usuario"
3. Verificar los roles y permisos asignados al usuario actual
4. Comprobar si el usuario tiene los permisos necesarios para acceder a una funcionalidad específica

### Análisis del Menú

1. Acceder al panel de depuración
2. Navegar a la pestaña "Menú"
3. Verificar que los elementos del menú se carguen correctamente
4. Comprobar que la estructura jerárquica sea la esperada

### Resolución de Problemas de Acceso

1. Acceder al panel de depuración
2. Navegar a la pestaña "Permisos del Menú"
3. Identificar elementos ocultos por falta de permisos
4. Verificar los requisitos de permisos y roles para esos elementos

### Análisis de Estructura de Permisos

1. Acceder al panel de depuración
2. Navegar a la pestaña "Estructura de Permisos"
3. Analizar los módulos y permisos disponibles
4. Verificar la asignación de permisos a roles

### Análisis de Estructura del Menú

1. Acceder al panel de depuración
2. Navegar a la pestaña "Estructura del Menú"
3. Analizar la estructura completa del menú
4. Verificar los requisitos de permisos y roles para cada elemento

## Mejores Prácticas

1. **Uso exclusivo en desarrollo**: Estas herramientas deben utilizarse solo en entorno de desarrollo, nunca en producción
2. **Actualización constante**: Mantener las herramientas actualizadas con los cambios en el sistema de permisos y menú
3. **Documentación**: Documentar nuevas funcionalidades añadidas a las herramientas de depuración
4. **Extensibilidad**: Diseñar las herramientas para que sean fácilmente extensibles con nuevas funcionalidades

## Extensión de las Herramientas

Para añadir nuevas funcionalidades a las herramientas de depuración:

1. Crear un nuevo componente en `src/components/debug/`
2. Seguir el patrón de diseño de los componentes existentes
3. Integrar el nuevo componente en DebugPanel.tsx añadiendo una nueva pestaña
4. Actualizar esta documentación con la nueva herramienta