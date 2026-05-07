import { authService, Module, Permission, Role, User } from '@/features/auth/services/authService'
import { menuService } from '@/services/menuService'
import React, { useEffect, useState } from 'react'
import { AuthContext } from './AuthContextInstance'
import { AuthContextType } from './AuthContextType'

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [roles, setRoles] = useState<Role[]>([])
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [modules, setModules] = useState<Module[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const isAuthenticated = !!user

  useEffect(() => {
    // Verificar si el usuario está autenticado
    if (authService.isAuthenticated()) {
      const userData = authService.getUserData()
      if (userData) {
        setUser(userData.user)
        setRoles(userData.roles || [])
        setPermissions(userData.permissions || [])
        setModules(userData.modules || [])
      } else {
        // Limpiar datos si están corruptos
        authService.logout()
      }
    }

    setIsLoading(false)
  }, [])

  const login = async (username: string, password: string) => {
    setIsLoading(true)
    try {
      const response = await authService.login({ username, password })
      
      if (response.success && response.data) {
        menuService.clearCache()
        setUser(response.data.user)
        // Los roles vienen dentro de user.roles o en data.roles (según el formato)
        const loginRoles = response.data.user?.roles || response.data.roles || []
        setRoles(loginRoles)
        setPermissions(response.data.permissions || [])
        setModules(response.data.modules || [])

        return response.data.user
      } else {
        throw new Error(response.message || 'Error en el login')
      }
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Error durante logout:', error)
    } finally {
      menuService.clearCache()
      setUser(null)
      setRoles([])
      setPermissions([])
      setModules([])
    }
  }

  const forgotPassword = async (email: string) => {
    try {
      // TODO: Implementar en authService cuando esté disponible en el backend
      throw new Error('Función no implementada aún')
    } catch (error) {
      console.error('Forgot password failed:', error)
      throw error
    }
  }

  const resetPassword = async (token: string, newPassword: string) => {
    try {
      // TODO: Implementar en authService cuando esté disponible en el backend
      throw new Error('Función no implementada aún')
    } catch (error) {
      console.error('Reset password failed:', error)
      throw error
    }
  }

  const changePassword = async (oldPassword: string, newPassword: string, confirmPassword: string) => {
    try {
      await authService.changePassword(oldPassword, newPassword, confirmPassword)
      // Actualizar el user en el estado para reflejar que ya no requiere cambio
      if (user?.requiere_cambio_password) {
        setUser({ ...user, requiere_cambio_password: false })
      }
    } catch (error) {
      console.error('Change password failed:', error)
      throw error
    }
  }

  // Funciones de verificación de roles y permisos
  const hasRole = (roleName: string): boolean => {
    if (!roles || !Array.isArray(roles)) return false
    return roles.some(role => (role.nombre_rol || role.nombre) === roleName)
  }

  const hasPermission = (permissionName: string): boolean => {
    if (!permissions || !Array.isArray(permissions)) return false
    return permissions.some(p => p.nombre_permiso === permissionName)
  }

  const hasAnyRole = (roleNames: string[]): boolean => {
    if (!roles || !Array.isArray(roles)) return false
    const userRoleNames = roles.map(r => r.nombre_rol || r.nombre || '')
    return roleNames.some(rn => userRoleNames.includes(rn))
  }

  const hasAnyPermission = (permissionNames: string[]): boolean => {
    if (!permissions || !Array.isArray(permissions)) return false
    const userPermNames = permissions.map(p => p.nombre_permiso)
    return permissionNames.some(pn => userPermNames.includes(pn))
  }

  const hasAllRoles = (roleNames: string[]): boolean => {
    if (!roles || !Array.isArray(roles)) return false
    const userRoleNames = roles.map(r => r.nombre_rol || r.nombre || '')
    return roleNames.every(rn => userRoleNames.includes(rn))
  }

  const hasAllPermissions = (permissionNames: string[]): boolean => {
    if (!permissions || !Array.isArray(permissions)) return false
    const userPermNames = permissions.map(p => p.nombre_permiso)
    return permissionNames.every(pn => userPermNames.includes(pn))
  }

  // Helpers para verificar tipo de usuario
  const isAdmin = (): boolean => {
    if (!user) return false
    return hasAnyRole(['Super Administrador', 'Administrador RRHH'])
  }

  const isRRHH = (): boolean => {
    if (!user) return false
    return hasAnyRole(['Super Administrador', 'Administrador RRHH', 'Analista RRHH'])
  }

  const isAdminOrRRHH = (): boolean => {
    return isAdmin() || isRRHH()
  }

  const isJefe = (): boolean => {
    if (!user) return false
    return hasAnyRole(['Jefe de Area'])
  }

  const getAccessibleModules = (): Module[] => {
    return modules // Devolver todos los módulos
  }

  const getUserRoles = (): string[] => {
    if (!roles || !Array.isArray(roles)) {
      return []
    }
    return roles.map(role => role.nombre_rol || role.nombre || '')
  }

  const getUserPermissions = (): string[] => {
    if (!permissions || !Array.isArray(permissions)) {
      return []
    }
    return permissions.map(permission => permission.nombre_permiso)
  }

  // Actualizar información del usuario (incluyendo roles y permisos)
  const updateUserInfo = (updatedUser: User) => {
    menuService.clearCache()
    setUser(updatedUser)
    // Actualizar también en el servicio de autenticación
    const currentData = authService.getUserData()
    if (currentData) {
      const updatedData = {
        ...currentData,
        user: updatedUser
      }
      // El servicio maneja la persistencia internamente
      localStorage.setItem('user_data', JSON.stringify(updatedData))
    }
  }

  const value: AuthContextType = {
    user,
    roles,
    permissions,
    modules,
    isAuthenticated,
    isLoading,
    login,
    logout,
    forgotPassword,
    resetPassword,
    changePassword,
    updateUserInfo,
    hasRole,
    hasPermission,
    hasAnyRole,
    hasAnyPermission,
    hasAllRoles,
    hasAllPermissions,
    getAccessibleModules,
    getUserRoles,
    getUserPermissions,
    isAdmin,
    isRRHH,
    isAdminOrRRHH,
    isJefe,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
