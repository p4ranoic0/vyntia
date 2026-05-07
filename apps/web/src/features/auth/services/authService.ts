/**
 * Servicio de autenticación que maneja la comunicación con la API del backend
 * Implementa enfoque híbrido: tokens en JSON + cookies generadas en frontend
 */

interface LoginCredentials {
  username: string;
  password: string;
}

interface User {
  usuario_id: string;
  username: string;
  nombres_usuario: string;
  apellidos_usuario: string;
  email: string;
  tipo_usuario: string;
  nivel_acceso: string;
  is_active: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
  es_admin_rrhh?: boolean;
  es_jefe?: boolean;
  empleado_id?: string | null;
  area_id?: string | null;
  requiere_cambio_password?: boolean;
  empleado?: {
    id: string | null;
    nombres: string | null;
    apellido_paterno: string | null;
    apellido_materno: string | null;
    numero_documento: string | null;
    ruta_fotografia: string | null;
  } | null;
  roles?: Array<{ id: string; nombre: string }>;
}

interface Role {
  rol_id?: string;
  id?: string;
  nombre_rol?: string;
  nombre?: string;
  descripcion_rol?: string;
  nivel_jerarquico?: number;
  es_rol_sistema?: boolean;
}

interface Permission {
  permiso_id: string;
  nombre_permiso: string;
  descripcion_permiso: string;
  modulo_id: string;
  tipo_permiso: string;
}

interface Module {
  modulo_id: string;
  nombre_modulo: string;
  descripcion_modulo: string;
  icono_modulo: string;
  ruta_modulo: string;
  orden_visualizacion: number;
}

interface AuthResponse {
  success: boolean;
  message: string;
  data?: {
    user: User;
    access: string; // Token de acceso JWT
    refresh: string; // Token de refresco JWT
    roles: Role[];
    permissions: Permission[];
    modules: Module[];
  };
  errors?: any;
}

interface UserMenuData {
  user: User;
  roles: Role[];
  permissions: Permission[];
  modules: Module[];
}

interface AuthPayload {
  user: User;
  access: string;
  refresh: string;
  roles?: Role[];
  permissions?: Permission[];
  modules?: Module[];
}

class AuthService {
  private baseURL = `${import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"}/api/v1`;
  private token: string | null = null;

  constructor() {
    // Verificar si hay token en localStorage al inicializar
    this.token = localStorage.getItem("access_token");
  }

  private normalizeEmpleado(raw: any): User["empleado"] | null {
    if (!raw) return null;
    return {
      id: raw.id ?? raw.empleado_id ?? null,
      nombres: raw.nombres ?? raw.nombres_empleado ?? null,
      apellido_paterno: raw.apellido_paterno ?? raw.ape_paterno ?? null,
      apellido_materno: raw.apellido_materno ?? raw.ape_materno ?? null,
      numero_documento: raw.numero_documento ?? raw.dni ?? null,
      ruta_fotografia: raw.ruta_fotografia ?? raw.foto ?? null,
    };
  }

  private normalizeUser(raw: any): User {
    const empleado = this.normalizeEmpleado(raw.empleado)
    return {
      usuario_id: raw.usuario_id ?? raw.id ?? raw.user_id ?? "",
      username: raw.username ?? "",
      nombres_usuario: raw.nombres_usuario ?? raw.nombres ?? "",
      apellidos_usuario: raw.apellidos_usuario ?? raw.apellidos ?? "",
      email: raw.email ?? "",
      tipo_usuario: raw.tipo_usuario ?? "",
      nivel_acceso: raw.nivel_acceso ?? "",
      is_active: raw.is_active ?? true,
      is_staff: raw.is_staff ?? raw.staff ?? false,
      is_superuser: raw.is_superuser ?? false,
      es_admin_rrhh: raw.es_admin_rrhh ?? false,
      es_jefe: raw.es_jefe ?? false,
      empleado_id: raw.empleado_id ?? empleado?.id ?? null,
      area_id: raw.area_id ?? raw.empleado?.area_id ?? null,
      requiere_cambio_password: raw.requiere_cambio_password,
      empleado,
      roles: raw.roles ?? [],
    };
  }

  private extractAuthPayload(raw: any): AuthPayload | null {
    if (!raw) return null;
    if (raw.success && raw.data) {
      const payload = raw.data;
      return {
        access: payload.access,
        refresh: payload.refresh,
        user: this.normalizeUser(payload.user),
        roles: payload.roles ?? [],
        permissions: payload.permissions ?? [],
        modules: payload.modules ?? [],
      };
    }
    if (raw.access && raw.refresh && raw.user) {
      return {
        access: raw.access,
        refresh: raw.refresh,
        user: this.normalizeUser(raw.user),
        roles: raw.roles ?? [],
        permissions: raw.permissions ?? [],
        modules: raw.modules ?? [],
      };
    }
    return null;
  }

