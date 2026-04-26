import React, { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Settings, Search, Save, X, Check, Key, UserCog, Plus, Minus, FolderOpen, User, FileText, Calendar, DollarSign, BarChart3 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { useToast } from '@/components/ui/use-toast'
import { apiClient } from '@/lib/api'
import { roleService, permissionService, rolePermissionService } from '@/services/securityService'

// Importar interfaces del servicio
import { Role, Permission, RolePermission } from '@/services/securityService'

export default function RolePermissionsPage() {// Estados
  const [selectedRoleId, setSelectedRoleId] = useState<string>('')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedPermissions, setSelectedPermissions] = useState<Set<number>>(new Set())
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  const { toast } = useToast()
  const queryClient = useQueryClient()

  // Query para obtener roles
  const { data: roles = [], isLoading: rolesLoading } = useQuery({
    queryKey: ['roles'],
    queryFn: roleService.getAll
  })

  // Query para obtener permisos
  const { data: permissions = [], isLoading: permissionsLoading } = useQuery({
    queryKey: ['permissions'],
    queryFn: permissionService.getAll
  })

  // Query para obtener permisos del rol seleccionado
  const { data: rolePermissions = [], isLoading: rolePermissionsLoading } = useQuery({
    queryKey: ['role-permissions', selectedRoleId],
    queryFn: async () => {
      const result = await rolePermissionService.getByRole(selectedRoleId!)
      return result
    },
    enabled: !!selectedRoleId && selectedRoleId.trim() !== ''
  })

  // Mutación para guardar permisos del rol
  const saveRolePermissionsMutation = useMutation({
    mutationFn: async ({ roleId, permissionIds }: { roleId: number; permissionIds: number[] }) => {
      return rolePermissionService.updateRolePermissions(roleId, permissionIds)
    },
    onSuccess: (_, { permissionIds }) => {
      const selectedRole = roles.find(role => role.id.toString() === selectedRoleId)
      // Invalidar la query específica del rol seleccionado
      queryClient.invalidateQueries({ queryKey: ['role-permissions', selectedRoleId] })
      // También invalidar todas las queries de role-permissions para asegurar consistencia
      queryClient.invalidateQueries({ queryKey: ['role-permissions'] })
      setHasUnsavedChanges(false)
      toast({
        title: '✅ Permisos actualizados',
        description: `Se han asignado ${permissionIds.length} permisos al rol "${selectedRole?.nombre || 'Seleccionado'}"`
      })
    },
    onError: (error) => {
      console.error('Error updating role permissions:', error)
      toast({
        title: '❌ Error al actualizar',
        description: 'No se pudieron actualizar los permisos del rol. Inténtalo de nuevo.',
        variant: 'destructive'
      })
    }
  })

  // Memoizar rolePermissions para evitar bucle infinito
  const memoizedRolePermissions = useMemo(() => rolePermissions, [JSON.stringify(rolePermissions)])

  // Efectos
  React.useEffect(() => {
    if (memoizedRolePermissions.length > 0) {
      const permissionIds = memoizedRolePermissions.map(
        (rp: RolePermission) => rp.permiso_id
      )
      setSelectedPermissions(new Set(permissionIds))
    } else {
      setSelectedPermissions(new Set())
    }
    setHasUnsavedChanges(false)
  }, [memoizedRolePermissions])

  // Funciones auxiliares
  const handleRoleSelect = (roleId: string) => {
    if (hasUnsavedChanges) {
      if (!window.confirm('Tienes cambios sin guardar. ¿Deseas continuar sin guardar?')) {
        return
      }
    }
    setSelectedRoleId(roleId)
    setHasUnsavedChanges(false)
  }

  const handlePermissionToggle = (permissionId: number) => {
    setSelectedPermissions(prev => {
      const newSet = new Set(prev)
      if (newSet.has(permissionId)) {
        newSet.delete(permissionId)
      } else {
        newSet.add(permissionId)
      }
      setHasUnsavedChanges(true)
      return newSet
    })
  }

  const handleSelectAll = () => {
    const filteredPermissionIds = filteredPermissions.map(p => p.permiso_id)
    setSelectedPermissions(new Set(filteredPermissionIds))
    setHasUnsavedChanges(true)
  }

  const handleDeselectAll = () => {
    setSelectedPermissions(new Set())
    setHasUnsavedChanges(true)
  }

  // Función para seleccionar/deseleccionar todos los permisos de un módulo
  const handleModuleToggle = (moduleName: string, select: boolean) => {
    const modulePermissions = groupedPermissions[moduleName] || []
    const modulePermissionIds = modulePermissions.map(p => p.permiso_id)
    
    setSelectedPermissions(prev => {
      const newSet = new Set(prev)
      if (select) {
        modulePermissionIds.forEach(id => newSet.add(id))
      } else {
        modulePermissionIds.forEach(id => newSet.delete(id))
      }
      return newSet
    })
    setHasUnsavedChanges(true)
  }

  // Función para verificar si todos los permisos de un módulo están seleccionados
  const isModuleFullySelected = (moduleName: string) => {
    const modulePermissions = groupedPermissions[moduleName] || []
    return modulePermissions.length > 0 && modulePermissions.every(p => selectedPermissions.has(p.permiso_id))
  }

  // Función para verificar si algunos permisos de un módulo están seleccionados
  const isModulePartiallySelected = (moduleName: string) => {
    const modulePermissions = groupedPermissions[moduleName] || []
    return modulePermissions.some(p => selectedPermissions.has(p.permiso_id)) && !isModuleFullySelected(moduleName)
  }

  // Función para obtener el icono del módulo
  const getModuleIcon = (moduleName: string) => {
    const name = moduleName.toLowerCase()
    if (name.includes('usuario') || name.includes('user')) return User
    if (name.includes('rrhh') || name.includes('recurso')) return User
    if (name.includes('contrato') || name.includes('document')) return FileText
    if (name.includes('vacacion') || name.includes('calendar')) return Calendar
    if (name.includes('nomina') || name.includes('salario') || name.includes('pago')) return DollarSign
    if (name.includes('reporte') || name.includes('estadistica')) return BarChart3
    if (name.includes('config') || name.includes('setting')) return Settings
    return FolderOpen // Icono por defecto
  }

  const handleSave = async () => {
    if (!selectedRoleId || isSaving) return
    
    const roleIdNumber = parseInt(selectedRoleId)
    
    // Validación adicional
    if (isNaN(roleIdNumber)) {
      console.error('Invalid roleId:', selectedRoleId, 'parsed to:', roleIdNumber)
      toast({
        title: "Error",
        description: "ID de rol inválido",
        variant: "destructive"
      })
      return
    }
    

    
    setIsSaving(true)
    try {
      const permissionIds = Array.from(selectedPermissions)
      await saveRolePermissionsMutation.mutateAsync({
        roleId: roleIdNumber,
        permissionIds
      })
    } catch (error) {
      // El error ya se maneja en onError del mutation
    } finally {
      setIsSaving(false)
    }
  }

  // Filtrar permisos según término de búsqueda
  const filteredPermissions = permissions.filter(permission =>
    (permission.nombre_permiso && permission.nombre_permiso.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (permission.descripcion_permiso && permission.descripcion_permiso.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (permission.modulo_nombre && permission.modulo_nombre.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  // Agrupar permisos por modulo_nombre
  const groupedPermissions = filteredPermissions.reduce((groups, permission) => {
    const group = permission.modulo_nombre || 'Sin categoría'
    if (!groups[group]) {
      groups[group] = []
    }
    groups[group].push(permission)
    return groups
  }, {} as { [key: string]: Permission[] })

  const selectedRole = selectedRoleId && selectedRoleId.trim() !== '' 
    ? roles.find(role => role.id === parseInt(selectedRoleId))
    : undefined

  if (rolesLoading || permissionsLoading) {
    return <LoadingSpinner />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Asignar Permisos a Roles</h1>
          <p className="text-muted-foreground">
            Configura qué permisos tiene cada rol en el sistema
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Panel de selección de rol */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <UserCog className="h-5 w-5" />
              <span>Seleccionar Rol</span>
            </CardTitle>
            <CardDescription>
              Elige el rol al que deseas asignar permisos
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Select value={selectedRoleId?.toString() || ''} onValueChange={handleRoleSelect}>
              <SelectTrigger>
                <SelectValue placeholder="Selecciona un rol" />
              </SelectTrigger>
              <SelectContent>
                {roles.filter(role => role.is_active).map(role => (
                  <SelectItem key={role.id} value={role.id.toString()}>
                    <div className="flex flex-col">
                      <span className="font-medium">{role.nombre}</span>
                      {role.descripcion && (
                        <span className="text-xs text-muted-foreground">
                          {role.descripcion}
                        </span>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {selectedRole && (
              <div className="mt-4 p-4 bg-muted rounded-lg">
                <h4 className="font-medium mb-2">Rol Seleccionado</h4>
                <p className="text-sm font-medium">{selectedRole.nombre}</p>
                {selectedRole.descripcion && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {selectedRole.descripcion}
                  </p>
                )}
                <div className="mt-3 flex items-center justify-between text-sm">
                  <span>Permisos asignados:</span>
                  <Badge variant="secondary">
                    {selectedPermissions.size} de {permissions.length}
                  </Badge>
                </div>
                
                {/* Botón de guardar fijo */}
                {hasUnsavedChanges && (
                  <div className="mt-4 flex items-center justify-end space-x-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {
                        const originalPermissionIds = memoizedRolePermissions.map(
                          (rp: RolePermission) => rp.permiso_id
                        )
                        setSelectedPermissions(new Set(originalPermissionIds))
                        setHasUnsavedChanges(false)
                      }}
                    >
                      <X className="mr-1 h-3 w-3" />
                      Descartar
                    </Button>
                    <Button 
                      size="sm"
                      onClick={handleSave}
                      disabled={saveRolePermissionsMutation.isPending}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <Save className="mr-1 h-3 w-3" />
                      {saveRolePermissionsMutation.isPending ? 'Guardando...' : 'Guardar Cambios'}
                    </Button>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Panel de permisos */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Key className="h-5 w-5" />
              <span>Permisos Disponibles</span>
            </CardTitle>
            <CardDescription>
              Selecciona los permisos que tendrá el rol
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!selectedRoleId ? (
              <div className="text-center py-8 text-muted-foreground">
                <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Selecciona un rol para configurar sus permisos</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Controles de búsqueda y acciones */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between space-x-4">
                    <div className="flex items-center space-x-2 flex-1">
                      <Search className="h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Buscar permisos..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="max-w-sm"
                      />
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={handleSelectAll}
                        disabled={rolePermissionsLoading || isSaving}
                      >
                        <Plus className="mr-1 h-3 w-3" />
                        Todos
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={handleDeselectAll}
                        disabled={rolePermissionsLoading || isSaving}
                      >
                        <Minus className="mr-1 h-3 w-3" />
                        Ninguno
                      </Button>
                    </div>
                  </div>
                  
                  {/* Indicadores visuales */}
                   <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                     <div className="flex items-center space-x-3">
                       <Badge variant="secondary" className="text-xs">
                         {selectedPermissions.size} de {filteredPermissions.length} seleccionados
                       </Badge>
                       {hasUnsavedChanges && !isSaving && (
                         <Badge variant="outline" className="text-xs text-orange-600 border-orange-200">
                           Cambios sin guardar
                         </Badge>
                       )}
                       {isSaving && (
                         <Badge variant="outline" className="text-xs text-blue-600 border-blue-200">
                           <LoadingSpinner className="h-3 w-3 mr-1" />
                           Guardando cambios...
                         </Badge>
                       )}
                     </div>
                     <div className="text-xs text-muted-foreground">
                       {filteredPermissions.length} permisos disponibles
                     </div>
                   </div>
                </div>

                {/* Lista de permisos agrupados */}
                {rolePermissionsLoading ? (
                  <div className="flex justify-center py-8">
                    <LoadingSpinner />
                  </div>
                ) : (
                  <div className="space-y-6">
                    {Object.entries(groupedPermissions).map(([contentType, groupPermissions]) => {
                      const ModuleIcon = getModuleIcon(contentType)
                      const selectedCount = groupPermissions.filter(p => selectedPermissions.has(p.permiso_id)).length
                      const totalCount = groupPermissions.length
                      const isFullySelected = isModuleFullySelected(contentType)
                      const isPartiallySelected = isModulePartiallySelected(contentType)

                      return (
                        <div key={contentType} className="border rounded-lg overflow-hidden">
                          <div className="bg-muted/30 px-4 py-3 border-b">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <div className={`p-2 rounded-md ${
                                  isFullySelected ? 'bg-primary text-primary-foreground' :
                                  isPartiallySelected ? 'bg-orange-100 text-orange-600' :
                                  'bg-muted text-muted-foreground'
                                }`}>
                                  <ModuleIcon className="h-4 w-4" />
                                </div>
                                <div>
                                  <h4 className="font-semibold text-sm">
                                    {contentType}
                                  </h4>
                                  <p className="text-xs text-muted-foreground">
                                    {selectedCount} de {totalCount} permisos seleccionados
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleModuleToggle(contentType, true)}
                                  disabled={isFullySelected || isSaving}
                                  className="h-7 px-2 text-xs"
                                >
                                  <Plus className="h-3 w-3 mr-1" />
                                  Todos
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleModuleToggle(contentType, false)}
                                  disabled={(!isPartiallySelected && !isFullySelected) || isSaving}
                                  className="h-7 px-2 text-xs"
                                >
                                  <Minus className="h-3 w-3 mr-1" />
                                  Ninguno
                                </Button>
                              </div>
                            </div>
                          </div>
                          <div className="p-4">
                            <div className="grid gap-3 md:grid-cols-2">
                              {groupPermissions.map(permission => (
                                <div 
                                  key={permission.permiso_id} 
                                  className="flex items-start space-x-3 p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                                >
                                  <Checkbox
                                    id={`permission-${permission.permiso_id}`}
                                    checked={selectedPermissions.has(permission.permiso_id)}
                                    onCheckedChange={() => handlePermissionToggle(permission.permiso_id)}
                                    className="mt-1"
                                    disabled={isSaving}
                                  />
                                  <div className="flex-1 min-w-0">
                                    <label 
                                      htmlFor={`permission-${permission.permiso_id}`}
                                      className="text-sm font-medium cursor-pointer"
                                    >
                                      {permission.nombre_permiso}
                                    </label>
                                    <p className="text-xs text-muted-foreground mt-1">
                                      {permission.descripcion_permiso || 'Sin descripción'}
                                    </p>
                                    <code className="text-xs bg-muted px-1 py-0.5 rounded mt-1 inline-block">
                                      {permission.tipo_permiso}
                                    </code>
                                  </div>
                                  {selectedPermissions.has(permission.permiso_id) && (
                                    <Check className="h-4 w-4 text-green-600 mt-1" />
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}

                {filteredPermissions.length === 0 && searchTerm && (
                  <div className="text-center py-8 text-muted-foreground">
                    <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p>No se encontraron permisos que coincidan con la búsqueda</p>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Panel de confirmación de cambios */}
      {hasUnsavedChanges && selectedRoleId && (
        <Card className="border-orange-200 bg-orange-50 dark:bg-orange-950/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Settings className="h-5 w-5 text-orange-600" />
                <div>
                  <p className="font-medium text-orange-800 dark:text-orange-200">
                    Tienes cambios sin guardar
                  </p>
                  <p className="text-sm text-orange-600 dark:text-orange-300">
                    Los cambios en los permisos del rol "{selectedRole?.nombre}" no se han guardado.
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => {
                    const originalPermissionIds = memoizedRolePermissions.map(
                      (rp: RolePermission) => rp.permiso_id
                    )
                    setSelectedPermissions(new Set(originalPermissionIds))
                    setHasUnsavedChanges(false)
                  }}
                >
                  <X className="mr-1 h-3 w-3" />
                  Descartar
                </Button>
                <Button 
                  size="sm"
                  onClick={handleSave}
                  disabled={saveRolePermissionsMutation.isPending}
                >
                  <Save className="mr-1 h-3 w-3" />
                  {saveRolePermissionsMutation.isPending ? 'Guardando...' : 'Guardar'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}