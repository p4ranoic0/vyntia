import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, 
  Shield, 
  Plus, 
  Minus, 
  Search, 
  Check, 
  X,
  AlertTriangle,
  Users,
  Settings
} from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import { Badge } from '@/shared/ui/badge'
import { Checkbox } from '@/shared/ui/checkbox'
import { Alert, AlertDescription } from '@/shared/ui/alert'
import { Separator } from '@/shared/ui/separator'
import { toast } from 'sonner'
import { 
  usersService, 
  rolesService, 
  type User, 
  type Role, 
  type UserRoleAssignment 
} from '@/services/usersService'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { UsersLayout } from '@/components/layout/UsersLayout'

export function RoleManagement() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [user, setUser] = useState<User | null>(null)
  const [availableRoles, setAvailableRoles] = useState<Role[]>([])
  const [userRoles, setUserRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRoles, setSelectedRoles] = useState<Set<string>>(new Set())
  const [rolesToRemove, setRolesToRemove] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (id) {
      loadData(id)
    }
  }, [id])

  const loadData = async (userId: string) => {
    try {
      setLoading(true)
      const [userData, rolesData] = await Promise.all([
        usersService.getById(userId),
        rolesService.getActive()
      ])
      
      setUser(userData)
      setAvailableRoles(rolesData)
      setUserRoles(userData.roles_activos || [])
      
      // Inicializar roles seleccionados con los roles actuales del usuario
      const currentRoleIds = new Set(userData.roles_activos?.map(role => role.id) || [])
      setSelectedRoles(currentRoleIds)
    } catch (error) {
      console.error('Error loading data:', error)
      toast.error('Error al cargar los datos')
      navigate('/usuarios/listado')
    } finally {
      setLoading(false)
    }
  }

  const filteredRoles = availableRoles.filter(role =>
    role.nombre_rol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    role.descripcion_rol?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleRoleToggle = (roleId: string, isCurrentlyAssigned: boolean) => {
    if (isCurrentlyAssigned) {
      // Si el rol está actualmente asignado, marcarlo para remover
      if (rolesToRemove.has(roleId)) {
        setRolesToRemove(prev => {
          const newSet = new Set(prev)
          newSet.delete(roleId)
          return newSet
        })
        setSelectedRoles(prev => new Set([...prev, roleId]))
      } else {
        setRolesToRemove(prev => new Set([...prev, roleId]))
        setSelectedRoles(prev => {
          const newSet = new Set(prev)
          newSet.delete(roleId)
          return newSet
        })
      }
    } else {
      // Si el rol no está asignado, agregarlo o quitarlo de la selección
      if (selectedRoles.has(roleId)) {
        setSelectedRoles(prev => {
          const newSet = new Set(prev)
          newSet.delete(roleId)
          return newSet
        })
      } else {
        setSelectedRoles(prev => new Set([...prev, roleId]))
      }
    }
  }

  const getRoleStatus = (roleId: string) => {
    const isCurrentlyAssigned = userRoles.some(role => role.id === roleId)
    const isSelected = selectedRoles.has(roleId)
    const isMarkedForRemoval = rolesToRemove.has(roleId)

    if (isCurrentlyAssigned && !isMarkedForRemoval) {
      return { status: 'assigned', label: 'Asignado', variant: 'success' as const }
    }
    if (isCurrentlyAssigned && isMarkedForRemoval) {
      return { status: 'removing', label: 'Se removerá', variant: 'destructive' as const }
    }
    if (!isCurrentlyAssigned && isSelected) {
      return { status: 'adding', label: 'Se asignará', variant: 'secondary' as const }
    }
    return { status: 'available', label: 'Disponible', variant: 'outline' as const }
  }

  const getChangeSummary = () => {
    const rolesToAdd = Array.from(selectedRoles).filter(
      roleId => !userRoles.some(role => role.id === roleId)
    )
    const rolesToRemoveArray = Array.from(rolesToRemove)

    return {
      toAdd: rolesToAdd.length,
      toRemove: rolesToRemoveArray.length,
      hasChanges: rolesToAdd.length > 0 || rolesToRemoveArray.length > 0
    }
  }

  const handleSubmit = async () => {
    if (!user) return

    const summary = getChangeSummary()
    if (!summary.hasChanges) {
      toast.info('No hay cambios para aplicar')
      return
    }

    try {
      setSubmitting(true)
      
      const assignment: UserRoleAssignment = {
        user_id: user.id,
        role_ids: Array.from(selectedRoles),
        remove_existing: true // Esto reemplazará todos los roles existentes
      }

      await usersService.assignRoles(assignment)
      
      toast.success('Roles actualizados exitosamente', {
        description: `${summary.toAdd} roles asignados, ${summary.toRemove} roles removidos`
      })
      
      // Recargar datos para reflejar los cambios
      await loadData(user.id)
      
      // Limpiar estados de cambios
      setRolesToRemove(new Set())
      
    } catch (error: any) {
      console.error('Error updating roles:', error)
      toast.error('Error al actualizar los roles')
    } finally {
      setSubmitting(false)
    }
  }

  const handleReset = () => {
    const currentRoleIds = new Set(userRoles.map(role => role.id))
    setSelectedRoles(currentRoleIds)
    setRolesToRemove(new Set())
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

  const changeSummary = getChangeSummary()

  return (
    <UsersLayout 
      title="Gestión de Roles y Permisos"
      description="Administra los roles y permisos asignados a los usuarios"
    >
      {/* Header Actions */}
      <div className="flex items-center justify-between mb-6">
        <Button variant="outline" onClick={() => navigate(`/usuarios/gestion/${user.id}`)}>
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
        {/* Panel principal de roles */}
        <div className="lg:col-span-2 space-y-6">
          {/* Buscador */}
          <Card>
            <CardHeader>
              <CardTitle>Roles Disponibles</CardTitle>
              <CardDescription>
                Selecciona los roles que deseas asignar al usuario
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  placeholder="Buscar roles..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>

              {/* Lista de roles */}
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {filteredRoles.map((role) => {
                  const isCurrentlyAssigned = userRoles.some(userRole => userRole.id === role.id)
                  const roleStatus = getRoleStatus(role.id)
                  
                  return (
                    <div
                      key={role.id}
                      className={`border rounded-lg p-4 transition-all duration-200 ${
                        roleStatus.status === 'removing' ? 'border-red-200 bg-red-50' :
                        roleStatus.status === 'adding' ? 'border-green-200 bg-green-50' :
                        roleStatus.status === 'assigned' ? 'border-blue-200 bg-blue-50' :
                        'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <Checkbox
                          checked={selectedRoles.has(role.id) && !rolesToRemove.has(role.id)}
                          onCheckedChange={() => handleRoleToggle(role.id, isCurrentlyAssigned)}
                          className="mt-1"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-sm">{role.nombre_rol}</h4>
                            <Badge variant={roleStatus.variant}>
                              {roleStatus.label}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mb-3">
                            {role.descripcion_rol || 'Sin descripción'}
                          </p>
                          
                          {/* Permisos del rol */}
                          {role.permisos && role.permisos.length > 0 && (
                            <div>
                              <p className="text-xs font-medium text-muted-foreground mb-2">
                                Permisos ({role.permisos.length}):
                              </p>
                              <div className="flex flex-wrap gap-1">
                                {role.permisos.slice(0, 3).map((permiso) => (
                                  <Badge key={permiso.id} variant="outline" className="text-xs">
                                    {permiso.nombre_permiso}
                                  </Badge>
                                ))}
                                {role.permisos.length > 3 && (
                                  <Badge variant="outline" className="text-xs">
                                    +{role.permisos.length - 3} más
                                  </Badge>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
                
                {filteredRoles.length === 0 && (
                  <div className="text-center py-8">
                    <Shield className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No se encontraron roles</h3>
                    <p className="text-muted-foreground">
                      {searchTerm ? 'Intenta con otros términos de búsqueda' : 'No hay roles disponibles'}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Panel lateral */}
        <div className="space-y-6">
          {/* Información del usuario */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Users className="w-5 h-5" />
                Usuario
              </CardTitle>
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
                <p className="text-sm font-medium text-muted-foreground">Tipo</p>
                <Badge variant="outline">{user.tipo_usuario}</Badge>
              </div>
            </CardContent>
          </Card>

          {/* Resumen de cambios */}
          {changeSummary.hasChanges && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Resumen de Cambios
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {changeSummary.toAdd > 0 && (
                  <div className="flex items-center gap-2 text-green-600">
                    <Plus className="w-4 h-4" />
                    <span className="text-sm">{changeSummary.toAdd} roles se asignarán</span>
                  </div>
                )}
                {changeSummary.toRemove > 0 && (
                  <div className="flex items-center gap-2 text-red-600">
                    <Minus className="w-4 h-4" />
                    <span className="text-sm">{changeSummary.toRemove} roles se removerán</span>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Roles actuales */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Roles Actuales</CardTitle>
              <CardDescription>
                {userRoles.length} roles asignados
              </CardDescription>
            </CardHeader>
            <CardContent>
              {userRoles.length > 0 ? (
                <div className="space-y-2">
                  {userRoles.map((role) => (
                    <div key={role.id} className="flex items-center justify-between">
                      <span className="text-sm">{role.nombre_rol}</span>
                      {rolesToRemove.has(role.id) ? (
                        <Badge variant="destructive" className="text-xs">
                          <X className="w-3 h-3 mr-1" />
                          Se removerá
                        </Badge>
                      ) : (
                        <Badge variant="success" className="text-xs">
                          <Check className="w-3 h-3 mr-1" />
                          Activo
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Sin roles asignados</p>
              )}
            </CardContent>
          </Card>

          {/* Advertencia */}
          <Alert>
            <AlertTriangle className="w-4 h-4" />
            <AlertDescription className="text-sm">
              <strong>Importante:</strong> Los cambios en los roles afectarán inmediatamente 
              los permisos del usuario en el sistema.
            </AlertDescription>
          </Alert>

          {/* Botones de acción */}
          <div className="space-y-3">
            <Button
              onClick={handleSubmit}
              disabled={!changeSummary.hasChanges || submitting}
              className="w-full"
            >
              {submitting ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Aplicando cambios...
                </>
              ) : (
                <>
                  <Check className="w-4 h-4 mr-2" />
                  Aplicar Cambios
                </>
              )}
            </Button>
            
            <Button
              variant="outline"
              onClick={handleReset}
              disabled={!changeSummary.hasChanges || submitting}
              className="w-full"
            >
              <X className="w-4 h-4 mr-2" />
              Descartar Cambios
            </Button>
            
            <Button
              variant="ghost"
              onClick={() => navigate(`/usuarios/gestion/${user.id}`)}
              disabled={submitting}
              className="w-full"
            >
              Cancelar
            </Button>
          </div>
        </div>
      </div>
    </UsersLayout>
  )
}

export default RoleManagement