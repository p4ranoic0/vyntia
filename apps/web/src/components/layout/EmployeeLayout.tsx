import { cn } from '@/lib/utils'
import { Briefcase, GraduationCap, Heart, Users } from 'lucide-react'
import React from 'react'
import { Link, useLocation } from 'react-router-dom'

interface EmployeeLayoutProps {
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
    title: 'Datos Personales',
    icon: Users,
    href: '/empleados/datos-personales',
    description: 'Información personal del empleado'
  },
  {
    title: 'Datos Laborales',
    icon: Briefcase,
    href: '/empleados/datos-laborales',
    description: 'Información laboral y contractual'
  },
  {
    title: 'Datos Académicos',
    icon: GraduationCap,
    href: '/empleados/datos-academicos',
    description: 'Formación académica y certificaciones'
  },
  {
    title: 'Datos Familiares',
    icon: Heart,
    href: '/empleados/datos-familiares',
    description: 'Información familiar y contactos de emergencia'
  }
]

export function EmployeeLayout({ children, title, description }: EmployeeLayoutProps) {
  const location = useLocation()

  const isActiveRoute = (href: string) => {
    return location.pathname === href || location.pathname.startsWith(href + '/')
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="border-b pb-3 sm:pb-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
              {title || 'Gestión de Empleados'}
            </h1>
            <p className="text-muted-foreground mt-1 text-xs sm:text-sm">
              {description || 'Administra la información de los empleados'}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b">
        <nav className="flex space-x-3 sm:space-x-8 overflow-x-auto -mx-1 px-1 scrollbar-hide" aria-label="Tabs">
          {subMenuItems.map((item) => {
            const Icon = item.icon
            const isActive = isActiveRoute(item.href)

            return (
              <Link
                key={item.href}
                to={item.href}
                className={cn(
                  'group inline-flex items-center py-3 sm:py-4 px-2 sm:px-1 border-b-2 font-medium text-xs sm:text-sm transition-colors whitespace-nowrap cursor-pointer',
                  isActive
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground hover:border-gray-300'
                )}
              >
                <Icon className={cn(
                  'w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2 transition-colors flex-shrink-0',
                  isActive
                    ? 'text-primary'
                    : 'text-muted-foreground group-hover:text-foreground'
                )} />
                <span className="hidden sm:inline">{item.title}</span>
                <span className="sm:hidden">{item.title.split(' ').pop()}</span>
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

export default EmployeeLayout