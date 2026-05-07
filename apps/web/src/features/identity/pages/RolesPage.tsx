import React, { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { MoreHorizontal, Plus, Edit, Trash2, UserCog, Search, Users } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/shared/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/shared/ui/dialog'
import { Label } from '@/shared/ui/label'
import { Textarea } from '@/shared/ui/textarea'
import { Badge } from '@/shared/ui/badge'
import { DataTable } from '@/shared/components/DataTable'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { useToast } from '@/shared/ui/use-toast'
import { roleService, type Role, type RoleFormData } from '@/features/identity/services/securityService'

export default function RolesPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [formData, setFormData] = useState<RoleFormData>({
    nombre: '',
    descripcion: '',
    is_active: true
  })

  const { toast } = useToast()
  const queryClient = useQueryClient()

  // Query para obtener roles - optimizado con caché
  const { data: roles = [], isLoading, error } = useQuery({
    queryKey: ['roles'],
    queryFn: roleService.getAll,
    staleTime: 5 * 60 * 1000 // 5 minutos de caché
  })

  // Mutación para crear rol
  const createRoleMutation = useMutation({
    mutationFn: roleService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] })
      setIsCreateDialogOpen(false)
      setSearchTerm('') // Limpiar búsqueda
      setCurrentPage(1) // Volver a la primera página
      resetForm()
      toast({
        title: 'Rol creado',
        description: 'El rol se ha creado exitosamente.'
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'No se pudo crear el rol.',
        variant: 'destructive'
      })
    }
  })

  // Mutación para editar rol
  const editRoleMutation = useMutation({
    mutationFn: ({ id, ...data }: RoleFormData & { id: number }) => roleService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] })
      setIsEditDialogOpen(false)
      setSelectedRole(null)
      resetForm()
      toast({
        title: 'Rol actualizado',
        description: 'El rol se ha actualizado exitosamente.'
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'No se pudo actualizar el rol.',
        variant: 'destructive'
      })
    }
  })

  // Mutación para eliminar rol
  const deleteRoleMutation = useMutation({
    mutationFn: roleService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] })
      toast({
        title: 'Rol eliminado',
        description: 'El rol se ha eliminado exitosamente.'
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'No se pudo eliminar el rol.',
        variant: 'destructive'
      })
    }
  })

  // Mutación para cambiar estado del rol
  const toggleRoleStatusMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: boolean }) => 
      roleService.update(id, { is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] })
      toast({
        title: 'Estado actualizado',
        description: 'El estado del rol se ha actualizado exitosamente.'
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'No se pudo actualizar el estado del rol.',
        variant: 'destructive'
      })
    }
  })

  // Funciones auxiliares
  const resetForm = () => {
    setFormData({
      nombre: '',
      descripcion: '',
      is_active: true
    })
  }

  const handleEdit = (role: Role) => {
    setSelectedRole(role)
    setFormData({
      nombre: role.nombre,
      descripcion: role.descripcion || '',
      is_active: role.is_active
    })
    setIsEditDialogOpen(true)
  }

  const handleDelete = (id: number) => {
    if (window.confirm('¿Está seguro de que desea eliminar este rol?')) {
      deleteRoleMutation.mutate(id)
    }
  }

  const handleToggleStatus = (role: Role) => {
    toggleRoleStatusMutation.mutate({
      id: role.id,
      is_active: !role.is_active
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (selectedRole) {
      editRoleMutation.mutate({ ...formData, id: selectedRole.id })
    } else {
      createRoleMutation.mutate(formData)
    }
  }

  // Funciones de manejo de paginación
  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize)
    setCurrentPage(1) // Resetear a la primera página
  }

  const handleSearchChange = (value: string) => {
    setSearchTerm(value)
    setCurrentPage(1) // Resetear a la primera página al buscar
  }

  // Definición de columnas para la tabla
  const columns: ColumnDef<Role>[] = [
    {
      accessorKey: 'nombre',
      header: 'Nombre del Rol',
      cell: ({ row }) => (
        <div className="flex items-center space-x-2">
          <UserCog className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium">{row.getValue('nombre')}</span>
        </div>
      )
    },
    {
      accessorKey: 'descripcion',
      header: 'Descripción',
      cell: ({ row }) => (
        <span className="text-sm text-muted-foreground max-w-xs truncate">
          {row.getValue('descripcion') || 'Sin descripción'}
        </span>
      )
    },
    {
      accessorKey: 'is_active',
      header: 'Estado',
      cell: ({ row }) => {
        const isActive = row.getValue('is_active') as boolean
        return (
          <Badge variant={isActive ? 'default' : 'secondary'}>
            {isActive ? 'Activo' : 'Inactivo'}
          </Badge>
        )
      }
    },
    {
      accessorKey: 'permissions_count',
      header: 'Permisos',
      cell: ({ row }) => (
        <div className="flex items-center space-x-1">
          <span className="text-sm font-medium">{row.getValue('permissions_count') || 0}</span>
          <span className="text-xs text-muted-foreground">permisos</span>
        </div>
      )
    },
    {
      accessorKey: 'users_count',
      header: 'Usuarios',
      cell: ({ row }) => (
        <div className="flex items-center space-x-1">
          <Users className="h-3 w-3 text-muted-foreground" />
          <span className="text-sm font-medium">{row.getValue('users_count') || 0}</span>
        </div>
      )
    },
    {
      id: 'actions',
      header: 'Acciones',
      cell: ({ row }) => {
        const role = row.original
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Abrir menú</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Acciones</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => handleEdit(role)}>
                <Edit className="mr-2 h-4 w-4" />
                Editar
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleToggleStatus(role)}>
                <UserCog className="mr-2 h-4 w-4" />
                {role.is_active ? 'Desactivar' : 'Activar'}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem 
                onClick={() => handleDelete(role.id)}
                className="text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Eliminar
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      }
    }
  ]

  // Filtrado local inteligente y paginación
  const filteredRoles = useMemo(() => {
    if (!searchTerm.trim()) return roles
    
    const searchLower = searchTerm.toLowerCase()
    return roles.filter(role => {
      const nombre = role.nombre?.toLowerCase() || ''
      const descripcion = role.descripcion?.toLowerCase() || ''
      const estado = role.is_active ? 'activo' : 'inactivo'
      
      return nombre.includes(searchLower) ||
             descripcion.includes(searchLower) ||
             estado.includes(searchLower)
    })
  }, [roles, searchTerm])

  // Nota: La paginación se maneja en el DataTable cuando se pasan props de pagination

  // Metadatos de paginación
  const pagination = useMemo(() => {
    const totalItems = filteredRoles.length
    const totalPages = Math.ceil(totalItems / pageSize)
    
    return {
      page: currentPage,
      page_size: pageSize,
      total_items: totalItems,
      total_pages: totalPages,
      has_next: currentPage < totalPages,
      has_previous: currentPage > 1
    }
  }, [filteredRoles.length, currentPage, pageSize])

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <h2 className="text-2xl font-bold text-destructive">Error</h2>
        <p className="text-muted-foreground mt-2">No se pudieron cargar los roles</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestión de Roles</h1>
          <p className="text-muted-foreground">
            Administra los roles del sistema y define niveles de acceso
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={resetForm}>
              <Plus className="mr-2 h-4 w-4" />
              Nuevo Rol
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <form onSubmit={handleSubmit}>
              <DialogHeader>
                <DialogTitle>Crear Nuevo Rol</DialogTitle>
                <DialogDescription>
                  Define un nuevo rol para organizar permisos y controlar el acceso al sistema.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="nombre">Nombre del Rol</Label>
                  <Input
                    id="nombre"
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    placeholder="Ej: Supervisor de RRHH"
                    required
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="descripcion">Descripción</Label>
                  <Textarea
                    id="descripcion"
                    value={formData.descripcion}
                    onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                    placeholder="Describe las responsabilidades y alcance de este rol..."
                    rows={3}
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="is_active">Rol activo</Label>
                </div>
              </div>
              <DialogFooter>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setIsCreateDialogOpen(false)}
                >
                  Cancelar
                </Button>
                <Button 
                  type="submit" 
                  disabled={createRoleMutation.isPending}
                >
                  {createRoleMutation.isPending ? 'Creando...' : 'Crear Rol'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <UserCog className="h-4 w-4 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Roles</p>
                <p className="text-2xl font-bold">{roles.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <UserCog className="h-4 w-4 text-green-600" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Roles Activos</p>
                <p className="text-2xl font-bold">{roles.filter(r => r.is_active).length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Usuarios</p>
                <p className="text-2xl font-bold">{roles.reduce((sum, role) => sum + (role.users_count || 0), 0)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <UserCog className="h-4 w-4 text-orange-600" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Roles Inactivos</p>
                <p className="text-2xl font-bold">{roles.filter(r => !r.is_active).length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabla de roles */}
      <Card>
        <CardHeader>
          <CardTitle>Roles del Sistema</CardTitle>
          <CardDescription>
            Lista de todos los roles configurados en el sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable 
            columns={columns} 
            data={filteredRoles}
            searchValue={searchTerm}
            onSearchChange={handleSearchChange}
            pagination={{
              page: currentPage,
              pageSize: pageSize,
              totalCount: pagination.total_items,
              onPageChange: handlePageChange,
              onPageSizeChange: handlePageSizeChange
            }}
          />
        </CardContent>
      </Card>

      {/* Dialog para editar */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle>Editar Rol</DialogTitle>
              <DialogDescription>
                Modifica la información del rol seleccionado.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-nombre">Nombre del Rol</Label>
                <Input
                  id="edit-nombre"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  placeholder="Ej: Supervisor de RRHH"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-descripcion">Descripción</Label>
                <Textarea
                  id="edit-descripcion"
                  value={formData.descripcion}
                  onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                  placeholder="Describe las responsabilidades y alcance de este rol..."
                  rows={3}
                />
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="edit-is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="rounded border-gray-300"
                />
                <Label htmlFor="edit-is_active">Rol activo</Label>
              </div>
            </div>
            <DialogFooter>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => {
                  setIsEditDialogOpen(false)
                  setSelectedRole(null)
                  resetForm()
                }}
              >
                Cancelar
              </Button>
              <Button 
                type="submit" 
                disabled={editRoleMutation.isPending}
              >
                {editRoleMutation.isPending ? 'Guardando...' : 'Guardar Cambios'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}