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
import { Button } from '@/shared/ui/button'
import { Card, CardContent } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'
import { Separator } from '@/shared/ui/separator'

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
    <div className="min-h-screen bg-background">
      {/* Header de administración */}
      <div className="bg-card border-b border-border">
        <div className="px-6 py-4">
          {/* Breadcrumbs */}
          <nav className="flex items-center space-x-2 text-sm text-muted-foreground mb-2">
            {getBreadcrumbs().map((crumb, index) => (
              <React.Fragment key={crumb.href}>
                {index > 0 && <ChevronRight className="h-4 w-4" />}
                <Link
                  to={crumb.href}
                  className="hover:text-foreground transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded cursor-pointer"
                >
                  {crumb.title}
                </Link>
              </React.Fragment>
            ))}
          </nav>

          {/* Título principal */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                {getCurrentPageTitle()}
              </h1>
              <p className="text-muted-foreground mt-1">
                Gestión centralizada del sistema de recursos humanos
              </p>
            </div>
            <Badge variant="secondary" className="text-xs font-medium gap-1">
              <Settings className="w-3 h-3" aria-hidden="true" />
              Panel de Admin
            </Badge>
          </div>
        </div>
      </div>

      {/* Navegación rápida (solo en dashboard) */}
      {currentPath === '/admin' && (
        <div className="bg-card border-b border-border">
          <div className="px-6 py-4">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {adminNavItems.slice(1).map((item) => {
                const IconComponent = item.icon
                const isActive = currentPath.startsWith(item.href)
                return (
                  <Button
                    key={item.href}
                    variant="ghost"
                    asChild
                    className={`h-auto p-3 flex flex-col items-center gap-2 cursor-pointer transition-colors duration-200 ${isActive ? 'bg-accent text-accent-foreground' : 'hover:bg-muted'}`}
                  >
                    <Link to={item.href}>
                      <IconComponent className={`h-5 w-5 ${isActive ? 'text-primary' : 'text-muted-foreground'}`} />
                      <span className={`text-xs font-medium ${isActive ? 'text-primary' : 'text-foreground'}`}>
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