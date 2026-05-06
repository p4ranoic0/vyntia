import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Key, Eye, EyeOff, Shield, AlertTriangle, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { toast } from 'sonner'
import { usersService, type User, type ChangePasswordData } from '@/services/usersService'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { UsersLayout } from '@/components/layout/UsersLayout'

export function ChangePassword() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  
  const [formData, setFormData] = useState<ChangePasswordData>({
    new_password: '',
    confirm_password: '',
    force_change_on_next_login: false,
    send_notification: true
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [passwordStrength, setPasswordStrength] = useState({
    score: 0,
    feedback: [] as string[]
  })

  useEffect(() => {
    if (id) {
      loadUserData(id)
    }
  }, [id])

  useEffect(() => {
    if (formData.new_password) {
      checkPasswordStrength(formData.new_password)
    } else {
      setPasswordStrength({ score: 0, feedback: [] })
    }
  }, [formData.new_password])

  const loadUserData = async (userId: string) => {
    try {
      setLoading(true)
      const userData = await usersService.getById(userId)
      setUser(userData)
    } catch (error) {
      console.error('Error loading user:', error)
      toast.error('Error al cargar los datos del usuario')
      navigate('/usuarios/listado')
    } finally {
      setLoading(false)
    }
  }

  const checkPasswordStrength = (password: string) => {
    let score = 0
    const feedback: string[] = []

    // Longitud mínima
    if (password.length >= 8) {
      score += 1
    } else {
      feedback.push('Debe tener al menos 8 caracteres')
    }

    // Mayúsculas
    if (/[A-Z]/.test(password)) {
      score += 1
    } else {
      feedback.push('Debe incluir al menos una letra mayúscula')
    }

    // Minúsculas
    if (/[a-z]/.test(password)) {
      score += 1
    } else {
      feedback.push('Debe incluir al menos una letra minúscula')
    }

    // Números
    if (/\d/.test(password)) {
      score += 1
    } else {
      feedback.push('Debe incluir al menos un número')
    }

    // Caracteres especiales
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      score += 1
    } else {
      feedback.push('Debe incluir al menos un carácter especial')
    }

    setPasswordStrength({ score, feedback })
  }

  const getPasswordStrengthColor = (score: number) => {
    if (score <= 2) return 'bg-red-500'
    if (score <= 3) return 'bg-yellow-500'
    if (score <= 4) return 'bg-blue-500'
    return 'bg-green-500'
  }

  const getPasswordStrengthText = (score: number) => {
    if (score <= 2) return 'Débil'
    if (score <= 3) return 'Regular'
    if (score <= 4) return 'Buena'
    return 'Excelente'
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.new_password) {
      newErrors.new_password = 'La nueva contraseña es requerida'
    } else if (formData.new_password.length < 8) {
      newErrors.new_password = 'La contraseña debe tener al menos 8 caracteres'
    } else if (passwordStrength.score < 3) {
      newErrors.new_password = 'La contraseña no cumple con los requisitos mínimos de seguridad'
    }

    if (!formData.confirm_password) {
      newErrors.confirm_password = 'Confirma la nueva contraseña'
    } else if (formData.new_password !== formData.confirm_password) {
      newErrors.confirm_password = 'Las contraseñas no coinciden'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm() || !user) return

    try {
      setSubmitting(true)
      await usersService.changePassword(user.id, formData)
      
      toast.success('Contraseña cambiada exitosamente', {
        description: formData.send_notification 
          ? 'Se ha enviado una notificación al usuario'
          : 'El usuario será notificado en su próximo acceso'
      })
      
      navigate(`/usuarios/gestion/${user.id}`)
    } catch (error: any) {
      console.error('Error changing password:', error)
      
      if (error.response?.data?.errors) {
        setErrors(error.response.data.errors)
      } else {
        toast.error('Error al cambiar la contraseña')
      }
    } finally {
      setSubmitting(false)
    }
  }

  const handleInputChange = (field: keyof ChangePasswordData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Limpiar errores del campo cuando el usuario empiece a escribir
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!user) {
    return (
      <div className="text-center py-8">
        <h3 className="text-lg font-semibold mb-2">Usuario no encontrado</h3>
        <p className="text-muted-foreground mb-4">
          El usuario que buscas no existe o ha sido eliminado.
        </p>
        <Button onClick={() => navigate('/usuarios/listado')}>Volver al listado</Button>
      </div>
    )
  }

  return (
    <UsersLayout 
      title="Cambio de Contraseña"
      description="Actualiza la contraseña de usuarios del sistema"
    >
      {/* Header Actions */}
      <div className="flex items-center justify-between mb-6">
        <Button
          variant="outline"
          onClick={() => navigate(`/usuarios/gestion/${user.id}`)}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver a Gestión
        </Button>
        <div className="text-right">
          <h2 className="text-xl font-semibold">
            {user.nombres_usuario} {user.apellidos_usuario}
          </h2>
          <p className="text-muted-foreground">@{user.username}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Formulario principal */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Nueva Contraseña</CardTitle>
              <CardDescription>
                Establece una nueva contraseña segura para el usuario
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Nueva contraseña */}
                <div className="space-y-2">
                  <Label htmlFor="new_password">Nueva Contraseña *</Label>
                  <div className="relative">
                    <Input
                      id="new_password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.new_password}
                      onChange={(e) => handleInputChange('new_password', e.target.value)}
                      className={errors.new_password ? 'border-red-500' : ''}
                      placeholder="Ingresa la nueva contraseña"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </Button>
                  </div>
                  {errors.new_password && (
                    <p className="text-sm text-red-600">{errors.new_password}</p>
                  )}
                  
                  {/* Indicador de fortaleza */}
                  {formData.new_password && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-300 ${
                              getPasswordStrengthColor(passwordStrength.score)
                            }`}
                            style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium">
                          {getPasswordStrengthText(passwordStrength.score)}
                        </span>
                      </div>
                      
                      {passwordStrength.feedback.length > 0 && (
                        <div className="text-sm text-muted-foreground">
                          <p className="font-medium mb-1">Para mejorar la seguridad:</p>
                          <ul className="list-disc list-inside space-y-1">
                            {passwordStrength.feedback.map((item, index) => (
                              <li key={index}>{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Confirmar contraseña */}
                <div className="space-y-2">
                  <Label htmlFor="confirm_password">Confirmar Contraseña *</Label>
                  <div className="relative">
                    <Input
                      id="confirm_password"
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={formData.confirm_password}
                      onChange={(e) => handleInputChange('confirm_password', e.target.value)}
                      className={errors.confirm_password ? 'border-red-500' : ''}
                      placeholder="Confirma la nueva contraseña"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </Button>
                  </div>
                  {errors.confirm_password && (
                    <p className="text-sm text-red-600">{errors.confirm_password}</p>
                  )}
                  
                  {/* Indicador de coincidencia */}
                  {formData.confirm_password && (
                    <div className="flex items-center gap-2 text-sm">
                      {formData.new_password === formData.confirm_password ? (
                        <>
                          <CheckCircle className="w-4 h-4 text-green-600" />
                          <span className="text-green-600">Las contraseñas coinciden</span>
                        </>
                      ) : (
                        <>
                          <AlertTriangle className="w-4 h-4 text-red-600" />
                          <span className="text-red-600">Las contraseñas no coinciden</span>
                        </>
                      )}
                    </div>
                  )}
                </div>

                {/* Opciones adicionales */}
                <div className="space-y-4 pt-4 border-t">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="force_change"
                      checked={formData.force_change_on_next_login}
                      onCheckedChange={(checked) => 
                        handleInputChange('force_change_on_next_login', checked as boolean)
                      }
                    />
                    <Label htmlFor="force_change" className="text-sm">
                      Forzar cambio de contraseña en el próximo acceso
                    </Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="send_notification"
                      checked={formData.send_notification}
                      onCheckedChange={(checked) => 
                        handleInputChange('send_notification', checked as boolean)
                      }
                    />
                    <Label htmlFor="send_notification" className="text-sm">
                      Enviar notificación por email al usuario
                    </Label>
                  </div>
                </div>

                {/* Botones */}
                <div className="flex gap-3 pt-6">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => navigate(`/usuarios/gestion/${user.id}`)}
                    disabled={submitting}
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    disabled={submitting || passwordStrength.score < 3}
                  >
                    {submitting ? (
                      <>
                        <LoadingSpinner size="sm" className="mr-2" />
                        Cambiando...
                      </>
                    ) : (
                      <>
                        <Key className="w-4 h-4 mr-2" />
                        Cambiar Contraseña
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Panel lateral con información */}
        <div className="space-y-6">
          {/* Información del usuario */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Usuario</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Nombre</p>
                <p className="text-sm">{user.nombres_usuario} {user.apellidos_usuario}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Usuario</p>
                <p className="text-sm font-mono">@{user.username}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Email</p>
                <p className="text-sm">{user.email || 'N/A'}</p>
              </div>
            </CardContent>
          </Card>

          {/* Políticas de seguridad */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Políticas de Seguridad
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>Mínimo 8 caracteres</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>Al menos una mayúscula y minúscula</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>Al menos un número</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>Al menos un carácter especial</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Advertencia de seguridad */}
          <Alert>
            <AlertTriangle className="w-4 h-4" />
            <AlertDescription className="text-sm">
              <strong>Importante:</strong> Esta acción cambiará la contraseña del usuario inmediatamente. 
              Asegúrate de comunicar la nueva contraseña de forma segura.
            </AlertDescription>
          </Alert>
        </div>
      </div>
    </UsersLayout>
  )
}

export default ChangePassword