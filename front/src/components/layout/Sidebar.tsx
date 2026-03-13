import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip'
import { useStaggerAnimation } from '@/hooks/useAnimations'
import { useAuth } from '@/hooks/useAuth'
import { cn } from '@/lib/utils'
import { Module } from '@/services/authService'
import { menuService, MenuItem as MenuServiceItem } from '@/services/menuService'
import {
    AlertCircle,
    BarChart3,
    Briefcase,
    Building2,
    Calendar,
    CalendarDays,
    ChevronLeft,
    ChevronRight,
    ClipboardCheck,
    Cog,
    Edit,
    FileCheck,
    FileText,
    FolderOpen,
    GraduationCap,
    Heart,
    Home,
    Key,
    Layout,
    LayoutDashboard,
    Link as LinkIcon,
    List,
    MapPin,
    PlusCircle,
    RefreshCw,
    Settings,
    Shield,
    ShieldCheck,
    Upload,
    User,
    UserPlus,
    Users,
    X
} from 'lucide-react'
import React, { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

interface SidebarProps {
  readonly isCollapsed: boolean
  readonly onToggle: () => void
  readonly isMobileOpen: boolean
  readonly onMobileToggle: () => void
}

interface MenuItem {
  id: string
  title: string
  icon: React.ComponentType<any>
  path?: string
  submenu?: MenuItem[]
}

// Función para convertir elementos del menuService al formato del Sidebar
const convertMenuItems = (menuServiceItems: MenuServiceItem[]): MenuItem[] => {
  const iconMap: Record<string, React.ComponentType<any>> = {
    // ===== Iconos kebab-case del backend (seed_menu.py) =====
    'layout-dashboard': LayoutDashboard,
    'landmark': FileText,
    'users': Users,
    'list': List,
    'user': User,
    'briefcase': Briefcase,
    'graduation-cap': GraduationCap,
    'heart': Heart,
    'calendar': Calendar,
    'plus-circle': PlusCircle,
    'file-text': FileText,
    'calendar-days': CalendarDays,
    'bar-chart': BarChart3,
    'settings': Settings,
    'folder-open': FolderOpen,
    'map-pin': MapPin,
    'shield': Shield,
    'shield-check': ShieldCheck,
    'building': Building2,
    'key': Key,
    'link': LinkIcon,
    'circle': Home, // fallback del backend cuando icono_modulo es null
    'file-check': FileCheck,
    'user-plus': UserPlus,

    // ===== Iconos legacy / aliases =====
    'dashboard': LayoutDashboard,
    'empleados': Users,
    'vacaciones': Calendar,
    'administracion': Cog,
    'reportes': BarChart3,
    'people': Users,
    'person_add': UserPlus,
    'security': Shield,
    'lista': List,
    'crear': UserPlus,
    'editar': Edit,
    'modulos': Layout,
    'usuarios': Users,
    'roles': Shield,
    'permisos': Key,
    'areas': Building2,
    'solicitudes': Calendar,
    'periodos': CalendarDays,
    'configuracion': Settings,

    // ===== Mapeo por ID de modulo =====
    'modulo-1': LayoutDashboard,
    'modulo-2': Users,
    'modulo-3': Calendar,
    'modulo-4': Cog,

    // ===== Mapeo por ID de submenu =====
    'admin-modulos': Layout,
    'admin-usuarios': Users,
    'admin-roles': ShieldCheck,
    'admin-areas': Building2,
    'onboarding': ClipboardCheck,
    'mi-onboarding': ClipboardCheck,
    'empleados-onboarding': ClipboardCheck,
    'legajo-gestion': Upload,
    'contratos': FileCheck,
    'plantillas-documentos': FileText,
    'plantillas': FileText,
  }

  return menuServiceItems.map(item => ({
    id: item.id,
    title: item.title,
    icon: iconMap[item.icon] || iconMap[item.id] || BarChart3,
    path: item.path,
    submenu: item.submenu ? convertMenuItems(item.submenu) : undefined
  }))
}

// Rutas de autoservicio del empleado que no deben aparecer como items
// separados en el menu admin (se acceden desde la lista de empleados)
const ADMIN_EXCLUDED_PATHS = new Set([
  '/empleados/datos-personales',
  '/empleados/datos-laborales',
  '/empleados/datos-academicos',
  '/empleados/datos-familiares',
])

// Titulos de secciones de autoservicio que no deben aparecer en admin
const ADMIN_EXCLUDED_TITLES = new Set([
  'datos personales',
  'datos laborales',
  'formacion academica',
  'formación académica',
  'datos familiares',
  'mis datos',
])

/**
 * Filtra items del menu backend que no deben aparecer en la vista admin.
 */
const filterMenuForAdmin = (items: MenuItem[]): MenuItem[] => {
  return items
    .filter(item => {
      const title = item.title.toLowerCase()
      if (ADMIN_EXCLUDED_TITLES.has(title)) return false
      if (item.path && ADMIN_EXCLUDED_PATHS.has(item.path)) return false
      return true
    })
    .map(item => {
      if (item.submenu) {
        const filteredSubmenu = item.submenu.filter(sub => {
          const title = sub.title.toLowerCase()
          if (ADMIN_EXCLUDED_TITLES.has(title)) return false
          if (sub.path && ADMIN_EXCLUDED_PATHS.has(sub.path)) return false
          return true
        })
        if (filteredSubmenu.length === 0 && !item.path) return null
        return { ...item, submenu: filteredSubmenu.length > 0 ? filteredSubmenu : undefined }
      }
      return item
    })
    .filter((item): item is MenuItem => item !== null)
}

export function Sidebar({ isCollapsed, onToggle, isMobileOpen, onMobileToggle }: Readonly<SidebarProps>) {
  const location = useLocation()
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [isLoadingMenu, setIsLoadingMenu] = useState(true)
  const [menuError, setMenuError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  const { user, modules, isAdminOrRRHH } = useAuth()

  const modulesToMenuItems = (items: Module[]): MenuItem[] => {
    return items
      .map((module) => ({
        id: `modulo-${module.modulo_id}`,
        title: module.nombre_modulo,
        icon: module.icono_modulo
          ? (convertMenuItems([
              {
                id: `modulo-${module.modulo_id}`,
                title: module.nombre_modulo,
                icon: module.icono_modulo,
                path: module.ruta_modulo || '/dashboard',
                order: module.orden_visualizacion,
              },
            ])[0]?.icon || BarChart3)
          : BarChart3,
        path: module.ruta_modulo || '/dashboard',
      }))
      .sort((a, b) => {
        const aOrder = items.find((m) => `modulo-${m.modulo_id}` === a.id)?.orden_visualizacion || 0
        const bOrder = items.find((m) => `modulo-${m.modulo_id}` === b.id)?.orden_visualizacion || 0
        return aOrder - bOrder
      })
  }

  const getFallbackMenu = (): MenuItem[] => {
    if (modules && modules.length > 0) {
      const dynamicMenu = modulesToMenuItems(modules)
      if (dynamicMenu.length > 0) {
        const filteredMenu = isAdminOrRRHH() ? filterMenuForAdmin(dynamicMenu) : dynamicMenu
        if (filteredMenu.length > 0) {
          return filteredMenu
        }
      }
    }

    return [
      {
        id: 'dashboard-fallback',
        title: 'Dashboard',
        icon: LayoutDashboard,
        path: '/dashboard',
      },
    ]
  }

  // Hook de animacion para items del menu
  const menuRef = useStaggerAnimation({ delay: 80, duration: 400 })

  // Cargar menú dinámico del backend
  useEffect(() => {
    const loadMenu = async () => {
      try {
        setIsLoadingMenu(true)
        setMenuError(null)
        const menu = await menuService.getUserMenu()

        if (menu && menu.length > 0) {
          let items = convertMenuItems(menu)
          if (isAdminOrRRHH()) {
            items = filterMenuForAdmin(items)
          }
          setMenuItems(items)
          setRetryCount(0)
        } else {
          console.warn('Menu vacio recibido, usando menu de fallback')
          setMenuItems(getFallbackMenu())
          setMenuError('Menu vacio recibido del servidor')
        }
      } catch (error) {
        console.error('Error al cargar el menu:', error)
        const errorMessage = error instanceof Error ? error.message : 'Error desconocido al cargar el menu'
        setMenuError(errorMessage)
        setMenuItems(getFallbackMenu())
        setRetryCount(prev => prev + 1)
      } finally {
        setIsLoadingMenu(false)
      }
    }

    loadMenu()
  }, [retryCount, user?.usuario_id, modules])

  const retryLoadMenu = () => {
    if (retryCount < 3) {
      setRetryCount(prev => prev + 1)
    }
  }

  const toggleExpanded = (itemId: string) => {
    const newExpanded = new Set(expandedItems)
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId)
    } else {
      newExpanded.add(itemId)
    }
    setExpandedItems(newExpanded)
  }

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/')
  }

  // Close mobile sidebar when navigating
  const handleNavClick = () => {
    if (isMobileOpen) {
      onMobileToggle()
    }
  }

  // Rendered content for a collapsed menu item (with tooltip)
  const renderCollapsedItem = (item: MenuItem) => {
    const hasSubmenu = item.submenu && item.submenu.length > 0
    const isItemActive = item.path ? isActive(item.path) : false
    const hasActiveChild = hasSubmenu && item.submenu?.some(sub => sub.path && isActive(sub.path))
    const IconComponent = item.icon

    const iconContent = (
      <div
        className={cn(
          'flex items-center justify-center w-10 h-10 rounded-lg cursor-pointer transition-colors duration-200',
          'hover:bg-muted',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
          (isItemActive || hasActiveChild)
            ? 'bg-primary/10 text-primary'
            : 'text-muted-foreground'
        )}
      >
        <IconComponent className="w-5 h-5" />
      </div>
    )

    // For items with submenu, show submenu in tooltip
    if (hasSubmenu) {
      return (
        <Tooltip key={item.id} delayDuration={100}>
          <TooltipTrigger asChild>
            <div className="flex justify-center mb-1">
              {item.path ? (
                <Link to={item.path} onClick={handleNavClick}>{iconContent}</Link>
              ) : (
                iconContent
              )}
            </div>
          </TooltipTrigger>
          <TooltipContent side="right" align="start" className="p-2 space-y-1">
            <p className="font-medium text-xs mb-1.5 text-muted-foreground">{item.title}</p>
            {item.submenu!.map(sub => (
              <Link
                key={sub.id}
                to={sub.path || '#'}
                onClick={handleNavClick}
                className={cn(
                  'flex items-center gap-2 px-2 py-1.5 rounded text-sm cursor-pointer transition-colors duration-200',
                  'hover:bg-muted',
                  sub.path && isActive(sub.path)
                    ? 'text-primary font-medium'
                    : 'text-foreground'
                )}
              >
                <sub.icon className="w-4 h-4" />
                {sub.title}
              </Link>
            ))}
          </TooltipContent>
        </Tooltip>
      )
    }

    // Simple item with tooltip
    return (
      <Tooltip key={item.id} delayDuration={100}>
        <TooltipTrigger asChild>
          <div className="flex justify-center mb-1">
            {item.path ? (
              <Link to={item.path}>{iconContent}</Link>
            ) : (
              iconContent
            )}
          </div>
        </TooltipTrigger>
        <TooltipContent side="right" className="text-sm">
          {item.title}
        </TooltipContent>
      </Tooltip>
    )
  }

  // Rendered content for an expanded menu item
  const renderExpandedItem = (item: MenuItem, level: number = 0) => {
    const hasSubmenu = item.submenu && item.submenu.length > 0
    const isExpanded = expandedItems.has(item.id)
    const isItemActive = item.path ? isActive(item.path) : false
    const hasActiveChild = hasSubmenu && item.submenu?.some(sub => sub.path && isActive(sub.path))
    const IconComponent = item.icon

    return (
      <div key={item.id} className={cn('mb-0.5', level > 0 && 'ml-4')}>
        <div className="flex items-center">
          {item.path && !hasSubmenu ? (
            <Link
              to={item.path}
              onClick={handleNavClick}
              className={cn(
                'flex items-center w-full px-3 py-2 text-sm rounded-lg cursor-pointer',
                'transition-colors duration-200',
                'hover:bg-muted hover:text-foreground',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
                isItemActive
                  ? 'bg-primary/10 text-primary font-medium'
                  : 'text-muted-foreground'
              )}
            >
              <IconComponent className="w-5 h-5 mr-3 flex-shrink-0" />
              <span className="truncate">{item.title}</span>
            </Link>
          ) : (
            <button
              onClick={() => toggleExpanded(item.id)}
              className={cn(
                'flex items-center w-full px-3 py-2 text-sm rounded-lg cursor-pointer',
                'transition-colors duration-200',
                'hover:bg-muted hover:text-foreground',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
                hasActiveChild
                  ? 'bg-primary/10 text-primary font-medium'
                  : 'text-muted-foreground'
              )}
            >
              <IconComponent className="w-5 h-5 mr-3 flex-shrink-0" />
              <span className="truncate flex-1 text-left">{item.title}</span>
              {hasSubmenu && (
                <ChevronRight
                  className={cn(
                    'w-4 h-4 transition-transform duration-200',
                    isExpanded && 'rotate-90'
                  )}
                />
              )}
            </button>
          )}
        </div>

        {hasSubmenu && isExpanded && (
          <div className="mt-0.5 space-y-0.5 animate-slide-in-bottom">
            {item.submenu!.map((subItem, subIndex) => (
              <div
                key={subItem.id}
                className="stagger-animation"
                style={{ '--stagger-delay': subIndex + 1 } as React.CSSProperties}
              >
                {renderExpandedItem(subItem, level + 1)}
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  let navigationContent: React.ReactNode

  if (isLoadingMenu) {
    navigationContent = (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-6 w-6 sm:h-8 sm:w-8 border-b-2 border-primary"></div>
        {!isCollapsed && (
          <span className="ml-2 text-xs sm:text-sm text-muted-foreground">Cargando menu...</span>
        )}
      </div>
    )
  } else if (isCollapsed) {
    navigationContent = menuItems.map(item => renderCollapsedItem(item))
  } else {
    navigationContent = menuItems.map((item, index) => (
      <div
        key={item.id}
        className="stagger-animation"
        style={{ '--stagger-delay': index } as React.CSSProperties}
      >
        {renderExpandedItem(item)}
      </div>
    ))
  }

  return (
    <TooltipProvider>
      {/* Overlay para móvil */}
      {isMobileOpen && (
        <button
          type="button"
          aria-label="Cerrar menú lateral"
          className="fixed inset-0 z-40 bg-black/50 lg:hidden transition-opacity duration-300"
          onClick={onMobileToggle}
        >
          <span className="sr-only">Cerrar menú lateral</span>
        </button>
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed top-0 left-0 z-50 h-full bg-card border-r border-border',
          'transition-transform duration-300 ease-in-out',
          'lg:relative lg:translate-x-0',
          isCollapsed ? 'w-16' : 'w-64',
          isMobileOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-3 sm:p-4 border-b border-border">
          <div className="flex items-center space-x-2 min-w-0">
            <Building2 className="w-7 h-7 sm:w-8 sm:h-8 text-primary flex-shrink-0" />
            {!isCollapsed && (
              <div className="flex flex-col min-w-0">
                <span className="text-lg sm:text-xl font-bold text-foreground truncate">HR Sistema</span>
                {user && (
                  <Badge variant={isAdminOrRRHH() ? 'default' : 'secondary'} className="text-[10px] mt-0.5 w-fit">
                    {isAdminOrRRHH() ? 'Administrador' : 'Personal'}
                  </Badge>
                )}
              </div>
            )}
          </div>
          {/* Close button for mobile */}
          <Button
            variant="ghost"
            size="icon"
            onClick={onMobileToggle}
            className="lg:hidden h-9 w-9 cursor-pointer"
          >
            <X className="w-5 h-5" />
          </Button>
          {/* Collapse toggle for desktop */}
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="hidden lg:flex cursor-pointer"
          >
            <ChevronLeft
              className={cn(
                'w-4 h-4 transition-transform duration-200',
                isCollapsed && 'rotate-180'
              )}
            />
          </Button>
        </div>

        {/* Notificación de Error del Menú */}
        {menuError && !isCollapsed && (
          <div className="mx-3 sm:mx-4 mt-2 p-2.5 sm:p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
            <div className="flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-destructive mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs sm:text-sm text-destructive font-medium">Error al cargar menu</p>
                <p className="text-[10px] sm:text-xs text-destructive/80 mt-1">{menuError}</p>
                {retryCount < 3 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={retryLoadMenu}
                    className="mt-2 h-7 text-xs border-destructive/20 text-destructive hover:bg-destructive/10 cursor-pointer"
                  >
                    <RefreshCw className="w-3 h-3 mr-1" />
                    Reintentar ({retryCount}/3)
                  </Button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav
          ref={menuRef}
          className="flex-1 p-2 sm:p-4 space-y-1 overflow-y-auto"
        >
          {navigationContent}
        </nav>
      </aside>
    </TooltipProvider>
  )
}
