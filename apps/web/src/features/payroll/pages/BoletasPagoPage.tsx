import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shared/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui/tabs'
import { useToast } from '@/shared/ui/use-toast'
import {
    useBoletas,
    useDescargaMasivaBoletas,
    useDownloadBoletaPdf,
    useGenerarBoletas,
    usePlanillas,
} from '@/features/payroll/hooks/useRemuneraciones'
import { Download, FileText, Loader2, PackageOpen } from 'lucide-react'
import { useState, type ReactNode } from 'react'

function getErrorMessage(error: unknown): string {
  if (error && typeof error === 'object' && 'response' in error) {
    const response = (error as Record<string, unknown>).response
    if (response && typeof response === 'object' && 'data' in response) {
      const data = (response as Record<string, unknown>).data
      if (data && typeof data === 'object' && 'message' in data) {
        const message = (data as Record<string, unknown>).message
        if (typeof message === 'string') return message
      }
    }
  }
  return ''
}

function toNumber(value: unknown): number {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string') {
    const parsed = Number.parseFloat(value.replace(',', '.').trim())
    return Number.isFinite(parsed) ? parsed : 0
  }
  return 0
}

function getBoletaBadgeVariant(estado?: string) {
  return estado === 'descargada' ? 'default' as const : 'outline' as const
}

function getPlanillaEstadoLabel(estado?: string): string {
  const labels: Record<string, string> = {
    generada: 'Calculada',
    aprobada: 'Aprobada',
    pagada: 'Pagada',
  }
  return labels[estado ?? ''] ?? estado ?? '-'
}

