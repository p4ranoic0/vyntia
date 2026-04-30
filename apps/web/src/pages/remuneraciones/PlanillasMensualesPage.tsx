import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useToast } from '@/components/ui/use-toast'
import { useCreatePlanilla, useDeletePlanilla, usePlanillas } from '@/hooks/useRemuneraciones'
import type { EstadoPlanilla, ModalidadContrato } from '@/services/payrollService'
import { Eye, Plus, Trash2 } from 'lucide-react'
import { useMemo, useState, type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'

function getErrorMessage(error: unknown, fallback: string): string {
  if (error && typeof error === 'object' && 'response' in error) {
    const response = (error as { response?: { data?: { message?: unknown } } }).response
    const message = response?.data?.message
    if (typeof message === 'string' && message.trim().length > 0) {
      return message
    }
  }
  return fallback
}

function toNumber(value: unknown): number {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }
  if (typeof value === 'string') {
    const normalized = value.replace(',', '.').trim()
    const parsed = Number.parseFloat(normalized)
    return Number.isFinite(parsed) ? parsed : 0
  }
  return 0
}

export default function PlanillasMensualesPage() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [periodo, setPeriodo] = useState('')
  const [modalidad, setModalidad] = useState<ModalidadContrato | 'all'>('all')
  const [estado, setEstado] = useState<EstadoPlanilla | 'all'>('all')
  const [showCreateDialog, setShowCreateDialog] = useState(false)

  // Form state
  const [newPeriodo, setNewPeriodo] = useState('')
  const [newModalidad, setNewModalidad] = useState<ModalidadContrato>('CAS')
  const [newMeta, setNewMeta] = useState('')
  const [newDescripcion, setNewDescripcion] = useState('')

  // Mapeo de modalidades frontend -> backend
  const mapModalidadToBackend = (modalidad: ModalidadContrato): ModalidadContrato => {
    const mapping: Record<ModalidadContrato, ModalidadContrato> = {
      CAS: 'plazo_determinado',
      CAP: 'plazo_indeterminado',
      NOMBRADO: 'plazo_indeterminado',
      PRACTICANTE: 'locacion',
      TERCERO: 'consultoria',
    }
    return mapping[modalidad] || modalidad
  }

  // Formatear período a YYYY-MM si viene del input month
  const formatPeriodo = (period: string): string => {
    if (!period) return ''
    // Si ya está en formato YYYY-MM, devolverlo tal cual
    if (/^\d{4}-\d{2}$/.test(period)) return period
    // Si viene del input month, transformar
    return period
  }

  const { data: planillas = [], isLoading, refetch } = usePlanillas({
    periodo: periodo || undefined,
    modalidad: modalidad === 'all' ? undefined : modalidad,
    estado: estado === 'all' ? undefined : estado,
  })

  const createMutation = useCreatePlanilla()
  const deleteMutation = useDeletePlanilla()

  const filtered = useMemo(() => {
    return planillas
  }, [planillas])

  const handleCreate = async () => {
    if (!newPeriodo || !newMeta) {
      toast({
        title: 'Campos requeridos',
        description: 'El periodo y meta presupuestal son obligatorios.',
        variant: 'destructive',
      })
      return
    }

    try {
      const formattedPeriodo = formatPeriodo(newPeriodo)
      const backendModalidad = mapModalidadToBackend(newModalidad)

      await createMutation.mutateAsync({
        periodo: formattedPeriodo,
        modalidad: backendModalidad,
        meta_presupuestal: newMeta,
        descripcion: newDescripcion,
      })

      toast({
        title: 'Planilla creada',
        description: 'La planilla se ha creado exitosamente.',
      })

      setShowCreateDialog(false)
      setNewPeriodo('')
      setNewMeta('')
      setNewDescripcion('')
      setNewModalidad('CAS')
      refetch()
    } catch (error: unknown) {
      const errorMsg = getErrorMessage(error, 'No se pudo crear la planilla.')
      toast({
        title: 'Error',
        description: errorMsg,
        variant: 'destructive',
      })
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('¿Estás seguro de eliminar esta planilla?')) return

    try {
      await deleteMutation.mutateAsync(id)
      toast({
        title: 'Planilla eliminada',
        description: 'La planilla se ha eliminado correctamente.',
      })
      refetch()
    } catch (error: unknown) {
      toast({
        title: 'Error',
        description: getErrorMessage(error, 'No se pudo eliminar la planilla.'),
        variant: 'destructive',
      })
    }
  }

  const getEstadoBadgeVariant = (estado?: string) => {
    switch (estado) {
      case 'aprobada':
      case 'pagada':
        return 'default'
      case 'calculada':
        return 'secondary'
      case 'anulada':
        return 'destructive'
      default:
        return 'outline'
    }
  }

  let planillasRows: ReactNode

  if (isLoading) {
    planillasRows = (
      <TableRow>
        <TableCell colSpan={9} className="text-center">
          Cargando planillas...
        </TableCell>
      </TableRow>
    )
  } else if (filtered.length === 0) {
    planillasRows = (
      <TableRow>
        <TableCell colSpan={9} className="text-center text-muted-foreground">
          No hay planillas que coincidan con los filtros.
        </TableCell>
      </TableRow>
    )
  } else {
    planillasRows = filtered.map((planilla) => {
      const totalIngresos = toNumber(
        planilla.total_remuneracion_bruta ?? planilla.total_ingresos
      )
      const totalDescuentos = toNumber(planilla.total_descuentos)
      const totalNeto = toNumber(planilla.total_neto_pagar ?? planilla.total_neto)
      return (
        <TableRow key={planilla.planilla_id}>
          <TableCell className="font-medium">{planilla.periodo}</TableCell>
          <TableCell>{planilla.modalidad || '-'}</TableCell>
          <TableCell>{planilla.meta_presupuestal || '-'}</TableCell>
          <TableCell className="text-right">{planilla.total_trabajadores ?? 0}</TableCell>
          <TableCell className="text-right">S/ {totalIngresos.toFixed(2)}</TableCell>
          <TableCell className="text-right">S/ {totalDescuentos.toFixed(2)}</TableCell>
          <TableCell className="text-right font-semibold">S/ {totalNeto.toFixed(2)}</TableCell>
          <TableCell>
            <Badge variant={getEstadoBadgeVariant(planilla.status)}>
              {planilla.status_texto || planilla.status || 'Desconocido'}
            </Badge>
          </TableCell>
          <TableCell className="text-right space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(`/remuneraciones/proceso-planillas?planilla=${planilla.planilla_id}`)}
            >
              <Eye className="h-4 w-4" />
            </Button>
            {planilla.status === 'borrador' && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleDelete(planilla.planilla_id)}
                disabled={deleteMutation.isPending}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </TableCell>
        </TableRow>
      )
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Planillas Mensuales</h1>
          <p className="text-muted-foreground mt-1">
            Gestión y consulta de planillas por periodo, modalidad y estado.
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Nueva Planilla
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
          <CardDescription>Filtra por período, modalidad y estado.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <div className="space-y-2">
            <Label htmlFor="periodo-filter">Periodo</Label>
            <Input
              id="periodo-filter"
              type="month"
              value={periodo}
              onChange={(e) => setPeriodo(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label>Modalidad</Label>
            <Select value={modalidad} onValueChange={(val) => setModalidad(val as ModalidadContrato | 'all')}>
              <SelectTrigger>
                <SelectValue placeholder="Selecciona modalidad" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas</SelectItem>
                <SelectItem value="CAS">CAS</SelectItem>
                <SelectItem value="CAP">CAP</SelectItem>
                <SelectItem value="NOMBRADO">Nombrado</SelectItem>
                <SelectItem value="PRACTICANTE">Practicante</SelectItem>
                <SelectItem value="TERCERO">Tercero</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Estado</Label>
            <Select value={estado} onValueChange={(val) => setEstado(val as EstadoPlanilla | 'all')}>
              <SelectTrigger>
                <SelectValue placeholder="Selecciona estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="borrador">Borrador</SelectItem>
                <SelectItem value="generada">Generada</SelectItem>
                <SelectItem value="calculada">Calculada</SelectItem>
                <SelectItem value="aprobada">Aprobada</SelectItem>
                <SelectItem value="pagada">Pagada</SelectItem>
                <SelectItem value="anulada">Anulada</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Resumen de Planillas ({filtered.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Periodo</TableHead>
                <TableHead>Modalidad</TableHead>
                <TableHead>Meta Presup.</TableHead>
                <TableHead className="text-right">Trabajadores</TableHead>
                <TableHead className="text-right">Total Ingresos</TableHead>
                <TableHead className="text-right">Total Descuentos</TableHead>
                <TableHead className="text-right">Neto Total</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead className="text-right">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>{planillasRows}</TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nueva Planilla Mensual</DialogTitle>
            <DialogDescription>
              Crea una nueva planilla para procesar remuneraciones.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="new-periodo">Periodo *</Label>
              <Input
                id="new-periodo"
                type="month"
                value={newPeriodo}
                onChange={(e) => setNewPeriodo(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label>Modalidad *</Label>
              <Select value={newModalidad} onValueChange={(val) => setNewModalidad(val as ModalidadContrato)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="CAS">CAS</SelectItem>
                  <SelectItem value="CAP">CAP</SelectItem>
                  <SelectItem value="NOMBRADO">Nombrado</SelectItem>
                  <SelectItem value="PRACTICANTE">Practicante</SelectItem>
                  <SelectItem value="TERCERO">Tercero</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="new-meta">Meta Presupuestal *</Label>
              <Input
                id="new-meta"
                placeholder="Ej: 001.0001.0001"
                value={newMeta}
                onChange={(e) => setNewMeta(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="new-descripcion">Descripción (opcional)</Label>
              <Input
                id="new-descripcion"
                placeholder="Descripción de la planilla"
                value={newDescripcion}
                onChange={(e) => setNewDescripcion(e.target.value)}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={handleCreate} disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creando...' : 'Crear Planilla'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
