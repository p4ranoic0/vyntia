import { apiClient } from "@/shared/api/api";
import { getErrorMessage } from "@/shared/api/errorUtils";
import {
  extractCollection,
  normalizeRole,
  normalizeUser,
} from "@/shared/api/apiNormalizers";

// Interfaces para usuarios
export interface User {
  id: string;
  username: string;
  email: string;
  nombres_usuario: string;
  apellidos_usuario: string;
  tipo_usuario: string;
  nivel_acceso: string;
  estado_usuario: string;
  is_active: boolean;
  date_joined: string;
  last_login?: string;
  empleado?: {
    id: string;
    nombres: string;
    ape_paterno: string;
    ape_materno: string;
    dni: string;
    area: {
      id: string;
      organo: string;
      siglas: string;
    };
  };
  roles_activos?: Role[];
  dias_sin_login?: number;
  ultimo_login_texto?: string;
}

export interface Role {
  id: string;
  nombre_rol: string;
  descripcion_rol: string;
  estado_rol: string;
  is_active: boolean;
  total_usuarios?: number;
  total_permisos?: number;
  permisos?: Permission[];
}

export interface Permission {
  id: string;
  nombre_permiso: string;
  descripcion_permiso: string;
  estado_permiso: string;
  modulo?: string;
}

export interface UserFormData {
  nombres_usuario: string;
  apellidos_usuario: string;
  username: string;
  email: string;
  tipo_usuario: string;
  nivel_acceso: string;
  estado_usuario: string;
  empleado?: string;
  password?: string;
  password_confirm?: string;
  roles?: string[];
}

export interface ChangePasswordData {
  old_password: string;
  new_password: string;
  confirm_password: string;
}

export interface UserRoleAssignment {
  user_id: string;
  roles_to_add?: string[];
  roles_to_remove?: string[];
  role_ids?: string[];
  remove_existing?: boolean;
}