export default function BoletasPagoPage() {
  const { toast } = useToast()
  const [periodo, setPeriodo] = useState('')
  const [generandoPlanillaId, setGenerandoPlanillaId] = useState<number | null>(null)

  const { data: allPlanillas = [], isLoading: loadingPlanillas } = usePlanillas()

  // Filter planillas that are ready for boleta generation (generada or aprobada)
  const planillas = allPlanillas.filter((p) =>
    ['generada', 'aprobada', 'pagada'].includes(p.status ?? '')
  )
  const { data: boletas = [], isLoading: loadingBoletas, refetch: refetchBoletas } = useBoletas({
    periodo: periodo || undefined,
  })

  const generarMutation = useGenerarBoletas()
  const downloadMutation = useDownloadBoletaPdf()
  const descargaMasivaMutation = useDescargaMasivaBoletas()

  const handleGenerarBoletas = async (planillaId: number) => {
    setGenerandoPlanillaId(planillaId)
    try {
      const result = await generarMutation.mutateAsync(planillaId)
      toast({
        title: 'Boletas generadas',
        description: `${result.boletas_creadas} boletas creadas, ${result.boletas_existentes} ya existían.`,
      })
      refetchBoletas()
    } catch (error: unknown) {
      const msg = getErrorMessage(error)
      toast({
        title: 'Error al generar boletas',
        description: msg || 'No se pudieron generar las boletas.',
        variant: 'destructive',
      })
    } finally {
      setGenerandoPlanillaId(null)
    }
  }

  const handleDownload = (boletaId: number) => {
    downloadMutation.mutate(boletaId)
  }

  const handleDescargaMasiva = (planillaId: number) => {
    descargaMasivaMutation.mutate(planillaId, {
      onSuccess: () => {
        toast({
          title: 'Descarga masiva',
          description: 'Se descargó el archivo ZIP con todas las boletas.',
        })
      },
      onError: (error: unknown) => {
        const msg = getErrorMessage(error)
        toast({
          title: 'Error en descarga masiva',
          description: msg || 'No se pudo descargar el archivo.',
          variant: 'destructive',
        })
      },
    })
  }

  // Planillas aprobadas rows
  let planillaRows: ReactNode
  if (loadingPlanillas) {
    planillaRows = (
      <TableRow>
        <TableCell colSpan={7} className="text-center">Cargando planillas...</TableCell>
      </TableRow>
    )
  } else if (planillas.length === 0) {
    planillaRows = (
      <TableRow>
        <TableCell colSpan={7} className="text-center text-muted-foreground">
          No hay planillas listas para generar boletas. Genera y calcula una planilla desde Proceso de Planillas.
        </TableCell>
      </TableRow>
    )
  } else {
    planillaRows = planillas.map((p) => (
      <TableRow key={p.id}>
        <TableCell className="font-medium">{p.periodo}</TableCell>
        <TableCell>{p.modalidad || '-'}</TableCell>
        <TableCell>{p.meta_presupuestal || '-'}</TableCell>
        <TableCell>
          <Badge variant={p.status === 'aprobada' || p.status === 'pagada' ? 'default' : 'secondary'}>
            {getPlanillaEstadoLabel(p.status)}
          </Badge>
        </TableCell>
        <TableCell className="text-right">{p.total_trabajadores ?? 0}</TableCell>
        <TableCell className="text-right font-semibold">
          S/ {toNumber(p.total_neto_pagar ?? p.total_neto).toFixed(2)}
        </TableCell>
        <TableCell className="text-right">
          <div className="flex items-center justify-end gap-2">
            <Button
              size="sm"
              onClick={() => handleGenerarBoletas(p.id)}
              disabled={generarMutation.isPending && generandoPlanillaId === p.id}
            >
              {generarMutation.isPending && generandoPlanillaId === p.id ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Generando...</>
              ) : (
                <><FileText className="mr-2 h-4 w-4" />Generar Boletas</>
              )}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleDescargaMasiva(p.id)}
              disabled={descargaMasivaMutation.isPending}
              title="Descargar todas las boletas en ZIP"
            >
              {descargaMasivaMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <PackageOpen className="h-4 w-4" />
              )}
            </Button>
          </div>
        </TableCell>
      </TableRow>
    ))
  }

  // Boletas rows
  let boletaRows: ReactNode
  if (loadingBoletas) {
    boletaRows = (
      <TableRow>
        <TableCell colSpan={7} className="text-center">Cargando boletas...</TableCell>
      </TableRow>
    )
  } else if (boletas.length === 0) {
    boletaRows = (
      <TableRow>
        <TableCell colSpan={7} className="text-center text-muted-foreground">
          {periodo
            ? 'No hay boletas para este período. Genera boletas desde una planilla aprobada.'
            : 'Selecciona un período o genera boletas desde una planilla aprobada.'}
        </TableCell>
      </TableRow>
    )
  } else {
    boletaRows = boletas.map((b) => (
      <TableRow key={b.id}>
        <TableCell className="font-medium">
          {b.empleado_nombre || b.empleado?.nombres_completos || '-'}
        </TableCell>
        <TableCell>{b.empleado_dni || b.empleado?.dni || '-'}</TableCell>
        <TableCell>{b.periodo || '-'}</TableCell>
        <TableCell className="text-right">
          S/ {toNumber(b.neto_pagar).toFixed(2)}
        </TableCell>
        <TableCell>
          <Badge variant={getBoletaBadgeVariant(b.status)}>
            {b.estado_texto || b.status}
          </Badge>
        </TableCell>
        <TableCell>{b.fecha_generacion ? new Date(b.fecha_generacion).toLocaleDateString() : '-'}</TableCell>
        <TableCell className="text-right">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleDownload(b.id)}
            disabled={downloadMutation.isPending}
          >
            <Download className="h-4 w-4" />
          </Button>
        </TableCell>
      </TableRow>
    ))
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Boletas de Pago</h1>
        <p className="text-muted-foreground mt-1">
          Genera y descarga boletas de pago para planillas aprobadas.
        </p>
      </div>

      <Tabs defaultValue="generar" className="space-y-4">
        <TabsList>
          <TabsTrigger value="generar">Generar Boletas</TabsTrigger>
          <TabsTrigger value="consultar">Consultar Boletas</TabsTrigger>
        </TabsList>

        <TabsContent value="generar" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Planillas Aprobadas</CardTitle>
              <CardDescription>
                Selecciona una planilla aprobada para generar las boletas de pago de cada empleado.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Período</TableHead>
                    <TableHead>Modalidad</TableHead>
                    <TableHead>Meta Presupuestal</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead className="text-right">Trabajadores</TableHead>
                    <TableHead className="text-right">Total Neto</TableHead>
                    <TableHead className="text-right">Acción</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>{planillaRows}</TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="consultar" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Consultar Boletas</CardTitle>
              <CardDescription>
                Filtra por período para ver las boletas generadas.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-[1fr_auto_auto]">
                <div className="space-y-2">
                  <Label htmlFor="periodo-boleta">Período</Label>
                  <Input
                    id="periodo-boleta"
                    type="month"
                    value={periodo}
                    onChange={(e) => setPeriodo(e.target.value)}
                  />
                </div>
                <div className="self-end">
                  <Button variant="outline" onClick={() => refetchBoletas()}>
                    Buscar
                  </Button>
                </div>
                {boletas.length > 0 && (
                  <div className="self-end">
                    <Button
                      variant="secondary"
                      onClick={() => {
                        const planillaId = (boletas[0] as any).detalle_planilla?.planilla?.id
                          ?? (boletas[0] as any).detalle_planilla?.planilla;
                        if (planillaId) handleDescargaMasiva(planillaId)
                      }}
                      disabled={descargaMasivaMutation.isPending}
                    >
                      {descargaMasivaMutation.isPending ? (
                        <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Descargando...</>
                      ) : (
                        <><PackageOpen className="mr-2 h-4 w-4" />Descargar Todas</>
                      )}
                    </Button>
                  </div>
                )}
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Empleado</TableHead>
                    <TableHead>DNI</TableHead>
                    <TableHead>Período</TableHead>
                    <TableHead className="text-right">Neto</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead>Fecha Gen.</TableHead>
                    <TableHead className="text-right">Descargar</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>{boletaRows}</TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
