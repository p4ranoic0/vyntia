'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/hooks/useAuth'
import { useToast } from '@/components/ui/use-toast'
import { Loader2, Eye, EyeOff, Lock, CheckCircle } from 'lucide-react'

/**
 * Schema de validación para el formulario de reset de contraseña
 */
const resetPasswordSchema = z.object({
  new_password: z
    .string()
    .min(8, 'La contraseña debe tener al menos 8 caracteres')
    .regex(/^(?=.*[a-zA-Z])(?=.*\d)/, 'La contraseña debe contener al menos una letra y un número'),
  confirm_password: z.string().min(1, 'Confirme su nueva contraseña'),
}).refine((data) => data.new_password === data.confirm_password, {
  message: 'Las contraseñas no coinciden',
  path: ['confirm_password'],
})

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>

/**
 * Componente para restablecer contraseña usando token
 * Solo requiere token (de URL) y nueva contraseña
 */
const ResetPasswordForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { resetPassword } = useAuth()
  const { toast } = useToast()
  
  // Obtener token de los parámetros de URL
  const token = searchParams.get('token')
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  })

  /**
   * Maneja el envío del formulario de reset de contraseña
   */
  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Token de recuperación no válido o faltante',
      })
      return
    }

    setIsLoading(true)
    
    try {
      await resetPassword(token, data.new_password)
      
      setIsSuccess(true)
      toast({
        title: 'Contraseña actualizada',
        description: 'Su contraseña ha sido actualizada exitosamente',
      })
      
      // Limpiar formulario
      reset()
      
      // Redirigir al login después de 3 segundos
      setTimeout(() => {
        navigate('/login')
      }, 3000)
      
    } catch (error) {
      console.error('Reset password error:', error)
      toast({
        variant: 'destructive',
        title: 'Error al actualizar contraseña',
        description: error instanceof Error ? error.message : 'Ocurrió un error inesperado',
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Si no hay token, mostrar error
  if (!token) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-md mx-auto">
          <Card>
            <CardHeader className="space-y-1">
              <CardTitle className="text-2xl font-bold text-center text-destructive">
                Token Inválido
              </CardTitle>
              <CardDescription className="text-center">
                El enlace de recuperación no es válido o ha expirado
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => navigate('/login')} 
                className="w-full"
              >
                Volver al Login
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // Si el reset fue exitoso, mostrar mensaje de éxito
  if (isSuccess) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-md mx-auto">
          <Card>
            <CardHeader className="space-y-1">
              <div className="flex justify-center mb-4">
                <CheckCircle className="h-16 w-16 text-green-500" />
              </div>
              <CardTitle className="text-2xl font-bold text-center text-green-600">
                ¡Contraseña Actualizada!
              </CardTitle>
              <CardDescription className="text-center">
                Su contraseña ha sido actualizada exitosamente. Será redirigido al login en unos segundos.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => navigate('/login')} 
                className="w-full"
              >
                Ir al Login
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-md mx-auto">
        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-center">
              Restablecer Contraseña
            </CardTitle>
            <CardDescription className="text-center">
              Ingrese su nueva contraseña
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* Nueva Contraseña */}
              <div className="space-y-2">
                <Label htmlFor="new_password">Nueva Contraseña</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="new_password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Ingrese su nueva contraseña"
                    className="pl-10 pr-10"
                    {...register('new_password')}
                    disabled={isLoading}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={isLoading}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                {errors.new_password && (
                  <p className="text-sm text-destructive">{errors.new_password.message}</p>
                )}
              </div>

              {/* Confirmar Contraseña */}
              <div className="space-y-2">
                <Label htmlFor="confirm_password">Confirmar Contraseña</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="confirm_password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="Confirme su nueva contraseña"
                    className="pl-10 pr-10"
                    {...register('confirm_password')}
                    disabled={isLoading}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    disabled={isLoading}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                {errors.confirm_password && (
                  <p className="text-sm text-destructive">{errors.confirm_password.message}</p>
                )}
              </div>

              {/* Botón de envío */}
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Actualizando contraseña...
                  </>
                ) : (
                  'Actualizar Contraseña'
                )}
              </Button>

              {/* Enlace para volver al login */}
              <div className="text-center">
                <Button
                  type="button"
                  variant="link"
                  onClick={() => navigate('/login')}
                  disabled={isLoading}
                  className="text-sm"
                >
                  Volver al Login
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default ResetPasswordForm