// Servicio para gestión de usuarios
export const usersService = {
  /**
   * Obtener lista de usuarios con filtros opcionales
   */
  async getAll(params?: Record<string, unknown>) {
    try {
      const response = await apiClient.get("/api/v1/identity/users/", {
        params,
      });
      const users = extractCollection(response.data);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return users.map((user: any) => normalizeUser(user)); // extractCollection returns unknown[]; normalizeUser expects raw API shape
    } catch (error) {
      console.error("Error fetching users:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Obtener usuario por ID
   */
  async getById(id: string) {
    try {
      const response = await apiClient.get(`/api/v1/identity/users/${id}/`);
      return { data: normalizeUser(response.data) };
    } catch (error) {
      console.error("Error fetching user:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Crear nuevo usuario
   */
  async create(data: UserFormData) {
    try {
      // Mapear los datos del frontend al formato esperado por el backend
      const backendData = {
        nombres_usuario: data.nombres_usuario,
        apellidos_usuario: data.apellidos_usuario,
        username: data.username,
        email: data.email,
        correo_institucional: data.email,
        tipo_usuario: data.tipo_usuario,
        nivel_acceso: data.nivel_acceso,
        estado_usuario: data.estado_usuario,
        empleado: data.empleado,
        password: data.password,
        password_confirm: data.password_confirm,
        roles: data.roles,
      };

      const response = await apiClient.post(
        "/api/v1/identity/users/",
        backendData,
      );
      return response.data;
    } catch (error) {
      console.error("Error creating user:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Actualizar usuario existente
   */
  async update(id: string, data: Partial<UserFormData>) {
    try {
      // Mapear los datos del frontend al formato esperado por el backend
      const backendData = {
        nombres_usuario: data.nombres_usuario,
        apellidos_usuario: data.apellidos_usuario,
        username: data.username,
        email: data.email,
        correo_institucional: data.email,
        tipo_usuario: data.tipo_usuario,
        nivel_acceso: data.nivel_acceso,
        estado_usuario: data.estado_usuario,
        empleado: data.empleado,
        roles: data.roles,
      };

      const response = await apiClient.patch(
        `/api/v1/identity/users/${id}/`,
        backendData,
      );
      return response.data;
    } catch (error) {
      console.error("Error updating user:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Eliminar usuario (soft delete)
   */
  async delete(id: string) {
    try {
      const response = await apiClient.delete(`/api/v1/identity/users/${id}/`);
      return response.data;
    } catch (error) {
      console.error("Error deleting user:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Cambiar contraseña de usuario
   */
  async changePassword(userId: string, data: ChangePasswordData) {
    try {
      const response = await apiClient.post(
        `/api/v1/identity/users/${userId}/change-password/`,
        data,
      );
      return response.data;
    } catch (error) {
      console.error("Error changing password:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Obtener usuarios sin login reciente
   */
  async getUsersWithoutRecentLogin(days: number = 30) {
    try {
      const response = await apiClient.get(
        `/api/v1/identity/users/sin_login_reciente/?dias=${days}`,
      );
      const data =
        response.data.data?.results ||
        response.data.results ||
        response.data.data ||
        response.data;
      return Array.isArray(data) ? data : [];
    } catch (error) {
      console.error("Error fetching users without recent login:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Obtener estadísticas de usuarios
   */
  async getStatistics() {
    try {
      const response = await apiClient.get(
        "/api/v1/identity/users/estadisticas/",
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching user statistics:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Buscar usuarios por roles asignados
   */
  async searchByRoles(params: {
    rol_ids?: string[];
    nombres?: string;
    estado?: string;
    operador?: "AND" | "OR";
  }) {
    try {
      const queryParams = new URLSearchParams();

      if (params.rol_ids && params.rol_ids.length > 0) {
        queryParams.append("rol_ids", params.rol_ids.join(","));
      }
      if (params.nombres) {
        queryParams.append("nombres", params.nombres);
      }
      if (params.estado) {
        queryParams.append("estado", params.estado);
      }
      if (params.operador) {
        queryParams.append("operador", params.operador);
      }

      const response = await apiClient.get(
        `/api/v1/identity/user-roles/buscar_usuarios_por_roles/?${queryParams.toString()}`,
      );
      const users = extractCollection(response.data);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return users.map((user: any) => normalizeUser(user)); // extractCollection returns unknown[]; normalizeUser expects raw API shape
    } catch (error) {
      console.error("Error searching users by roles:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Actualizar roles de un usuario
   */
  async updateUserRoles(userId: string, assignment: UserRoleAssignment) {
    try {
      const response = await apiClient.post(
        `/api/v1/identity/users/${userId}/asignar_rol/`,
        assignment,
      );
      return response.data;
    } catch (error) {
      console.error("Error updating user roles:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Asignar roles a un usuario
   */
  async assignUserRoles(
    userId: string,
    data: { roles: string[]; fecha_expiracion?: string },
  ) {
    try {
      const response = await apiClient.post(
        `/api/v1/identity/users/${userId}/asignar_rol/`,
        data,
      );
      return response.data;
    } catch (error) {
      console.error("Error assigning user roles:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Remover un rol de un usuario
   */
  async removeUserRole(userId: string, rolId: string) {
    try {
      const response = await apiClient.post(
        `/api/v1/identity/users/${userId}/remover_rol/`,
        { rol_id: rolId },
      );
      return response.data;
    } catch (error) {
      console.error("Error removing user role:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Asignar roles a un usuario (método alternativo)
   */
  async assignRoles(assignment: UserRoleAssignment) {
    try {
      const response = await apiClient.post(
        "/api/v1/identity/user-roles/asignar_multiple/",
        {
          usuario_ids: [assignment.user_id],
          rol_ids: assignment.role_ids || [],
          remove_existing: assignment.remove_existing || false,
        },
      );
      return response.data;
    } catch (error) {
      console.error("Error assigning roles:", error);
      throw new Error(getErrorMessage(error));
    }
  },
};

// Servicio para gestión de roles
export const rolesService = {
  /**
   * Obtener lista de roles
   */
  async getAll(params?: Record<string, unknown>) {
    try {
      const response = await apiClient.get("/api/v1/identity/roles/", { params });
      const roles = extractCollection(response.data);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return roles.map((role: any) => normalizeRole(role)); // extractCollection returns unknown[]; normalizeRole expects raw API shape
    } catch (error) {
      console.error("Error fetching roles:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Obtener rol por ID
   */
  async getById(id: string) {
    try {
      const response = await apiClient.get(`/api/v1/identity/roles/${id}/`);
      return normalizeRole(response.data);
    } catch (error) {
      console.error("Error fetching role:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Crear nuevo rol
   */
  async create(data: {
    nombre_rol: string;
    descripcion_rol: string;
    estado_rol: string;
  }) {
    try {
      const response = await apiClient.post("/api/v1/identity/roles/", data);
      return response.data;
    } catch (error) {
      console.error("Error creating role:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Actualizar rol existente
   */
  async update(
    id: string,
    data: Partial<{
      nombre_rol: string;
      descripcion_rol: string;
      estado_rol: string;
    }>,
  ) {
    try {
      const response = await apiClient.patch(`/api/v1/identity/roles/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating role:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Eliminar rol (soft delete)
   */
  async delete(id: string) {
    try {
      const response = await apiClient.delete(`/api/v1/identity/roles/${id}/`);
      return response.data;
    } catch (error) {
      console.error("Error deleting role:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Obtener roles activos
   */
  async getActive() {
    try {
      const response = await apiClient.get("/api/v1/identity/roles/activos/");

      // Manejar diferentes estructuras de respuesta del backend
      let data;
      if (response.data.success && response.data.data) {
        data = response.data.data.results || response.data.data;
      } else if (response.data.results) {
        data = response.data.results;
      } else if (Array.isArray(response.data.data)) {
        data = response.data.data;
      } else if (Array.isArray(response.data)) {
        data = response.data;
      } else {
        data = [];
      }

      const roles = Array.isArray(data) ? data : [];

      return { data: roles };
    } catch (error) {
      console.error("Error fetching active roles:", error);
      console.error("Error details:", error.response?.data);
      throw new Error(getErrorMessage(error));
    }
  },
};

// Servicio para gestión de permisos
export const permissionsService = {
  /**
   * Obtener lista de permisos
   */
  async getAll(params?: Record<string, unknown>) {
    try {
      const response = await apiClient.get("/api/v1/identity/permissions/", {
        params,
      });
      const data =
        response.data.data?.results ||
        response.data.results ||
        response.data.data ||
        response.data;
      const permissions = Array.isArray(data) ? data : [];

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return permissions.map((permission: any) => ({ // raw API response; shape mapped to Permission interface below
        id: permission.permiso_id || permission.id,
        nombre_permiso: permission.nombre_permiso,
        descripcion_permiso: permission.descripcion_permiso,
        estado_permiso: permission.estado_permiso,
        modulo: permission.modulo,
      }));
    } catch (error) {
      console.error("Error fetching permissions:", error);
      throw new Error(getErrorMessage(error));
    }
  },

  /**
   * Obtener permiso por ID
   */
  async getById(id: string) {
    try {
      const response = await apiClient.get(`/api/v1/identity/permissions/${id}/`);
      const permission = response.data;

      return {
        id: permission.permiso_id || permission.id,
        nombre_permiso: permission.nombre_permiso,
        descripcion_permiso: permission.descripcion_permiso,
        estado_permiso: permission.estado_permiso,
        modulo: permission.modulo,
      };
    } catch (error) {
      console.error("Error fetching permission:", error);
      throw new Error(getErrorMessage(error));
    }
  },
};

export default usersService;
