import React from 'react'
import { Loader2, RotateCw } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  className?: string
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'default' | 'dots' | 'pulse' | 'bounce' | 'rotate' | 'progress'
  color?: 'primary' | 'secondary' | 'accent' | 'muted'
  text?: string
  fullScreen?: boolean
  progress?: number // Valor de progreso entre 0 y 100
  showProgress?: boolean // Mostrar porcentaje de progreso
}

const sizeClasses = {
  xs: 'w-3 h-3',
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12',
}

const colorClasses = {
  primary: 'text-primary',
  secondary: 'text-secondary',
  accent: 'text-accent',
  muted: 'text-muted-foreground',
}

const textSizeClasses = {
  xs: 'text-xs',
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
  xl: 'text-xl',
}

// Componente de spinner básico
function DefaultSpinner({ size, color, className }: { size: string; color: string; className?: string }) {
  return (
    <Loader2 className={cn('animate-spin', size, color, className)} />
  )
}

// Componente de puntos animados
function DotsSpinner({ size, color }: { size: keyof typeof sizeClasses; color: string }) {
  const dotSize = size === 'xs' ? 'w-1 h-1' : size === 'sm' ? 'w-1.5 h-1.5' : size === 'md' ? 'w-2 h-2' : size === 'lg' ? 'w-2.5 h-2.5' : 'w-3 h-3'
  
  return (
    <div className="flex space-x-1">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={cn(
            'rounded-full animate-pulse',
            dotSize,
            color.replace('text-', 'bg-'),
          )}
          style={{
            animationDelay: `${i * 0.2}s`,
            animationDuration: '1s',
          }}
        />
      ))}
    </div>
  )
}

// Componente de pulso
function PulseSpinner({ size, color }: { size: string; color: string }) {
  return (
    <div className={cn('rounded-full animate-pulse', size, color.replace('text-', 'bg-'))} />
  )
}

// Componente de rebote
function BounceSpinner({ size, color }: { size: keyof typeof sizeClasses; color: string }) {
  const dotSize = size === 'xs' ? 'w-1 h-1' : size === 'sm' ? 'w-1.5 h-1.5' : size === 'md' ? 'w-2 h-2' : size === 'lg' ? 'w-2.5 h-2.5' : 'w-3 h-3'
  
  return (
    <div className="flex space-x-1">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={cn(
            'rounded-full animate-bounce',
            dotSize,
            color.replace('text-', 'bg-'),
          )}
          style={{
            animationDelay: `${i * 0.1}s`,
          }}
        />
      ))}
    </div>
  )
}

// Componente de rotación personalizada
function RotateSpinner({ size, color, className }: { size: string; color: string; className?: string }) {
  return (
    <RotateCw className={cn('animate-spin', size, color, className)} style={{ animationDuration: '2s' }} />
  )
}

// Componente de barra de progreso
function ProgressSpinner({ 
  size, 
  color, 
  progress = 0,
  showProgress = false 
}: { 
  size: keyof typeof sizeClasses; 
  color: string; 
  progress?: number;
  showProgress?: boolean;
}) {
  // Asegurar que el progreso esté entre 0 y 100
  const safeProgress = Math.max(0, Math.min(100, progress))
  
  // Determinar el ancho basado en el tamaño
  const widthClass = {
    xs: 'w-16',
    sm: 'w-24',
    md: 'w-32',
    lg: 'w-40',
    xl: 'w-48',
  }[size]
  
  return (
    <div className="flex flex-col items-center space-y-2">
      <div className={cn('bg-muted rounded-full overflow-hidden', widthClass, 'h-2')}>
        <div 
          className={cn('h-full rounded-full transition-all duration-300 ease-out', color.replace('text-', 'bg-'))} 
          style={{ width: `${safeProgress}%` }}
        />
      </div>
      {showProgress && (
        <span className={cn('text-xs font-medium', color)}>
          {safeProgress.toFixed(0)}%
        </span>
      )}
    </div>
  )
}

export function LoadingSpinner({ 
  className, 
  size = 'md', 
  variant = 'default',
  color = 'primary',
  text,
  fullScreen = false,
  progress = 0,
  showProgress = false
}: LoadingSpinnerProps) {
  const sizeClass = sizeClasses[size]
  const colorClass = colorClasses[color]
  const textSizeClass = textSizeClasses[size]

  const renderSpinner = () => {
    switch (variant) {
      case 'dots':
        return <DotsSpinner size={size} color={colorClass} />
      case 'pulse':
        return <PulseSpinner size={sizeClass} color={colorClass} />
      case 'bounce':
        return <BounceSpinner size={size} color={colorClass} />
      case 'rotate':
        return <RotateSpinner size={sizeClass} color={colorClass} className={className} />
      case 'progress':
        return <ProgressSpinner size={size} color={colorClass} progress={progress} showProgress={showProgress} />
      default:
        return <DefaultSpinner size={sizeClass} color={colorClass} className={className} />
    }
  }

  const content = (
    <div className={cn(
      'flex flex-col items-center justify-center gap-3',
      fullScreen ? 'fixed inset-0 bg-background/80 backdrop-blur-sm z-50' : 'p-4'
    )}>
      {renderSpinner()}
      {text && (
        <p className={cn(
          'font-medium text-center animate-pulse',
          textSizeClass,
          colorClass
        )}>
          {text}
        </p>
      )}
    </div>
  )

  return content
}