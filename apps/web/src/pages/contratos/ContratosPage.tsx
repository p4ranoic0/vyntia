import { LoadingSpinner } from '@/components/common/LoadingSpinner'
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
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { Textarea } from '@/components/ui/textarea'
import {
    contractsService,
    ESTADO_CONTRATO_BADGE,
    ESTADO_CONTRATO_LABELS,
    JORNADA_LABELS,
    TIPO_CONTRATO_LABELS,
    TIPOS_REQUIEREN_FECHA_FIN,
    type Contrato,
    type ContratoFilters,
    type ContratoFormData,
    type ContratoListItem,
} from '@/services/contractsService'
import { employeesService, type Employee } from '@/services/employeesService'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
    AlertTriangle,
    Award,
    CheckCircle,
    Clock,
    Eye,
    FileDown,
    FileText,
    Plus,
    RefreshCw,
    Search,
    XCircle,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import { toast } from 'sonner'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function formatCurrency(value?: number | null): string {
  if (value == null) return '-'
  return new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(value)
}

function diasBadge(dias?: number | null) {
  if (dias == null) return <span className="text-muted-foreground">-</span>
  if (dias < 0)
    return <Badge className="bg-red-100 text-red-800">Vencido</Badge>
  if (dias <= 30)
    return <Badge className="bg-yellow-100 text-yellow-800">{dias}d</Badge>
  return <span className="text-muted-foreground">{dias}d</span>
}

// ---------------------------------------------------------------------------
// Create Contract Dialog
// ---------------------------------------------------------------------------

interface CreateDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  employees: Employee[]
  isPending: boolean
  onSubmit: (data: ContratoFormData) => void
}

