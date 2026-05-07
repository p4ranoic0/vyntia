import { Module, Permission, Role, User } from "@/features/auth/services/authService";

/**
 * Tipo de datos para el contexto de autenticación
 */
export interface AuthContextType {
  user: User | null;
  roles: Role[];
  permissions: Permission[];
  modules: Module[];
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  forgotPassword: (email: string) => Promise<{ message: string }>;
  resetPassword: (
    token: string,
    newPassword: string,
  ) => Promise<{ message: string }>;
  changePassword: (
    oldPassword: string,
    newPassword: string,
    confirmPassword: string,
  ) => Promise<{ message: string }>;
  // Funciones de utilidad para roles y permisos
  hasRole: (roleName: string) => boolean;
  hasPermission: (permissionName: string) => boolean;
  hasAnyRole: (roleNames: string[]) => boolean;
  hasAnyPermission: (permissionNames: string[]) => boolean;
  hasAllRoles: (roleNames: string[]) => boolean;
  hasAllPermissions: (permissionNames: string[]) => boolean;
  getAccessibleModules: () => Module[];
  getUserRoles: () => string[];
  getUserPermissions: () => string[];
  updateUserInfo: (updatedUser: User) => void;
  // Helpers de tipo de usuario
  isAdmin: () => boolean;
  isRRHH: () => boolean;
  isAdminOrRRHH: () => boolean;
  isJefe: () => boolean;
}
