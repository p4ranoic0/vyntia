import React, { useState, useEffect } from 'react'
import { Key, Eye, EyeOff, AlertTriangle, CheckCircle } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Checkbox } from '@/shared/ui/checkbox'
import { Alert, AlertDescription } from '@/shared/ui/alert'
import { toast } from 'sonner'
import { usersService, type User, type ChangePasswordData } from '@/features/identity/services/usersService'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'

interface ChangePasswordModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  userId: number
  onSuccess?: () => void
}

export function ChangePasswordModal({ open, onOpenChange, userId, onSuccess }: ChangePasswordModalProps) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [formData, setFormData] = useState<ChangePasswordData>({
    new_password: '',
    confirm_password: '',
    force_change: false
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [passwordStrength, setPasswordStrength] = useState({
    score: 0,
    feedback: [] as string[]
  })

  useEffect(() => {
    if (open && userId) {
      fetchUser()
    }
  }, [open, userId]) // eslint-disable-line react-hooks/exhaustive-deps -- fetchUser re-created each render; adding it would cause infinite loop

  useEffect(() => {
    if (formData.new_password) {
      calculatePasswordStrength(formData.new_password)
    } else {
      setPasswordStrength({ score: 0, feedback: [] })
    }
  }, [formData.new_password])

  const fetchUser = async () => {
    try {
      setLoading(true)
      const userData = await usersService.getById(userId)
      setUser(userData.data)
    } catch (error) {
      console.error('Error al cargar usuario:', error)
      toast.error('Error al cargar los datos del usuario')
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (field: keyof ChangePasswordData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const resetForm = () => {
    setFormData({
      new_password: '',
      confirm_password: '',
      force_change: false
    })
    setErrors({})
    setPasswordStrength({ score: 0, feedback: [] })
  }

  const getPasswordStrengthColor = () => {
    if (passwordStrength.score <= 2) return 'bg-red-500'
    if (passwordStrength.score <= 3) return 'bg-yellow-500'
    if (passwordStrength.score <= 4) return 'bg-blue-500'
    return 'bg-green-500'
  }

  const calculatePasswordStrength = (password: string) => {
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
      feedback.push('Debe incluir al menos un carácter especial (!@#$%^&*)')
    }

    setPasswordStrength({ score, feedback })
  }

  const getPasswordStrengthText = () => {
    if (passwordStrength.score <= 2) return 'Débil'
    if (passwordStrength.score <= 3) return 'Regular'
    if (passwordStrength.score <= 4) return 'Buena'
    return 'Excelente'
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.new_password) {
      newErrors.new_password = 'La nueva contraseña es requerida'
    } else if (formData.new_password.length < 8) {
      newErrors.new_password = 'La contraseña debe tener al menos 8 caracteres'
    } else if (passwordStrength.score < 3) {
      newErrors.new_password = 'La contraseña debe ser más segura'
    }

    if (!formData.confirm_password) {
      newErrors.confirm_password = 'Confirme la nueva contraseña'
    } else if (formData.new_password !== formData.confirm_password) {
      newErrors.confirm_password = 'Las contraseñas no coinciden'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    try {
      setLoading(true)
      await usersService.changePassword(userId, formData)
      toast.success('Contraseña cambiada exitosamente')
      resetForm()
      onOpenChange(false)
      onSuccess?.()
    } catch (error) {
      console.error('Error al cambiar contraseña:', error)
      const err = error as { response?: { data?: { errors?: Record<string, string>; message?: string } } }
      if (err.response?.data?.errors) {
        setErrors(err.response.data.errors)
      } else {
        toast.error(err.response?.data?.message || 'Error al cambiar la contraseña')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    resetForm()
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            Cambiar Contraseña
          </DialogTitle>
          <DialogDescription>
            {user && (
              <>
                Cambiar la contraseña para <strong>{user.nombres_usuario} {user.apellidos_usuario}</strong>
              </>
            )}
          </DialogDescription>
        </DialogHeader>

        {loading && !user ? (
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner />
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {user && (
              <div className="bg-muted/50 p-4 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-sm font-medium text-primary">
                      {user.nombres_usuario?.[0]}{user.apellidos_usuario?.[0]}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium">{user.nombres_usuario} {user.apellidos_usuario}</p>
                    <p className="text-sm text-muted-foreground">@{user.username}</p>
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="new_password">Nueva Contraseña</Label>
                <div className="relative">
                  <Input
                    id="new_password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.new_password}
                    onChange={(e) => handleInputChange('new_password', e.target.value)}
                    className={errors.new_password ? 'border-red-500' : ''}
                    placeholder="Ingrese la nueva contraseña"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                {errors.new_password && (
                  <p className="text-sm text-red-500">{errors.new_password}</p>
                )}
              </div>

              {formData.new_password && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Fortaleza de la contraseña:</span>
                    <span className={`font-medium ${
                      passwordStrength.score <= 2 ? 'text-red-500' :
                      passwordStrength.score === 3 ? 'text-yellow-500' :
                      passwordStrength.score === 4 ? 'text-blue-500' : 'text-green-500'
                    }`}>
                      {getPasswordStrengthText()}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all ${getPasswordStrengthColor()}`}
                      style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                    />
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

              <div className="space-y-2">
                <Label htmlFor="confirm_password">Confirmar Nueva Contraseña</Label>
                <div className="relative">
                  <Input
                    id="confirm_password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.confirm_password}
                    onChange={(e) => handleInputChange('confirm_password', e.target.value)}
                    className={errors.confirm_password ? 'border-red-500' : ''}
                    placeholder="Confirme la nueva contraseña"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                {errors.confirm_password && (
                  <p className="text-sm text-red-500">{errors.confirm_password}</p>
                )}
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="force_change"
                  checked={formData.force_change}
                  onCheckedChange={(checked) => handleInputChange('force_change', checked as boolean)}
                />
                <Label htmlFor="force_change" className="text-sm">
                  Forzar cambio de contraseña en el próximo inicio de sesión
                </Label>
              </div>

              {passwordStrength.score >= 3 && formData.new_password === formData.confirm_password && formData.confirm_password && (
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertDescription>
                    La contraseña cumple con los requisitos de seguridad.
                  </AlertDescription>
                </Alert>
              )}

              {passwordStrength.score < 3 && formData.new_password && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    La contraseña no cumple con los requisitos mínimos de seguridad.
                  </AlertDescription>
                </Alert>
              )}
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={handleClose}>
                Cancelar
              </Button>
              <Button 
                type="submit" 
                disabled={loading || passwordStrength.score < 3 || formData.new_password !== formData.confirm_password}
              >
                {loading ? (
                  <LoadingSpinner className="mr-2" />
                ) : (
                  <Key className="mr-2 h-4 w-4" />
                )}
                Cambiar Contraseña
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}