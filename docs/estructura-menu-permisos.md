# Estructura del Menú y Sistema de Permisos

## Descripción General

Este documento describe la estructura del menú dinámico y el sistema de permisos implementado en la Intranet. El objetivo es proporcionar una guía clara sobre cómo se configura el menú, cómo se relaciona con los permisos y roles, y cómo se puede extender o modificar.

## Estructura del Menú

### Modelo de Datos

El menú se estructura como un árbol jerárquico donde cada elemento puede tener hijos. La estructura básica de un elemento de menú es:

```typescript
interface MenuItem {
  id: string;
  name: string;
  icon?: string;
  path?: string;
  permissions?: string[];
  roles?: string[];
  children?: MenuItem[];
}
```

Donde:
- **id**: Identificador único del elemento
- **name**: Texto a mostrar en el menú
- **icon**: Nombre del icono de Lucide React (opcional)
- **path**: Ruta de navegación (opcional para elementos padre)
- **permissions**: Lista de permisos requeridos para ver el elemento (opcional)
- **roles**: Lista de roles requeridos para ver el elemento (opcional)
- **children**: Lista de elementos hijos (opcional)

### Flujo de Carga del Menú

1. El frontend solicita el menú al backend mediante `apiClient.get('/api/v1/auth/menu/')`
2. El backend filtra los elementos del menú según los permisos del usuario
3. El frontend recibe el menú y lo procesa mediante `menuService.getUserMenu()`
4. El servicio de menú aplica filtros adicionales si es necesario mediante `filterMenuByPermissions()`
5. El menú filtrado se almacena en caché para mejorar el rendimiento
6. Los componentes de la interfaz utilizan el menú para renderizar la navegación

## Sistema de Permisos

### Tipos de Permisos

El sistema utiliza dos niveles de control de acceso:

1. **Roles**: Agrupaciones de permisos que definen un perfil de usuario (ej. ADMIN, USUARIO, RRHH)
2. **Permisos**: Capacidades específicas para realizar acciones (ej. VER_USUARIOS, EDITAR_USUARIOS)

### Estructura de Permisos

Los permisos se organizan por módulos y acciones:

```typescript
interface Permission {
  id: string;
  name: string;
  codename: string;
  module: string;
}

interface Role {
  id: string;
  name: string;
  permissions: Permission[];
}
```

Donde:
- **module**: Agrupa permisos relacionados con una funcionalidad específica
- **codename**: Identificador único del permiso utilizado en verificaciones
- **name**: Nombre descriptivo del permiso

### Verificación de Permisos

El sistema proporciona varias funciones para verificar permisos:

```typescript
// Verifica si el usuario tiene un rol específico
hasRole(role: string): boolean

// Verifica si el usuario tiene un permiso específico
hasPermission(permission: string): boolean

// Verifica si el usuario tiene al menos uno de los roles especificados
hasAnyRole(roles: string[]): boolean

// Verifica si el usuario tiene al menos uno de los permisos especificados
hasAnyPermission(permissions: string[]): boolean
```

## Integración de Menú y Permisos

### Filtrado de Menú por Permisos

El proceso de filtrado del menú se realiza en dos niveles:

1. **Backend**: Filtra elementos según permisos del usuario antes de enviar el menú
2. **Frontend**: Aplica filtros adicionales mediante `filterMenuByPermissions()`

La función `filterMenuItems` recorre recursivamente el árbol del menú y aplica las siguientes reglas:

- Si un elemento no tiene requisitos de permisos o roles, se incluye
- Si un elemento requiere permisos, el usuario debe tener al menos uno
- Si un elemento requiere roles, el usuario debe tener al menos uno
- Los elementos hijos se filtran recursivamente
- Si un elemento padre no tiene hijos después del filtrado, se elimina

### Menú Básico de Fallback

Si el menú del backend está vacío o no se puede cargar, el sistema proporciona un menú básico de fallback mediante `getBasicMenu()`. Este menú incluye elementos esenciales como:

- Dashboard
- Mi Perfil

## Herramientas de Depuración

El sistema incluye varias herramientas para depurar el menú y los permisos:

### MenuDebug

Muestra información sobre el estado actual del menú:
- Estado de carga
- Errores
- Elementos del menú

### UserPermissionsDebug

Muestra información sobre los permisos del usuario:
- Roles asignados
- Permisos disponibles
- Estado de autenticación

### MenuPermissionsDebug

Analiza el acceso a elementos del menú según permisos:
- Elementos visibles
- Elementos ocultos por falta de permisos
- Requisitos de permisos por elemento

### PermissionsStructureDebug

Muestra la estructura completa de permisos y roles:
- Módulos disponibles
- Permisos por módulo
- Roles y sus permisos asociados

### MenuStructureDebug

Muestra la estructura completa del menú:
- Jerarquía de elementos
- Permisos requeridos por elemento
- Roles requeridos por elemento

## Extensión del Sistema

### Añadir Nuevos Elementos al Menú

Para añadir nuevos elementos al menú, se debe modificar la configuración en el backend:

1. Definir el nuevo elemento con su estructura completa
2. Asignar permisos y roles adecuados
3. Incluirlo en la respuesta del endpoint `/api/v1/auth/menu/`

### Crear Nuevos Permisos

Para crear nuevos permisos:

1. Definir el permiso en el backend con un codename único
2. Asignar el permiso a los roles correspondientes
3. Actualizar la documentación de permisos

## Mejores Prácticas

1. **Nomenclatura consistente**: Utilizar un formato consistente para los codenames de permisos (ej. `MODULO_ACCION`)
2. **Granularidad adecuada**: Definir permisos específicos para acciones concretas
3. **Documentación**: Mantener actualizada la documentación de permisos y roles
4. **Pruebas**: Implementar pruebas para verificar el correcto funcionamiento del menú y los permisos
5. **Caché**: Utilizar la caché del menú para mejorar el rendimiento, pero limpiarla cuando sea necesario

## Recomendaciones para Desarrollo

1. Utilizar las herramientas de depuración durante el desarrollo
2. Verificar que los nuevos elementos del menú se muestren correctamente según los permisos
3. Mantener la estructura del menú limpia y organizada
4. Evitar dependencias circulares entre módulos
5. Considerar la experiencia de usuario al diseñar la estructura del menú