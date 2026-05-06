import React, { useState, useEffect } from 'react'
import { Save, User, Mail, Lock, Shield, Building2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Separator } from '@/components/ui/separator'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { toast } from 'sonner'
import { usersService, rolesService, type UserFormData, type Role } from '@/services/usersService'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'

interface Employee {
  id: number
  nombres: string
  ape_paterno: string
  ape_materno: string
  dni: string
  area: {
    id: number
    organo: string
    siglas: string
  }
}

interface UserFormModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  userId?: number
  onSuccess?: () => void
}

export function UserFormModal({ open, onOpenChange, userId, onSuccess }: UserFormModalProps) {
  const isEditing = Boolean(userId)

  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(false)
  const [roles, setRoles] = useState<Role[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  
  const [formData, setFormData] = useState<UserFormData>({
    nombres_usuario: '',
    apellidos_usuario: '',
    username: '',
    email: '',
    tipo_usuario: 'empleado',
    nivel_acceso: 'basico',
    estado_usuario: 'activo',
    empleado: undefined,
    password: '',
    password_confirm: '',
    roles: []
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  // Cargar datos iniciales cuando se abre el modal
  useEffect(() => {
    if (open) {
      loadInitialData()
      if (isEditing && userId) {
        loadUserData(userId)
      } else {
        resetForm()
      }
    }
  }, [open, isEditing, userId])

  const loadInitialData = async () => {
    try {
      // Cargar roles activos
      const rolesData = await rolesService.getActive()
      setRoles(rolesData.data)

      // TODO: Cargar empleados disponibles
      // const employeesData = await employeesService.getAll()
      // setEmployees(employeesData)
    } catch (error) {
      console.error('Error loading initial data:', error)
      toast.error('Error al cargar los datos iniciales')
    }
  }

  const loadUserData = async (userId: number) => {
    try {
      setLoadingData(true)
      const userData = await usersService.getById(userId)
      const user = userData.data
      
      setFormData({
        nombres_usuario: user.nombres_usuario || '',
        apellidos_usuario: user.apellidos_usuario || '',
        username: user.username || '',
        email: user.email || '',
        tipo_usuario: user.tipo_usuario || 'empleado',
        nivel_acceso: user.nivel_acceso || 'basico',
        estado_usuario: user.estado_usuario || 'activo',
        empleado: user.empleado_detalle?.id,
        password: '',
        password_confirm: '',
        roles: user.roles_activos?.map(role => role.id) || []
      })
    } catch (error) {
      console.error('Error loading user:', error)
      toast.error('Error al cargar los datos del usuario')
      onOpenChange(false)
    } finally {
      setLoadingData(false)
    }
  }

  const resetForm = () => {
    setFormData({
      nombres_usuario: '',
      apellidos_usuario: '',
      username: '',
      email: '',
      tipo_usuario: 'empleado',
      nivel_acceso: 'basico',
      estado_usuario: 'activo',
      empleado: undefined,
      password: '',
      password_confirm: '',
      roles: []
    })
    setErrors({})
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    // Validaciones básicas
    if (!formData.nombres_usuario.trim()) {
      newErrors.nombres_usuario = 'Los nombres son requeridos'
    }

    if (!formData.apellidos_usuario.trim()) {
      newErrors.apellidos_usuario = 'Los apellidos son requeridos'
    }

    if (!formData.username.trim()) {
      newErrors.username = 'El nombre de usuario es requerido'
    } else if (formData.username.length < 3) {
      newErrors.username = 'El nombre de usuario debe tener al menos 3 caracteres'
    }

    if (!formData.email.trim()) {
      newErrors.email = 'El email es requerido'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'El formato del email no es válido'
    }

    // Validación de contraseña solo para usuarios nuevos
    if (!isEditing) {
      if (!formData.password) {
        newErrors.password = 'La contraseña es requerida'
      } else if (formData.password.length < 8) {
        newErrors.password = 'La contraseña debe tener al menos 8 caracteres'
      }

      if (formData.password !== formData.password_confirm) {
        newErrors.password_confirm = 'Las contraseñas no coinciden'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    try {
      setLoading(true)
      
      if (isEditing && userId) {
        await usersService.update(userId, formData)
        toast.success('Usuario actualizado correctamente')
      } else {
        await usersService.create(formData)
        toast.success('Usuario creado correctamente')
      }
      
      onSuccess?.()
      onOpenChange(false)
    } catch (error: any) {
      console.error('Error saving user:', error)
      
      if (error.response?.data?.errors) {
        setErrors(error.response.data.errors)
      } else {
        toast.error(error.response?.data?.message || 'Error al guardar el usuario')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (field: keyof UserFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Limpiar error del campo cuando el usuario empiece a escribir
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const handleRoleToggle = (roleId: number, checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      roles: checked 
        ? [...(prev.roles || []), roleId]
        : (prev.roles || []).filter(id => id !== roleId)
    }))
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            {isEditing ? 'Editar Usuario' : 'Crear Nuevo Usuario'}
          </DialogTitle>
          <DialogDescription>
            {isEditing 
              ? 'Modifica los datos del usuario seleccionado'
              : 'Completa los datos para crear un nuevo usuario en el sistema'
            }
          </DialogDescription>
        </DialogHeader>

        {loadingData ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner />
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Información Personal */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm font-medium">
                <User className="h-4 w-4" />
                Información Personal
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="nombres_usuario">Nombres *</Label>
                  <Input
                    id="nombres_usuario"
                    value={formData.nombres_usuario}
                    onChange={(e) => handleInputChange('nombres_usuario', e.target.value)}
                    placeholder="Ingresa los nombres"
                    className={errors.nombres_usuario ? 'border-red-500' : ''}
                  />
                  {errors.nombres_usuario && (
                    <p className="text-sm text-red-500">{errors.nombres_usuario}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="apellidos_usuario">Apellidos *</Label>
                  <Input
                    id="apellidos_usuario"
                    value={formData.apellidos_usuario}
                    onChange={(e) => handleInputChange('apellidos_usuario', e.target.value)}
                    placeholder="Ingresa los apellidos"
                    className={errors.apellidos_usuario ? 'border-red-500' : ''}
                  />
                  {errors.apellidos_usuario && (
                    <p className="text-sm text-red-500">{errors.apellidos_usuario}</p>
                  )}
                </div>
              </div>
            </div>

            <Separator />

            {/* Información de Cuenta */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm font-medium">
                <Mail className="h-4 w-4" />
                Información de Cuenta
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Nombre de Usuario *</Label>
                  <Input
                    id="username"
                    value={formData.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    placeholder="Ingresa el nombre de usuario"
                    className={errors.username ? 'border-red-500' : ''}
                  />
                  {errors.username && (
                    <p className="text-sm text-red-500">{errors.username}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    placeholder="Ingresa el email"
                    className={errors.email ? 'border-red-500' : ''}
                  />
                  {errors.email && (
                    <p className="text-sm text-red-500">{errors.email}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Contraseña (solo para usuarios nuevos) */}
            {!isEditing && (
              <>
                <Separator />
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <Lock className="h-4 w-4" />
                    Contraseña
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="password">Contraseña *</Label>
                      <Input
                        id="password"
                        type="password"
                        value={formData.password}
                        onChange={(e) => handleInputChange('password', e.target.value)}
                        placeholder="Ingresa la contraseña"
                        className={errors.password ? 'border-red-500' : ''}
                      />
                      {errors.password && (
                        <p className="text-sm text-red-500">{errors.password}</p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="password_confirm">Confirmar Contraseña *</Label>
                      <Input
                        id="password_confirm"
                        type="password"
                        value={formData.password_confirm}
                        onChange={(e) => handleInputChange('password_confirm', e.target.value)}
                        placeholder="Confirma la contraseña"
                        className={errors.password_confirm ? 'border-red-500' : ''}
                      />
                      {errors.password_confirm && (
                        <p className="text-sm text-red-500">{errors.password_confirm}</p>
                      )}
                    </div>
                  </div>
                </div>
              </>
            )}

            <Separator />

            {/* Configuración de Usuario */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm font-medium">
                <Shield className="h-4 w-4" />
                Configuración de Usuario
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="tipo_usuario">Tipo de Usuario</Label>
                  <Select
                    value={formData.tipo_usuario}
                    onValueChange={(value) => handleInputChange('tipo_usuario', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona el tipo" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="empleado">Empleado</SelectItem>
                      <SelectItem value="administrador">Administrador</SelectItem>
                      <SelectItem value="supervisor">Supervisor</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="nivel_acceso">Nivel de Acceso</Label>
                  <Select
                    value={formData.nivel_acceso}
                    onValueChange={(value) => handleInputChange('nivel_acceso', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona el nivel" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="basico">Básico</SelectItem>
                      <SelectItem value="intermedio">Intermedio</SelectItem>
                      <SelectItem value="avanzado">Avanzado</SelectItem>
                      <SelectItem value="total">Total</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="estado_usuario">Estado</Label>
                  <Select
                    value={formData.estado_usuario}
                    onValueChange={(value) => handleInputChange('estado_usuario', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona el estado" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="activo">Activo</SelectItem>
                      <SelectItem value="inactivo">Inactivo</SelectItem>
                      <SelectItem value="suspendido">Suspendido</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            {/* Roles */}
            {roles && roles.length > 0 && (
              <>
                <Separator />
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <Shield className="h-4 w-4" />
                    Roles del Usuario
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {roles.map((role) => (
                      <div key={role.id} className="flex items-center space-x-2">
                        <Checkbox
                          id={`role-${role.id}`}
                          checked={formData.roles?.includes(role.id) || false}
                          onCheckedChange={(checked) => handleRoleToggle(role.id, checked as boolean)}
                        />
                        <Label
                          htmlFor={`role-${role.id}`}
                          className="text-sm font-normal cursor-pointer"
                        >
                          {role.nombre_rol}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={loading}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <LoadingSpinner className="mr-2" />
                ) : (
                  <Save className="mr-2 h-4 w-4" />
                )}
                {isEditing ? 'Actualizar Usuario' : 'Crear Usuario'}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}