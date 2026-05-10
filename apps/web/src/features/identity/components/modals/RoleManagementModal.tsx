import React, { useState, useEffect } from 'react'
import {
  Shield,
  Plus,
  Minus,
  Search,
  Check,
  X,
  Users,
  Settings
} from 'lucide-react'
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
import { Badge } from '@/shared/ui/badge'
import { Checkbox } from '@/shared/ui/checkbox'
import { Alert, AlertDescription } from '@/shared/ui/alert'
// import { ScrollArea } from '@/shared/ui/scroll-area' // Componente no disponible
import { toast } from 'sonner'
import {
  usersService,
  rolesService,
  type User,
  type Role,
} from '@/features/identity/services/usersService'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'

interface RoleManagementModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  userId: string
  onSuccess?: () => void
}

export function RoleManagementModal({ open, onOpenChange, userId, onSuccess }: RoleManagementModalProps) {
  const [user, setUser] = useState<User | null>(null)
  const [availableRoles, setAvailableRoles] = useState<Role[]>([])
  const [userRoles, setUserRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRoles, setSelectedRoles] = useState<Set<string>>(new Set())
  const [isInitialized, setIsInitialized] = useState(false)

  // Cargar datos cuando se abre el modal
  useEffect(() => {
    if (open && userId) {
      // No resetear selectedRoles aquí, se hará en loadData
      setIsInitialized(false)
      loadData(userId)
      setSearchTerm('')
    }
  }, [open, userId]) // eslint-disable-line react-hooks/exhaustive-deps -- loadData re-created each render; adding it would cause infinite loop

  // Efecto para inicializar selectedRoles cuando userRoles cambie
  useEffect(() => {

    if (userRoles.length > 0 || isInitialized) {
      const currentRoleIds = new Set(userRoles.map(role => role.id))
  
      setSelectedRoles(currentRoleIds)
      setIsInitialized(true)
    }
  }, [userRoles, isInitialized])

  const loadData = async (userId: string) => {
    try {
      setLoading(true)
      setIsInitialized(false) // Reset initialization state
  
      
      const [userData, rolesData] = await Promise.all([
        usersService.getById(userId),
        rolesService.getActive()
      ])
      

      
      setUser(userData.data)
      // Manejar la estructura de respuesta del servicio de roles
      const availableRolesList = rolesData?.data || rolesData || []
      setAvailableRoles(availableRolesList)
      
      // Asegurar que roles_activos sea un array válido
      const activeRoles = userData.data.roles_activos || []

      setUserRoles(activeRoles)
      

      
      // Marcar como inicializado después de cargar los datos
      setIsInitialized(true)

    } catch (error) {
      console.error('Error loading data:', error)
      console.error('Error details:', error.response?.data || error.message)
      toast.error(`Error al cargar los datos: ${error.response?.data?.message || error.message}`)
      onOpenChange(false)
    } finally {
      setLoading(false)
    }
  }

  const filteredRoles = (availableRoles || []).filter(role =>
    role.nombre_rol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    role.descripcion_rol?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleRoleToggle = (roleId: string, _isCurrentlyAssigned: boolean) => { // param kept for caller compatibility
    // Simplemente alternar la selección del rol
    if (selectedRoles.has(roleId)) {
      // Si está seleccionado, deseleccionarlo
      setSelectedRoles(prev => {
        const newSet = new Set(prev)
        newSet.delete(roleId)
        return newSet
      })
    } else {
      // Si no está seleccionado, seleccionarlo
      setSelectedRoles(prev => new Set([...prev, roleId]))
    }
  }

  const getRoleStatus = (roleId: string) => {
    const isCurrentlyAssigned = userRoles.some(role => role.id === roleId)
    const isSelected = selectedRoles.has(roleId)
    
    

    if (isCurrentlyAssigned && isSelected) {
      return 'assigned'
    } else if (isCurrentlyAssigned && !isSelected) {
      return 'to-remove'
    } else if (!isCurrentlyAssigned && isSelected) {
      return 'to-add'
    } else {
      return 'unassigned'
    }
  }

  const getRoleStatusBadge = (status: string) => {
    switch (status) {
      case 'assigned':
        return <Badge variant="default" className="bg-green-100 text-green-800">Asignado</Badge>
      case 'to-remove':
        return <Badge variant="destructive">A Remover</Badge>
      case 'to-add':
        return <Badge variant="default" className="bg-blue-100 text-blue-800">A Agregar</Badge>
      default:
        return <Badge variant="outline">No Asignado</Badge>
    }
  }

  const getChangesCount = () => {
    const rolesToAdd = Array.from(selectedRoles).filter(roleId => 
      !userRoles.some(role => role.id === roleId)
    )
    
    // Calcular roles a remover: roles actuales del usuario que ya no están seleccionados
    const rolesToRemoveCount = userRoles.filter(role => !selectedRoles.has(role.id)).length
    
    return {
      toAdd: rolesToAdd.length,
      toRemove: rolesToRemoveCount,
      total: rolesToAdd.length + rolesToRemoveCount
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const changes = getChangesCount()
    if (changes.total === 0) {
      toast.info('No hay cambios para aplicar')
      return
    }

    try {
      setSubmitting(true)
      
      const rolesToAdd = Array.from(selectedRoles).filter(roleId => 
        !userRoles.some(role => role.id === roleId)
      )
      
      // Calcular roles a remover: roles actuales del usuario que ya no están seleccionados
      const rolesToRemoveArray = userRoles
        .filter(role => !selectedRoles.has(role.id))
        .map(role => role.id)
      
      // Procesar asignaciones y remociones por separado
      const promises = []
      
      // Asignar nuevos roles
      if (rolesToAdd.length > 0) {
        const assignmentData = {
          roles: rolesToAdd
        }
        promises.push(usersService.assignUserRoles(userId, assignmentData))
      }
      
      // Remover roles
      for (const rolId of rolesToRemoveArray) {
        promises.push(usersService.removeUserRole(userId, rolId))
      }
      
      await Promise.all(promises)
      
      toast.success(`Roles actualizados correctamente. ${changes.toAdd} agregados, ${changes.toRemove} removidos.`)
      onSuccess?.()
      onOpenChange(false)
    } catch (error) {
      console.error('Error updating roles:', error)
      const err = error as { response?: { data?: { message?: string } } }
      toast.error(err.response?.data?.message || 'Error al actualizar los roles')
    } finally {
      setSubmitting(false)
    }
  }

  const handleSelectAll = () => {
    // Solo seleccionar roles que no están actualmente asignados
    const currentRoleIds = new Set(userRoles.map(role => role.id))
    const unassignedRoleIds = filteredRoles
      .filter(role => !currentRoleIds.has(role.id))
      .map(role => role.id)
    
    // Combinar roles actualmente asignados con todos los no asignados
    const newSelectedRoles = new Set([...currentRoleIds, ...unassignedRoleIds])
    setSelectedRoles(newSelectedRoles)
  }

  const handleDeselectAll = () => {
    // Solo mantener los roles que están actualmente asignados
    const currentRoleIds = new Set(userRoles.map(role => role.id))
    setSelectedRoles(currentRoleIds)
  }

  const handleResetChanges = () => {
    const currentRoleIds = new Set(userRoles.map(role => role.id))
    setSelectedRoles(currentRoleIds)
  }

  const changes = getChangesCount()

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Gestión de Roles
          </DialogTitle>
          <DialogDescription>
            {user && (
              <span>
                Administrar roles para <strong>{user.nombres_usuario} {user.apellidos_usuario}</strong>
              </span>
            )}
          </DialogDescription>
        </DialogHeader>

        {loading ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Información del Usuario */}
            {user && (
              <div className="bg-muted/50 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <Users className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{user.nombres_usuario} {user.apellidos_usuario}</p>
                      <p className="text-sm text-muted-foreground">{user.email}</p>
                      <p className="text-xs text-muted-foreground">
                        Usuario: {user.username} • Tipo: {user.tipo_usuario}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">
                      Roles Actuales: {userRoles.length}
                    </p>
                    {changes.total > 0 && (
                      <p className="text-xs text-muted-foreground">
                        Cambios pendientes: {changes.total}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Controles de Búsqueda y Acciones */}
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar roles por nombre o descripción..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleSelectAll}
                  disabled={submitting}
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Todos
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleDeselectAll}
                  disabled={submitting}
                >
                  <Minus className="h-4 w-4 mr-1" />
                  Ninguno
                </Button>
                {changes.total > 0 && (
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleResetChanges}
                    disabled={submitting}
                  >
                    <X className="h-4 w-4 mr-1" />
                    Resetear
                  </Button>
                )}
              </div>
            </div>

            {/* Lista de Roles */}
            <div className="border rounded-lg">
              <div className="p-4 border-b bg-muted/30">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">Roles Disponibles</h3>
                  <span className="text-sm text-muted-foreground">
                    {filteredRoles.length} de {(availableRoles || []).length} roles
                  </span>
                </div>
              </div>
              
              <div className="h-[400px] overflow-y-auto">
                <div className="p-4 space-y-3">
                  {filteredRoles.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      {searchTerm ? 'No se encontraron roles que coincidan con la búsqueda' : 'No hay roles disponibles'}
                    </div>
                  ) : (
                    filteredRoles.map((role) => {
                      const status = getRoleStatus(role.id)
                      const isCurrentlyAssigned = userRoles.some(r => r.id === role.id)
                      const isChecked = selectedRoles.has(role.id)
                      
              
                      
                      return (
                        <div
                          key={role.id}
                          className={`flex items-center justify-between p-3 border rounded-lg transition-colors ${
                            status === 'to-remove' ? 'bg-red-50 border-red-200' :
                            status === 'to-add' ? 'bg-blue-50 border-blue-200' :
                            status === 'assigned' ? 'bg-green-50 border-green-200' :
                            'hover:bg-muted/50'
                          }`}
                        >
                          <div className="flex items-center space-x-3">
                            <Checkbox
                              checked={isChecked}
                              onCheckedChange={() => handleRoleToggle(role.id, isCurrentlyAssigned)}
                              disabled={submitting}
                            />
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <h4 className="font-medium">{role.nombre_rol}</h4>
                                {getRoleStatusBadge(status)}
                              </div>
                              {role.descripcion_rol && (
                                <p className="text-sm text-muted-foreground mt-1">
                                  {role.descripcion_rol}
                                </p>
                              )}
                              <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                                <span key={`nivel-${role.id}`}>Nivel: {role.nivel_rol}</span>
                                <span key={`estado-${role.id}`}>Estado: {role.estado_rol}</span>
                                {role.created_at && (
                                  <span key={`fecha-${role.id}`}>Creado: {new Date(role.created_at).toLocaleDateString()}</span>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex items-center">
                            {status === 'assigned' && (
                              <Check className="h-5 w-5 text-green-600" />
                            )}
                            {status === 'to-remove' && (
                              <X className="h-5 w-5 text-red-600" />
                            )}
                            {status === 'to-add' && (
                              <Plus className="h-5 w-5 text-blue-600" />
                            )}
                          </div>
                        </div>
                      )
                    })
                  )}
                </div>
              </div>
            </div>

            {/* Resumen de Cambios */}
            {changes.total > 0 && (
              <Alert>
                <Settings className="h-4 w-4" />
                <AlertDescription>
                  <strong>Cambios pendientes:</strong>
                  {changes.toAdd > 0 && (
                    <span key="changes-add" className="ml-2 text-blue-600">
                      {changes.toAdd} rol(es) a agregar
                    </span>
                  )}
                  {changes.toAdd > 0 && changes.toRemove > 0 && <span key="changes-separator" className="mx-1">•</span>}
                  {changes.toRemove > 0 && (
                    <span key="changes-remove" className="text-red-600">
                      {changes.toRemove} rol(es) a remover
                    </span>
                  )}
                </AlertDescription>
              </Alert>
            )}

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={submitting}
              >
                Cancelar
              </Button>
              <Button
                onClick={handleSubmit}
                disabled={submitting || changes.total === 0}
              >
                {submitting ? (
                  <LoadingSpinner className="mr-2" />
                ) : (
                  <Shield className="mr-2 h-4 w-4" />
                )}
                Aplicar Cambios ({changes.total})
              </Button>
            </DialogFooter>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}