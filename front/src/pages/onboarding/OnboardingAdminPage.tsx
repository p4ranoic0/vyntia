import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from '@/components/ui/dialog'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'
import { DocumentViewer } from '@/components/common/DocumentViewer'
import { legajoService, type Documento } from '@/services/legajoService'
import { getErrorMessage } from '@/lib/errorUtils'
import {
  onboardingService, getEstadoLabel,
  type OnboardingStatus, type OnboardingCreateData,
} from '@/services/onboardingService'
import {
  CheckCircle2, Clock, Eye, Mail, RefreshCw, Search, ShieldCheck, UserPlus, XCircle,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

export default function OnboardingAdminPage() {
  const [onboardings, setOnboardings] = useState<OnboardingStatus[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [filterEstado, setFilterEstado] = useState<string>('todos')
  const [searchTerm, setSearchTerm] = useState('')
  const [createOpen, setCreateOpen] = useState(false)
  const [selectedOnboarding, setSelectedOnboarding] = useState<OnboardingStatus | null>(null)

  const fetchOnboardings = async () => {
    try {
      setIsLoading(true)
      const params: Record<string, any> = {}
      if (filterEstado !== 'todos') params.estado = filterEstado
      const data = await onboardingService.getAll(params)
      setOnboardings(data.results)
    } catch {
      toast.error('Error al cargar los onboardings')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchOnboardings()
  }, [filterEstado])

  const filteredOnboardings = onboardings.filter((o) =>
    !searchTerm ||
    o.empleado_nombre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    o.empleado_documento?.includes(searchTerm)
  )

  const getEstadoBadge = (estado: string) => {
    switch (estado) {
      case 'completado': return <Badge className="bg-green-600">Completado</Badge>
      case 'observado': return <Badge variant="destructive">Observado</Badge>
      case 'pendiente_validacion': return <Badge className="bg-blue-600">En Validacion</Badge>
      case 'pendiente_datos': return <Badge variant="secondary">Pendiente Datos</Badge>
      case 'pendiente_documentos': return <Badge variant="outline">Pendiente Docs</Badge>
      default: return <Badge variant="secondary">{getEstadoLabel(estado)}</Badge>
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
        <Button onClick={() => setCreateOpen(true)}>
          <UserPlus className="mr-2 h-4 w-4" />
          Iniciar Onboarding
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-4 pb-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por nombre o DNI..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={filterEstado} onValueChange={setFilterEstado}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos los estados</SelectItem>
                <SelectItem value="pendiente_datos">Pendiente Datos</SelectItem>
                <SelectItem value="pendiente_documentos">Pendiente Documentos</SelectItem>
                <SelectItem value="pendiente_validacion">Pendiente Validacion</SelectItem>
                <SelectItem value="observado">Observado</SelectItem>
                <SelectItem value="completado">Completado</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" onClick={fetchOnboardings}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Empleado</TableHead>
                <TableHead>DNI</TableHead>
                <TableHead>Usuario</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead className="text-center">Progreso</TableHead>
                <TableHead>Fecha Inicio</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8">
                    <div className="flex items-center justify-center">
                      <div className="animate-spin h-6 w-6 border-4 border-primary border-t-transparent rounded-full" />
                    </div>
                  </TableCell>
                </TableRow>
              ) : filteredOnboardings.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                    No se encontraron procesos de onboarding
                  </TableCell>
                </TableRow>
              ) : (
                filteredOnboardings.map((o) => (
                  <TableRow
                    key={o.onboarding_id}
                    className="cursor-pointer hover:bg-accent/50"
                    onClick={() => setSelectedOnboarding(o)}
                  >
                    <TableCell className="font-medium">{o.empleado_nombre}</TableCell>
                    <TableCell className="font-mono text-sm">{o.empleado_documento}</TableCell>
                    <TableCell className="text-sm">{o.usuario_username}</TableCell>
                    <TableCell>{getEstadoBadge(o.estado_onboarding)}</TableCell>
                    <TableCell className="text-center">
                      <span className="font-semibold">{o.progreso_porcentaje}%</span>
                    </TableCell>
                    <TableCell className="text-sm">
                      {new Date(o.fecha_inicio).toLocaleDateString('es-PE')}
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setSelectedOnboarding(o) }}>
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
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
        onSuccess={() => {
          setCreateOpen(false)
          fetchOnboardings()
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

function CreateOnboardingDialog({
  open, onClose, onSuccess,
}: { open: boolean; onClose: () => void; onSuccess: () => void }) {
  const [formData, setFormData] = useState<OnboardingCreateData>({
    nombres_empleado: '',
    apellido_paterno: '',
    apellido_materno: '',
    numero_documento: '',
    correo_personal: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<{ username: string; email_enviado: boolean } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      const response = await onboardingService.crear(formData)
      setResult({ username: response.username, email_enviado: response.email_enviado })
      toast.success(`Onboarding iniciado para ${formData.nombres_empleado}`)
    } catch (err: any) {
      console.error('Onboarding error response:', err?.response?.data)
      toast.error(getErrorMessage(err, 'Error al crear onboarding'))
    } finally {
      setSubmitting(false)
    }
  }

  const handleClose = () => {
    setResult(null)
    setFormData({
      nombres_empleado: '', apellido_paterno: '', apellido_materno: '',
      numero_documento: '', correo_personal: '',
    })
    if (result) onSuccess()
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
            <div className="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
              <CheckCircle2 className="h-8 w-8 text-green-600 shrink-0" />
              <div>
                <p className="font-semibold text-green-800 dark:text-green-200">Onboarding creado exitosamente</p>
                <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                  Usuario: <span className="font-mono font-bold">{result.username}</span>
                </p>
                <p className="text-sm text-green-700 dark:text-green-300">
                  Email: {result.email_enviado ? 'Enviado' : 'No se pudo enviar'}
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
              <Button type="submit" disabled={submitting}>
                {submitting ? 'Creando...' : 'Iniciar Onboarding'}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}

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
      await onboardingService.validar(onboarding.onboarding_id, 'aprobar', observaciones)
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
      await onboardingService.validar(onboarding.onboarding_id, 'rechazar', observaciones)
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
      await onboardingService.reenviarEmail(onboarding.onboarding_id)
      toast.success('Email reenviado exitosamente')
    } catch {
      toast.error('Error al reenviar email')
    }
  }

  const handleActualizarEstado = async () => {
    try {
      await onboardingService.actualizarEstado(onboarding.onboarding_id)
      toast.success('Estado actualizado')
      onUpdate()
    } catch {
      toast.error('Error al actualizar estado')
    }
  }

  const handleValidarDocumento = async (docId: number) => {
    try {
      await legajoService.validar(docId)
      toast.success('Documento validado')
      const docs = await legajoService.getByEmpleado(onboarding.empleado)
      setDocumentos(docs)
    } catch {
      toast.error('Error al validar documento')
    }
  }

  const handleRechazarDocumento = async (docId: number) => {
    const motivo = prompt('Motivo del rechazo:')
    if (!motivo) return
    try {
      await legajoService.rechazar(docId, motivo)
      toast.success('Documento rechazado')
      const docs = await legajoService.getByEmpleado(onboarding.empleado)
      setDocumentos(docs)
    } catch {
      toast.error('Error al rechazar documento')
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
              DNI: {onboarding.empleado_documento} | Usuario: {onboarding.usuario_username}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Checklist */}
            <div>
              <h4 className="text-sm font-semibold mb-3">Checklist de Completitud</h4>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: 'Datos personales', done: onboarding.datos_personales_completos },
                  { label: 'Datos laborales', done: onboarding.datos_laborales_completos },
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
                    <div key={doc.documento_id} className="flex items-center justify-between p-3 border rounded-lg">
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
                            onClick={() => setViewerDoc({ url: doc.archivo!, nombre: doc.nombre_documento })}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        )}
                        {doc.estado_documento === 'pendiente_revision' && (
                          <>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-green-600"
                              onClick={() => handleValidarDocumento(doc.documento_id)}
                            >
                              <ShieldCheck className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-red-600"
                              onClick={() => handleRechazarDocumento(doc.documento_id)}
                            >
                              <XCircle className="h-4 w-4" />
                            </Button>
                          </>
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
                  <Button onClick={handleValidar} disabled={validando} className="bg-green-600 hover:bg-green-700">
                    <ShieldCheck className="h-4 w-4 mr-2" />
                    {validando ? 'Validando...' : 'Aprobar Todo'}
                  </Button>
                  <Button variant="destructive" onClick={handleRechazar} disabled={rechazando}>
                    <XCircle className="h-4 w-4 mr-2" />
                    {rechazando ? 'Rechazando...' : 'Observar'}
                  </Button>
                  <Button variant="outline" onClick={handleReenviarEmail}>
                    <Mail className="h-4 w-4 mr-2" />
                    Reenviar Email
                  </Button>
                  <Button variant="outline" onClick={handleActualizarEstado}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Actualizar Estado
                  </Button>
                </div>
              </div>
            )}
          </div>
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
