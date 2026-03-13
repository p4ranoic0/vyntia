# Sistema de Autenticación y Autorización

## Descripción General

El sistema de autenticación y autorización de la Intranet está diseñado para proporcionar un control de acceso basado en roles y permisos. Este documento describe la arquitectura, componentes y flujo de trabajo del sistema.

## Arquitectura

El sistema sigue una arquitectura cliente-servidor:

- **Backend**: Implementado en Django con Django REST Framework
- **Frontend**: Implementado en React con TypeScript

## Componentes Principales

### Backend

#### Modelos

- **User**: Extiende el modelo de usuario de Django con campos adicionales
- **Role**: Define roles en el sistema (ej. ADMIN, USUARIO, RRHH)
- **Permission**: Define permisos específicos (ej. VER_USUARIOS, EDITAR_USUARIOS)
- **UserRole**: Relación muchos a muchos entre usuarios y roles

#### Serializadores

- **LoginSerializer**: Valida credenciales y autentica al usuario
- **UserProfileSerializer**: Serializa información del perfil del usuario

#### Vistas

- **LoginAPIView**: Maneja la autenticación y genera tokens JWT
- **UserPermissionsAPIView**: Proporciona roles y permisos del usuario
- **ChangePasswordAPIView**: Permite cambiar la contraseña

### Frontend

#### Contexto de Autenticación

- **AuthContext**: Proporciona estado de autenticación y funciones relacionadas a toda la aplicación
- **AuthProvider**: Componente que envuelve la aplicación y gestiona el estado de autenticación

#### Hooks

- **useAuth**: Hook personalizado para acceder al contexto de autenticación
- **useMenu**: Hook para cargar el menú dinámico basado en permisos

#### Servicios

- **apiClient**: Cliente HTTP configurado para incluir tokens de autenticación
- **menuService**: Servicio para obtener y gestionar el menú dinámico

## Flujo de Autenticación

1. El usuario ingresa credenciales en el formulario de login
2. El frontend envía las credenciales al endpoint `/api/v1/auth/login/`
3. El backend valida las credenciales y devuelve:
   - Token JWT
   - Información del usuario (incluyendo roles y permisos)
4. El frontend almacena el token en cookies y la información del usuario en el contexto
5. Las solicitudes posteriores incluyen el token en el encabezado de autorización

## Control de Acceso

### Roles y Permisos

El sistema utiliza un modelo de control de acceso basado en roles (RBAC) con las siguientes características:

- Cada usuario puede tener múltiples roles
- Cada rol puede tener múltiples permisos
- Los permisos determinan las acciones que un usuario puede realizar

### Verificación de Permisos

#### Backend

- Utiliza permisos personalizados de Django REST Framework
- Verifica permisos en cada endpoint de la API

#### Frontend

- Utiliza funciones del contexto de autenticación para verificar permisos:
  - `hasRole(role)`: Verifica si el usuario tiene un rol específico
  - `hasPermission(permission)`: Verifica si el usuario tiene un permiso específico
  - `hasAnyRole(roles)`: Verifica si el usuario tiene al menos uno de los roles especificados
  - `hasAnyPermission(permissions)`: Verifica si el usuario tiene al menos uno de los permisos especificados

## Menú Dinámico

El sistema implementa un menú dinámico basado en los permisos del usuario:

1. El frontend solicita el menú al endpoint `/api/v1/auth/menu/`
2. El backend filtra los elementos del menú según los permisos del usuario
3. El frontend renderiza el menú utilizando el hook `useMenu`

### Estructura del Menú

Cada elemento del menú puede tener:

- **id**: Identificador único
- **name**: Nombre a mostrar
- **icon**: Icono a mostrar (nombre del icono de Lucide React)
- **path**: Ruta de navegación
- **permissions**: Lista de permisos requeridos para ver el elemento
- **roles**: Lista de roles requeridos para ver el elemento
- **children**: Subelementos del menú (estructura recursiva)

## Herramientas de Depuración

El sistema incluye herramientas de depuración para facilitar el desarrollo y la resolución de problemas:

- **DebugPanel**: Panel de depuración con múltiples pestañas
- **MenuDebug**: Muestra información sobre el estado del menú
- **UserPermissionsDebug**: Muestra información sobre los permisos del usuario
- **MenuPermissionsDebug**: Analiza el acceso a elementos del menú según permisos
- **PermissionsStructureDebug**: Muestra la estructura de permisos y roles
- **MenuStructureDebug**: Muestra la estructura completa del menú

## Mejores Prácticas

1. **Verificación en ambos lados**: Implementar verificación de permisos tanto en el frontend como en el backend
2. **Granularidad de permisos**: Definir permisos específicos para acciones concretas
3. **Caché de menú**: Utilizar caché para mejorar el rendimiento del menú dinámico
4. **Tokens seguros**: Utilizar tokens JWT con tiempo de expiración adecuado
5. **Manejo de errores**: Implementar manejo de errores consistente en autenticación y autorización

## Recomendaciones para Desarrollo

1. Utilizar las funciones `hasRole` y `hasPermission` para controlar el acceso a componentes y funcionalidades
2. Mantener actualizada la documentación de roles y permisos
3. Utilizar las herramientas de depuración durante el desarrollo
4. Implementar pruebas automatizadas para verificar el control de acceso