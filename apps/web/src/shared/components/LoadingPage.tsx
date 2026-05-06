import React from 'react'
import { LoadingSpinner } from './LoadingSpinner'
import { cn } from '@/shared/utils/cn'

interface LoadingPageProps {
  title?: string
  subtitle?: string
  variant?: 'default' | 'dots' | 'pulse' | 'bounce' | 'rotate'
  className?: string
}

/**
 * Componente de loading para páginas completas
 * Proporciona una experiencia de carga elegante y consistente
 */
export function LoadingPage({ 
  title = 'Cargando...', 
  subtitle,
  variant = 'default',
  className 
}: LoadingPageProps) {
  return (
    <div className={cn(
      'min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-background to-muted/20',
      className
    )}>
      <div className="text-center space-y-6 max-w-md mx-auto px-6">
        {/* Logo o icono de la aplicación */}
        <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-8">
          <div className="w-8 h-8 bg-primary rounded-full animate-pulse" />
        </div>
        
        {/* Spinner principal */}
        <LoadingSpinner 
          size="xl" 
          variant={variant}
          color="primary"
        />
        
        {/* Título */}
        <div className="space-y-2">
          <h2 className="text-2xl font-semibold text-foreground animate-pulse">
            {title}
          </h2>
          {subtitle && (
            <p className="text-muted-foreground animate-pulse">
              {subtitle}
            </p>
          )}
        </div>
        
        {/* Barra de progreso animada */}
        <div className="w-full max-w-xs mx-auto">
          <div className="h-1 bg-muted rounded-full overflow-hidden">
            <div className="h-full bg-primary rounded-full animate-pulse" 
                 style={{
                   animation: 'loading-bar 2s ease-in-out infinite',
                 }} />
          </div>
        </div>
      </div>
      
      <style jsx>{`
        @keyframes loading-bar {
          0% { width: 0%; }
          50% { width: 70%; }
          100% { width: 100%; }
        }
      `}</style>
    </div>
  )
}

/**
 * Componente de loading para secciones específicas
 */
export function LoadingSection({ 
  title = 'Cargando contenido...', 
  height = 'h-64',
  variant = 'default' 
}: {
  title?: string
  height?: string
  variant?: 'default' | 'dots' | 'pulse' | 'bounce' | 'rotate'
}) {
  return (
    <div className={cn(
      'flex flex-col items-center justify-center border border-dashed border-muted rounded-lg bg-muted/5',
      height
    )}>
      <LoadingSpinner 
        size="lg" 
        variant={variant}
        color="muted"
        text={title}
      />
    </div>
  )
}

/**
 * Componente de loading para botones
 */
export function LoadingButton({ 
  children, 
  isLoading = false, 
  variant = 'default',
  size = 'sm',
  ...props 
}: {
  children: React.ReactNode
  isLoading?: boolean
  variant?: 'default' | 'dots' | 'pulse' | 'bounce' | 'rotate'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  [key: string]: any
}) {
  return (
    <button 
      {...props}
      disabled={isLoading || props.disabled}
      className={cn(
        'inline-flex items-center gap-2 transition-all duration-200',
        isLoading && 'cursor-not-allowed opacity-70',
        props.className
      )}
    >
      {isLoading && (
        <LoadingSpinner 
          size={size} 
          variant={variant}
          color="primary"
        />
      )}
      {children}
    </button>
  )
}