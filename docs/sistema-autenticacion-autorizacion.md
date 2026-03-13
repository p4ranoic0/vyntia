# Sistema de Autenticación y Autorización

Este documento describe el sistema de autenticación y autorización implementado en la intranet.

## Arquitectura General

El sistema utiliza un enfoque basado en roles y permisos para gestionar el acceso a diferentes funcionalidades de la aplicación. La arquitectura se compone de los siguientes elementos principales:

### Modelos Principales

#### Usuario

El modelo `Usuario` es la entidad central del sistema de autenticación y autorización. Extiende el modelo base de Django para usuarios y añade campos específicos para la aplicación.

**Características principales:**
- Tipos de usuario (administrador, empleado, etc.)
- Niveles de acceso (personal, departamental, total)
- Estados (activo, inactivo, suspendido, bloqueado)
- Gestión de contraseñas (expiración, bloqueo por intentos fallidos)
- Métodos para verificar permisos y roles

#### Rol

El modelo `Rol` define los diferentes roles que pueden ser asignados a los usuarios.

**Características principales:**
- Nombre y descripción del rol
- Nivel jerárquico
- Estado (activo, inactivo)
- Indicador de rol de sistema

#### Permiso

El modelo `Permiso` define las acciones específicas que pueden realizarse en el sistema.

**Características principales:**
- Nombre y descripción del permiso
- Asociación con un módulo del sistema
- Tipo de permiso (leer, crear, actualizar, eliminar, aprobar)
- Estado (activo, inactivo)

#### Módulo

El modelo `Modulos` representa las diferentes secciones o funcionalidades del sistema.

**Características principales:**
- Nombre y descripción del módulo
- Icono y ruta para la interfaz de usuario
- Orden de visualización
- Estado (activo, inactivo, mantenimiento)

### Relaciones entre Modelos

#### UsuarioRoles

El modelo `UsuarioRoles` gestiona la relación entre usuarios y roles.

**Características principales:**
- Asignación de roles a usuarios
- Fecha de asignación y expiración
- Estado de la asignación (activo, inactivo, suspendido, expirado)
- Métodos para verificar vigencia y expiración

#### RolPermisos

El modelo `RolPermisos` gestiona la relación entre roles y permisos.

**Características principales:**
- Asignación de permisos a roles
- Fecha de asignación
- Métodos para gestionar asignaciones

## Flujo de Autenticación

1. El usuario inicia sesión a través del endpoint `/api/v1/auth/login/`
2. El sistema valida las credenciales y genera un token JWT
3. El token incluye información sobre el usuario, sus roles y permisos
4. El frontend almacena el token y lo utiliza para autenticar las solicitudes posteriores

## Flujo de Autorización

1. El usuario solicita acceso a una funcionalidad o recurso
2. El sistema verifica si el usuario tiene los permisos necesarios a través de sus roles asignados
3. El acceso se concede o deniega según los permisos del usuario

## Generación del Menú

El menú de la aplicación se genera dinámicamente según los permisos del usuario:

1. El frontend solicita el menú a través del endpoint `/api/v1/auth/menu/`
2. El backend obtiene los permisos activos del usuario a través de sus roles
3. Se construye un menú personalizado basado en los módulos activos y los permisos del usuario
4. El menú incluye solo las opciones a las que el usuario tiene acceso

### Estructura del Menú

El menú se estructura en elementos principales y subelementos:

- **Dashboard**: Accesible para todos los usuarios autenticados
- **Empleados**: Incluye subelementos como "Listado", "Crear", etc., según los permisos
- **Vacaciones**: Accesible según los permisos del usuario
- **Administración**: Incluye subelementos como "Módulos", "Usuarios", "Roles", según los permisos
- **Reportes**: Accesible según los permisos del usuario

## Métodos Clave para Verificación de Permisos

### Usuario

- `roles_activos()`: Obtiene los roles activos y no expirados del usuario
- `permisos_activos()`: Obtiene los permisos activos del usuario a través de sus roles
- `puede_acceder_a_area(area)`: Verifica si el usuario puede acceder a un área específica
- `puede_ver_empleado(empleado)`: Verifica si el usuario puede ver información de un empleado

### Rol

- `permisos()`: Obtiene todos los permisos asignados a un rol
- `usuarios()`: Obtiene todos los usuarios asignados a un rol

### Permiso

- Métodos para verificar el tipo de permiso (lectura, escritura, eliminación, aprobación)
- Métodos para obtener permisos por tipo o módulo

## Seguridad Adicional

- Bloqueo de cuenta después de múltiples intentos fallidos de inicio de sesión
- Expiración de contraseñas después de un período definido
- Tokens de recuperación de contraseña con expiración
- Registro de accesos (IP, user agent)

## Consideraciones para Desarrollo

- Siempre verificar permisos antes de permitir acciones en el backend
- Utilizar los métodos proporcionados por los modelos para verificar permisos
- Mantener actualizados los estados de módulos, permisos y roles
- Considerar la expiración de roles al verificar permisos