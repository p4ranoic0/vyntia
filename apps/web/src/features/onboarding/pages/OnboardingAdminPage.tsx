import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Checkbox } from '@/shared/ui/checkbox'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Progress } from '@/shared/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select'
import { Skeleton } from '@/shared/ui/skeleton'
import { Textarea } from '@/shared/ui/textarea'
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from '@/shared/ui/dialog'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/shared/ui/table'
import { DocumentViewer } from '@/shared/components/DocumentViewer'
import { legajoService, type Documento } from '@/features/documents/services/legajoService'
import { apiClient } from '@/shared/api/api'
import { getErrorMessage } from '@/shared/api/errorUtils'
import {
  onboardingService, getEstadoLabel,
  type OnboardingCreateData,
  type OnboardingStatus as ServiceOnboardingStatus,
} from '@/services/onboardingService'
import { computeAlert } from '@/features/onboarding/types/onboarding'
import { corregirCorreo } from '@/features/onboarding/services/onboardingUploadService'
import {
  AlertTriangle, CheckCircle2, Clock, Eye, Mail, RefreshCw, Search, ShieldCheck, UserPlus, X, XCircle,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

// Use the richer service type as OnboardingStatus for this page
type OnboardingStatus = ServiceOnboardingStatus & {
  last_login?: string | null
  email_bienvenida_enviado?: boolean
  datos_laborales_completos?: boolean
}

export default function OnboardingAdminPage() {
  const [onboardings, setOnboardings] = useState<OnboardingStatus[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [createOpen, setCreateOpen] = useState(false)
  const [selectedOnboarding, setSelectedOnboarding] = useState<OnboardingStatus | null>(null)

  // Filter state
  const [searchText, setSearchText] = useState('')
  const [filterEstado, setFilterEstado] = useState('')
  const [filterAlerts, setFilterAlerts] = useState(false)
  const [filterMinPct, setFilterMinPct] = useState('')
  const [filterMaxPct, setFilterMaxPct] = useState('')

  // Email failure banner state
  const [emailFailedOnboarding, setEmailFailedOnboarding] = useState<{
    onboardingId: number
    empleadoNombre: string
  } | null>(null)
  const [showCorreoInput, setShowCorreoInput] = useState(false)
  const [nuevoCorreo, setNuevoCorreo] = useState('')
  const [correoLoading, setCorreoLoading] = useState(false)

  const fetchOnboardings = async () => {
    try {
      setIsLoading(true)
      const data = await onboardingService.getAll({ page_size: 100 })
      setOnboardings(data.results)
    } catch {
      toast.error('Error al cargar los onboardings')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchOnboardings()
  }, [])

  // Client-side filtering — data set is small
  const filtered = onboardings.filter((o) => {
    if (
      searchText &&
      !o.empleado_nombre?.toLowerCase().includes(searchText.toLowerCase()) &&
      !o.empleado_documento?.includes(searchText)
    ) return false
    if (filterEstado && o.estado_onboarding !== filterEstado) return false
    if (filterAlerts && !computeAlert({ fecha_email_bienvenida: o.fecha_email_bienvenida ?? null, last_login: (o as any).last_login ?? null })) return false
    if (filterMinPct !== '' && o.progreso_porcentaje < Number(filterMinPct)) return false
    if (filterMaxPct !== '' && o.progreso_porcentaje > Number(filterMaxPct)) return false
    return true
  })

  const clearFilters = () => {
    setSearchText('')
    setFilterEstado('')
    setFilterAlerts(false)
    setFilterMinPct('')
    setFilterMaxPct('')
  }

  const getEstadoBadge = (o: OnboardingStatus) => {
    const emailNotSent = o.email_bienvenida_enviado === false && o.estado_onboarding !== 'completado'
    const badge = (() => {
      switch (o.estado_onboarding) {
        case 'completado': return <Badge className="bg-green-600 text-white">Completado</Badge>
        case 'observado': return <Badge variant="destructive">Observado</Badge>
        case 'pendiente_validacion': return <Badge className="bg-yellow-500 text-white">Pend. Validacion</Badge>
        case 'pendiente_datos': return <Badge variant="secondary">Pend. Datos</Badge>
        case 'pendiente_documentos': return <Badge className="bg-blue-600 text-white">Pend. Documentos</Badge>
        default: return <Badge variant="secondary">{getEstadoLabel(o.estado_onboarding)}</Badge>
      }
    })()
    return (
      <div className="flex flex-col gap-1">
        {badge}
        {emailNotSent && (
          <Badge variant="outline" className="text-amber-600 border-amber-400 text-xs">
            Sin correo
          </Badge>
        )}
      </div>
    )
  }

  const handleReenviarEmail = async (id: number) => {
    try {
      await onboardingService.reenviarEmail(id)
      toast.success('Correo reenviado exitosamente')
    } catch {
      toast.error('No se pudo reenviar el correo')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold">Gestion de Onboarding</h1>
          <p className="text-muted-foreground">
            {onboardings.length} proceso{onboardings.length !== 1 ? 's' : ''} de incorporacion
          </p>
        </div>
        <Button onClick={() => setCreateOpen(true)} className="cursor-pointer">
          <UserPlus className="mr-2 h-4 w-4" />
          Iniciar Onboarding
        </Button>
      </div>

      {/* Filters bar */}
      <Card>
        <CardContent className="pt-4 pb-4">
          <div className="flex flex-wrap gap-3 items-end">
            {/* Search */}
            <div className="relative flex-1 min-w-[200px] max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por nombre o DNI"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Estado */}
            <Select value={filterEstado || 'todos'} onValueChange={(v) => setFilterEstado(v === 'todos' ? '' : v)}>
              <SelectTrigger className="w-[200px] cursor-pointer">
                <SelectValue placeholder="Estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos los estados</SelectItem>
                <SelectItem value="pendiente_datos">Pendiente datos</SelectItem>
                <SelectItem value="pendiente_documentos">Pendiente documentos</SelectItem>
                <SelectItem value="pendiente_validacion">Pendiente validacion</SelectItem>
                <SelectItem value="observado">Observado</SelectItem>
                <SelectItem value="completado">Completado</SelectItem>
              </SelectContent>
            </Select>

            {/* % Range */}
            <div className="flex items-center gap-1">
              <Input
                type="number"
                min={0}
                max={100}
                placeholder="Min %"
                value={filterMinPct}
                onChange={(e) => setFilterMinPct(e.target.value)}
                className="w-20"
              />
              <span className="text-muted-foreground text-sm">–</span>
              <Input
                type="number"
                min={0}
                max={100}
                placeholder="Max %"
                value={filterMaxPct}
                onChange={(e) => setFilterMaxPct(e.target.value)}
                className="w-20"
              />
            </div>

            {/* Alerts toggle */}
            <div className="flex items-center gap-2">
              <Checkbox
                id="con-alertas"
                checked={filterAlerts}
                onCheckedChange={(v) => setFilterAlerts(Boolean(v))}
                className="cursor-pointer"
              />
              <Label htmlFor="con-alertas" className="cursor-pointer text-sm">Con alertas</Label>
            </div>

            {/* Refresh */}
            <Button
              variant="outline"
              size="icon"
              onClick={fetchOnboardings}
              className="cursor-pointer"
              title="Actualizar lista"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>

            {/* Clear filters */}
            <Button
              variant="ghost"
              onClick={clearFilters}
              className="cursor-pointer transition-colors duration-200"
            >
              Limpiar filtros
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Email failure alert banner */}
      {emailFailedOnboarding && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 space-y-3">
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-amber-900">
                Onboarding creado para {emailFailedOnboarding.empleadoNombre}
              </p>
              <p className="text-sm text-amber-700">
                El correo de bienvenida no pudo enviarse. Verifique la direccion o la configuracion SMTP.
              </p>
            </div>
            <button
              onClick={() => setEmailFailedOnboarding(null)}
              className="ml-auto text-amber-500 hover:text-amber-700 cursor-pointer transition-colors duration-200"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="outline"
              disabled={correoLoading}
              className="cursor-pointer transition-colors duration-200"
              onClick={async () => {
                setCorreoLoading(true)
                try {
                  await onboardingService.reenviarEmail(emailFailedOnboarding.onboardingId)
                  toast.success('Correo reenviado exitosamente')
                  setEmailFailedOnboarding(null)
                } catch {
                  toast.error('No se pudo reenviar. Verifique la configuracion SMTP.')
                } finally {
                  setCorreoLoading(false)
                }
              }}
            >
              Reintentar enviar
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="cursor-pointer transition-colors duration-200"
              onClick={() => setShowCorreoInput((v) => !v)}
            >
              Corregir correo y reintentar
            </Button>
          </div>
          {showCorreoInput && (
            <div className="flex gap-2 items-center">
              <Input
                type="email"
                placeholder="Nuevo correo electronico"
                value={nuevoCorreo}
                onChange={(e) => setNuevoCorreo(e.target.value)}
                className="max-w-xs"
              />
              <Button
                size="sm"
                disabled={!nuevoCorreo || correoLoading}
                className="cursor-pointer transition-colors duration-200"
                onClick={async () => {
                  setCorreoLoading(true)
                  try {
                    await corregirCorreo(emailFailedOnboarding.onboardingId, nuevoCorreo)
                    toast.success('Correo corregido y email reenviado')
                    setEmailFailedOnboarding(null)
                    setShowCorreoInput(false)
                    setNuevoCorreo('')
                    fetchOnboardings()
                  } catch {
                    toast.error('Error al corregir el correo. Verifique la direccion.')
                  } finally {
                    setCorreoLoading(false)
                  }
                }}
              >
                {correoLoading ? 'Enviando...' : 'Enviar'}
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Empleado</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Progreso</TableHead>
                <TableHead>Fecha inicio</TableHead>
                <TableHead className="text-center">Alerta</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-40" /></TableCell>
                    <TableCell><Skeleton className="h-5 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-8 mx-auto" /></TableCell>
                    <TableCell><Skeleton className="h-8 w-32" /></TableCell>
                  </TableRow>
                ))
              ) : filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                    No se encontraron procesos de onboarding
                  </TableCell>
                </TableRow>
              ) : (
                filtered.map((o) => (
                  <OnboardingTableRow
                    key={o.id}
                    onboarding={o}
                    onView={() => setSelectedOnboarding(o)}
                    onReenviarEmail={() => handleReenviarEmail(o.id)}
                    onRefetch={fetchOnboardings}
                    getEstadoBadge={getEstadoBadge}
                  />
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Create Dialog */}
      <CreateOnboardingDialog
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onSuccess={(failed) => {
          setCreateOpen(false)
          fetchOnboardings()
          if (failed) {
            setEmailFailedOnboarding(failed)
            setShowCorreoInput(false)
            setNuevoCorreo('')
          }
        }}
      />

      {/* Detail Dialog */}
      {selectedOnboarding && (
        <OnboardingDetailDialog
          onboarding={selectedOnboarding}
          onClose={() => setSelectedOnboarding(null)}
          onUpdate={() => {
            setSelectedOnboarding(null)
            fetchOnboardings()
          }}
        />
      )}
    </div>
  )
}

// ─── Row component with inline validate/reject dialogs ─────────────────────

function OnboardingTableRow({
  onboarding: o,
  onView,
  onReenviarEmail,
  onRefetch,
  getEstadoBadge,
}: {
  onboarding: OnboardingStatus
  onView: () => void
  onReenviarEmail: () => void
  onRefetch: () => void
  getEstadoBadge: (o: OnboardingStatus) => React.ReactNode
}) {
  const [validateOpen, setValidateOpen] = useState(false)
  const [rejectOpen, setRejectOpen] = useState(false)
  const [observaciones, setObservaciones] = useState('')
  const [loading, setLoading] = useState(false)

  const hasAlert = computeAlert({
    fecha_email_bienvenida: o.fecha_email_bienvenida ?? null,
    last_login: (o as any).last_login ?? null,
  })

  const handleValidar = async () => {
    setLoading(true)
    try {
      await onboardingService.validar(o.id, 'aprobar', observaciones)
      toast.success('Onboarding aprobado exitosamente')
      setValidateOpen(false)
      onRefetch()
    } catch {
      toast.error('Error al aprobar el onboarding')
    } finally {
      setLoading(false)
    }
  }

  const handleRechazar = async () => {
    if (!observaciones.trim()) {
      toast.error('Ingrese las observaciones para el rechazo')
      return
    }
    setLoading(true)
    try {
      await onboardingService.validar(o.id, 'rechazar', observaciones)
      toast.success('Onboarding observado')
      setRejectOpen(false)
      onRefetch()
    } catch {
      toast.error('Error al rechazar el onboarding')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <TableRow className="hover:bg-muted/50 transition-colors duration-200">
        <TableCell>
          <div>
            <p className="font-medium">{o.empleado_nombre}</p>
            <p className="text-xs text-muted-foreground font-mono">{o.empleado_documento}</p>
          </div>
        </TableCell>
        <TableCell>{getEstadoBadge(o)}</TableCell>
        <TableCell>
          <div className="flex items-center gap-2">
            <Progress value={o.progreso_porcentaje} className="h-2 w-24" />
            <span className="text-sm font-semibold tabular-nums">{o.progreso_porcentaje}%</span>
          </div>
        </TableCell>
        <TableCell className="text-sm">
          {new Date(o.fecha_inicio).toLocaleDateString('es-PE')}
        </TableCell>
        <TableCell className="text-center">
          {hasAlert && (
            <AlertTriangle className="h-4 w-4 text-amber-500 inline-block" />
          )}
        </TableCell>
        <TableCell>
          <div className="flex items-center gap-1 flex-wrap">
            <Button
              variant="ghost"
              size="sm"
              className="cursor-pointer transition-colors duration-200"
              title="Ver detalle"
              onClick={onView}
            >
              <Eye className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="cursor-pointer transition-colors duration-200"
              title="Reenviar correo"
              onClick={onReenviarEmail}
            >
              <Mail className="h-4 w-4" />
            </Button>
            {o.estado_onboarding !== 'completado' && (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  className="cursor-pointer text-green-600 hover:text-green-700 transition-colors duration-200"
                  title="Validar onboarding"
                  onClick={() => { setObservaciones(''); setValidateOpen(true) }}
                >
                  <ShieldCheck className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="cursor-pointer text-red-600 hover:text-red-700 transition-colors duration-200"
                  title="Rechazar onboarding"
                  onClick={() => { setObservaciones(''); setRejectOpen(true) }}
                >
                  <XCircle className="h-4 w-4" />
                </Button>
              </>
            )}
          </div>
        </TableCell>
      </TableRow>

      {/* Validate Dialog */}
      <Dialog open={validateOpen} onOpenChange={setValidateOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Validar onboarding</DialogTitle>
            <DialogDescription>
              Confirme la aprobacion del onboarding de {o.empleado_nombre}.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <Label>Observaciones (opcional)</Label>
            <Textarea
              value={observaciones}
              onChange={(e) => setObservaciones(e.target.value)}
              placeholder="Observaciones opcionales..."
              rows={3}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setValidateOpen(false)} disabled={loading}>
              Cancelar
            </Button>
            <Button onClick={handleValidar} disabled={loading} className="bg-green-600 hover:bg-green-700">
              <ShieldCheck className="h-4 w-4 mr-2" />
              {loading ? 'Aprobando...' : 'Aprobar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={rejectOpen} onOpenChange={setRejectOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Rechazar onboarding</DialogTitle>
            <DialogDescription>
              Ingrese las observaciones para observar el onboarding de {o.empleado_nombre}.
              Las observaciones son obligatorias.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <Label>Observaciones *</Label>
            <Textarea
              value={observaciones}
              onChange={(e) => setObservaciones(e.target.value)}
              placeholder="Motivo del rechazo..."
              rows={3}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRejectOpen(false)} disabled={loading}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleRechazar} disabled={loading}>
              <XCircle className="h-4 w-4 mr-2" />
              {loading ? 'Rechazando...' : 'Observar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

// ─── Create Dialog ──────────────────────────────────────────────────────────

function CreateOnboardingDialog({
  open, onClose, onSuccess,
}: {
  open: boolean
  onClose: () => void
  onSuccess: (failed?: { onboardingId: number; empleadoNombre: string } | null) => void
}) {
  const [formData, setFormData] = useState<OnboardingCreateData>({
    nombres_empleado: '',
    apellido_paterno: '',
    apellido_materno: '',
    numero_documento: '',
    correo_personal: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<{ username: string; email_enviado: boolean; id?: string; empleado_nombre?: string } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      const response = await onboardingService.crear(formData)
      setResult({
        username: response.username,
        email_enviado: response.email_enviado,
        id: response.id,
        empleado_nombre: response.empleado_nombre,
      })
      toast.success(`Onboarding iniciado para ${formData.nombres_empleado}`)
    } catch (err: any) {
      console.error('Onboarding error response:', err?.response?.data)
      toast.error(getErrorMessage(err, 'Error al crear onboarding'))
    } finally {
      setSubmitting(false)
    }
  }

  const handleClose = () => {
    const failedInfo =
      result && !result.email_enviado && result.id
        ? { onboardingId: result.id, empleadoNombre: result.empleado_nombre || formData.nombres_empleado }
        : null
    setResult(null)
    setFormData({
      nombres_empleado: '', apellido_paterno: '', apellido_materno: '',
      numero_documento: '', correo_personal: '',
    })
    if (result) onSuccess(failedInfo)
    else onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Iniciar Onboarding</DialogTitle>
          <DialogDescription>
            Ingrese los datos basicos del nuevo empleado. Se creara su cuenta y se enviara un email de bienvenida.
          </DialogDescription>
        </DialogHeader>

        {result ? (
          <div className="space-y-4 py-4">
            <div className={`flex items-center gap-3 p-4 rounded-lg ${result.email_enviado ? 'bg-green-50 dark:bg-green-950/20' : 'bg-amber-50 dark:bg-amber-950/20'}`}>
              <CheckCircle2 className={`h-8 w-8 shrink-0 ${result.email_enviado ? 'text-green-600' : 'text-amber-600'}`} />
              <div>
                <p className={`font-semibold ${result.email_enviado ? 'text-green-800 dark:text-green-200' : 'text-amber-800 dark:text-amber-200'}`}>
                  Onboarding creado exitosamente
                </p>
                <p className={`text-sm mt-1 ${result.email_enviado ? 'text-green-700 dark:text-green-300' : 'text-amber-700 dark:text-amber-300'}`}>
                  Usuario: <span className="font-mono font-bold">{result.username}</span>
                </p>
                <p className={`text-sm ${result.email_enviado ? 'text-green-700 dark:text-green-300' : 'text-amber-700 dark:text-amber-300'}`}>
                  Email: {result.email_enviado ? 'Enviado correctamente' : 'No se pudo enviar — podra reintentarlo desde la lista'}
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button onClick={handleClose}>Cerrar</Button>
            </DialogFooter>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Nombres *</Label>
                <Input
                  required
                  value={formData.nombres_empleado}
                  onChange={(e) => setFormData({ ...formData, nombres_empleado: e.target.value })}
                />
              </div>
              <div>
                <Label>Apellido Paterno *</Label>
                <Input
                  required
                  value={formData.apellido_paterno}
                  onChange={(e) => setFormData({ ...formData, apellido_paterno: e.target.value })}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Apellido Materno</Label>
                <Input
                  value={formData.apellido_materno}
                  onChange={(e) => setFormData({ ...formData, apellido_materno: e.target.value })}
                />
              </div>
              <div>
                <Label>DNI *</Label>
                <Input
                  required
                  maxLength={8}
                  value={formData.numero_documento}
                  onChange={(e) => setFormData({ ...formData, numero_documento: e.target.value })}
                />
              </div>
            </div>
            <div>
              <Label>Correo Personal *</Label>
              <Input
                required
                type="email"
                value={formData.correo_personal}
                onChange={(e) => setFormData({ ...formData, correo_personal: e.target.value })}
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose} disabled={submitting}>
                Cancelar
              </Button>
              <Button type="submit" disabled={submitting} className="cursor-pointer">
                {submitting ? 'Creando...' : 'Iniciar Onboarding'}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}

// ─── Detail Dialog ──────────────────────────────────────────────────────────

function OnboardingDetailDialog({
  onboarding, onClose, onUpdate,
}: {
  onboarding: OnboardingStatus
  onClose: () => void
  onUpdate: () => void
}) {
  const [documentos, setDocumentos] = useState<Documento[]>([])
  const [loadingDocs, setLoadingDocs] = useState(true)
  const [viewerDoc, setViewerDoc] = useState<{ url: string; nombre: string } | null>(null)
  const [validando, setValidando] = useState(false)
  const [rechazando, setRechazando] = useState(false)
  const [observaciones, setObservaciones] = useState('')
  const [rechazarDocId, setRechazarDocId] = useState<number | null>(null)
  const [motivoRechazoDoc, setMotivoRechazoDoc] = useState('')
  const [rechazandoDoc, setRechazandoDoc] = useState(false)

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const docs = await legajoService.getByEmpleado(onboarding.empleado)
        setDocumentos(docs)
      } catch {
        // ignore
      } finally {
        setLoadingDocs(false)
      }
    }
    fetchDocs()
  }, [onboarding.empleado])

  const handleValidar = async () => {
    setValidando(true)
    try {
      await onboardingService.validar(onboarding.id, 'aprobar', observaciones)
      toast.success('Onboarding validado exitosamente')
      onUpdate()
    } catch {
      toast.error('Error al validar')
    } finally {
      setValidando(false)
    }
  }

  const handleRechazar = async () => {
    if (!observaciones.trim()) {
      toast.error('Ingrese las observaciones')
      return
    }
    setRechazando(true)
    try {
      await onboardingService.validar(onboarding.id, 'rechazar', observaciones)
      toast.success('Onboarding observado')
      onUpdate()
    } catch {
      toast.error('Error al rechazar')
    } finally {
      setRechazando(false)
    }
  }

  const handleReenviarEmail = async () => {
    try {
      await onboardingService.reenviarEmail(onboarding.id)
      toast.success('Email reenviado exitosamente')
    } catch {
      toast.error('Error al reenviar email')
    }
  }

  const handleActualizarEstado = async () => {
    try {
      await onboardingService.actualizarEstado(onboarding.id)
      toast.success('Estado actualizado')
      onUpdate()
    } catch {
      toast.error('Error al actualizar estado')
    }
  }

  // aprobar_documento — calls onboarding-specific endpoint which triggers email notification (ONBD-14)
  const handleValidarDocumento = async (docId: number) => {
    try {
      await apiClient.post(
        `/api/v1/onboarding/processes/${onboarding.id}/documentos/${docId}/aprobar/`
      )
      toast.success('Documento aprobado')
      const docs = await legajoService.getByEmpleado(onboarding.empleado)
      setDocumentos(docs)
    } catch {
      toast.error('Error al aprobar el documento')
    }
  }

  const handleRechazarDocumentoConfirm = async () => {
    if (!motivoRechazoDoc.trim() || rechazarDocId === null) return
    setRechazandoDoc(true)
    try {
      await apiClient.post(
        `/api/v1/onboarding/processes/${onboarding.id}/documentos/${rechazarDocId}/rechazar/`,
        { motivo: motivoRechazoDoc }
      )
      toast.success('Documento rechazado y notificacion enviada al empleado')
      setRechazarDocId(null)
      setMotivoRechazoDoc('')
      const docs = await legajoService.getByEmpleado(onboarding.empleado)
      setDocumentos(docs)
    } catch {
      toast.error('Error al rechazar el documento')
    } finally {
      setRechazandoDoc(false)
    }
  }

  const getDocEstadoBadge = (estado: string) => {
    switch (estado) {
      case 'aprobado': return <Badge className="bg-green-600 text-xs">Aprobado</Badge>
      case 'rechazado': return <Badge variant="destructive" className="text-xs">Rechazado</Badge>
      case 'pendiente_revision': return <Badge variant="outline" className="text-xs">Pendiente</Badge>
      default: return <Badge variant="secondary" className="text-xs">{estado}</Badge>
    }
  }

  return (
    <>
      <Dialog open onOpenChange={onClose}>
        <DialogContent className="sm:max-w-3xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Onboarding: {onboarding.empleado_nombre}</DialogTitle>
            <DialogDescription>
              DNI: {onboarding.empleado_documento} | Usuario: {(onboarding as any).usuario_username}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Progress overview */}
            <div className="flex items-center gap-4">
              <Progress value={onboarding.progreso_porcentaje} className="flex-1 h-3" />
              <span className="font-bold text-lg tabular-nums">{onboarding.progreso_porcentaje}%</span>
            </div>

            {/* Checklist */}
            <div>
              <h4 className="text-sm font-semibold mb-3">Checklist de Completitud</h4>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: 'Datos personales', done: onboarding.datos_personales_completos },
                  { label: 'Datos laborales', done: (onboarding as any).datos_laborales_completos },
                  { label: 'DNI', done: onboarding.dni_subido },
                  { label: 'Declaraciones juradas', done: onboarding.declaraciones_juradas_subidas },
                  { label: 'Certificados academicos', done: onboarding.certificados_academicos_subidos },
                  { label: 'Certificados trabajo', done: onboarding.certificados_trabajo_subidos },
                  { label: 'Documentos familiares', done: onboarding.documentos_familiares_subidos },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-2 text-sm">
                    {item.done ? (
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                    ) : (
                      <Clock className="h-4 w-4 text-amber-500" />
                    )}
                    <span className={item.done ? 'text-green-700' : ''}>{item.label}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Documentos subidos */}
            <div>
              <h4 className="text-sm font-semibold mb-3">
                Documentos Subidos ({documentos.length})
              </h4>
              {loadingDocs ? (
                <p className="text-sm text-muted-foreground">Cargando documentos...</p>
              ) : documentos.length === 0 ? (
                <p className="text-sm text-muted-foreground">Aun no se han subido documentos</p>
              ) : (
                <div className="space-y-2">
                  {documentos.map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3 min-w-0">
                        <div>
                          <p className="text-sm font-medium truncate">{doc.nombre_documento}</p>
                          <p className="text-xs text-muted-foreground">
                            {doc.tipo_documento} | {doc.categoria}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {getDocEstadoBadge(doc.estado_documento)}
                        {doc.archivo && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="cursor-pointer"
                            onClick={() => setViewerDoc({ url: doc.archivo!, nombre: doc.nombre_documento })}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        )}
                        {doc.estado_documento !== 'aprobado' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-green-600 cursor-pointer"
                            title="Aprobar documento"
                            onClick={() => handleValidarDocumento(doc.id)}
                          >
                            <ShieldCheck className="h-4 w-4" />
                          </Button>
                        )}
                        {doc.estado_documento !== 'rechazado' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 cursor-pointer"
                            title="Rechazar documento"
                            onClick={() => { setRechazarDocId(doc.id); setMotivoRechazoDoc('') }}
                          >
                            <XCircle className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Actions */}
            {onboarding.estado_onboarding !== 'completado' && (
              <div className="space-y-4 border-t pt-4">
                <div>
                  <Label>Observaciones</Label>
                  <Textarea
                    value={observaciones}
                    onChange={(e) => setObservaciones(e.target.value)}
                    placeholder="Observaciones opcionales para aprobacion, obligatorias para rechazo..."
                    rows={3}
                  />
                </div>
                <div className="flex gap-2 flex-wrap">
                  <Button onClick={handleValidar} disabled={validando} className="bg-green-600 hover:bg-green-700 cursor-pointer">
                    <ShieldCheck className="h-4 w-4 mr-2" />
                    {validando ? 'Validando...' : 'Aprobar Todo'}
                  </Button>
                  <Button variant="destructive" onClick={handleRechazar} disabled={rechazando} className="cursor-pointer">
                    <XCircle className="h-4 w-4 mr-2" />
                    {rechazando ? 'Rechazando...' : 'Observar'}
                  </Button>
                  <Button variant="outline" onClick={handleReenviarEmail} className="cursor-pointer">
                    <Mail className="h-4 w-4 mr-2" />
                    Reenviar Email
                  </Button>
                  <Button variant="outline" onClick={handleActualizarEstado} className="cursor-pointer">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Actualizar Estado
                  </Button>
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Document rejection dialog — replaces prompt() */}
      <Dialog open={rechazarDocId !== null} onOpenChange={(open) => { if (!open) setRechazarDocId(null) }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Rechazar documento</DialogTitle>
            <DialogDescription>
              Ingrese el motivo del rechazo del documento.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <Label>Motivo del rechazo *</Label>
            <Textarea
              value={motivoRechazoDoc}
              onChange={(e) => setMotivoRechazoDoc(e.target.value)}
              placeholder="Motivo del rechazo..."
              rows={3}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRechazarDocId(null)} disabled={rechazandoDoc}>
              Cancelar
            </Button>
            <Button
              variant="destructive"
              onClick={handleRechazarDocumentoConfirm}
              disabled={!motivoRechazoDoc.trim() || rechazandoDoc}
            >
              {rechazandoDoc ? 'Rechazando...' : 'Rechazar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {viewerDoc && (
        <DocumentViewer
          url={viewerDoc.url}
          nombre={viewerDoc.nombre}
          open={!!viewerDoc}
          onClose={() => setViewerDoc(null)}
        />
      )}
    </>
  )
}
