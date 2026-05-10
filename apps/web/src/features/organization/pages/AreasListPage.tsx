import { AreaForm } from '@/features/organization/components/AreaForm'
import { DataTable } from '@/shared/components/DataTable'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { AreasLayout } from '@/shared/layout/AreasLayout'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/shared/ui/dropdown-menu'
import { Input } from '@/shared/ui/input'
import { useToast } from '@/shared/ui/use-toast'
import { getErrorMessage } from '@/shared/api/errorUtils'
import { departmentsService, Area as AreaType, CreateAreaData } from '@/features/organization/services/departmentsService'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ColumnDef } from '@tanstack/react-table'
import { Building2, Edit, MoreHorizontal, Plus, Search, Trash2, Users } from 'lucide-react'
import { useState } from 'react'

// Usando la interfaz Area del servicio

export function AreasListPage() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [selectedArea, setSelectedArea] = useState<AreaType | null>(null)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingArea, setEditingArea] = useState<AreaType | null>(null)

  const { data: areasData, isLoading, error } = useQuery({
    queryKey: ['areas'],
    queryFn: () => departmentsService.getAreas(),
  })

  const areas = areasData?.data || []

  // Delete area mutation
  const deleteAreaMutation = useMutation({
    mutationFn: (id: number) => departmentsService.deleteArea(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['areas'] })
      toast({
        title: 'Área eliminada',
        description: 'El área se ha eliminado exitosamente.',
      })
      setIsDeleteDialogOpen(false)
      setSelectedArea(null)
    },
    onError: (error: unknown) => {
      toast({
        title: 'Error',
        description: getErrorMessage(error, 'No se pudo eliminar el área.'),
        variant: 'destructive',
      })
    },
  })

  const handleEdit = (area: AreaType) => {
    setEditingArea(area)
    setIsFormOpen(true)
  }

  const handleCreate = () => {
    setEditingArea(null)
    setIsFormOpen(true)
  }

  const handleDelete = (area: AreaType) => {
    setSelectedArea(area)
    setIsDeleteDialogOpen(true)
  }

  const confirmDelete = () => {
    if (selectedArea) {
      deleteAreaMutation.mutate(selectedArea.id)
    }
  }

  // Mutación para crear área
  const createAreaMutation = useMutation({
    mutationFn: (data: CreateAreaData) => departmentsService.createArea(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['areas'] })
      toast({
        title: 'Área creada',
        description: 'El área se ha creado exitosamente.',
      })
      setIsFormOpen(false)
      setEditingArea(null)
    },
    onError: (error: unknown) => {
      toast({
        title: 'Error',
        description: getErrorMessage(error, 'No se pudo crear el área.'),
        variant: 'destructive',
      })
    },
  })

  // Mutación para actualizar área
  const updateAreaMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateAreaData> }) => departmentsService.updateArea(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['areas'] })
      toast({
        title: 'Área actualizada',
        description: 'El área se ha actualizado exitosamente.',
      })
      setIsFormOpen(false)
      setEditingArea(null)
    },
    onError: (error: unknown) => {
      toast({
        title: 'Error',
        description: getErrorMessage(error, 'No se pudo actualizar el área.'),
        variant: 'destructive',
      })
    },
  })

  const handleFormSubmit = async (data: CreateAreaData) => {
    if (editingArea) {
      await updateAreaMutation.mutateAsync({ id: editingArea.id, data })
    } else {
      await createAreaMutation.mutateAsync(data)
    }
  }

  const columns: ColumnDef<AreaType>[] = [
    {
      accessorKey: 'nombre_organo',
      header: 'Órgano',
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue('nombre_organo')}</div>
      ),
    },
    {
      accessorKey: 'nombre_unidad_organica',
      header: 'Unidad Orgánica',
      cell: ({ row }) => (
        <div>{row.getValue('nombre_unidad_organica') || 'N/A'}</div>
      ),
    },
    {
      accessorKey: 'siglas_area',
      header: 'Siglas',
      cell: ({ row }) => (
        <Badge variant="outline">{row.getValue('siglas_area')}</Badge>
      ),
    },
    {
      accessorKey: 'nombre_completo',
      header: 'Nombre Completo',
      cell: ({ row }) => (
        <div>{row.getValue('nombre_completo') || 'Sin definir'}</div>
      ),
    },
    {
      accessorKey: 'empleados_activos_count',
      header: 'Empleados Activos',
      cell: ({ row }) => (
        <div className="flex items-center gap-1">
          <Users className="h-4 w-4 text-muted-foreground" />
          {row.getValue('empleados_activos_count') || 0}
        </div>
      ),
    },
    {
      accessorKey: 'estado_area',
      header: 'Estado',
      cell: ({ row }) => {
        const estado = row.getValue('estado_area') as string
        return (
          <Badge variant={estado === 'activo' ? 'default' : 'secondary'}>
            {estado === 'activo' ? 'Activo' : 'Inactivo'}
          </Badge>
        )
      },
    },
    {
      id: 'actions',
      header: 'Acciones',
      cell: ({ row }) => {
        const area = row.original
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
              <DropdownMenuItem onClick={() => navigator.clipboard.writeText(area.id)}>
                Copiar ID
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => handleEdit(area)}>
                <Edit className="mr-2 h-4 w-4" />
                Editar
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => handleDelete(area)}
                className="text-red-600"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Eliminar
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-600 mb-2">Error al cargar las áreas</p>
          <Button onClick={() => window.location.reload()}>Reintentar</Button>
        </div>
      </div>
    )
  }

  return (
    <AreasLayout 
      title="Listado de Áreas" 
      description="Gestiona las áreas organizacionales de la empresa"
    >
      <div className="space-y-4 sm:space-y-6">
        {/* Header con botón de acción */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar áreas..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8"
            />
          </div>
          <Button className="bg-blue-600 hover:bg-blue-700 cursor-pointer w-full sm:w-auto" onClick={handleCreate}>
            <Plus className="h-4 w-4 mr-2" />
            Nueva Área
          </Button>
        </div>

      {/* Stats Cards */}
      <div className="grid gap-3 sm:gap-4 grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Áreas</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{areas.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Áreas Activas</CardTitle>
            <Building2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {areas.filter(area => area.estado_area === 'activo').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Empleados Activos</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {areas.reduce((total, area) => total + (area.empleados_activos_count || 0), 0)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Áreas Inactivas</CardTitle>
            <Users className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {areas.filter(area => area.estado_area === 'inactivo').length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Data Table */}
      <Card>
        <CardHeader>
          <CardTitle>Listado de Áreas</CardTitle>
          <CardDescription>
            Visualiza y gestiona todas las áreas organizacionales
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <DataTable columns={columns} data={areas} />
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      {isDeleteDialogOpen && selectedArea && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-card p-4 sm:p-6 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Confirmar Eliminación</h3>
            <p className="text-gray-600 mb-6">
              ¿Estás seguro de que deseas eliminar el área "{selectedArea.nombre_organo}"? 
              Esta acción no se puede deshacer.
            </p>
            <div className="flex justify-end gap-3">
              <Button 
                variant="outline" 
                onClick={() => {
                  setIsDeleteDialogOpen(false)
                  setSelectedArea(null)
                }}
                disabled={deleteAreaMutation.isPending}
              >
                Cancelar
              </Button>
              <Button 
                variant="destructive" 
                onClick={confirmDelete}
                disabled={deleteAreaMutation.isPending}
              >
                {deleteAreaMutation.isPending ? 'Eliminando...' : 'Eliminar'}
              </Button>
            </div>
          </div>
        </div>
      )}
      </div>

      {/* Formulario de área */}
      <AreaForm
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        area={editingArea}
        onSubmit={handleFormSubmit}
        isLoading={createAreaMutation.isPending || updateAreaMutation.isPending}
      />
    </AreasLayout>
  )
}