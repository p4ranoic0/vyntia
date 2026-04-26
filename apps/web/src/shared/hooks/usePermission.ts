/**
 * usePermission Hook - SHARED
 *
 * Hook que verifica permisos del usuario actual.
 *
 * Uso:
 * const { hasPermission, hasRole } = usePermission()
 * if (hasPermission('empleado.delete')) { ... }
 * if (hasRole('admin')) { ... }
 */

import { useAuth } from "@/features/auth";

interface PermissionCheckOptions {
  requireAll?: boolean; // true = ALL permissions required, false = ANY permission
}

export const usePermission = () => {
  const { user } = useAuth();

  const hasPermission = (
    permission: string,
    options: PermissionCheckOptions = {},
  ) => {
    if (!user?.permissions) return false;

    const { requireAll = false } = options;
    const requiredPerms = permission.split(",").map((p) => p.trim());

    if (requireAll) {
      return requiredPerms.every((p) => user.permissions.includes(p));
    }

    return requiredPerms.some((p) => user.permissions.includes(p));
  };

  const hasRole = (role: string | string[]) => {
    if (!user?.roles) return false;

    const roles = Array.isArray(role) ? role : [role];
    return roles.some((r) => user.roles.includes(r));
  };

  const hasAnyPermission = (...permissions: string[]) => {
    if (!user?.permissions) return false;
    return permissions.some((p) => user.permissions.includes(p));
  };

  const hasAllPermissions = (...permissions: string[]) => {
    if (!user?.permissions) return false;
    return permissions.every((p) => user.permissions.includes(p));
  };

  return {
    hasPermission,
    hasRole,
    hasAnyPermission,
    hasAllPermissions,
  };
};