  /**
   * Realiza el login del usuario
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseURL}/auth/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(credentials),
      });

      const data = await response.json();
      const payload = this.extractAuthPayload(data);

      if (response.ok && payload) {
        localStorage.setItem("access_token", payload.access);
        localStorage.setItem("refresh_token", payload.refresh);
        this.token = payload.access;

        const userData: UserMenuData = {
          user: payload.user,
          roles: payload.roles ?? [],
          permissions: payload.permissions ?? [],
          modules: payload.modules ?? [],
        };
        localStorage.setItem("user_data", JSON.stringify(userData));

        return {
          success: true,
          message: data.message || "Login exitoso",
          data: {
            user: payload.user,
            access: payload.access,
            refresh: payload.refresh,
            roles: payload.roles ?? [],
            permissions: payload.permissions ?? [],
            modules: payload.modules ?? [],
          },
        };
      }

      return {
        success: false,
        message: data?.message || data?.error || "Error en el login",
        errors: data?.errors,
      };
    } catch (error) {
      console.error("Error en login:", error);
      return {
        success: false,
        message: "Error de conexión con el servidor",
        errors: { network: "No se pudo conectar con el servidor" },
      };
    }
  }

  /**
   * Obtiene los datos del menú del usuario autenticado
   */
  async getUserMenuData(): Promise<UserMenuData | null> {
    // Verificar autenticación usando localStorage
    const accessToken = this.getToken();
    if (!accessToken) {
      return null;
    }

    try {
      const response = await fetch(`${this.baseURL}/auth/user-menu/`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        credentials: "include", // Importante para manejar cookies
      });

      if (response.ok) {
        const data = await response.json();
        return data.data;
      } else {
        console.error("Error al obtener datos del menú:", response.statusText);
        return null;
      }
    } catch (error) {
      console.error("Error al obtener datos del menú:", error);
      return null;
    }
  }

  /**
   * Verifica si el usuario tiene un permiso específico
   */
  hasPermission(permissionName: string, permissions: Permission[]): boolean {
    return permissions.some(
      (permission) => permission.nombre_permiso === permissionName,
    );
  }

  /**
   * Verifica si el usuario tiene un rol específico
   */
  hasRole(roleName: string, roles: Role[]): boolean {
    return roles.some((role) => role.nombre_rol === roleName);
  }

  /**
   * Filtra los módulos según los permisos del usuario
   */
  getAccessibleModules(modules: Module[], permissions: Permission[]): Module[] {
    return modules
      .filter((module) => {
        // Verificar si el usuario tiene al menos un permiso de lectura para este módulo
        return permissions.some(
          (permission) =>
            permission.modulo_id === module.modulo_id &&
            (permission.tipo_permiso === "leer" ||
              permission.tipo_permiso === "ejecutar"),
        );
      })
      .sort((a, b) => a.orden_visualizacion - b.orden_visualizacion);
  }

  /**
   * Cierra la sesión del usuario
   */
  async logout(): Promise<void> {
    try {
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        await fetch(`${this.baseURL}/auth/logout/`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${this.getToken()}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      }
    } catch (error) {
      console.error("Error al cerrar sesión:", error);
    } finally {
      // Limpiar datos locales
      this.token = null;
      localStorage.removeItem("user_data");
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  }

  /**
   * Verifica si el usuario está autenticado
   */
  isAuthenticated(): boolean {
    const userData = localStorage.getItem("user_data");
    const accessToken = localStorage.getItem("access_token");
    return userData !== null && accessToken !== null;
  }

  /**
   * Obtiene el token de acceso actual
   */
  getToken(): string | null {
    return localStorage.getItem("access_token") || this.token;
  }

  /**
   * Obtiene los datos del usuario desde localStorage
   */
  getUserData(): UserMenuData | null {
    const userData = localStorage.getItem("user_data");
    if (!userData) return null;
    try {
      const parsed = JSON.parse(userData);
      if (parsed?.user) {
        return {
          user: this.normalizeUser(parsed.user),
          roles: parsed.roles ?? [],
          permissions: parsed.permissions ?? [],
          modules: parsed.modules ?? [],
        };
      }
      if (parsed?.username || parsed?.usuario_id || parsed?.id) {
        return {
          user: this.normalizeUser(parsed),
          roles: [],
          permissions: [],
          modules: [],
        };
      }
      return null;
    } catch {
      return null;
    }
  }

  /**
   * Cambia la contraseña del usuario autenticado
   */
  async changePassword(oldPassword: string, newPassword: string, confirmPassword: string): Promise<{ success: boolean; message: string }> {
    const accessToken = this.getToken();
    if (!accessToken) {
      throw new Error('No autenticado');
    }

    const response = await fetch(`${this.baseURL}/auth/user-profile/change-password/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        old_password: oldPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      }),
    });

    const data = await response.json();

    if (response.ok && data.success) {
      // Actualizar user_data para reflejar que ya no requiere cambio
      const userData = this.getUserData();
      if (userData?.user) {
        userData.user.requiere_cambio_password = false;
        localStorage.setItem('user_data', JSON.stringify(userData));
      }
      return { success: true, message: data.message || 'Contraseña cambiada exitosamente' };
    } else {
      const errorMsg = data.message || data.errors?.old_password?.[0] || data.errors?.new_password?.[0] || 'Error al cambiar la contraseña';
      throw new Error(errorMsg);
    }
  }
}

// Exportar una instancia singleton del servicio
export const authService = new AuthService();
export type {
  AuthResponse,
  LoginCredentials,
  Module,
  Permission,
  Role,
  User,
  UserMenuData,
};
