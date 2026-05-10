import { apiClient } from "@/shared/api/api";
import {
  extractCollection,
  normalizeSecurityRole,
} from "@/shared/api/apiNormalizers";

// Interfaces para paginación
export interface PaginationMeta {
  current_page: number;
  total_pages: number;
  total_items: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
  next_page: number | null;
  previous_page: number | null;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    pagination: PaginationMeta;
  };
}

// Interfaces para el módulo de seguridad
export interface Role {
  id: string;
  nombre: string;
  descripcion?: string;
  is_active: boolean;
  permissions_count: number;
  users_count: number;
  permisos?: Permission[];
}

export interface Permission {
  id: string;
  nombre_permiso: string;
  descripcion_permiso?: string;
  modulo_id: string;
  modulo_nombre: string;
  tipo_permiso: string;
  estado_permiso: string;
  es_activo: boolean;
}

export interface Module {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
}

export interface RolePermission {
  id: string;
  rol_id: string;
  permiso_id: string;
  fecha_asignacion: string;
  asignado_por_usuario_id: string;
  rol_nombre: string;
  permiso_nombre: string;
  modulo_nombre: string;
  asignado_por_nombre: string;
}

// Interfaces para formularios
export interface RoleFormData {
  nombre: string;
  descripcion: string;
  is_active: boolean;
}

export interface PermissionFormData {
  nombre_permiso: string;
  descripcion_permiso: string;
  modulo_id: string;
  tipo_permiso: string;
  estado_permiso?: string;
}

export interface ModuleFormData {
  name: string;
  description: string;
}

export interface RolePermissionFormData {
  role: string;
  permission: string;
  granted: boolean;
}

// Servicio para gestión de roles
export const roleService = {
  async getAll(params?: Record<string, unknown>) {
    const response = await apiClient.getRoles(params);
    const roles = extractCollection(response.data);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return roles.map((role: any) => normalizeSecurityRole(role)); // extractCollection returns unknown[]; normalizeSecurityRole expects raw API shape
  },

  async getById(id: string) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await apiClient.get<any>(`/api/v1/identity/roles/${id}/`); // raw API response shape varies
    const role = normalizeSecurityRole(response.data);

    return {
      ...role,
      created_at: response.data?.created_at,
      updated_at: response.data?.updated_at,
    };
  },

  async create(data: RoleFormData) {
    // Mapear los datos del frontend al formato esperado por el backend
    const backendData = {
      nombre_rol: data.nombre,
      descripcion_rol: data.descripcion,
      estado_rol: data.is_active ? "activo" : "inactivo",
    };
    const response = await apiClient.createRol(backendData);
    return response.data;
  },

  async update(id: string, data: Partial<RoleFormData>) {
    // Mapear los datos del frontend al formato esperado por el backend
    const backendData: Record<string, string> = {};
    if (data.nombre !== undefined) backendData.nombre_rol = data.nombre;
    if (data.descripcion !== undefined)
      backendData.descripcion_rol = data.descripcion;
    if (data.is_active !== undefined)
      backendData.estado_rol = data.is_active ? "activo" : "inactivo";

    const response = await apiClient.updateRol(id, backendData);
    return response.data;
  },

  async delete(id: string) {
    const response = await apiClient.deleteRol(id);
    return response.data;
  },
};

// Servicio para gestión de permisos
export const permissionService = {
  async getAll(params?: Record<string, unknown>): Promise<Permission[]> {
    const response = await apiClient.getPermisos(params);
    // El backend devuelve los datos en data.data.results
    const data =
      response.data.data?.results ||
      response.data.results ||
      response.data.data ||
      response.data;
    return Array.isArray(data) ? data : [];
  },

  async getAllPaginated(
    page: number = 1,
    pageSize: number = 20,
    search?: string,
  ): Promise<PaginatedResponse<Permission>> {
    const params: Record<string, unknown> = {
      page,
      page_size: pageSize,
    };

    if (search) {
      params.search = search;
    }

    const response = await apiClient.getPermisos(params);

    // Extraer datos y metadatos de paginación
    const data =
      response.data.data?.results ||
      response.data.results ||
      response.data.data ||
      response.data;
    const pagination = response.data.meta?.pagination || {
      current_page: page,
      total_pages: 1,
      total_items: Array.isArray(data) ? data.length : 0,
      page_size: pageSize,
      has_next: false,
      has_previous: false,
      next_page: null,
      previous_page: null,
    };

    return {
      data: Array.isArray(data) ? data : [],
      meta: { pagination },
    };
  },

  async getById(id: string) {
    const response = await apiClient.get<Permission>(
      `/api/v1/identity/permissions/${id}/`,
    );
    return response.data;
  },

  async create(data: PermissionFormData) {
    const response = await apiClient.createPermiso(data);
    return response.data;
  },

  async update(id: string, data: Partial<PermissionFormData>) {
    const response = await apiClient.updatePermiso(id, data);
    return response.data;
  },

  async delete(id: string) {
    const response = await apiClient.deletePermiso(id);
    return response.data;
  },
};

// Servicio para gestión de módulos
export const moduleService = {
  async getAll(params?: Record<string, unknown>) {
    const response = await apiClient.get<Module[]>(
      "/api/v1/identity/modules/",
      params,
    );
    return response.data.results || response.data;
  },

  async getById(id: string) {
    const response = await apiClient.get<Module>(`/api/v1/identity/modules/${id}/`);
    return response.data;
  },

  async create(data: ModuleFormData) {
    const response = await apiClient.post<Module>(
      "/api/v1/identity/modules/",
      data,
    );
    return response.data;
  },

  async update(id: string, data: Partial<ModuleFormData>) {
    const response = await apiClient.patch<Module>(
      `/api/v1/identity/modules/${id}/`,
      data,
    );
    return response.data;
  },

  async delete(id: string) {
    const response = await apiClient.delete(`/api/v1/identity/modules/${id}/`);
    return response.data;
  },
};

