import React, { useState, useEffect } from 'react'
import { 
  Users, 
  Plus, 
  Search, 
  Filter, 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  Eye,
  UserCheck,
  UserX,
  Key,
  Shield
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { toast } from 'sonner'
import { usersService, rolesService, type User, type Role } from '@/services/usersService'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'
import { UsersLayout } from '@/components/layout/UsersLayout'

// Importar los modales
import { UserFormModal } from '@/components/users/modals/UserFormModal'
import { ChangePasswordModal } from '@/components/users/modals/ChangePasswordModal'
import { RoleManagementModal } from '@/components/users/modals/RoleManagementModal'
import { UserDetailsModal } from '@/components/users/modals/UserDetailsModal'

export function UsersList() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [roleFilter, setRoleFilter] = useState<string>('all')
  const [roles, setRoles] = useState<Role[]>([])
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [userToDelete, setUserToDelete] = useState<User | null>(null)
  
  // Estados para los modales
  const [userFormModalOpen, setUserFormModalOpen] = useState(false)
  const [passwordModalOpen, setPasswordModalOpen] = useState(false)
  const [roleModalOpen, setRoleModalOpen] = useState(false)
  const [detailsModalOpen, setDetailsModalOpen] = useState(false)
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null)


  // Cargar usuarios y roles al montar el componente
  useEffect(() => {
    loadUsers()
    loadRoles()
  }, [])

  const loadUsers = async () => {
    try {
      setLoading(true)
      const data = await usersService.getAll()
      setUsers(data)
    } catch (error) {
      console.error('Error loading users:', error)
      toast.error('Error al cargar los usuarios')
    } finally {
      setLoading(false)
    }
  }

  const loadRoles = async () => {
    try {
      const response = await rolesService.getActive()

      // Manejar la estructura de respuesta del servicio de roles
      const rolesArray = response?.data || response || []

      setRoles(rolesArray)
    } catch (error) {
      console.error('Error loading roles:', error)
      toast.error('Error al cargar los roles')
      setRoles([]) // Asegurar que roles sea un array vacío en caso de error
    }
  }

  const searchUsersByRole = async () => {
    if (roleFilter === 'all') {
      loadUsers()
      return
    }

    try {
      setLoading(true)
      const data = await usersService.searchByRoles({
        rol_ids: [parseInt(roleFilter)],
        nombres: searchTerm || undefined,
        estado: statusFilter !== 'all' ? (statusFilter === 'active' ? 'activo' : 'inactivo') : undefined,
        operador: 'AND'
      })
      setUsers(data)
    } catch (error) {
      console.error('Error searching users by role:', error)
      toast.error('Error al buscar usuarios por rol')
    } finally {
      setLoading(false)
    }
  }

  // Efecto para buscar cuando cambian los filtros de rol
  useEffect(() => {
    if (roleFilter !== 'all') {
      searchUsersByRole()
    } else {
      loadUsers()
    }
  }, [roleFilter])

  // Efecto para actualizar búsqueda cuando cambian otros filtros y hay un rol seleccionado
  useEffect(() => {
    if (roleFilter !== 'all') {
      searchUsersByRole()
    }
  }, [searchTerm, statusFilter])

  const handleDeleteUser = async () => {
    if (!userToDelete) return

    try {
      await usersService.delete(userToDelete.id)
      toast.success('Usuario eliminado correctamente')
      loadUsers() // Recargar la lista
    } catch (error) {
      console.error('Error deleting user:', error)
      toast.error('Error al eliminar el usuario')
    } finally {
      setDeleteDialogOpen(false)
      setUserToDelete(null)
    }
  }

  const openDeleteDialog = (user: User) => {
    setUserToDelete(user)
    setDeleteDialogOpen(true)
  }

  // Filtrar usuarios según los criterios de búsqueda (solo cuando no se está filtrando por rol)
  const filteredUsers = roleFilter === 'all' ? users.filter(user => {
    const matchesSearch = 
      user.nombres_usuario?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.apellidos_usuario?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email?.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesStatus = statusFilter === 'all' || 
      (statusFilter === 'active' && user.is_active) ||
      (statusFilter === 'inactive' && !user.is_active)

    const matchesType = typeFilter === 'all' || user.tipo_usuario === typeFilter

    return matchesSearch && matchesStatus && matchesType
  }) : users.filter(user => {
    // Cuando se filtra por rol, solo aplicar filtros de tipo ya que la búsqueda y estado se manejan en el backend
    const matchesType = typeFilter === 'all' || user.tipo_usuario === typeFilter
    return matchesType
  })

  const getStatusBadge = (user: User) => {
    if (user.is_active) {
      return <Badge variant="success">Activo</Badge>
    } else {
      return <Badge variant="destructive">Inactivo</Badge>
    }
  }

  const getTypeBadge = (type: string) => {
    const typeColors: Record<string, string> = {
      'administrador': 'bg-red-100 text-red-800',
      'supervisor': 'bg-blue-100 text-blue-800',
      'empleado': 'bg-green-100 text-green-800',
      'invitado': 'bg-gray-100 text-gray-800'
    }

    if (!type) {
      return (
        <Badge variant="outline" className="text-muted-foreground">
          Sin tipo asignado
        </Badge>
      )
    }

    return (
      <Badge className={typeColors[type] || 'bg-gray-100 text-gray-800'}>
        {type.charAt(0).toUpperCase() + type.slice(1)}
      </Badge>
    )
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <UsersLayout 
      title="Listado de Usuarios" 
      description="Visualiza y administra todos los usuarios del sistema"
    >
      {/* Header Actions */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              placeholder="Buscar usuarios..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-80"
            />
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Estado" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              <SelectItem value="active">Activos</SelectItem>
              <SelectItem value="inactive">Inactivos</SelectItem>
            </SelectContent>
          </Select>
          <Select value={roleFilter} onValueChange={setRoleFilter}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Filtrar por rol" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos los roles</SelectItem>
              {(roles || []).filter(role => role.id).map((role) => (
                <SelectItem key={role.id} value={role.id!.toString()}>
                  {role.nombre_rol}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <Button onClick={() => {
            setSelectedUserId(null)
            setUserFormModalOpen(true)
          }}>
          <Plus className="mr-2 h-4 w-4" />
          Nuevo Usuario
        </Button>
      </div>

      {/* Filtros adicionales */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center space-x-4">
          {roleFilter !== 'all' && (
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="bg-blue-50 text-blue-700">
                <Shield className="w-3 h-3 mr-1" />
                Filtrado por: {roles.find(r => r.id && r.id.toString() === roleFilter)?.nombre_rol}
              </Badge>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setRoleFilter('all')}
                className="h-6 px-2 text-xs"
              >
                Limpiar filtro
              </Button>
            </div>
          )}
        </div>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filtrar por tipo" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos los tipos</SelectItem>
            <SelectItem value="administrador">Administrador</SelectItem>
            <SelectItem value="supervisor">Supervisor</SelectItem>
            <SelectItem value="empleado">Empleado</SelectItem>
            <SelectItem value="invitado">Invitado</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Tabla de usuarios */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Lista de Usuarios ({filteredUsers.length})
          </CardTitle>
          <CardDescription>
            Gestiona los usuarios registrados en el sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredUsers.length === 0 ? (
            <div className="text-center py-8">
              <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No se encontraron usuarios</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm || statusFilter !== 'all' || typeFilter !== 'all'
                  ? 'No hay usuarios que coincidan con los filtros aplicados.'
                  : 'No hay usuarios registrados en el sistema.'}
              </p>
              {!searchTerm && statusFilter === 'all' && typeFilter === 'all' && (
                <Button onClick={() => {
                   setSelectedUserId(null)
                   setUserFormModalOpen(true)
                 }}>
                  <Plus className="w-4 h-4 mr-2" />
                  Crear Primer Usuario
                </Button>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Usuario</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead>Área</TableHead>
                    <TableHead>Último Acceso</TableHead>
                    <TableHead>Roles</TableHead>
                    <TableHead className="text-right">Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredUsers.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="font-medium">
                            {user.nombres_usuario} {user.apellidos_usuario}{user.id}
                          </span>
                          <span className="text-sm text-muted-foreground">
                            @{user.username}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>{getTypeBadge(user.tipo_usuario)}</TableCell>
                      <TableCell>{getStatusBadge(user)}</TableCell>
                      <TableCell>
                        {user.empleado?.area ? (
                          <div className="flex flex-col">
                            <span className="text-sm font-medium">
                              {user.empleado.area.organo}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              {user.empleado.area.siglas}
                            </span>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">Sin área</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="text-sm">
                            {user.last_login ? formatDate(user.last_login) : (
                              <span className="text-muted-foreground">Nunca ha iniciado sesión</span>
                            )}
                          </span>
                          {user.last_login && user.dias_sin_login !== undefined && (
                            <span className="text-xs text-muted-foreground">
                              {user.dias_sin_login} días
                            </span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {user.roles_activos && user.roles_activos.length > 0 ? (
                            <>
                              {user.roles_activos.slice(0, 2).map((role) => (
                                <Badge key={role.id} variant="outline" className="text-xs">
                                  {role.nombre_rol}
                                </Badge>
                              ))}
                              {user.roles_activos.length > 2 && (
                                <Badge variant="outline" className="text-xs">
                                  +{user.roles_activos.length - 2}
                                </Badge>
                              )}
                            </>
                          ) : (
                            <span className="text-muted-foreground text-sm">Sin roles asignados</span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <span className="sr-only">Abrir menú</span>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                            <DropdownMenuItem onClick={() => {
                              setSelectedUserId(user.id)
                              setDetailsModalOpen(true)
                            }}>
                              <Eye className="w-4 h-4 mr-2" />
                              Ver Detalles
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => {
                              setSelectedUserId(user.id)
                              setUserFormModalOpen(true)
                            }}>
                              <Edit className="w-4 h-4 mr-2" />
                              Editar
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => {
                              setSelectedUserId(user.id)
                              setPasswordModalOpen(true)
                            }}>
                              <Key className="w-4 h-4 mr-2" />
                              Cambiar Contraseña
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => {
                              setSelectedUserId(user.id)
                              setRoleModalOpen(true)
                            }}>
                              <Shield className="w-4 h-4 mr-2" />
                              Gestionar Roles
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-destructive"
                              onClick={() => openDeleteDialog(user)}
                            >
                              <Trash2 className="w-4 h-4 mr-2" />
                              Eliminar
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog de confirmación para eliminar */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Estás seguro?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción eliminará permanentemente el usuario "{userToDelete?.nombres_usuario} {userToDelete?.apellidos_usuario}" 
              y todos sus datos asociados. Esta acción no se puede deshacer.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteUser}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Eliminar
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Modales */}
      <UserFormModal
        open={userFormModalOpen}
        onOpenChange={setUserFormModalOpen}
        userId={selectedUserId || undefined}
        onSuccess={() => {
          loadUsers()
          setUserFormModalOpen(false)
          setSelectedUserId(null)
        }}
      />

      {selectedUserId && (
        <>
          <ChangePasswordModal
            open={passwordModalOpen}
            onOpenChange={setPasswordModalOpen}
            userId={selectedUserId}
            onSuccess={() => {
              setPasswordModalOpen(false)
              setSelectedUserId(null)
            }}
          />

          <RoleManagementModal
            open={roleModalOpen}
            onOpenChange={setRoleModalOpen}
            userId={selectedUserId}
            onSuccess={() => {
              loadUsers()
              setRoleModalOpen(false)
              setSelectedUserId(null)
            }}
          />

          <UserDetailsModal
            open={detailsModalOpen}
            onOpenChange={setDetailsModalOpen}
            userId={selectedUserId}
          />
        </>
      )}
    </UsersLayout>
  )
}

export default UsersList