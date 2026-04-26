import React from 'react'
import { Button, ButtonProps } from '@/components/ui/button'
import { CheckCircle2, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { LoadingSpinner } from './LoadingSpinner'

type ButtonStatus = 'idle' | 'loading' | 'success' | 'error'

interface LoadingButtonProps extends ButtonProps {
  status?: ButtonStatus
  loadingText?: string
  successText?: string
  errorText?: string
  showProgress?: boolean
  progress?: number
  resetAfter?: number // milisegundos para volver al estado idle después de success/error
}

export function LoadingButton({ 
  children, 
  status = 'idle',
  loadingText,
  successText = 'Completado',
  errorText = 'Error',
  disabled,
  className,
  showProgress = false,
  progress = 0,
  resetAfter = 2000, // 2 segundos por defecto
  ...props 
}: LoadingButtonProps) {
  // Estado local para manejar la transición automática de vuelta a idle
  const [internalStatus, setInternalStatus] = React.useState<ButtonStatus>(status)
  
  // Actualizar el estado interno cuando cambia el estado externo
  React.useEffect(() => {
    setInternalStatus(status)
    
    // Si el estado es success o error, volver a idle después de resetAfter ms
    if ((status === 'success' || status === 'error') && resetAfter > 0) {
      const timer = setTimeout(() => {
        setInternalStatus('idle')
      }, resetAfter)
      
      return () => clearTimeout(timer)
    }
  }, [status, resetAfter])
  
  // Asegurar que el progreso esté entre 0 y 100
  const safeProgress = Math.max(0, Math.min(100, progress))
  
  // Determinar el contenido del botón según el estado
  const renderContent = () => {
    switch (internalStatus) {
      case 'loading':
        return (
          <>
            <LoadingSpinner 
              variant={showProgress ? "progress" : "default"} 
              size="sm" 
              progress={safeProgress} 
              showProgress={showProgress} 
              className="mr-2 h-4 w-4" 
            />
            {loadingText || children}
          </>
        )
      case 'success':
        return (
          <>
            <CheckCircle2 className="mr-2 h-4 w-4 text-green-500" />
            {successText}
          </>
        )
      case 'error':
        return (
          <>
            <AlertCircle className="mr-2 h-4 w-4 text-destructive" />
            {errorText}
          </>
        )
      default:
        return children
    }
  }
  
  // Determinar las clases según el estado
  const getVariantClass = () => {
    switch (internalStatus) {
      case 'success':
        return 'bg-green-500 hover:bg-green-600 text-white'
      case 'error':
        return 'bg-destructive hover:bg-destructive/90 text-destructive-foreground'
      default:
        return ''
    }
  }
  
  return (
    <Button
      className={cn(
        getVariantClass(),
        className
      )}
      disabled={(internalStatus === 'loading') || disabled}
      {...props}
    >
      {/* Ya no necesitamos la barra de progreso separada ya que está integrada en el LoadingSpinner */}
      {renderContent()}
    </Button>
  )
}