import React from 'react'
import { cn } from '@/shared/utils/cn'

interface SkeletonProps {
  className?: string
  variant?: 'default' | 'rounded' | 'circular'
  animation?: 'pulse' | 'wave' | 'none'
}

/**
 * Componente base de skeleton para placeholders de carga
 */
export function Skeleton({ 
  className, 
  variant = 'default',
  animation = 'pulse',
  ...props 
}: SkeletonProps & React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'bg-muted',
        {
          'animate-pulse': animation === 'pulse',
          'animate-wave': animation === 'wave',
          'rounded-md': variant === 'rounded',
          'rounded-full': variant === 'circular',
        },
        className
      )}
      {...props}
    />
  )
}

interface LoadingSkeletonProps {
  variant?: 'text' | 'card' | 'avatar' | 'button'
  lines?: number
  className?: string
}

/**
 * Componente de esqueleto de carga para diferentes tipos de contenido
 */
export function LoadingSkeleton({ 
  variant = 'text', 
  lines = 1,
  className,
  ...props 
}: LoadingSkeletonProps & React.HTMLAttributes<HTMLDivElement>) {
  // Renderizar diferentes variantes de esqueletos
  const renderSkeleton = () => {
    switch (variant) {
      case 'avatar':
        return <Skeleton variant="circular" className={cn("h-12 w-12", className)} {...props} />
      
      case 'button':
        return <Skeleton className={cn("h-10 w-24 rounded-md", className)} {...props} />
      
      case 'card':
        return (
          <div className={cn("space-y-3", className)} {...props}>
            <Skeleton variant="circular" className="h-12 w-12" />
            <Skeleton className="h-4 w-full max-w-[250px]" />
            <Skeleton className="h-3 w-full max-w-[200px]" />
          </div>
        )
      
      case 'text':
      default:
        return (
          <div className={cn("space-y-2", className)} {...props}>
            {Array.from({ length: lines }).map((_, i) => (
              <Skeleton 
                key={i} 
                className={cn(
                  "h-4", 
                  i === lines - 1 && lines > 1 ? "w-4/5" : "w-full"
                )} 
              />
            ))}
          </div>
        )
    }
  }

  return renderSkeleton()
}

/**
 * Skeleton para tarjetas de usuario/empleado
 */
export function UserCardSkeleton() {
  return (
    <div className="p-6 border rounded-lg space-y-4">
      <div className="flex items-center space-x-4">
        <Skeleton variant="circular" className="h-12 w-12" />
        <div className="space-y-2 flex-1">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-24" />
        </div>
      </div>
      <div className="space-y-2">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-4/5" />
      </div>
    </div>
  )
}

/**
 * Skeleton para tablas de datos
 */
export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {/* Encabezado de tabla */}
      <div className="flex gap-4 pb-2 border-b">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-4 w-40" />
        <Skeleton className="h-4 w-24" />
      </div>
      
      {/* Filas de tabla */}
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 py-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-40" />
          <Skeleton className="h-4 w-24" />
        </div>
      ))}
    </div>
  )
}

/**
 * Skeleton para formularios
 */
export function FormSkeleton() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-10 w-full rounded-md" />
      </div>
      
      <div className="space-y-2">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-10 w-full rounded-md" />
      </div>
      
      <div className="space-y-2">
        <Skeleton className="h-4 w-40" />
        <Skeleton className="h-24 w-full rounded-md" />
      </div>
      
      <div className="pt-4">
        <Skeleton className="h-10 w-32 rounded-md" />
      </div>
    </div>
  )
}

/**
 * Skeleton para tarjetas de estadísticas
 */
export const StatsSkeleton = () => {
  return (
    <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 4 }).map((_, index) => (
        <div key={index} className="p-6 border rounded-lg space-y-4">
          <div className="flex items-center justify-between">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-8 w-8 rounded-lg" />
          </div>
          <div>
            <Skeleton className="h-8 w-16 mb-2" />
            <Skeleton className="h-3 w-32" />
          </div>
        </div>
      ))}
    </div>
  )
}

/**
 * Skeleton para listas
 */
export function ListSkeleton({ items = 5 }: { items?: number }) {
  return (
    <div className="space-y-3 border rounded-lg p-4">
      <Skeleton className="h-5 w-32 mb-4" />
      
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-center space-x-3 py-2 border-b last:border-0">
          <Skeleton variant="circular" className="h-8 w-8" />
          <div className="space-y-1 flex-1">
            <Skeleton className="h-4 w-full max-w-[180px]" />
            <Skeleton className="h-3 w-24" />
          </div>
          <Skeleton className="h-6 w-16 rounded-md" />
        </div>
      ))}
    </div>
  )
}

/**
 * Skeleton para dashboard completo
 */
export function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      {/* Título */}
      <div className="space-y-1">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-64" />
      </div>
      
      {/* Estadísticas */}
      <StatsSkeleton />
      
      {/* Contenido principal */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Panel principal */}
        <div className="lg:col-span-2 border rounded-lg p-6 space-y-4">
          <div className="flex justify-between items-center">
            <Skeleton className="h-5 w-40" />
            <Skeleton className="h-8 w-24 rounded-md" />
          </div>
          
          <div className="space-y-4 pt-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center space-x-3 py-2 border-b last:border-0">
                <Skeleton variant="circular" className="h-10 w-10" />
                <div className="space-y-1 flex-1">
                  <Skeleton className="h-4 w-full max-w-[220px]" />
                  <Skeleton className="h-3 w-40" />
                </div>
                <Skeleton className="h-8 w-20 rounded-md" />
              </div>
            ))}
          </div>
        </div>
        
        {/* Panel lateral */}
        <div className="border rounded-lg p-6 space-y-4">
          <Skeleton className="h-5 w-32" />
          <div className="space-y-3 pt-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="p-3 border rounded-md space-y-2">
                <Skeleton className="h-4 w-full max-w-[150px]" />
                <Skeleton className="h-3 w-full" />
                <div className="flex justify-between items-center pt-2">
                  <Skeleton className="h-3 w-16" />
                  <Skeleton className="h-6 w-6 rounded-full" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Skeleton para barra lateral
 */
export function SidebarSkeleton() {
  return (
    <div className="w-64 h-screen border-r p-4 space-y-6">
      {/* Logo */}
      <div className="flex items-center space-x-3 px-2 py-4">
        <Skeleton variant="circular" className="h-8 w-8" />
        <Skeleton className="h-5 w-32" />
      </div>
      
      {/* Menú */}
      <div className="space-y-1">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex items-center space-x-3 px-3 py-2 rounded-md">
            <Skeleton className="h-5 w-5" />
            <Skeleton className="h-4 w-24" />
          </div>
        ))}
      </div>
      
      {/* Sección inferior */}
      <div className="pt-6 mt-6 border-t space-y-3">
        <div className="flex items-center space-x-3 px-3 py-2">
          <Skeleton className="h-5 w-5" />
          <Skeleton className="h-4 w-20" />
        </div>
        <div className="flex items-center space-x-3 px-3 py-2">
          <Skeleton className="h-5 w-5" />
          <Skeleton className="h-4 w-16" />
        </div>
      </div>
    </div>
  )
}