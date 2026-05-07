import { apiClient } from "@/shared/api/api";
import { authService } from "@/features/auth/services/authService";

export interface MenuItem {
  id: string;
  title: string;
  icon: string;
  path?: string;
  order: number;
  submenu?: MenuItem[];
}

export interface MenuResponse {
  menu: MenuItem[];
}

// Cache del menú para evitar llamadas innecesarias al backend
let menuCache: MenuItem[] | null = null;
let cacheTimestamp: number | null = null;
let cacheUserKey: string | null = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutos en milisegundos

/**
 * Servicio para gestionar el menú dinámico del usuario
 */
export const menuService = {
  /**
   * Obtener el menú del usuario basado en sus permisos
   * Utiliza caché local para optimizar el rendimiento
   */
  async getUserMenu(forceRefresh: boolean = false): Promise<MenuItem[]> {
    const userData = authService.getUserData();
    const user = userData?.user;
    const userKey = user
      ? `${user.usuario_id}:${user.tipo_usuario ?? ""}`
      : "anonymous";

    if (cacheUserKey && cacheUserKey !== userKey) {
      this.clearCache();
    }

    if (forceRefresh) {
      this.clearCache();
    }

    // Verificar si tenemos caché válido
    if (menuCache && cacheTimestamp) {
      const now = Date.now();
      if (now - cacheTimestamp < CACHE_DURATION) {
        return this.filterMenuByPermissions(menuCache);
      }
    }

    try {
      const response = await apiClient.get<any>("/api/v1/auth/menu/");

      let menuData: MenuItem[] = [];

      // Manejar diferentes estructuras de respuesta del backend
      if (
        response.data &&
        response.data.success === true &&
        response.data.data
      ) {
        menuData = response.data.data.menu || response.data.data;
      } else if (Array.isArray(response.data)) {
        menuData = response.data;
      } else if (
        response.data &&
        response.data.menu &&
        Array.isArray(response.data.menu)
      ) {
        menuData = response.data.menu;
      } else if (
        response.data &&
        response.data.data &&
        response.data.data.menu
      ) {
        menuData = response.data.data.menu;
      }

      if (!menuData || menuData.length === 0) {
        return [];
      }

      // Actualizar caché
      menuCache = menuData;
      cacheTimestamp = Date.now();
      cacheUserKey = userKey;

      return this.filterMenuByPermissions(menuData);
    } catch (error) {
      // Si hay caché disponible, usarlo como fallback
      if (menuCache && menuCache.length > 0) {
        return this.filterMenuByPermissions(menuCache);
      }
      throw error;
    }
  },

  /**
   * Filtrar elementos del menú basado en permisos y roles del usuario
   */
  filterMenuByPermissions(menu: MenuItem[]): MenuItem[] {
    const userData = authService.getUserData();

    if (!userData || !userData.user) {
      return [];
    }

    if (userData.user && userData.user.usuario_id) {
      return menu;
    }

    return [];
  },

  /**
   * Filtrar recursivamente los elementos del menú
   */
  filterMenuItems(
    items: MenuItem[],
    userPermissions: string[],
    userRoles: string[],
  ): MenuItem[] {
    return items.filter((item) => {
      if (item.requiredPermissions && item.requiredPermissions.length > 0) {
        const hasRequiredPermission = item.requiredPermissions.some(
          (permission) => userPermissions.includes(permission),
        );
        if (!hasRequiredPermission) {
          return false;
        }
      }

      if (item.requiredRoles && item.requiredRoles.length > 0) {
        const hasRequiredRole = item.requiredRoles.some((role) =>
          userRoles.includes(role),
        );
        if (!hasRequiredRole) {
          return false;
        }
      }

      if (item.submenu && item.submenu.length > 0) {
        item.submenu = this.filterMenuItems(
          item.submenu,
          userPermissions,
          userRoles,
        );
      }

      return true;
    });
  },

  /**
   * Devuelve un menú básico por defecto
   */
  getBasicMenu(): MenuItem[] {
    return [
      {
        id: "dashboard",
        title: "Dashboard",
        icon: "dashboard",
        path: "/dashboard",
        order: 1,
      },
      {
        id: "profile",
        title: "Mi Perfil",
        icon: "person",
        path: "/profile",
        order: 2,
      },
    ];
  },

  /**
   * Limpiar caché del menú
   */
  clearCache(): void {
    menuCache = null;
    cacheTimestamp = null;
    cacheUserKey = null;
  },

  /**
   * Verificar si el caché es válido
   */
  isCacheValid(): boolean {
    if (!menuCache || !cacheTimestamp) {
      return false;
    }
    const now = Date.now();
    return now - cacheTimestamp < CACHE_DURATION;
  },
};
