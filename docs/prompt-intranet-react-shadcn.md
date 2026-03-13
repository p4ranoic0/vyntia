🎯 Prompt Final Mejorado: Desarrollo Frontend Intranet (React + Shadcn UI + Estilo Sneat PRO)

🛠️ Tecnologías a utilizar
- React (Vite o Next.js)
- Shadcn UI + Tailwind CSS
- Lucide React o similar
- TanStack Query (react-query)
- Zod + React Hook Form
- JWT + manejo de tokens
- Cookies seguras (HttpOnly si aplica)

🔐 Autenticación
- Login via POST /login/ con username y password
- Se espera recibir:
  - access, refresh
  - Objeto user con id, username, y detalles del empleado
- Requisitos clave:
  - Almacenar los tokens adecuadamente
  - Proteger rutas privadas
  - Mostrar los datos del usuario logueado en el header

➕ Mejora sugerida (Refresh Token avanzado):
- Implementar lógica automática para interceptar errores 401 y refrescar el token silenciosamente antes de reintentar la petición.
- Esto debe suceder de forma invisible para el usuario, manteniendo la sesión fluida.

🧭 Layout General (Estilo Sneat Dashboard PRO)
Sidebar (colapsable)
- Menú persistente con íconos para cada entidad
- Resaltado de ítem activo

Header/Navbar
- Menú de usuario: “Perfil”, “Configuración”, “Cerrar sesión”
- Dark/Light Mode toggle
- (Opcional) Barra de búsqueda global

Área de contenido
- Renderizado dinámico de tablas, formularios y vistas

🧱 Responsive Design (Optimización Móvil)
- El layout debe ser responsive y mobile-first
- Incluir consideraciones para uso táctil: tamaños touch-friendly, scroll horizontal en tablas, etc.

🔁 CRUD por Módulo
Para cada entidad, implementar:
- Tablas con:
  - Paginación (servidor o cliente)
  - Ordenamiento por columnas
  - Búsqueda/filtros por campos clave
- Formularios para crear y editar (modal o página)
- Vista detallada (expandible o dedicada)
- Eliminación con confirmación

🧩 Módulos a Implementar
1. Empleados
2. Usuarios, Roles y Permisos (incluye reg-permisos)
3. Boletas (descarga/visualización si hay archivo)
4. Áreas
5. Datos Familiares, Académicos y Laborales
6. Ubicaciones (reg_ubicacion)

📦 API Endpoints
GET/POST/PUT/DELETE:

http://127.0.0.1:8000/areas/
http://127.0.0.1:8000/empleados/
http://127.0.0.1:8000/datos-familiares/
http://127.0.0.1:8000/datos-academicos/
http://127.0.0.1:8000/datos-laborales/
http://127.0.0.1:8000/boletas/
http://127.0.0.1:8000/ubicaciones/
http://127.0.0.1:8000/usuarios/
http://127.0.0.1:8000/roles/
http://127.0.0.1:8000/permisos/
http://127.0.0.1:8000/reg-permisos/

Auth:
http://127.0.0.1:8000/login/

🔄 Manejo de Estado y Fetching
- Usar TanStack Query para:
  - Caching automático
  - Refetch controlado
  - Sincronización con el backend
- Loading states claros (spinners, skeletons)
- Error handling con feedback claro

➕ Mejora sugerida (UX en errores):
- Implementar un componente Toast o Alert genérico
- Mostrar mensajes amigables para el usuario
  - Ej. “No se pudo guardar, intente nuevamente”
- Evitar errores crudos del backend (500, tracebacks, etc.) al usuario final

🎨 UI & Estilo
- Usar exclusivamente componentes de Shadcn UI
- Personalizar tailwind.config.js y globals.css para parecerse al look de Sneat
- Tipografías, colores y spacing coherente
- Iconografía clara, bien ubicada y significativa

📁 Estructura del proyecto (sugerida)
src/
  ├─ components/         // Elementos reutilizables
  ├─ pages/              // Rutas principales
  ├─ features/           // Empleados, roles, boletas, etc.
  ├─ hooks/              // Custom hooks
  ├─ lib/api/            // Endpoints, funciones de fetch
  ├─ context/            // Auth, theme, etc.
  ├─ constants/          // Constantes globales
  ├─ styles/             // globals.css y estilos tailwind

✅ Entregables
- Aplicación funcional conectada al backend DRF
- Código bien estructurado, modular y mantenible
- README con pasos para instalar, correr, configurar .env, etc.

---

### 🧩 Base de Datos (Modelo Relacional)

La aplicación debe respetar la estructura relacional que se observa en el siguiente modelo (imagen incluida en los adjuntos).  
Las entidades principales incluyen:  
- `empleado` (relacionado con `usuario`, `boleta`, `datos_familiares`, `datos_academicos`, `datos_laborales`, `reg_ubicacion`)
- `usuario` (relacionado con `rol` y `empleado`)
- `rol`, `permiso`, `reg_permiso` (para gestión de accesos)
- `boleta`, `area`, `ubicaciones`

**Referencia visual:** Diagrama relacional (`1f2933ae-b2dd-49f4-b16b-fc54e9613175.png`)

---

### 🌐 Endpoints REST API (DRF Backend - Python)

```json
{
  "areas": "http://127.0.0.1:8000/areas/",
  "empleados": "http://127.0.0.1:8000/empleados/",
  "datos-familiares": "http://127.0.0.1:8000/datos-familiares/",
  "datos-academicos": "http://127.0.0.1:8000/datos-academicos/",
  "datos-laborales": "http://127.0.0.1:8000/datos-laborales/",
  "boletas": "http://127.0.0.1:8000/boletas/",
  "ubicaciones": "http://127.0.0.1:8000/ubicaciones/",
  "usuarios": "http://127.0.0.1:8000/usuarios/",
  "roles": "http://127.0.0.1:8000/roles/",
  "permisos": "http://127.0.0.1:8000/permisos/",
  "reg-permisos": "http://127.0.0.1:8000/reg-permisos/"
}
```

**Login Endpoint**: `http://127.0.0.1:8000/login/`

**Ejemplo de respuesta al login:**
```json
{
  "refresh": "<JWT_REFRESH_TOKEN>",
  "access": "<JWT_ACCESS_TOKEN>",
  "user": {
    "id": 74,
    "username": "hgarcia",
    "empleado": {
      "id": 74,
      "nombres": "HENRRY RAUL",
      "ape_paterno": "GARCIA",
      "ape_materno": "ESTOFANERO",
      "dni": "43550602"
    }
  }
}
```