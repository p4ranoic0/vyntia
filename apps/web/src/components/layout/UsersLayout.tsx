import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/shared/utils/cn'
import {
  Users,
  UserCheck,
  UserCog,
  Shield,
  Key,
  Settings
} from 'lucide-react'

interface UsersLayoutProps {
  children: React.ReactNode
  title?: string
  description?: string
}

interface SubMenuItem {
  title: string
  icon: React.ComponentType<{ className?: string }>
  href: string
  description: string
}

const subMenuItems: SubMenuItem[] = [
  {
    title: 'Listado de Usuarios',
    icon: Users,
    href: '/usuarios/listado',
    description: 'Ver y administrar todos los usuarios del sistema'
  },
  {
    title: 'Crear Usuario',
    icon: UserCheck,
    href: '/usuarios/crear',
    description: 'Registrar un nuevo usuario en el sistema'
  },
  {
    title: 'Gestión de Usuarios',
    icon: UserCog,
    href: '/usuarios/gestion',
    description: 'Administrar y analizar usuarios existentes'
  },
  {
    title: 'Roles y Permisos',
    icon: Shield,
    href: '/usuarios/roles',
    description: 'Configurar roles y permisos de usuarios'
  },
  {
    title: 'Cambio de Contraseña',
    icon: Key,
    href: '/usuarios/cambio-password',
    description: 'Gestionar cambios de contraseña de usuarios'
  }
]

export function UsersLayout({ children, title, description }: UsersLayoutProps) {
  const location = useLocation()

  const isActiveRoute = (href: string) => {
    return location.pathname === href || location.pathname.startsWith(href + '/')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b pb-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              {title || 'Gestión de Usuarios'}
            </h1>
            <p className="text-muted-foreground mt-1">
              {description || 'Administra usuarios, roles y permisos del sistema'}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b">
        <nav className="flex space-x-8" aria-label="Tabs">
          {subMenuItems.map((item) => {
            const Icon = item.icon
            const isActive = isActiveRoute(item.href)
            
            return (
              <Link
                key={item.href}
                to={item.href}
                className={cn(
                  'group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                  isActive
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground hover:border-gray-300'
                )}
              >
                <Icon className={cn(
                  'w-5 h-5 mr-2 transition-colors',
                  isActive
                    ? 'text-primary'
                    : 'text-muted-foreground group-hover:text-foreground'
                )} />
                {item.title}
              </Link>
            )
          })}
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1">
        {children}
      </div>
    </div>
  )
}

export default UsersLayout