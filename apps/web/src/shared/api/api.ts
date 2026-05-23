import axios, { AxiosError, AxiosInstance, AxiosResponse } from "axios";

import { decodeJwtClaims } from "@/shared/tenant/jwtClaims";
import { resolveTenantFromHost } from "@/shared/tenant/tenantContext";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

// Mock mode for development when backend is not available
const MOCK_MODE = false; // Conectar directamente con el backend

/**
 * Returns true if the JWT's tenant_slug claim matches the current host's
 * tenant subdomain — or if the token has no tenant claim (legacy/admin/exchange).
 * Used by the request interceptor to defend against stale tokens after
 * cross-subdomain hops.
 */
function isTokenForCurrentTenant(token: string): boolean {
  const claims = decodeJwtClaims(token);
  // Token without tenant_slug claim (legacy/admin/exchange tokens) is permissive
  if (!claims?.tenant_slug) return true;
  const host = resolveTenantFromHost(globalThis.location.host);
  // On a tenant subdomain, claim must match
  if (host.type === "tenant") {
    return claims.tenant_slug === host.slug;
  }
  // On reserved hosts (admin/app/etc), tenant tokens are not relevant — they shouldn't be sent
  // but we don't reject (legacy compatibility)
  return true;
}

export interface Role {
  id: string;
  nombre: string;
  descripcion: string;
  estado: string;
}

export interface Permission {
  id: string;
  nombre: string;
  descripcion: string;
  modulo: string;
  estado: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  nombres_usuario?: string;
  apellidos_usuario?: string;
  requiere_cambio_password?: boolean;
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
  roles?: Role[];
  permisos?: Permission[];
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface ApiResponse<T> {
  results?: T[];
  count?: number;
  next?: string | null;
  previous?: string | null;
  data?: T;
}

// Mock data for development
const mockUser: User = {
  id: "1",
  username: "admin",
  email: "admin@company.com",
  is_active: true,
  nombres_usuario: "Admin",
  apellidos_usuario: "User",
  requiere_cambio_password: false, // Por defecto no requiere cambio de contraseña
  empleado: {
    id: "1",
    nombres: "Admin",
    ape_paterno: "User",
    ape_materno: "",
    dni: "12345678",
    area: {
      id: "1",
      organo: "Recursos Humanos",
      siglas: "RH",
    },
  },
  roles: [
    {
      id: "1",
      nombre: "Administrador",
      descripcion: "Acceso completo al sistema",
      estado: "activo",
    },
  ],
  permisos: [
    {
      id: "1",
      nombre: "ver_dashboard",
      descripcion: "Ver dashboard principal",
      modulo: "dashboard",
      estado: "activo",
    },
    {
      id: "2",
      nombre: "gestionar_usuarios",
      descripcion: "Gestionar usuarios del sistema",
      modulo: "usuarios",
      estado: "activo",
    },
  ],
};

const mockAuthResponse: AuthResponse = {
  access: "mock-access-token",
  refresh: "mock-refresh-token",
  user: mockUser,
};

class ApiClient {
  private readonly axiosInstance: AxiosInstance;

  constructor(baseURL: string) {
    // Crear instancia de Axios con soporte para cookies
    this.axiosInstance = axios.create({
      baseURL,
      timeout: 10000,
      withCredentials: true, // Importante para enviar cookies
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Configurar interceptores
    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Interceptor de request - agregar token de autorización automáticamente
    this.axiosInstance.interceptors.request.use(
      (config) => {
        // Obtener token del localStorage
        const token = localStorage.getItem("access_token");

        // Si existe token y no es una petición de login, agregar header de autorización
        if (token && !config.url?.includes("/auth/login/")) {
          if (isTokenForCurrentTenant(token)) {
            config.headers.Authorization = `Bearer ${token}`;
          } else {
            // Stale token from a different tenant subdomain — clear and let 401 path redirect
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
          }
        }

        // Si el body es FormData, eliminar Content-Type para que Axios
        // establezca multipart/form-data con el boundary correcto
        if (config.data instanceof FormData) {
          delete config.headers["Content-Type"];
        }

        return config;
      },
      (error) => {
        throw error;
      },
    );

    // Interceptor de response - manejar errores de autenticación
    this.axiosInstance.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error: AxiosError) => {
        // Si el error es 401, el token ha expirado o es inválido
        if (error.response?.status === 401) {
          // Limpiar datos locales y redirigir al login
          this.handleAuthenticationError();
        }

        throw error;
      },
    );
  }

