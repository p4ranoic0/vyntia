import { cn } from '@/shared/utils/cn'
import { BarChart3, Building2, List, Plus } from 'lucide-react'
import React from 'react'
import { Link, useLocation } from 'react-router-dom'

interface AreasLayoutProps {
  children: React.ReactNode
  title: string
  description?: string
}

const navigationItems = [
  {
    name: 'Listado de Áreas',
    shortName: 'Listado',
    href: '/areas/listado',
    icon: List,
    description: 'Ver todas las áreas organizacionales'
  },
  {
    name: 'Crear Área',
    shortName: 'Crear',
    href: '/areas/crear',
    icon: Plus,
    description: 'Registrar nueva área'
  },
  {
    name: 'Gestión de Áreas',
    shortName: 'Gestión',
    href: '/areas/gestion',
    icon: BarChart3,
    description: 'Análisis y reportes'
  }
]

export function AreasLayout({ children, title, description }: AreasLayoutProps) {
  const location = useLocation()

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-3 sm:pb-5">
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="p-1.5 sm:p-2 bg-blue-100 rounded-lg">
            <Building2 className="h-5 w-5 sm:h-6 sm:w-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-gray-900">{title}</h1>
            {description && (
              <p className="text-xs sm:text-sm text-gray-600 mt-0.5 sm:mt-1">{description}</p>
            )}
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-3 sm:space-x-8 overflow-x-auto scrollbar-hide" aria-label="Tabs">
          {navigationItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.href

            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'group inline-flex items-center py-3 sm:py-4 px-2 sm:px-1 border-b-2 font-medium text-xs sm:text-sm transition-colors whitespace-nowrap cursor-pointer',
                  isActive
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                )}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon
                  className={cn(
                    'mr-1.5 sm:mr-2 h-4 w-4 sm:h-5 sm:w-5 transition-colors flex-shrink-0',
                    isActive
                      ? 'text-blue-500'
                      : 'text-gray-400 group-hover:text-gray-500'
                  )}
                  aria-hidden="true"
                />
                <span className="hidden sm:inline">{item.name}</span>
                <span className="sm:hidden">{item.shortName}</span>
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
