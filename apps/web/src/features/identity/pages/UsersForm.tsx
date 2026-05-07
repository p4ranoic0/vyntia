import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Save, User, Mail, Lock, Shield, Building2 } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Separator } from '@/shared/ui/separator'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui/select'
import { Checkbox } from '@/shared/ui/checkbox'
import { toast } from 'sonner'
import { usersService, rolesService, type UserFormData, type Role } from '@/features/identity/services/usersService'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { UsersLayout } from '@/components/layout/UsersLayout'

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

export function UsersForm() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const isEditing = Boolean(id)

  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(isEditing)
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

  // Cargar datos iniciales
  useEffect(() => {
    loadInitialData()
  }, [])

  // Cargar usuario para edición
  useEffect(() => {
    if (isEditing && id) {
      loadUserData(parseInt(id))
    }
  }, [isEditing, id])

  const loadInitialData = async () => {
    try {
      // Cargar roles activos
      const rolesData = await rolesService.getActive()
      setRoles(rolesData)

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
      const user = await usersService.getById(userId)
      
      setFormData({
        nombres_usuario: user.nombres_usuario || '',
        apellidos_usuario: user.apellidos_usuario || '',
        username: user.username || '',
        email: user.email || '',
        tipo_usuario: user.tipo_usuario || 'empleado',
        nivel_acceso: user.nivel_acceso || 'basico',
        estado_usuario: user.estado_usuario || 'activo',
        empleado: user.empleado?.id,
        roles: user.roles_activos?.map(role => role.id) || []
      })
    } catch (error) {
      console.error('Error loading user:', error)
      toast.error('Error al cargar los datos del usuario')
      navigate('/usuarios/listado')
    } finally {
      setLoadingData(false)
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

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
      newErrors.email = 'El email no tiene un formato válido'
    }

    if (!isEditing) {
      if (!formData.password) {
        newErrors.password = 'La contraseña es requerida'
      } else if (formData.password.length < 8) {
        newErrors.password = 'La contraseña debe tener al menos 8 caracteres'
      }

      if (!formData.password_confirm) {
        newErrors.password_confirm = 'Confirma la contraseña'
      } else if (formData.password !== formData.password_confirm) {
        newErrors.password_confirm = 'Las contraseñas no coinciden'
      }
    }

    if (!formData.tipo_usuario) {
      newErrors.tipo_usuario = 'El tipo de usuario es requerido'
    }

    if (!formData.nivel_acceso) {
      newErrors.nivel_acceso = 'El nivel de acceso es requerido'
    }

    if (!formData.estado_usuario) {
      newErrors.estado_usuario = 'El estado es requerido'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      toast.error('Por favor corrige los errores en el formulario')
      return
    }

    try {
      setLoading(true)
      
      if (isEditing && id) {
        await usersService.update(parseInt(id), formData)
        toast.success('Usuario actualizado correctamente')
      } else {
        await usersService.create(formData)
        toast.success('Usuario creado correctamente')
      }
      
      navigate('/usuarios/listado')
    } catch (error) {
      console.error('Error saving user:', error)
      toast.error(isEditing ? 'Error al actualizar el usuario' : 'Error al crear el usuario')
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

  const handleRoleChange = (roleId: number, checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      roles: checked 
        ? [...(prev.roles || []), roleId]
        : (prev.roles || []).filter(id => id !== roleId)
    }))
  }

  if (loadingData) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <UsersLayout 
      title={isEditing ? 'Editar Usuario' : 'Crear Usuario'}
      description={isEditing ? 'Modifica los datos del usuario seleccionado' : 'Completa la información para crear un nuevo usuario'}
    >
      {/* Header Actions */}
      <div className="flex items-center justify-between mb-6">
        <Button variant="outline" onClick={() => navigate('/usuarios/listado')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver al Listado
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Información Personal */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              Información Personal
            </CardTitle>
            <CardDescription>
              Datos básicos del usuario
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="nombres_usuario">Nombres *</Label>
                <Input
                  id="nombres_usuario"
                  value={formData.nombres_usuario}
                  onChange={(e) => handleInputChange('nombres_usuario', e.target.value)}
                  placeholder="Ingresa los nombres"
                  className={errors.nombres_usuario ? 'border-destructive' : ''}
                />
                {errors.nombres_usuario && (
                  <p className="text-sm text-destructive">{errors.nombres_usuario}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="apellidos_usuario">Apellidos *</Label>
                <Input
                  id="apellidos_usuario"
                  value={formData.apellidos_usuario}
                  onChange={(e) => handleInputChange('apellidos_usuario', e.target.value)}
                  placeholder="Ingresa los apellidos"
                  className={errors.apellidos_usuario ? 'border-destructive' : ''}
                />
                {errors.apellidos_usuario && (
                  <p className="text-sm text-destructive">{errors.apellidos_usuario}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Información de Cuenta */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="w-5 h-5" />
              Información de Cuenta
            </CardTitle>
            <CardDescription>
              Credenciales de acceso al sistema
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="username">Nombre de Usuario *</Label>
                <Input
                  id="username"
                  value={formData.username}
                  onChange={(e) => handleInputChange('username', e.target.value)}
                  placeholder="Ingresa el nombre de usuario"
                  className={errors.username ? 'border-destructive' : ''}
                />
                {errors.username && (
                  <p className="text-sm text-destructive">{errors.username}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  placeholder="usuario@ejemplo.com"
                  className={errors.email ? 'border-destructive' : ''}
                />
                {errors.email && (
                  <p className="text-sm text-destructive">{errors.email}</p>
                )}
              </div>
            </div>

            {!isEditing && (
              <>
                <Separator />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="password">Contraseña *</Label>
                    <Input
                      id="password"
                      type="password"
                      value={formData.password}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      placeholder="Ingresa la contraseña"
                      className={errors.password ? 'border-destructive' : ''}
                    />
                    {errors.password && (
                      <p className="text-sm text-destructive">{errors.password}</p>
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
                      className={errors.password_confirm ? 'border-destructive' : ''}
                    />
                    {errors.password_confirm && (
                      <p className="text-sm text-destructive">{errors.password_confirm}</p>
                    )}
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Configuración de Usuario */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Configuración de Usuario
            </CardTitle>
            <CardDescription>
              Tipo de usuario, nivel de acceso y estado
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="tipo_usuario">Tipo de Usuario *</Label>
                <Select
                  value={formData.tipo_usuario}
                  onValueChange={(value) => handleInputChange('tipo_usuario', value)}
                >
                  <SelectTrigger className={errors.tipo_usuario ? 'border-destructive' : ''}>
                    <SelectValue placeholder="Selecciona el tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="administrador">Administrador</SelectItem>
                    <SelectItem value="supervisor">Supervisor</SelectItem>
                    <SelectItem value="empleado">Empleado</SelectItem>
                    <SelectItem value="invitado">Invitado</SelectItem>
                  </SelectContent>
                </Select>
                {errors.tipo_usuario && (
                  <p className="text-sm text-destructive">{errors.tipo_usuario}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="nivel_acceso">Nivel de Acceso *</Label>
                <Select
                  value={formData.nivel_acceso}
                  onValueChange={(value) => handleInputChange('nivel_acceso', value)}
                >
                  <SelectTrigger className={errors.nivel_acceso ? 'border-destructive' : ''}>
                    <SelectValue placeholder="Selecciona el nivel" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="alto">Alto</SelectItem>
                    <SelectItem value="medio">Medio</SelectItem>
                    <SelectItem value="basico">Básico</SelectItem>
                  </SelectContent>
                </Select>
                {errors.nivel_acceso && (
                  <p className="text-sm text-destructive">{errors.nivel_acceso}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="estado_usuario">Estado *</Label>
                <Select
                  value={formData.estado_usuario}
                  onValueChange={(value) => handleInputChange('estado_usuario', value)}
                >
                  <SelectTrigger className={errors.estado_usuario ? 'border-destructive' : ''}>
                    <SelectValue placeholder="Selecciona el estado" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="activo">Activo</SelectItem>
                    <SelectItem value="inactivo">Inactivo</SelectItem>
                    <SelectItem value="suspendido">Suspendido</SelectItem>
                  </SelectContent>
                </Select>
                {errors.estado_usuario && (
                  <p className="text-sm text-destructive">{errors.estado_usuario}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Asignación de Roles */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Asignación de Roles
            </CardTitle>
            <CardDescription>
              Selecciona los roles que tendrá el usuario
            </CardDescription>
          </CardHeader>
          <CardContent>
            {roles.length === 0 ? (
              <p className="text-muted-foreground">No hay roles disponibles</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {roles.map((role) => (
                  <div key={role.id} className="flex items-center space-x-2">
                    <Checkbox
                      id={`role-${role.id}`}
                      checked={formData.roles?.includes(role.id) || false}
                      onCheckedChange={(checked) => handleRoleChange(role.id, checked as boolean)}
                    />
                    <Label htmlFor={`role-${role.id}`} className="text-sm font-medium">
                      {role.nombre_rol}
                    </Label>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Botones de acción */}
        <div className="flex justify-end gap-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate('/usuarios/listado')}
            disabled={loading}
          >
            Cancelar
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? (
              <LoadingSpinner size="sm" className="mr-2" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            {isEditing ? 'Actualizar Usuario' : 'Crear Usuario'}
          </Button>
        </div>
      </form>
    </UsersLayout>
  )
}

export default UsersForm