  // Manejar errores de autenticación
  private handleAuthenticationError(): void {
    // Limpiar datos del usuario del localStorage
    localStorage.removeItem("user_data");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    // Solo redirigir si no estamos ya en la página de login
    if (globalThis.location.pathname !== "/login") {
      globalThis.location.href = "/login";
    }
  }

  // Métodos de autenticación
  async login(username: string, password: string): Promise<AuthResponse> {
    if (MOCK_MODE) {
      return mockAuthResponse;
    }

    try {
      const response = await this.axiosInstance.post("/api/v1/auth/login/", {
        username,
        password,
      });

      const authData = response.data;

      let payload = null;
      if (authData?.data?.access && authData?.data?.refresh) {
        payload = authData.data;
      } else if (authData?.access && authData?.refresh) {
        payload = authData;
      }

      if (payload) {
        localStorage.setItem("access_token", payload.access);
        localStorage.setItem("refresh_token", payload.refresh);
        localStorage.setItem(
          "user_data",
          JSON.stringify({
            user: payload.user,
            roles: payload.roles || [],
            permissions: payload.permissions || [],
            modules: payload.modules || [],
          }),
        );
        return payload;
      }

      throw new Error("Respuesta de login inválida");
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    }
  }

  async logout(): Promise<void> {
    try {
      // Llamar al endpoint de logout para limpiar las cookies del servidor
      await this.axiosInstance.post("/api/v1/auth/logout/");
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      // Limpiar datos locales
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user_data");
    }
  }

  async forgotPassword(email: string): Promise<{ message: string }> {
    if (MOCK_MODE) {
      return { message: "Password reset email sent successfully" };
    }

    try {
      const response = await this.axiosInstance.post(
        "/api/v1/auth/forgot-password/",
        {
          email,
        },
      );
      return response.data;
    } catch (error) {
      console.error("Forgot password error:", error);
      throw error;
    }
  }

  async resetPassword(
    token: string,
    newPassword: string,
  ): Promise<{ message: string }> {
    if (MOCK_MODE) {
      return { message: "Password reset successfully" };
    }

    try {
      const response = await this.axiosInstance.post(
        "/api/v1/auth/reset-password/",
        {
          token,
          new_password: newPassword,
        },
      );
      return response.data;
    } catch (error) {
      console.error("Reset password error:", error);
      throw error;
    }
  }

  async changePassword(
    oldPassword: string,
    newPassword: string,
    confirmPassword: string,
  ): Promise<{ message: string }> {
    if (MOCK_MODE) {
      return { message: "Password changed successfully" };
    }

    try {
      const response = await this.axiosInstance.post(
        "/api/v1/auth/change-password/",
        {
          old_password: oldPassword,
          new_password: newPassword,
          confirm_password: confirmPassword,
        },
      );
      return response.data;
    } catch (error) {
      console.error("Change password error:", error);
      throw error;
    }
  }

  // Verificar salud del backend
  async checkBackendHealth(): Promise<boolean> {
    try {
      await this.axiosInstance.get("/health/");
      return true;
    } catch {
      return false;
    }
  }

  // Métodos HTTP genéricos simplificados
  async get<T>(
    endpoint: string,
    params?: Record<string, any>,
  ): Promise<AxiosResponse<T>> {
    return this.axiosInstance.get(endpoint, { params });
  }

