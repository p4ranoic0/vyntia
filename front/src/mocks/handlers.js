import { http } from 'msw';

// Datos de ejemplo para las respuestas simuladas
const mockUserData = {
  id: 1,
  username: 'admin',
  email: 'admin@example.com',
  first_name: 'Admin',
  last_name: 'User',
  is_active: true,
  is_staff: true,
  is_superuser: true,
  roles: ['admin'],
  permissions: ['view_user', 'add_user', 'change_user', 'delete_user'],
};

const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiaWF0IjoxNTE2MjM5MDIyfQ.L8i6g3PfcHlioHCCPURC9pmXT7gdJpx3kOoyAfNUwCc';

const mockMenu = {
  menu: [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: 'home',
      path: '/dashboard',
      children: [],
    },
    {
      id: 'profile',
      label: 'Perfil',
      icon: 'user',
      path: '/profile',
      children: [],
    },
    {
      id: 'admin',
      label: 'Administración',
      icon: 'settings',
      path: '/admin',
      children: [
        {
          id: 'users',
          label: 'Usuarios',
          icon: 'users',
          path: '/admin/users',
        },
        {
          id: 'roles',
          label: 'Roles',
          icon: 'shield',
          path: '/admin/roles',
        },
      ],
    },
  ],
};

const mockMenuStructure = {
  menu_structure: [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: 'home',
      path: '/dashboard',
      requires_auth: true,
      permissions: [],
      children: [],
    },
    {
      id: 'profile',
      label: 'Perfil',
      icon: 'user',
      path: '/profile',
      requires_auth: true,
      permissions: [],
      children: [],
    },
    {
      id: 'admin',
      label: 'Administración',
      icon: 'settings',
      path: '/admin',
      requires_auth: true,
      permissions: ['is_staff'],
      children: [
        {
          id: 'users',
          label: 'Usuarios',
          icon: 'users',
          path: '/admin/users',
          requires_auth: true,
          permissions: ['view_user'],
        },
        {
          id: 'roles',
          label: 'Roles',
          icon: 'shield',
          path: '/admin/roles',
          requires_auth: true,
          permissions: ['view_role'],
        },
      ],
    },
  ],
};

const mockPermissionsStructure = {
  permissions_structure: {
    roles: [
      {
        id: 1,
        name: 'admin',
        description: 'Administrador del sistema',
        permissions: ['view_user', 'add_user', 'change_user', 'delete_user', 'view_role', 'add_role', 'change_role', 'delete_role'],
      },
      {
        id: 2,
        name: 'user',
        description: 'Usuario estándar',
        permissions: ['view_user'],
      },
    ],
    permissions: [
      {
        id: 1,
        codename: 'view_user',
        name: 'Can view user',
        content_type: 'auth',
      },
      {
        id: 2,
        codename: 'add_user',
        name: 'Can add user',
        content_type: 'auth',
      },
      {
        id: 3,
        codename: 'change_user',
        name: 'Can change user',
        content_type: 'auth',
      },
      {
        id: 4,
        codename: 'delete_user',
        name: 'Can delete user',
        content_type: 'auth',
      },
      {
        id: 5,
        codename: 'view_role',
        name: 'Can view role',
        content_type: 'auth',
      },
      {
        id: 6,
        codename: 'add_role',
        name: 'Can add role',
        content_type: 'auth',
      },
      {
        id: 7,
        codename: 'change_role',
        name: 'Can change role',
        content_type: 'auth',
      },
      {
        id: 8,
        codename: 'delete_role',
        name: 'Can delete role',
        content_type: 'auth',
      },
    ],
  },
};