function CreateContratoDialog({ open, onOpenChange, employees, isPending, onSubmit }: CreateDialogProps) {
  const [form, setForm] = useState<Partial<ContratoFormData>>({
    tipo_documento: '',
    jornada_laboral: 'COMPLETA',
  })
  const [selectedEmpleadoId, setSelectedEmpleadoId] = useState<string>('')

  const selectedEmployee = useMemo(
    () => employees.find((e) => e.id === Number(selectedEmpleadoId)),
    [employees, selectedEmpleadoId],
  )

  const handleEmpleadoChange = (value: string) => {
    setSelectedEmpleadoId(value)
    const emp = employees.find((e) => e.id === Number(value))
    if (emp) {
      setForm((prev) => ({
        ...prev,
        empleado: emp.id,
        area: emp.area?.id ?? undefined,
      }))
    }
  }

  const handleChange = (field: keyof ContratoFormData, value: string | number) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = () => {
    if (!form.empleado || !form.tipo_documento || !form.fecha_inicio || !form.cargo || !form.salario_bruto) {
      toast.error('Completa todos los campos obligatorios')
      return
    }
    if (form.tipo_documento && TIPOS_REQUIEREN_FECHA_FIN.has(form.tipo_documento) && !form.fecha_fin) {
      toast.error('Este tipo de contrato requiere fecha de fin')
      return
    }
    if (form.fecha_fin && form.fecha_inicio && form.fecha_fin <= form.fecha_inicio) {
      toast.error('La fecha de fin debe ser posterior a la fecha de inicio')
      return
    }
    if (!form.area) {
      toast.error('El empleado seleccionado no tiene área asignada')
      return
    }
    onSubmit(form as ContratoFormData)
  }

  const resetForm = () => {
    setForm({ tipo_documento: '', jornada_laboral: 'COMPLETA' })
    setSelectedEmpleadoId('')
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) resetForm()
        onOpenChange(v)
      }}
    >
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Nuevo Contrato / Adenda</DialogTitle>
          <DialogDescription>Registra un nuevo contrato o adenda para un empleado.</DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {/* Empleado */}
          <div className="grid gap-2">
            <Label htmlFor="empleado">Empleado *</Label>
            <Select value={selectedEmpleadoId} onValueChange={handleEmpleadoChange}>
              <SelectTrigger id="empleado">
                <SelectValue placeholder="Seleccionar empleado" />
              </SelectTrigger>
              <SelectContent>
                {employees.map((emp) => (
                  <SelectItem key={emp.id} value={String(emp.id)}>
                    {emp.nombres} {emp.ape_paterno} {emp.ape_materno}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Area (auto) */}
          <div className="grid gap-2">
            <Label>Area</Label>
            <Input
              disabled
              value={selectedEmployee?.area?.organo ?? 'Se asigna del empleado'}
            />
          </div>

          {/* Tipo documento */}
          <div className="grid gap-2">
            <Label htmlFor="tipo_documento">Tipo de Documento *</Label>
            <Select
              value={form.tipo_documento ?? ''}
              onValueChange={(v) => handleChange('tipo_documento', v)}
            >
              <SelectTrigger id="tipo_documento">
                <SelectValue placeholder="Seleccionar tipo" />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(TIPO_CONTRATO_LABELS).map(([key, label]) => (
                  <SelectItem key={key} value={key}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Fechas */}
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="fecha_inicio">Fecha Inicio *</Label>
              <Input
                id="fecha_inicio"
                type="date"
                value={form.fecha_inicio ?? ''}
                onChange={(e) => handleChange('fecha_inicio', e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="fecha_fin">Fecha Fin</Label>
              <Input
                id="fecha_fin"
                type="date"
                value={form.fecha_fin ?? ''}
                onChange={(e) => handleChange('fecha_fin', e.target.value)}
              />
            </div>
          </div>

          {/* Salario y Cargo */}
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="salario_bruto">Salario Bruto (S/) *</Label>
              <Input
                id="salario_bruto"
                type="number"
                min="0"
                step="0.01"
                value={form.salario_bruto ?? ''}
                onChange={(e) => handleChange('salario_bruto', Number(e.target.value))}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="cargo">Cargo *</Label>
              <Input
                id="cargo"
                value={form.cargo ?? ''}
                onChange={(e) => handleChange('cargo', e.target.value)}
                placeholder="Ej: Analista de Sistemas"
              />
            </div>
          </div>

          {/* Jornada */}
          <div className="grid gap-2">
            <Label htmlFor="jornada_laboral">Jornada Laboral</Label>
            <Select
              value={form.jornada_laboral ?? 'COMPLETA'}
              onValueChange={(v) => handleChange('jornada_laboral', v)}
            >
              <SelectTrigger id="jornada_laboral">
                <SelectValue placeholder="Seleccionar jornada" />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(JORNADA_LABELS).map(([key, label]) => (
                  <SelectItem key={key} value={key}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Funciones */}
          <div className="grid gap-2">
            <Label htmlFor="funciones">Funciones</Label>
            <Textarea
              id="funciones"
              rows={3}
              value={form.funciones ?? ''}
              onChange={(e) => handleChange('funciones', e.target.value)}
              placeholder="Descripcion de funciones del puesto..."
            />
          </div>

          {/* Observaciones */}
          <div className="grid gap-2">
            <Label htmlFor="observaciones">Observaciones</Label>
            <Textarea
              id="observaciones"
              rows={2}
              value={form.observaciones ?? ''}
              onChange={(e) => handleChange('observaciones', e.target.value)}
              placeholder="Observaciones adicionales..."
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isPending}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit} disabled={isPending}>
            {isPending ? (
              <>
                <LoadingSpinner className="mr-2 h-4 w-4" />
                Guardando...
              </>
            ) : (
              <>
                <Plus className="mr-2 h-4 w-4" />
                Crear Contrato
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ---------------------------------------------------------------------------
// Detail Dialog
// ---------------------------------------------------------------------------

interface DetailDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  contratoId: number | null
  onRenovarSuccess: () => void
}

function DetailContratoDialog({ open, onOpenChange, contratoId, onRenovarSuccess }: DetailDialogProps) {
  const queryClient = useQueryClient()
  const [showRenovar, setShowRenovar] = useState(false)
  const [renovarForm, setRenovarForm] = useState({
    fecha_inicio: '',
    fecha_fin: '',
    salario_bruto: '',
    observaciones: '',
  })

  const { data: contrato, isLoading } = useQuery<Contrato>({
    queryKey: ['contrato', contratoId],
    queryFn: () => contractsService.getById(contratoId!),
    enabled: open && contratoId != null,
  })

  const generarPdfMutation = useMutation({
    mutationFn: () => {
      if (!contratoId) throw new Error('No se selecciono contrato')
      const esAdenda = contrato?.es_adenda || contrato?.tipo_documento?.startsWith('ADENDA_')
      return esAdenda
        ? contractsService.generarAdendaPdf({ adenda_id: contratoId })
        : contractsService.generarContratoPdf({ contrato_id: contratoId })
    },
    onSuccess: (data) => {
      const label = contrato?.es_adenda ? 'Adenda' : 'Contrato'
      toast.success(`${label} PDF generado exitosamente`)
      if (data.archivo_url) {
        window.open(data.archivo_url, '_blank', 'noopener,noreferrer')
      }
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al generar PDF')
    },
  })

  const renovarMutation = useMutation({
    mutationFn: (data: { fecha_inicio: string; fecha_fin?: string; salario_bruto?: number; observaciones?: string }) =>
      contractsService.renovar(contratoId!, data),
    onSuccess: () => {
      toast.success('Contrato renovado exitosamente')
      queryClient.invalidateQueries({ queryKey: ['contratos'] })
      queryClient.invalidateQueries({ queryKey: ['contrato', contratoId] })
      setShowRenovar(false)
      setRenovarForm({ fecha_inicio: '', fecha_fin: '', salario_bruto: '', observaciones: '' })
      onRenovarSuccess()
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al renovar contrato')
    },
  })

  const handleRenovar = () => {
    if (!renovarForm.fecha_inicio) {
      toast.error('La fecha de inicio es obligatoria')
      return
    }
    renovarMutation.mutate({
      fecha_inicio: renovarForm.fecha_inicio,
      fecha_fin: renovarForm.fecha_fin || undefined,
      salario_bruto: renovarForm.salario_bruto ? Number(renovarForm.salario_bruto) : undefined,
      observaciones: renovarForm.observaciones || undefined,
    })
  }

  const handleClose = (v: boolean) => {
    if (!v) {
      setShowRenovar(false)
      setRenovarForm({ fecha_inicio: '', fecha_fin: '', salario_bruto: '', observaciones: '' })
    }
    onOpenChange(v)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Detalle del Contrato</DialogTitle>
          <DialogDescription>
            {contrato ? `${contrato.numero_contrato}${contrato.numero_adenda ? ` / ${contrato.numero_adenda}` : ''}` : 'Cargando...'}
          </DialogDescription>
        </DialogHeader>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner />
          </div>
        ) : contrato ? (
          <div className="space-y-6 py-2">
            {/* Estado badge */}
            <div className="flex items-center gap-3">
              <Badge className={ESTADO_CONTRATO_BADGE[contrato.status] ?? 'bg-gray-100 text-gray-800'}>
                {contrato.estado_texto ?? ESTADO_CONTRATO_LABELS[contrato.status] ?? contrato.status}
              </Badge>
              {contrato.es_adenda && (
                <Badge variant="outline">Adenda</Badge>
              )}
              {contrato.esta_vigente && (
                <Badge className="bg-green-100 text-green-800">Vigente</Badge>
              )}
            </div>

            {/* Empleado info */}
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Empleado</Label>
                <p className="text-lg font-semibold">
                  {contrato.empleado_detalle?.nombre_completo ??
                    `${contrato.empleado_detalle?.nombres_empleado ?? ''} ${contrato.empleado_detalle?.apellido_paterno ?? ''} ${contrato.empleado_detalle?.apellido_materno ?? ''}`.trim()}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Area</Label>
                <p className="text-lg">{contrato.area_detalle?.nombre ?? '-'}</p>
              </div>
            </div>

            {/* Contrato info */}
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Tipo de Documento</Label>
                <p>{contrato.tipo_documento_texto ?? TIPO_CONTRATO_LABELS[contrato.tipo_documento] ?? contrato.tipo_documento}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Cargo</Label>
                <p>{contrato.cargo}</p>
              </div>
            </div>

            {/* Fechas */}
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Fecha Inicio</Label>
                <p>{formatDate(contrato.fecha_inicio)}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Fecha Fin</Label>
                <p>{formatDate(contrato.fecha_fin)}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Fecha Firma</Label>
                <p>{formatDate(contrato.fecha_firma)}</p>
              </div>
            </div>

            {/* Salario y Jornada */}
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Salario Bruto</Label>
                <p className="font-semibold">{formatCurrency(contrato.salario_bruto)}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Salario Neto</Label>
                <p>{formatCurrency(contrato.salario_neto)}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Jornada</Label>
                <p>{contrato.jornada_texto ?? JORNADA_LABELS[contrato.jornada_laboral] ?? contrato.jornada_laboral}</p>
              </div>
            </div>

            {/* Duracion */}
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Duracion</Label>
                <p>
                  {contrato.duracion_meses != null
                    ? `${contrato.duracion_meses} meses (${contrato.duracion_dias} dias)`
                    : '-'}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Dias hasta vencimiento</Label>
                <p>{contrato.dias_hasta_vencimiento != null ? `${contrato.dias_hasta_vencimiento} dias` : '-'}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Lugar de Trabajo</Label>
                <p>{contrato.lugar_trabajo ?? '-'}</p>
              </div>
            </div>

            {/* Funciones */}
            {contrato.funciones && (
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Funciones</Label>
                <p className="mt-1 p-3 bg-gray-50 rounded-md whitespace-pre-line">{contrato.funciones}</p>
              </div>
            )}

            {/* Horario */}
            {contrato.horario_trabajo && (
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Horario de Trabajo</Label>
                <p className="mt-1">{contrato.horario_trabajo}</p>
              </div>
            )}

            {/* Observaciones */}
            {contrato.observaciones && (
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Observaciones</Label>
                <p className="mt-1 p-3 bg-gray-50 rounded-md">{contrato.observaciones}</p>
              </div>
            )}

            {/* Actions */}
            <div className="border-t pt-4">
              <div className="flex gap-2 flex-wrap">
                <Button
                  variant="outline"
                  onClick={() => generarPdfMutation.mutate()}
                  disabled={generarPdfMutation.isPending}
                >
                  {generarPdfMutation.isPending ? (
                    <>
                      <LoadingSpinner className="mr-2 h-4 w-4" />
                      Generando PDF...
                    </>
                  ) : (
                    <>
                      <FileDown className="mr-2 h-4 w-4" />
                      Generar PDF
                    </>
                  )}
                </Button>
                {(contrato.status === 'ACTIVO' || contrato.status === 'VENCIDO') && !showRenovar && (
                  <Button onClick={() => setShowRenovar(true)} className="bg-blue-600 hover:bg-blue-700">
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Renovar Contrato
                  </Button>
                )}
              </div>
              {showRenovar && (
                  <div className="space-y-4">
                    <h4 className="font-medium">Renovar Contrato</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="grid gap-2">
                        <Label htmlFor="renovar_fecha_inicio">Nueva Fecha Inicio *</Label>
                        <Input
                          id="renovar_fecha_inicio"
                          type="date"
                          value={renovarForm.fecha_inicio}
                          onChange={(e) =>
                            setRenovarForm((p) => ({ ...p, fecha_inicio: e.target.value }))
                          }
                        />
                      </div>
                      <div className="grid gap-2">
                        <Label htmlFor="renovar_fecha_fin">Nueva Fecha Fin</Label>
                        <Input
                          id="renovar_fecha_fin"
                          type="date"
                          value={renovarForm.fecha_fin}
                          onChange={(e) =>
                            setRenovarForm((p) => ({ ...p, fecha_fin: e.target.value }))
                          }
                        />
                      </div>
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="renovar_salario">Nuevo Salario Bruto (opcional)</Label>
                      <Input
                        id="renovar_salario"
                        type="number"
                        min="0"
                        step="0.01"
                        value={renovarForm.salario_bruto}
                        onChange={(e) =>
                          setRenovarForm((p) => ({ ...p, salario_bruto: e.target.value }))
                        }
                        placeholder="Dejar vacio para mantener el actual"
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="renovar_obs">Observaciones</Label>
                      <Textarea
                        id="renovar_obs"
                        rows={2}
                        value={renovarForm.observaciones}
                        onChange={(e) =>
                          setRenovarForm((p) => ({ ...p, observaciones: e.target.value }))
                        }
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={handleRenovar} disabled={renovarMutation.isPending}>
                        {renovarMutation.isPending ? (
                          <>
                            <LoadingSpinner className="mr-2 h-4 w-4" />
                            Procesando...
                          </>
                        ) : (
                          <>
                            <CheckCircle className="mr-2 h-4 w-4" />
                            Confirmar Renovacion
                          </>
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => {
                          setShowRenovar(false)
                          setRenovarForm({ fecha_inicio: '', fecha_fin: '', salario_bruto: '', observaciones: '' })
                        }}
                      >
                        Cancelar
                      </Button>
                    </div>
                  </div>
                )}
              </div>
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">No se pudo cargar el contrato.</div>
        )}
      </DialogContent>
    </Dialog>
  )
}

// ---------------------------------------------------------------------------
// Certificate Generation Dialog
// ---------------------------------------------------------------------------

interface CertificadoDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  employees: Employee[]
}

function GenerarCertificadoDialog({ open, onOpenChange, employees }: CertificadoDialogProps) {
  const [selectedEmpleadoId, setSelectedEmpleadoId] = useState<string>('')
  const [proposito, setProposito] = useState('')
  const [incluirSalario, setIncluirSalario] = useState(false)

  const certificadoMutation = useMutation({
    mutationFn: (data: { empleado_id: number; proposito?: string; incluir_salario?: boolean }) =>
      contractsService.generarCertificado(data),
    onSuccess: (data) => {
      toast.success(`Certificado generado: ${data.numero_certificado || 'OK'}`)
      if (data.archivo_url) {
        window.open(data.archivo_url, '_blank', 'noopener,noreferrer')
      }
      resetForm()
      onOpenChange(false)
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al generar certificado')
    },
  })

  const resetForm = () => {
    setSelectedEmpleadoId('')
    setProposito('')
    setIncluirSalario(false)
  }

  const handleSubmit = () => {
    if (!selectedEmpleadoId) {
      toast.error('Selecciona un empleado')
      return
    }
    certificadoMutation.mutate({
      empleado_id: Number(selectedEmpleadoId),
      proposito: proposito || undefined,
      incluir_salario: incluirSalario,
    })
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) resetForm()
        onOpenChange(v)
      }}
    >
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Generar Certificado de Trabajo</DialogTitle>
          <DialogDescription>Genera un certificado laboral en PDF para el empleado seleccionado.</DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {/* Empleado */}
          <div className="grid gap-2">
            <Label htmlFor="cert-empleado">Empleado *</Label>
            <Select value={selectedEmpleadoId} onValueChange={setSelectedEmpleadoId}>
              <SelectTrigger id="cert-empleado">
                <SelectValue placeholder="Seleccionar empleado" />
              </SelectTrigger>
              <SelectContent>
                {employees.map((emp) => (
                  <SelectItem key={emp.id} value={String(emp.id)}>
                    {emp.nombres} {emp.ape_paterno} {emp.ape_materno}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Proposito */}
          <div className="grid gap-2">
            <Label htmlFor="cert-proposito">Proposito (opcional)</Label>
            <Textarea
              id="cert-proposito"
              rows={2}
              value={proposito}
              onChange={(e) => setProposito(e.target.value)}
              placeholder="Ej: Para tramites bancarios, para estudios..."
            />
          </div>

          {/* Incluir salario */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="cert-salario"
              checked={incluirSalario}
              onChange={(e) => setIncluirSalario(e.target.checked)}
              className="rounded border-gray-300"
            />
            <Label htmlFor="cert-salario">Incluir informacion salarial</Label>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={certificadoMutation.isPending}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit} disabled={certificadoMutation.isPending}>
            {certificadoMutation.isPending ? (
              <>
                <LoadingSpinner className="mr-2 h-4 w-4" />
                Generando...
              </>
            ) : (
              <>
                <Award className="mr-2 h-4 w-4" />
                Generar Certificado
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ---------------------------------------------------------------------------
// Generate Contract PDF Dialog
// ---------------------------------------------------------------------------

interface GenerarContratoPdfDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  contratoId: number | null
  contratoNumero?: string
  esAdenda?: boolean
}

function GenerarContratoPdfDialog({ open, onOpenChange, contratoId, contratoNumero, esAdenda }: GenerarContratoPdfDialogProps) {
  const generarMutation = useMutation({
    mutationFn: (id: number) =>
      esAdenda
        ? contractsService.generarAdendaPdf({ adenda_id: id })
        : contractsService.generarContratoPdf({ contrato_id: id }),
    onSuccess: (data) => {
      const label = esAdenda ? 'Adenda' : 'Contrato'
      toast.success(`${label} PDF generado exitosamente`)
      if (data.archivo_url) {
        window.open(data.archivo_url, '_blank', 'noopener,noreferrer')
      }
      onOpenChange(false)
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al generar PDF')
    },
  })

  const handleGenerar = () => {
    if (!contratoId) return
    generarMutation.mutate(contratoId)
  }

  const label = esAdenda ? 'Adenda' : 'Contrato'

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Generar {label} PDF</DialogTitle>
          <DialogDescription>
            Se generara un PDF del {label.toLowerCase()} {contratoNumero || ''} y se guardara en el legajo digital.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={generarMutation.isPending}>
            Cancelar
          </Button>
          <Button onClick={handleGenerar} disabled={generarMutation.isPending}>
            {generarMutation.isPending ? (
              <>
                <LoadingSpinner className="mr-2 h-4 w-4" />
                Generando...
              </>
            ) : (
              <>
                <FileDown className="mr-2 h-4 w-4" />
                Generar PDF
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function ContratosPage() {
  const queryClient = useQueryClient()

  // UI State
  const [searchTerm, setSearchTerm] = useState('')
  const [estadoFilter, setEstadoFilter] = useState<string>('')
  const [tipoFilter, setTipoFilter] = useState<string>('')
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [selectedContratoId, setSelectedContratoId] = useState<number | null>(null)
  const [selectedContratoNumero, setSelectedContratoNumero] = useState<string>('')
  const [selectedEsAdenda, setSelectedEsAdenda] = useState(false)
  const [isDetailOpen, setIsDetailOpen] = useState(false)
  const [isCertificadoOpen, setIsCertificadoOpen] = useState(false)
  const [isGenerarPdfOpen, setIsGenerarPdfOpen] = useState(false)

  // Data queries
  const {
    data: contratos = [],
    isLoading,
    error,
  } = useQuery<ContratoListItem[]>({
    queryKey: ['contratos', estadoFilter, tipoFilter],
    queryFn: () => {
      const filters: ContratoFilters = {}
      if (estadoFilter) filters.status = estadoFilter
      if (tipoFilter) filters.tipo_documento = tipoFilter
      return contractsService.getAll(filters)
    },
  })

  const { data: estadisticas } = useQuery<Record<string, unknown>>({
    queryKey: ['contratos-estadisticas'],
    queryFn: () => contractsService.getEstadisticas(),
  })

  const { data: alertas = [] } = useQuery<ContratoListItem[]>({
    queryKey: ['contratos-alertas'],
    queryFn: () => contractsService.getAlertasVencimiento(30),
  })

  const { data: employees = [] } = useQuery<Employee[]>({
    queryKey: ['employees-list'],
    queryFn: () => employeesService.getAll(),
  })

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: ContratoFormData) => contractsService.create(data),
    onSuccess: () => {
      toast.success('Contrato creado exitosamente')
      queryClient.invalidateQueries({ queryKey: ['contratos'] })
      queryClient.invalidateQueries({ queryKey: ['contratos-estadisticas'] })
      queryClient.invalidateQueries({ queryKey: ['contratos-alertas'] })
      setIsCreateOpen(false)
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al crear contrato')
    },
  })

  // Derived stats
  const stats = useMemo(() => {
    const total =
      (estadisticas?.total as number) ??
      contratos.length
    const activos =
      (estadisticas?.activos as number) ??
      contratos.filter((c) => c.status === 'ACTIVO').length
    const porVencer = alertas.length
    const vencidos =
      (estadisticas?.vencidos as number) ??
      contratos.filter((c) => c.status === 'VENCIDO').length
    return { total, activos, porVencer, vencidos }
  }, [estadisticas, contratos, alertas])

  // Filtered list (search on top of server-side filters)
  const filteredContratos = useMemo(() => {
    if (!searchTerm) return contratos
    const term = searchTerm.toLowerCase()
    return contratos.filter(
      (c) =>
        c.numero_contrato?.toLowerCase().includes(term) ||
        c.empleado_nombre?.toLowerCase().includes(term) ||
        c.cargo?.toLowerCase().includes(term) ||
        c.area_nombre?.toLowerCase().includes(term),
    )
  }, [contratos, searchTerm])

  // Handlers
  const handleRowClick = (contrato: ContratoListItem) => {
    setSelectedContratoId(contrato.contrato_id)
    setSelectedContratoNumero(contrato.numero_contrato)
    setIsDetailOpen(true)
  }

  const handleClearFilters = () => {
    setSearchTerm('')
    setEstadoFilter('')
    setTipoFilter('')
  }

  // Loading / Error states
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
          <p className="text-red-600 mb-2">Error al cargar los contratos</p>
          <Button onClick={() => queryClient.invalidateQueries({ queryKey: ['contratos'] })}>
            Reintentar
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Contratos y Adendas</h1>
          <p className="text-muted-foreground">
            Gestion de contratos laborales y adendas del personal
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => setIsCertificadoOpen(true)}>
            <Award className="mr-2 h-4 w-4" />
            Certificado de Trabajo
          </Button>
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Nuevo Contrato
          </Button>
        </div>
      </div>

      {/* Alertas banner */}
      {alertas.length > 0 && (
        <div className="flex items-center gap-3 rounded-lg border border-yellow-300 bg-yellow-50 p-4">
          <AlertTriangle className="h-5 w-5 text-yellow-600 shrink-0" />
          <div className="flex-1">
            <p className="font-medium text-yellow-800">
              {alertas.length} contrato{alertas.length !== 1 ? 's' : ''} por vencer en los proximos 30 dias
            </p>
            <p className="text-sm text-yellow-700">
              Revisa los contratos proximos a vencer y gestiona sus renovaciones.
            </p>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Contratos</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Activos</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.activos}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Por Vencer (30d)</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.porVencer}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vencidos</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.vencidos}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            {/* Search */}
            <div className="space-y-2">
              <Label htmlFor="search">Buscar</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Nombre, contrato, cargo..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>

            {/* Estado */}
            <div className="space-y-2">
              <Label>Estado</Label>
              <Select value={estadoFilter} onValueChange={setEstadoFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos los estados" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los estados</SelectItem>
                  {Object.entries(ESTADO_CONTRATO_LABELS).map(([key, label]) => (
                    <SelectItem key={key} value={key}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Tipo documento */}
            <div className="space-y-2">
              <Label>Tipo de Documento</Label>
              <Select value={tipoFilter} onValueChange={setTipoFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos los tipos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los tipos</SelectItem>
                  {Object.entries(TIPO_CONTRATO_LABELS).map(([key, label]) => (
                    <SelectItem key={key} value={key}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Clear */}
            <div className="space-y-2">
              <Label>&nbsp;</Label>
              <Button variant="outline" className="w-full" onClick={handleClearFilters}>
                Limpiar Filtros
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Contracts Table */}
      <Card>
        <CardHeader>
          <CardTitle>Contratos ({filteredContratos.length})</CardTitle>
          <CardDescription>Lista de contratos y adendas registrados</CardDescription>
        </CardHeader>
        <CardContent>
          {filteredContratos.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium">No hay contratos</p>
              <p className="text-muted-foreground">
                {searchTerm || estadoFilter || tipoFilter
                  ? 'No se encontraron contratos con los filtros aplicados'
                  : 'No hay contratos registrados. Crea el primero.'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>N. Contrato</TableHead>
                    <TableHead>Empleado</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Fecha Inicio</TableHead>
                    <TableHead>Fecha Fin</TableHead>
                    <TableHead>Cargo</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead className="text-right">Salario Neto</TableHead>
                    <TableHead>Vencimiento</TableHead>
                    <TableHead>Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredContratos.map((contrato) => (
                    <TableRow
                      key={contrato.contrato_id}
                      className="cursor-pointer"
                      onClick={() => handleRowClick(contrato)}
                    >
                      <TableCell className="font-medium">{contrato.numero_contrato}</TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{contrato.empleado_nombre}</p>
                          <p className="text-xs text-muted-foreground">{contrato.area_nombre}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">
                          {contrato.tipo_documento_texto ?? TIPO_CONTRATO_LABELS[contrato.tipo_documento] ?? contrato.tipo_documento}
                        </span>
                      </TableCell>
                      <TableCell>{formatDate(contrato.fecha_inicio)}</TableCell>
                      <TableCell>{formatDate(contrato.fecha_fin)}</TableCell>
                      <TableCell>{contrato.cargo}</TableCell>
                      <TableCell>
                        <Badge className={ESTADO_CONTRATO_BADGE[contrato.status] ?? 'bg-gray-100 text-gray-800'}>
                          {contrato.estado_texto ?? ESTADO_CONTRATO_LABELS[contrato.status] ?? contrato.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">{formatCurrency(contrato.salario_neto)}</TableCell>
                      <TableCell>{diasBadge(contrato.dias_hasta_vencimiento)}</TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleRowClick(contrato)
                            }}
                          >
                            <Eye className="mr-1 h-3 w-3" />
                            Ver
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              setSelectedContratoId(contrato.contrato_id)
                              setSelectedContratoNumero(contrato.numero_contrato)
                              setSelectedEsAdenda(contrato.tipo_documento?.startsWith('ADENDA_') ?? false)
                              setIsGenerarPdfOpen(true)
                            }}
                          >
                            <FileDown className="mr-1 h-3 w-3" />
                            PDF
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Dialog */}
      <CreateContratoDialog
        open={isCreateOpen}
        onOpenChange={setIsCreateOpen}
        employees={employees}
        isPending={createMutation.isPending}
        onSubmit={(data) => createMutation.mutate(data)}
      />

      {/* Detail Dialog */}
      <DetailContratoDialog
        open={isDetailOpen}
        onOpenChange={setIsDetailOpen}
        contratoId={selectedContratoId}
        onRenovarSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['contratos-estadisticas'] })
          queryClient.invalidateQueries({ queryKey: ['contratos-alertas'] })
        }}
      />

      {/* Certificado Dialog */}
      <GenerarCertificadoDialog
        open={isCertificadoOpen}
        onOpenChange={setIsCertificadoOpen}
        employees={employees}
      />

      {/* Generar Contrato PDF Dialog */}
      <GenerarContratoPdfDialog
        open={isGenerarPdfOpen}
        onOpenChange={setIsGenerarPdfOpen}
        contratoId={selectedContratoId}
        contratoNumero={selectedContratoNumero}
        esAdenda={selectedEsAdenda}
      />
    </div>
  )
}