  async post<T>(endpoint: string, data?: any): Promise<AxiosResponse<T>> {
    return this.axiosInstance.post(endpoint, data);
  }

  async put<T>(endpoint: string, data?: any): Promise<AxiosResponse<T>> {
    return this.axiosInstance.put(endpoint, data);
  }

  async patch<T>(endpoint: string, data?: any): Promise<AxiosResponse<T>> {
    return this.axiosInstance.patch(endpoint, data);
  }

  async delete<T>(endpoint: string): Promise<AxiosResponse<T>> {
    return this.axiosInstance.delete(endpoint);
  }

  async getBlob(
    endpoint: string,
    params?: Record<string, any>,
  ): Promise<AxiosResponse<Blob>> {
    return this.axiosInstance.get(endpoint, {
      params,
      responseType: "blob",
    });
  }

  // Métodos específicos del dominio (simplificados)
  async getEmpleados(params?: Record<string, any>) {
    try {
      const response = await this.get("/api/v1/employees/", params);

      // El backend devuelve: { success, message, data: [...], meta: { pagination: {...} } }
      const rawData = response.data;
      const employees = Array.isArray(rawData?.data) ? rawData.data : [];
      const pagination = rawData?.meta?.pagination || {};

      return {
        results: employees,
        count: pagination.total_items || employees.length,
        currentPage: pagination.current_page || 1,
        totalPages: pagination.total_pages || 1,
        pageSize: pagination.page_size || employees.length,
        hasNext: pagination.has_next || false,
        hasPrevious: pagination.has_previous || false,
      };
    } catch (error) {
      console.error("Error fetching employees:", error);
      throw error;
    }
  }

  async getEmpleadoDetail(id: string) {
    const response = await this.get(`/api/v1/employees/${id}/`);
    return response.data?.data || response.data;
  }

  async createEmpleado(data: any) {
    return this.post("/api/v1/employees/", data);
  }

  async updateEmpleado(id: string, data: any) {
    return this.patch(`/api/v1/employees/${id}/`, data);
  }

  async deleteEmpleado(id: string) {
    return this.delete(`/api/v1/employees/${id}/`);
  }

  // Áreas
  async getAreas(params?: Record<string, any>) {
    return this.get("/api/v1/organization/departments/", params);
  }

  async createArea(data: any) {
    return this.post("/api/v1/organization/departments/", data);
  }

  async updateArea(id: string, data: any) {
    return this.patch(`/api/v1/organization/departments/${id}/`, data);
  }

  async deleteArea(id: string) {
    return this.delete(`/api/v1/organization/departments/${id}/`);
  }

  // Usuarios
  async getUsuarios(params?: Record<string, any>) {
    return this.get("/api/v1/identity/users/", params);
  }

  async createUsuario(data: any) {
    return this.post("/api/v1/identity/users/", data);
  }

  async updateUsuario(id: string, data: any) {
    return this.patch(`/api/v1/identity/users/${id}/`, data);
  }

  async deleteUsuario(id: string) {
    return this.delete(`/api/v1/identity/users/${id}/`);
  }

  // Roles
  async getRoles(params?: Record<string, any>) {
    return this.get("/api/v1/identity/roles/", params);
  }

  async createRol(data: any) {
    return this.post("/api/v1/identity/roles/", data);
  }

  async updateRol(id: string, data: any) {
    return this.patch(`/api/v1/identity/roles/${id}/`, data);
  }

  async deleteRol(id: string) {
    return this.delete(`/api/v1/identity/roles/${id}/`);
  }

  // Permisos
  async getPermisos(params?: Record<string, any>) {
    return this.get("/api/v1/identity/permissions/", params);
  }

  async createPermiso(data: any) {
    return this.post("/api/v1/identity/permissions/", data);
  }

  async updatePermiso(id: string, data: any) {
    return this.patch(`/api/v1/identity/permissions/${id}/`, data);
  }

  async deletePermiso(id: string) {
    return this.delete(`/api/v1/identity/permissions/${id}/`);
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