// Handlers para simular respuestas de la API
export const handlers = [
  // Login
  http.post('http://localhost:8000/api/v1/auth/login/', ({ request }) => {
    return request.json().then(body => {
      const { username, password } = body;
    
      if (username === 'admin' && password === 'admin123') {
        return new Response(
          JSON.stringify({
            token: mockToken,
            user: mockUserData,
          }),
          {
            status: 200,
            headers: { 'Content-Type': 'application/json' }
          }
        );
      }
      
      return new Response(
        JSON.stringify({
          detail: 'Credenciales inválidas',
        }),
        {
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    });
  }),
  
  // Obtener menú del usuario
  http.get('http://localhost:8000/api/v1/auth/menu/', ({ request }) => {
    // Verificar token de autenticación
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new Response(
        JSON.stringify({
          detail: 'Autenticación requerida',
        }),
        {
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    return new Response(
      JSON.stringify(mockMenu),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }),
  
  // Obtener estructura del menú
  http.get('http://localhost:8000/api/v1/auth/menu-structure/', ({ request }) => {
    // Verificar token de autenticación
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new Response(
        JSON.stringify({
          detail: 'Autenticación requerida',
        }),
        {
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    return new Response(
      JSON.stringify(mockMenuStructure),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }),
  
  // Obtener estructura de permisos
  http.get('http://localhost:8000/api/v1/auth/permissions-structure/', ({ request }) => {
    // Verificar token de autenticación
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new Response(
        JSON.stringify({
          detail: 'Autenticación requerida',
        }),
        {
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    return new Response(
      JSON.stringify(mockPermissionsStructure),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }),

  // Obtener módulos
  http.get('http://localhost:8000/api/v1/auth/modules/', ({ request }) => {
    // Verificar token de autenticación
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new Response(
        JSON.stringify({
          detail: 'Autenticación requerida',
        }),
        {
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    return new Response(
      JSON.stringify({
        success: true,
        data: [
          {
            id: 'auth',
            nombre: 'Autenticación',
            descripcion: 'Módulo de autenticación y autorización',
            permisos: [
              {
                id: 'view_user',
                nombre: 'Ver usuarios',
                descripcion: 'Permite ver la lista de usuarios',
                modulo: 'auth'
              },
              {
                id: 'add_user',
                nombre: 'Agregar usuarios',
                descripcion: 'Permite agregar nuevos usuarios',
                modulo: 'auth'
              },
              {
                id: 'change_user',
                nombre: 'Modificar usuarios',
                descripcion: 'Permite modificar usuarios existentes',
                modulo: 'auth'
              },
              {
                id: 'delete_user',
                nombre: 'Eliminar usuarios',
                descripcion: 'Permite eliminar usuarios',
                modulo: 'auth'
              }
            ]
          },
          {
            id: 'admin',
            nombre: 'Administración',
            descripcion: 'Módulo de administración del sistema',
            permisos: [
              {
                id: 'view_role',
                nombre: 'Ver roles',
                descripcion: 'Permite ver la lista de roles',
                modulo: 'admin'
              },
              {
                id: 'add_role',
                nombre: 'Agregar roles',
                descripcion: 'Permite agregar nuevos roles',
                modulo: 'admin'
              },
              {
                id: 'change_role',
                nombre: 'Modificar roles',
                descripcion: 'Permite modificar roles existentes',
                modulo: 'admin'
              },
              {
                id: 'delete_role',
                nombre: 'Eliminar roles',
                descripcion: 'Permite eliminar roles',
                modulo: 'admin'
              }
            ]
          }
        ]
      }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }),

  // Obtener roles
  http.get('http://localhost:8000/api/v1/auth/roles/', ({ request }) => {
    // Verificar token de autenticación
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new Response(
        JSON.stringify({
          detail: 'Autenticación requerida',
        }),
        {
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    return new Response(
      JSON.stringify({
        success: true,
        data: [
          {
            id: 'admin',
            nombre: 'Administrador',
            descripcion: 'Administrador del sistema',
            permisos: ['view_user', 'add_user', 'change_user', 'delete_user', 'view_role', 'add_role', 'change_role', 'delete_role']
          },
          {
            id: 'user',
            nombre: 'Usuario',
            descripcion: 'Usuario estándar',
            permisos: ['view_user']
          }
        ]
      }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }),
];