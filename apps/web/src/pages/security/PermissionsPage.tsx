import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { MoreHorizontal, Plus, Edit, Trash2, Key, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { DataTable } from '@/components/common/DataTable'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { useToast } from '@/components/ui/use-toast'
import { permissionService, type Permission, type PermissionFormData } from '@/services/securityService'

export default function PermissionsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [selectedPermission, setSelectedPermission] = useState<Permission | null>(null)
  const [formData, setFormData] = useState<PermissionFormData>({
    nombre_permiso: '',
    descripcion_permiso: '',
    modulo_id: '',
    tipo_permiso: 'leer',
    estado_permiso: 'activo'
  })

  const { toast } = useToast()
  const queryClient = useQueryClient()

  // Query para obtener todos los permisos (sin filtro del servidor)
  const { data: allPermissions = [], isLoading, error } = useQuery({
    queryKey: ['permissions'],
    queryFn: () => permissionService.getAll(),
    staleTime: 5 * 60 * 1000, // 5 minutos
  })

  // Filtrado local de permisos
  const filteredPermissions = allPermissions.filter(permission => {
    if (!searchTerm) return true
    const searchLower = searchTerm.toLowerCase()
    return (
      permission.nombre_permiso.toLowerCase().includes(searchLower) ||
      permission.descripcion_permiso?.toLowerCase().includes(searchLower) ||
      permission.tipo_permiso.toLowerCase().includes(searchLower) ||
      permission.modulo_nombre?.toLowerCase().includes(searchLower)
    )
  })

  // Paginación local
  const totalItems = filteredPermissions.length
  const totalPages = Math.ceil(totalItems / pageSize)
  const startIndex = (currentPage - 1) * pageSize
  const endIndex = startIndex + pageSize
  const paginatedPermissions = filteredPermissions.slice(startIndex, endIndex)

  // Metadatos de paginación para el DataTable
  const pagination = {
    total_items: totalItems,
    total_pages: totalPages,
    current_page: currentPage,
    page_size: pageSize
  }

  // Mutación para crear permiso
  const createPermissionMutation = useMutation({
    mutationFn: permissionService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['permissions'] })
      setIsCreateDialogOpen(false)
      resetForm()
      // Limpiar búsqueda y volver a la primera página después de crear
      setSearchTerm('')
      setCurrentPage(1)
      toast({
        title: 'Permiso creado',
        description: 'El permiso se ha creado exitosamente.'
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'No se pudo crear el permiso.',
        variant: 'destructive'
      })
    }
  })

  // Mutación para editar permiso
  const editPermissionMutation = useMutation({
    mutationFn: ({ id, ...data }: PermissionFormData & { id: string }) =>
      permissionService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['permissions'] })
      setIsEditDialogOpen(false)
      setSelectedPermission(null)
      resetForm()
      toast({
        title: 'Permiso actualizado',
        description: 'El permiso se ha actualizado exitosamente.'
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'No se pudo actualizar el permiso.',
        variant: 'destructive'
      })
    }
  })

  // Mutación para eliminar permiso
  const deletePermissionMutation = useMutation({
    mutationFn: permissionService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['permissions'] })
      toast({
        title: 'Permiso eliminado',
        description: 'El permiso se ha eliminado exitosamente.'
      })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'No se pudo eliminar el permiso.',
        variant: 'destructive'
      })
    }
  })

  // Funciones auxiliares
  const resetForm = () => {
    setFormData({
      nombre_permiso: '',
      descripcion_permiso: '',
      modulo_id: 1,
      tipo_permiso: 'leer',
      estado_permiso: 'activo'
    })
  }

  const handleEdit = (permission: Permission) => {
    setSelectedPermission(permission)
    setFormData({
      nombre_permiso: permission.nombre_permiso,
      descripcion_permiso: permission.descripcion_permiso,
      modulo_id: permission.modulo_id,
      tipo_permiso: permission.tipo_permiso,
      estado_permiso: permission.estado_permiso || 'activo'
    })
    setIsEditDialogOpen(true)
  }

  const handleDelete = (id: string) => {
    if (window.confirm('¿Está seguro de que desea eliminar este permiso?')) {
      deletePermissionMutation.mutate(id)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (selectedPermission) {
      editPermissionMutation.mutate({ ...formData, id: selectedPermission.id })
    } else {
      createPermissionMutation.mutate(formData)
    }
  }

  // Definición de columnas para la tabla
  const columns: ColumnDef<Permission>[] = [
    {
      accessorKey: 'nombre_permiso',
      header: 'Nombre',
      cell: ({ row }) => (
        <div className="flex items-center space-x-2">
          <Key className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium">{row.getValue('nombre_permiso')}</span>
        </div>
      )
    },
    {
      accessorKey: 'tipo_permiso',
      header: 'Tipo',
      cell: ({ row }) => (
        <code className="bg-muted px-2 py-1 rounded text-sm">
          {row.getValue('tipo_permiso')}
        </code>
      )
    },
    {
      accessorKey: 'modulo_nombre',
      header: 'Módulo',
      cell: ({ row }) => (
        <span className="text-muted-foreground">
          {row.getValue('modulo_nombre') || 'Sin módulo'}
        </span>
      )
    },
    {
      accessorKey: 'descripcion_permiso',
      header: 'Descripción',
      cell: ({ row }) => (
        <span className="text-sm text-muted-foreground max-w-xs truncate">
          {row.getValue('descripcion_permiso') || 'Sin descripción'}
        </span>
      )
    },
    {
      accessorKey: 'estado_permiso',
      header: 'Estado',
      cell: ({ row }) => (
        <span className={`px-2 py-1 rounded text-xs ${
          row.getValue('estado_permiso') === 'activo' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-red-100 text-red-800'
        }`}>
          {row.getValue('estado_permiso')}
        </span>
      )
    },
    {
      id: 'actions',
      header: 'Acciones',
      cell: ({ row }) => {
        const permission = row.original
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
              <DropdownMenuItem onClick={() => handleEdit(permission)}>
                <Edit className="mr-2 h-4 w-4" />
                Editar
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => handleDelete(permission.id)}
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

  // Función para manejar cambios en la búsqueda (sin debounce, filtrado instantáneo)
  const handleSearchChange = (value: string) => {
    setSearchTerm(value)
    setCurrentPage(1) // Resetear a la primera página al buscar
  }

  // Función para manejar cambios de página
  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <h2 className="text-2xl font-bold text-destructive">Error</h2>
        <p className="text-muted-foreground mt-2">No se pudieron cargar los permisos</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestión de Permisos</h1>
          <p className="text-muted-foreground">
            Administra los permisos del sistema y controla el acceso a funcionalidades
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={resetForm}>
              <Plus className="mr-2 h-4 w-4" />
              Nuevo Permiso
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <form onSubmit={handleSubmit}>
              <DialogHeader>
                <DialogTitle>Crear Nuevo Permiso</DialogTitle>
                <DialogDescription>
                  Define un nuevo permiso para controlar el acceso a funcionalidades del sistema.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="nombre_permiso">Nombre del Permiso</Label>
                  <Input
                    id="nombre_permiso"
                    value={formData.nombre_permiso}
                    onChange={(e) => setFormData({ ...formData, nombre_permiso: e.target.value })}
                    placeholder="Ej: Crear Usuario"
                    required
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="tipo_permiso">Tipo de Permiso</Label>
                  <select
                    id="tipo_permiso"
                    value={formData.tipo_permiso}
                    onChange={(e) => setFormData({ ...formData, tipo_permiso: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                    required
                  >
                    <option value="crear">Crear</option>
                    <option value="leer">Leer</option>
                    <option value="actualizar">Actualizar</option>
                    <option value="eliminar">Eliminar</option>
                    <option value="ejecutar">Ejecutar</option>
                    <option value="aprobar">Aprobar</option>
                  </select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="modulo_id">Módulo ID</Label>
                  <Input
                    id="modulo_id"
                    type="number"
                    value={formData.modulo_id}
                    onChange={(e) => setFormData({ ...formData, modulo_id: parseInt(e.target.value) })}
                    placeholder="ID del módulo"
                    required
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="descripcion_permiso">Descripción</Label>
                  <Textarea
                    id="descripcion_permiso"
                    value={formData.descripcion_permiso}
                    onChange={(e) => setFormData({ ...formData, descripcion_permiso: e.target.value })}
                    placeholder="Describe qué permite hacer este permiso..."
                    rows={3}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="estado_permiso">Estado</Label>
                  <select
                    id="estado_permiso"
                    value={formData.estado_permiso}
                    onChange={(e) => setFormData({ ...formData, estado_permiso: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                  >
                    <option value="activo">Activo</option>
                    <option value="inactivo">Inactivo</option>
                  </select>
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
                  disabled={createPermissionMutation.isPending}
                >
                  {createPermissionMutation.isPending ? 'Creando...' : 'Crear Permiso'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filtros y búsqueda */}
      <Card>
        <CardHeader>
          <CardTitle>Permisos del Sistema</CardTitle>
          <CardDescription>
            Lista de todos los permisos disponibles en el sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable 
            columns={columns} 
            data={paginatedPermissions}
            searchValue={searchTerm}
            onSearchChange={handleSearchChange}
            pagination={{
              page: currentPage,
              pageSize: pageSize,
              totalCount: pagination.total_items,
              onPageChange: handlePageChange,
              onPageSizeChange: (size) => {
                setPageSize(size)
                setCurrentPage(1)
              }
            }}
          />
        </CardContent>
      </Card>

      {/* Dialog para editar */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle>Editar Permiso</DialogTitle>
              <DialogDescription>
                Modifica la información del permiso seleccionado.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-nombre_permiso">Nombre del Permiso</Label>
                <Input
                  id="edit-nombre_permiso"
                  value={formData.nombre_permiso}
                  onChange={(e) => setFormData({ ...formData, nombre_permiso: e.target.value })}
                  placeholder="Ej: Crear Usuario"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-tipo_permiso">Tipo de Permiso</Label>
                <select
                  id="edit-tipo_permiso"
                  value={formData.tipo_permiso}
                  onChange={(e) => setFormData({ ...formData, tipo_permiso: e.target.value })}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                  required
                >
                  <option value="crear">Crear</option>
                  <option value="leer">Leer</option>
                  <option value="actualizar">Actualizar</option>
                  <option value="eliminar">Eliminar</option>
                  <option value="ejecutar">Ejecutar</option>
                  <option value="aprobar">Aprobar</option>
                </select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-modulo_id">Módulo ID</Label>
                <Input
                  id="edit-modulo_id"
                  type="number"
                  value={formData.modulo_id}
                  onChange={(e) => setFormData({ ...formData, modulo_id: parseInt(e.target.value) })}
                  placeholder="ID del módulo"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-descripcion_permiso">Descripción</Label>
                <Textarea
                  id="edit-descripcion_permiso"
                  value={formData.descripcion_permiso}
                  onChange={(e) => setFormData({ ...formData, descripcion_permiso: e.target.value })}
                  placeholder="Describe qué permite hacer este permiso..."
                  rows={3}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-estado_permiso">Estado</Label>
                <select
                  id="edit-estado_permiso"
                  value={formData.estado_permiso}
                  onChange={(e) => setFormData({ ...formData, estado_permiso: e.target.value })}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                >
                  <option value="activo">Activo</option>
                  <option value="inactivo">Inactivo</option>
                </select>
              </div>
            </div>
            <DialogFooter>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => {
                  setIsEditDialogOpen(false)
                  setSelectedPermission(null)
                  resetForm()
                }}
              >
                Cancelar
              </Button>
              <Button 
                type="submit" 
                disabled={editPermissionMutation.isPending}
              >
                {editPermissionMutation.isPending ? 'Guardando...' : 'Guardar Cambios'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}