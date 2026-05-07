import { useState, useEffect } from 'react'
import { authService, Module } from '@/features/auth/services/authService'
import { useAuth } from './useAuth'
import { useLoading } from '@/shared/components'

// Interfaz para compatibilidad con el componente Sidebar
interface MenuItem {
  id: string
  name: string
  title: string
  icon: string
  path?: string
  href?: string
  order: number
  children?: MenuItem[]
  subItems?: MenuItem[]
  submenu?: MenuItem[]
}

/**
 * Hook personalizado para gestionar el menú dinámico del usuario
 * Incluye estados de loading mejorados y manejo de errores
 */
export const useMenu = () => {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const { isLoading, startLoading, stopLoading } = useLoading(true)
  const [error, setError] = useState<string | null>(null)
  const { isAuthenticated, user, modules, permissions } = useAuth()

  /**
   * Convierte módulos del authService a formato MenuItem para compatibilidad
   */
  const convertModulesToMenuItems = (modules: Module[]): MenuItem[] => {
    return modules.map(module => ({
      id: `modulo-${module.modulo_id}`,
      name: module.nombre_modulo,
      title: module.nombre_modulo,
      icon: module.icono_modulo || 'dashboard',
      path: module.ruta_modulo || `/${module.nombre_modulo.toLowerCase()}`,
      href: module.ruta_modulo || `/${module.nombre_modulo.toLowerCase()}`,
      order: module.orden_visualizacion,
      children: [],
      subItems: [],
      submenu: []
    })).sort((a, b) => a.order - b.order)
  }

  /**
   * Función para cargar el menú desde el contexto de autenticación
   */
  const loadMenu = async () => {
    console.log('🎯 useMenu: Iniciando loadMenu')
    console.log('🔐 useMenu: isAuthenticated:', isAuthenticated)
    console.log('👤 useMenu: user:', user)
    console.log('📋 useMenu: modules:', modules)
    
    if (!isAuthenticated || !user) {
      console.log('❌ useMenu: Usuario no autenticado, limpiando menú')
      setMenuItems([])
      stopLoading()
      return
    }

    try {
      console.log('⏳ useMenu: Iniciando carga del menú')
      startLoading()
      setError(null)
      
      // Obtener módulos accesibles desde el servicio de autenticación
      const accessibleModules = authService.getAccessibleModules(modules || [], permissions || [])
      console.log('✅ useMenu: Módulos accesibles obtenidos:', accessibleModules)
      
      // Convertir módulos a formato MenuItem
      const menuItemsFromModules = convertModulesToMenuItems(accessibleModules)
      console.log('✅ useMenu: Menú convertido exitosamente:', menuItemsFromModules)
      
      setMenuItems(menuItemsFromModules)
    } catch (err) {
      console.error('❌ useMenu: Error al cargar el menú:', err)
      setError('Error al cargar el menú')
      
      // Menú básico de fallback
      const fallbackMenu: MenuItem[] = [
        {
          id: 'dashboard',
          name: 'Dashboard',
          title: 'Dashboard',
          icon: 'dashboard',
          path: '/dashboard',
          href: '/dashboard',
          order: 1,
          children: [],
          subItems: [],
          submenu: []
        }
      ]
      setMenuItems(fallbackMenu)
    } finally {
      stopLoading()
      console.log('🏁 useMenu: Carga del menú finalizada')
    }
  }

  // TEMPORALMENTE DESHABILITADO - Menú estático en uso
  // useEffect(() => {
  //   console.log('useMenu - Estado de autenticación:', { 
  //     isAuthenticated, 
  //     user: user?.username,
  //     modulesCount: modules?.length || 0
  //   })
  //   loadMenu()
  // }, [isAuthenticated, user, modules])

  return {
    menuItems,
    isLoading,
    error,
    refreshMenu: loadMenu
  }
}