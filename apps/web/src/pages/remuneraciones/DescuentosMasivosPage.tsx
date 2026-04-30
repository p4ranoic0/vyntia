import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useToast } from '@/components/ui/use-toast'
import { 
  useDescuentosMasivos, 
  useCreateDescuento, 
  useProcesarDescuento,
  useAnularDescuento,
  useDeleteDescuento,
  useConceptosRemuneracion,
} from '@/hooks/useRemuneraciones'
import type { ConfiguracionRemuneracion, DescuentoMasivo } from '@/services/payrollService'
import { Upload, Trash2, Play, XCircle, AlertCircle } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

function getEstadoBadgeVariant(estado: string) {
  switch (estado) {
    case 'aplicado':
      return 'default'
    case 'procesado':
      return 'secondary'
    case 'anulado':
      return 'destructive'
    default:
      return 'outline'
  }
}

export default function DescuentosMasivosPage() {
  const { toast } = useToast()
  const [showUploadDialog, setShowUploadDialog] = useState(false)
  const [showErrorDialog, setShowErrorDialog] = useState(false)
  const [processingErrors, setProcessingErrors] = useState<string[]>([])
  const [selectedPeriodo, setSelectedPeriodo] = useState('')
  const [selectedEstado, setSelectedEstado] = useState<'all' | string>('all')

  // Form state
  const [periodo, setPeriodo] = useState('')
  const [conceptoId, setConceptoId] = useState('')
  const [archivo, setArchivo] = useState<File | null>(null)

  const { data: descuentos = [], isLoading, refetch } = useDescuentosMasivos({
    periodo: selectedPeriodo || undefined,
  })

  const { data: conceptos = [] } = useConceptosRemuneracion({ tipo: 'descuento' })

  const createMutation = useCreateDescuento()
  const procesarMutation = useProcesarDescuento()
  const anularMutation = useAnularDescuento()
  const deleteMutation = useDeleteDescuento()

  const handleUpload = async () => {
    if (!periodo || !conceptoId || !archivo) {
      toast({
        title: 'Error',
        description: 'Completa todos los campos requeridos',
        variant: 'destructive',
      })
      return
    }

    try {
      const payload = {
        periodo,
        configuracion_concepto_id: Number.parseInt(conceptoId, 10),
        archivo_origen: archivo,
      } as unknown as Parameters<typeof createMutation.mutateAsync>[0]

      await createMutation.mutateAsync(payload)

      toast({
        title: 'Éxito',
        description: 'Archivo cargado exitosamente',
      })

      setShowUploadDialog(false)
      setPeriodo('')
      setConceptoId('')
      setArchivo(null)
      refetch()
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error al cargar archivo'
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      })
    }
  }

  const handleProcesar = async (id: number) => {
    try {
      const resultado = await procesarMutation.mutateAsync(id)

      if (resultado.registros_error > 0) {
        setProcessingErrors(resultado.errores || [])
        setShowErrorDialog(true)
      }

      toast({
        title: 'Procesamiento completado',
        description: `Procesados: ${resultado.registros_procesados} de ${resultado.total_registros}. Errores: ${resultado.registros_error}`,
      })

      refetch()
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error al procesar descuento'
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      })
    }
  }

  const handleAnular = async (id: number) => {
    if (!confirm('¿Estás seguro de anular este descuento? Se revertirán todos los descuentos aplicados.')) {
      return
    }

    try {
      const resultado = await anularMutation.mutateAsync(id)

      toast({
        title: 'Descuento anulado',
        description: `Se eliminaron ${resultado.conceptos_eliminados} conceptos`,
      })

      refetch()
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error al anular descuento'
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      })
    }
  }

  const handleDelete = async (id: number, estado: EstadoDescuento) => {
    if (estado !== 'pendiente') {
      toast({
        title: 'Error',
        description: 'Solo se pueden eliminar descuentos pendientes',
        variant: 'destructive',
      })
      return
    }

    if (!confirm('¿Estás seguro de eliminar este descuento?')) {
      return
    }

    try {
      await deleteMutation.mutateAsync(id)
      toast({
        title: 'Éxito',
        description: 'Descuento eliminado',
      })
      refetch()
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error al eliminar'
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      })
    }
  }

  const conceptosDescuento = conceptos.filter((c: ConfiguracionRemuneracion) => c.tipo === 'descuento')

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Descuentos Masivos</h1>
          <p className="text-muted-foreground">
            Carga y procesa descuentos masivos desde archivos Excel
          </p>
        </div>
        <Button onClick={() => setShowUploadDialog(true)}>
          <Upload className="mr-2 h-4 w-4" />
          Cargar Descuento
        </Button>
      </div>

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Periodo</Label>
              <Input
                type="month"
                value={selectedPeriodo}
                onChange={(e) => setSelectedPeriodo(e.target.value)}
                placeholder="YYYY-MM"
              />
            </div>
            <div className="space-y-2">
              <Label>Estado</Label>
              <Select value={selectedEstado} onValueChange={(val) => setSelectedEstado(val as EstadoDescuento | 'all')}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  <SelectItem value="pendiente">Pendiente</SelectItem>
                  <SelectItem value="procesado">Procesado</SelectItem>
                  <SelectItem value="aplicado">Aplicado</SelectItem>
                  <SelectItem value="anulado">Anulado</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabla de descuentos */}
      <Card>
        <CardHeader>
          <CardTitle>Descuentos Cargados</CardTitle>
          <CardDescription>
            Lista de archivos Excel cargados para descuentos masivos
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Periodo</TableHead>
                <TableHead>Concepto</TableHead>
                <TableHead>Total Registros</TableHead>
                <TableHead>Procesados</TableHead>
                <TableHead>Errores</TableHead>
                <TableHead className="text-right">Monto Total</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Usuario</TableHead>
                <TableHead>Fecha Carga</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading && (
                <TableRow>
                  <TableCell colSpan={10} className="text-center">
                    Cargando...
                  </TableCell>
                </TableRow>
              )}
              {!isLoading && descuentos.length === 0 && (
                <TableRow>
                  <TableCell colSpan={10} className="text-center text-muted-foreground">
                    No hay descuentos masivos cargados
                  </TableCell>
                </TableRow>
              )}
              {!isLoading && descuentos.length > 0 && descuentos.map((descuento: DescuentoMasivo) => (
                <TableRow key={descuento.descuento_masivo_id}>
                  <TableCell>{descuento.periodo}</TableCell>
                  <TableCell>{descuento.configuracion_concepto?.nombre || 'N/A'}</TableCell>
                  <TableCell>{descuento.total_registros}</TableCell>
                  <TableCell>{descuento.registros_procesados}</TableCell>
                  <TableCell>
                    {descuento.registros_error > 0 ? (
                      <span className="text-red-600 font-medium">{descuento.registros_error}</span>
                    ) : (
                      descuento.registros_error
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    S/ {Number(descuento.monto_total || 0).toFixed(2)}
                  </TableCell>
                  <TableCell>
                    <Badge variant={getEstadoBadgeVariant(descuento.status)}>
                      {descuento.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{descuento.usuario_carga?.username || 'N/A'}</TableCell>
                  <TableCell>
                    {new Date(descuento.fecha_carga).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {descuento.status === 'pendiente' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleProcesar(descuento.descuento_masivo_id)}
                          disabled={procesarMutation.isPending}
                        >
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                      {descuento.status === 'procesado' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleAnular(descuento.descuento_masivo_id)}
                          disabled={anularMutation.isPending}
                        >
                          <XCircle className="h-4 w-4" />
                        </Button>
                      )}
                      {descuento.status === 'pendiente' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(descuento.descuento_masivo_id, descuento.status)}
                          disabled={deleteMutation.isPending}
                        >
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Dialog para cargar descuento */}
      <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cargar Descuento Masivo</DialogTitle>
            <DialogDescription>
              Sube un archivo Excel con los descuentos a aplicar. El archivo debe contener las columnas: DNI, MONTO, OBSERVACION (opcional).
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Periodo *</Label>
              <Input
                type="month"
                value={periodo}
                onChange={(e) => setPeriodo(e.target.value)}
                placeholder="YYYY-MM"
              />
            </div>
            <div className="space-y-2">
              <Label>Concepto de Descuento *</Label>
              <Select value={conceptoId} onValueChange={setConceptoId}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un concepto" />
                </SelectTrigger>
                <SelectContent>
                  {conceptosDescuento.map((concepto: ConfiguracionRemuneracion) => (
                    <SelectItem key={concepto.configuracion_id} value={concepto.configuracion_id.toString()}>
                      {concepto.nombre}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Archivo Excel *</Label>
              <Input
                type="file"
                accept=".xlsx,.xls"
                onChange={(e) => setArchivo(e.target.files?.[0] || null)}
              />
              <p className="text-xs text-muted-foreground">
                Formato: DNI | MONTO | OBSERVACION (opcional)
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowUploadDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={handleUpload} disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Cargando...' : 'Cargar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog de errores */}
      <Dialog open={showErrorDialog} onOpenChange={setShowErrorDialog}>
        <DialogContent className="max-w-2xl max-h-[600px] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Errores de Procesamiento</DialogTitle>
            <DialogDescription>
              Se encontraron los siguientes errores durante el procesamiento
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            {processingErrors.map((error) => (
              <Alert key={error} variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            ))}
          </div>
          <DialogFooter>
            <Button onClick={() => setShowErrorDialog(false)}>Cerrar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
