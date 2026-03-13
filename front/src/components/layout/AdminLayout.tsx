import React from 'react'
import { Outlet, useLocation, Link } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Users, 
  UserCheck, 
  Building2, 
  Shield, 
  Calendar,
  ChevronRight,
  Settings,
  Key,
  UserCog
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'

interface AdminLayoutProps {
  children?: React.ReactNode
}

// Navegación específica para administración
const adminNavItems = [
  {
    title: 'Dashboard',
    href: '/admin',
    icon: LayoutDashboard,
    description: 'Vista general del sistema'
  },
  {
    title: 'Empleados',
    href: '/empleados',
    icon: Users,
    description: 'Gestión de empleados'
  },
  {
    title: 'Usuarios',
    href: '/usuarios',
    icon: UserCheck,
    description: 'Administración de usuarios'
  },
  {
    title: 'Áreas',
    href: '/areas',
    icon: Building2,
    description: 'Gestión de áreas'
  },
  {
    title: 'Roles',
    href: '/seguridad/roles',
    icon: Shield,
    description: 'Administración de roles'
  },
  {
    title: 'Vacaciones',
    href: '/vacaciones',
    icon: Calendar,
    description: 'Gestión de vacaciones'
  },
  {
    title: 'Permisos',
    href: '/seguridad/permisos',
    icon: Key,
    description: 'Gestión de permisos'
  },
  {
    title: 'Roles-Permisos',
    href: '/seguridad/roles-permisos',
    icon: UserCog,
    description: 'Asignar permisos a roles'
  }
]

export function AdminLayout({ children }: AdminLayoutProps) {
  const location = useLocation()
  const currentPath = location.pathname

  // Determinar el título de la página actual
  const getCurrentPageTitle = () => {
    if (currentPath === '/admin') return 'Panel de Administración'
    
    const currentItem = adminNavItems.find(item => 
      currentPath.startsWith(item.href)
    )
    return currentItem ? `Administración - ${currentItem.title}` : 'Administración'
  }

  // Determinar breadcrumbs
  const getBreadcrumbs = () => {
    const breadcrumbs = [{ title: 'Administración', href: '/admin' }]
    
    if (currentPath !== '/admin') {
      const currentItem = adminNavItems.find(item => 
        currentPath.startsWith(item.href)
      )
      if (currentItem) {
        breadcrumbs.push({ title: currentItem.title, href: currentItem.href })
      }
    }
    
    return breadcrumbs
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header de administración */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4">
          {/* Breadcrumbs */}
          <nav className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
            {getBreadcrumbs().map((crumb, index) => (
              <React.Fragment key={crumb.href}>
                {index > 0 && <ChevronRight className="h-4 w-4" />}
                <Link 
                  to={crumb.href}
                  className="hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
                >
                  {crumb.title}
                </Link>
              </React.Fragment>
            ))}
          </nav>
          
          {/* Título principal */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {getCurrentPageTitle()}
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Gestión centralizada del sistema de recursos humanos
              </p>
            </div>
            <Badge variant="outline" className="text-sm">
              <Settings className="w-3 h-3 mr-1" />
              Admin
            </Badge>
          </div>
        </div>
      </div>

      {/* Navegación rápida (solo en dashboard) */}
      {currentPath === '/admin' && (
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="px-6 py-4">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {adminNavItems.slice(1).map((item) => {
                const IconComponent = item.icon
                return (
                  <Button
                    key={item.href}
                    variant="ghost"
                    asChild
                    className="h-auto p-3 flex flex-col items-center gap-2 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <Link to={item.href}>
                      <IconComponent className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                      <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                        {item.title}
                      </span>
                    </Link>
                  </Button>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* Contenido principal */}
      <div className="px-6 py-6">
        {children || <Outlet />}
      </div>
    </div>
  )
}

export default AdminLayout