// Servicio para gestión de permisos de roles
export const rolePermissionService = {
  async getAll(params?: Record<string, unknown>) {
    const response = await apiClient.get<RolePermission[]>(
      "/api/v1/identity/role-permissions/",
      params,
    );
    return response.data.results || response.data;
  },

  async getByRoleId(roleId: string) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await apiClient.get<any>( // raw APIResponse envelope; shape varies
      `/api/v1/identity/role-permissions/por_rol/?rol_id=${roleId}`,
    );
    // El backend devuelve los datos en response.data.data cuando usa APIResponse.success
    return response.data.data || response.data;
  },

  async create(data: RolePermissionFormData) {
    // Convertir el formato del frontend al formato esperado por el backend
    // Django espera los IDs de las ForeignKeys directamente
    const backendData = {
      rol_id: data.role,
      permiso_id: data.permission,
    };

    // Crear nueva asignación de permiso a rol

    const response = await apiClient.post<RolePermission>(
      "/api/v1/identity/role-permissions/",
      backendData,
    );
    return response.data;
  },

  async update(id: string, data: Partial<RolePermissionFormData>) {
    // Convertir el formato del frontend al formato esperado por el backend
    // Django espera los IDs de las ForeignKeys directamente
    const backendData: Record<string, string> = {};
    if (data.role !== undefined) backendData.rol_id = data.role;
    if (data.permission !== undefined) backendData.permiso_id = data.permission;
    const response = await apiClient.patch<RolePermission>(
      `/api/v1/identity/role-permissions/${id}/`,
      backendData,
    );
    return response.data;
  },

  async delete(id: string) {
    const response = await apiClient.delete(`/api/v1/identity/role-permissions/${id}/`);
    return response.data;
  },

  async assignPermissionsToRole(roleId: string, permissionIds: string[]) {
    const promises = permissionIds.map(async (permissionId) => {
      try {
        return await this.create({
          role: roleId,
          permission: permissionId,
          granted: true,
        });
      } catch (error) {
        // Si el error es 409 (Conflict), significa que ya existe la relación
        const err = error as { response?: { status?: number } }
        if (err.response?.status === 409) {
          // Permiso ya asignado, continuar sin error
          return null; // Retornar null para indicar que se saltó
        }
        throw error; // Re-lanzar otros errores
      }
    });
    const results = await Promise.all(promises);
    return results.filter((result) => result !== null); // Filtrar los null
  },

  async removePermissionsFromRole(roleId: string, permissionIds: string[]) {
    // Primero obtener los role-permissions existentes para este rol
    const existingRolePermissions = await this.getByRoleId(roleId);

    // Filtrar los que coinciden con los permisos a remover
    const toDelete =
      existingRolePermissions.results?.filter((rp: RolePermission) =>
        permissionIds.includes(rp.permiso_id),
      ) || [];

    // Eliminar permisos seleccionados

    // Eliminar cada uno usando el id del role-permission
    const promises = toDelete.map((rp: RolePermission) =>
      this.delete(rp.id),
    );
    return await Promise.all(promises);
  },

  // Método alias para compatibilidad con RolePermissionsPage
  async getByRole(roleId: string) {
    return this.getByRoleId(roleId);
  },

  // Método para actualizar permisos de un rol de manera masiva
  async updateRolePermissions(roleId: string, permissionIds: string[]) {
    try {
      // Actualizar permisos de rol de manera masiva

      // Obtener permisos actuales del rol
      const currentRolePermissions = await this.getByRoleId(roleId);
      const currentPermissionIds =
        currentRolePermissions.results?.map(
          (rp: RolePermission) => rp.permiso_id,
        ) || [];

      // Determinar permisos a agregar y remover
      const permissionsToAdd = permissionIds.filter(
        (id) => !currentPermissionIds.includes(id),
      );
      const permissionsToRemove = currentPermissionIds.filter(
        (id) => !permissionIds.includes(id),
      );

      // Ejecutar operaciones en paralelo
      const operations = [];

      if (permissionsToAdd.length > 0) {
        operations.push(this.assignPermissionsToRole(roleId, permissionsToAdd));
      }

      if (permissionsToRemove.length > 0) {
        operations.push(
          this.removePermissionsFromRole(roleId, permissionsToRemove),
        );
      }

      await Promise.all(operations);

      // Retornar los permisos actualizados
      return await this.getByRoleId(roleId);
    } catch (error) {
      console.error("Error updating role permissions:", error);
      throw error;
    }
  },
};

// Servicio combinado para operaciones complejas
export const securityService = {
  // Obtener resumen completo de seguridad
  getSecuritySummary: async () => {
    const [roles, permissions, modules] = await Promise.all([
      roleService.getAll(),
      permissionService.getAll(),
      moduleService.getAll(),
    ]);

    return {
      roles,
      permissions,
      modules,
      totalRoles: roles.length,
      totalPermissions: permissions.length,
      totalModules: modules.length,
      activeRoles: roles.filter((r) => r.is_active).length,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      activeModules: modules.filter((m: any) => m.activo ?? m.is_active).length, // Module has no `activo` in type; backend may return it
    };
  },

  // Obtener estructura completa de permisos por módulo
  getPermissionsByModule: async () => {
    const [permissions, modules] = await Promise.all([
      permissionService.getAll(),
      moduleService.getAll(),
    ]);

    return modules.map((module) => ({
      ...module,
      permissions: permissions.filter((p) => p.modulo_nombre === module.nombre),
    }));
  },
};
