import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/components/ui/use-toast'
import {
    useAprobarPlanilla,
    useCalcularPlanilla,
    useDetallesPlanilla,
    useEstadisticasPlanilla,
    useGenerarPlanilla,
    usePlanilla,
    usePreviewPlanilla,
} from '@/hooks/useRemuneraciones'
import { Calculator, Check, Eye, FileSpreadsheet, TrendingUp } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { useSearchParams } from 'react-router-dom'

function getErrorMessage(error: unknown): string {
  if (error && typeof error === 'object' && 'response' in error) {
    const response = (error as Record<string, unknown>).response
    if (response && typeof response === 'object' && 'data' in response) {
      const data = (response as Record<string, unknown>).data
      if (data && typeof data === 'object' && 'message' in data) {
        const message = (data as Record<string, unknown>).message
        if (typeof message === 'string') {
          return message
        }
      }
    }
  }
  return ''
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

export default function ProcesoPlanillasPage() {
  const { toast } = useToast()
  const [searchParams] = useSearchParams()
  const [previewData, setPreviewData] = useState<Record<string, unknown> | null>(null)
  const planillaIdParam = searchParams.get('planilla')
  const planillaId = planillaIdParam ? Number.parseInt(planillaIdParam, 10) : null

  const { data: planilla, isLoading: loadingPlanilla, refetch: refetchPlanilla } = usePlanilla(planillaId)
  const { data: detalles = [], isLoading: loadingDetalles, refetch: refetchDetalles } = useDetallesPlanilla({
    planilla: planillaId || undefined,
  })
  const { data: estadisticas, refetch: refetchEstadisticas } = useEstadisticasPlanilla(planillaId)

  const generarMutation = useGenerarPlanilla()
  const calcularMutation = useCalcularPlanilla()
  const previewMutation = usePreviewPlanilla()
  const aprobarMutation = useAprobarPlanilla()

  const handleGenerar = async () => {
    if (!planillaId) return

    try {
      const result = await generarMutation.mutateAsync(planillaId)
      toast({
        title: 'Planilla generada',
        description: `Se agregaron ${result.empleados_agregados ?? 0} empleados a la planilla.`,
      })
      refetchPlanilla()
      refetchDetalles()
      refetchEstadisticas()
    } catch (error: unknown) {
      const errorMsg = getErrorMessage(error)
      toast({
        title: 'Error al generar',
        description: errorMsg || 'No se pudo generar la planilla.',
        variant: 'destructive',
      })
    }
  }

  const handleCalcular = async () => {
    if (!planillaId) return

    try {
      await calcularMutation.mutateAsync(planillaId)
      toast({
        title: 'Planilla calculada',
        description: 'Los haberes y descuentos han sido calculados.',
      })
      refetchPlanilla()
      refetchDetalles()
      refetchEstadisticas()
    } catch (error: unknown) {
      const errorMsg = getErrorMessage(error)
      toast({
        title: 'Error al calcular',
        description: errorMsg || 'No se pudo calcular la planilla.',
        variant: 'destructive',
      })
    }
  }

  const handlePreview = async () => {
    if (!planillaId) return

    try {
      const result = await previewMutation.mutateAsync(planillaId)
      setPreviewData(result)
      toast({
        title: 'Vista previa generada',
        description: 'Se obtuvo la simulación de la planilla sin persistir cambios.',
      })
    } catch (error: unknown) {
      const errorMsg = getErrorMessage(error)
      toast({
        title: 'Vista previa no disponible',
        description: errorMsg || 'El endpoint de preview aún no está disponible en backend.',
        variant: 'destructive',
      })
    }
  }

  const handleAprobar = async () => {
    if (!planillaId) return

    if (!confirm('¿Estás seguro de aprobar esta planilla? Esta acción no se puede deshacer.')) return

    try {
      await aprobarMutation.mutateAsync(planillaId)
      toast({
        title: 'Planilla aprobada',
        description: 'La planilla ha sido aprobada exitosamente.',
      })
      refetchPlanilla()
    } catch (error: unknown) {
      const errorMsg = getErrorMessage(error)
      toast({
        title: 'Error al aprobar',
        description: errorMsg || 'No se pudo aprobar la planilla.',
        variant: 'destructive',
      })
    }
  }

  if (!planillaId) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Proceso de Planillas</h1>
          <p className="text-muted-foreground mt-1">
            Selecciona una planilla desde el listado de Planillas Mensuales.
          </p>
        </div>
      </div>
    )
  }

  if (loadingPlanilla) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">Cargando planilla...</div>
      </div>
    )
  }

  if (!planilla) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12 text-destructive">No se encontró la planilla.</div>
      </div>
    )
  }

  const currentEstado = planilla.estado ?? ''
  const canGenerate = ['borrador', 'procesando'].includes(currentEstado)
  const canCalculate = ['borrador', 'generada', 'procesando'].includes(currentEstado)
  const canApprove = currentEstado === 'generada'

  let detalleRows: ReactNode

  if (loadingDetalles) {
    detalleRows = (
      <TableRow>
        <TableCell colSpan={9} className="text-center">
          Cargando detalles...
        </TableCell>
      </TableRow>
    )
  } else if (detalles.length === 0) {
    detalleRows = (
      <TableRow>
        <TableCell colSpan={9} className="text-center text-muted-foreground">
          No hay detalles. Genera la planilla primero.
        </TableCell>
      </TableRow>
    )
  } else {
    detalleRows = detalles.map((detalle) => (
      <TableRow key={detalle.detalle_id}>
        <TableCell className="font-medium">
          {detalle.empleado.nombres_completos}
        </TableCell>
        <TableCell>{detalle.empleado.dni}</TableCell>
        <TableCell>{detalle.empleado.area_nombre}</TableCell>
        <TableCell className="text-right">{detalle.dias_laborados}</TableCell>
        <TableCell className="text-right">
          S/ {toNumber(detalle.remuneracion_basica).toFixed(2)}
        </TableCell>
        <TableCell className="text-right">
          S/ {toNumber(detalle.total_ingresos).toFixed(2)}
        </TableCell>
        <TableCell className="text-right">
          S/ {toNumber(detalle.total_descuentos).toFixed(2)}
        </TableCell>
        <TableCell className="text-right font-semibold">
          S/ {toNumber(detalle.neto_pagar).toFixed(2)}
        </TableCell>
        <TableCell>
          <Badge variant={detalle.estado === 'activo' ? 'default' : 'secondary'}>
            {detalle.estado_texto || detalle.estado}
          </Badge>
        </TableCell>
      </TableRow>
    ))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Proceso de Planilla: {planilla.periodo}</h1>
          <p className="text-muted-foreground mt-1">
            {planilla.modalidad} - {planilla.meta_presupuestal}
          </p>
        </div>
        <Badge variant={planilla.estado === 'aprobada' ? 'default' : 'outline'} className="text-sm">
          {planilla.estado_texto || planilla.estado}
        </Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Trabajadores</CardTitle>
            <FileSpreadsheet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{planilla.total_trabajadores}</div>
            <p className="text-xs text-muted-foreground">Empleados en planilla</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Ingresos</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">S/ {toNumber(planilla.total_remuneracion_bruta ?? planilla.total_ingresos).toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">Remuneraciones brutas</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Descuentos</CardTitle>
            <Calculator className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">S/ {toNumber(planilla.total_descuentos).toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">AFP/ONP y otros</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Neto</CardTitle>
            <Check className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">S/ {toNumber(planilla.total_neto_pagar ?? planilla.total_neto).toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">A pagar</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Acciones de Proceso</CardTitle>
          <CardDescription>
            Generar detalles, calcular aportes y aprobar para cierre.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button
            onClick={handleGenerar}
            disabled={!canGenerate || generarMutation.isPending}
          >
            <FileSpreadsheet className="mr-2 h-4 w-4" />
            {generarMutation.isPending ? 'Generando...' : 'Generar Planilla'}
          </Button>

          <Button
            onClick={handleCalcular}
            disabled={!canCalculate || calcularMutation.isPending}
            variant="secondary"
          >
            <Calculator className="mr-2 h-4 w-4" />
            {calcularMutation.isPending ? 'Calculando...' : 'Calcular Planilla'}
          </Button>

          <Button
            onClick={handlePreview}
            disabled={previewMutation.isPending}
            variant="outline"
          >
            <Eye className="mr-2 h-4 w-4" />
            {previewMutation.isPending ? 'Generando vista previa...' : 'Vista Previa'}
          </Button>

          <Button
            onClick={handleAprobar}
            disabled={!canApprove || aprobarMutation.isPending}
            variant="default"
          >
            <Check className="mr-2 h-4 w-4" />
            {aprobarMutation.isPending ? 'Aprobando...' : 'Aprobar Planilla'}
          </Button>
        </CardContent>
      </Card>

      {previewData && (
        <Card>
          <CardHeader>
            <CardTitle>Vista Previa (Simulación)</CardTitle>
            <CardDescription>
              Resultado de simulación sin registrar cambios definitivos en la planilla.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="max-h-80 overflow-auto rounded bg-slate-950 p-4 text-xs text-slate-100">
              {JSON.stringify(previewData, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="detalles" className="space-y-4">
        <TabsList>
          <TabsTrigger value="detalles">Detalles ({detalles.length})</TabsTrigger>
          <TabsTrigger value="estadisticas">Estadísticas</TabsTrigger>
        </TabsList>

        <TabsContent value="detalles" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Detalles de Planilla</CardTitle>
              <CardDescription>
                Información de cada empleado incluido en esta planilla.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Empleado</TableHead>
                    <TableHead>DNI</TableHead>
                    <TableHead>Área</TableHead>
                    <TableHead className="text-right">Días Lab.</TableHead>
                    <TableHead className="text-right">Rem. Básica</TableHead>
                    <TableHead className="text-right">Total Ingresos</TableHead>
                    <TableHead className="text-right">Total Desc.</TableHead>
                    <TableHead className="text-right">Neto</TableHead>
                    <TableHead>Estado</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>{detalleRows}</TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="estadisticas" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Estadísticas de Planilla</CardTitle>
              <CardDescription>
                Resumen agregado de la planilla procesada.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {estadisticas ? (
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <Label>Promedio de Remuneración</Label>
                    <div className="text-2xl font-bold">
                      S/ {toNumber(estadisticas.promedio_remuneracion).toFixed(2)}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Total ESSALUD</Label>
                    <div className="text-2xl font-bold">
                      S/ {toNumber(estadisticas.total_essalud).toFixed(2)}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Total AFP</Label>
                    <div className="text-2xl font-bold">
                      S/ {toNumber(estadisticas.total_afp).toFixed(2)}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  No hay estadísticas disponibles.
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
