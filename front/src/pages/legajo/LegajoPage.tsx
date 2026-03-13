import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  FileText, Upload, Trash2, Eye, Plus, FolderOpen, Calendar,
  Building2, CheckCircle, XCircle, FileCheck, Shield,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog, DialogContent, DialogDescription, DialogFooter,
  DialogHeader, DialogTitle,
} from '@/components/ui/dialog'
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { DocumentViewer } from '@/components/common/DocumentViewer'
import { useAuth } from '@/hooks/useAuth'
import { toast } from 'sonner'
import {
  legajoService,
  type Documento,
  type DocumentoFormData,
  TIPO_DOCUMENTO_LABELS,
  CATEGORIA_LABELS,
  TIPOS_INSTITUCIONALES,
  TIPO_CATEGORIA_MAP,
} from '@/services/legajoService'
import {
  contratosService,
  type ContratoListItem,
  TIPO_CONTRATO_LABELS,
  ESTADO_CONTRATO_BADGE,
} from '@/services/contratosService'

const CATEGORIAS = Object.entries(CATEGORIA_LABELS)

const ESTADO_BADGE: Record<string, string> = {
  activo: 'bg-green-100 text-green-800',
  inactivo: 'bg-gray-100 text-gray-800',
  vencido: 'bg-red-100 text-red-800',
  pendiente_revision: 'bg-yellow-100 text-yellow-800',
  aprobado: 'bg-blue-100 text-blue-800',
  rechazado: 'bg-red-100 text-red-800',
  archivado: 'bg-gray-100 text-gray-800',
}

const ESTADO_LABELS: Record<string, string> = {
  activo: 'Activo',
  inactivo: 'Inactivo',
  vencido: 'Vencido',
  pendiente_revision: 'Pendiente',
  aprobado: 'Aprobado',
  rechazado: 'Rechazado',
  archivado: 'Archivado',
}

/* --------------------------------------------------------
   DocumentoCard
   -------------------------------------------------------- */

interface DocCardProps {
  readonly doc: Documento
  readonly onDelete: (id: number) => void
  readonly onView: (doc: Documento) => void
  readonly isAdmin: boolean
  readonly onValidar?: (id: number) => void
  readonly onRechazar?: (id: number) => void
}

function DocumentoCard({ doc, onDelete, onView, isAdmin, onValidar, onRechazar }: DocCardProps) {
  const esInstitucional = TIPOS_INSTITUCIONALES.includes(doc.tipo_documento)

  return (
    <div className="flex items-start justify-between p-4 border rounded-lg hover:bg-muted/30 transition-colors">
      <div className="flex items-start gap-3 flex-1 min-w-0">
        <div className={`p-2 rounded-lg mt-0.5 ${esInstitucional ? 'bg-purple-50' : 'bg-blue-50'}`}>
          {esInstitucional ? (
            <Building2 className={`h-4 w-4 ${esInstitucional ? 'text-purple-600' : 'text-blue-600'}`} />
          ) : (
            <FileText className="h-4 w-4 text-blue-600" />
          )}
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-medium text-sm truncate">{doc.nombre_documento}</p>
          <p className="text-xs text-muted-foreground mt-0.5">
            {TIPO_DOCUMENTO_LABELS[doc.tipo_documento] ?? doc.tipo_documento}
          </p>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${ESTADO_BADGE[doc.estado_documento] ?? 'bg-gray-100 text-gray-800'}`}
            >
              {ESTADO_LABELS[doc.estado_documento] ?? doc.estado_documento}
            </span>
            {doc.fecha_vencimiento && (
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                Vence: {new Date(doc.fecha_vencimiento).toLocaleDateString('es-PE')}
              </span>
            )}
            {esInstitucional && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                <Shield className="h-3 w-3 mr-1" />Institucional
              </span>
            )}
          </div>
        </div>
      </div>
      <div className="flex gap-1 ml-2 shrink-0">
        {doc.archivo && (
          <Button variant="ghost" size="sm" onClick={() => onView(doc)} title="Ver documento">
            <Eye className="h-4 w-4" />
          </Button>
        )}
        {isAdmin && doc.estado_documento === 'pendiente_revision' && (
          <>
            <Button
              variant="ghost" size="sm"
              onClick={() => onValidar?.(doc.documento_id)}
              className="text-green-600 hover:text-green-700 hover:bg-green-50"
              title="Validar"
            >
              <CheckCircle className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost" size="sm"
              onClick={() => onRechazar?.(doc.documento_id)}
              className="text-orange-600 hover:text-orange-700 hover:bg-orange-50"
              title="Rechazar"
            >
              <XCircle className="h-4 w-4" />
            </Button>
          </>
        )}
        {isAdmin && (
          <Button
            variant="ghost" size="sm"
            onClick={() => onDelete(doc.documento_id)}
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
            title="Eliminar"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  )
}

/* --------------------------------------------------------
   ContratoCard
   -------------------------------------------------------- */

type ContratoCardProps = {
  readonly contrato: ContratoListItem
}

function ContratoCard({ contrato }: ContratoCardProps) {
  return (
    <div className="flex items-start justify-between p-4 border rounded-lg hover:bg-muted/30 transition-colors">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-indigo-50 rounded-lg mt-0.5">
          <FileCheck className="h-4 w-4 text-indigo-600" />
        </div>
        <div>
          <p className="font-medium text-sm">{contrato.numero_contrato}{contrato.numero_adenda ? ` - ${contrato.numero_adenda}` : ''}</p>
          <p className="text-xs text-muted-foreground mt-0.5">
            {TIPO_CONTRATO_LABELS[contrato.tipo_documento] ?? contrato.tipo_documento}
            {contrato.cargo ? ` - ${contrato.cargo}` : ''}
          </p>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${ESTADO_CONTRATO_BADGE[contrato.estado] ?? 'bg-gray-100 text-gray-800'}`}>
              {contrato.estado_texto ?? contrato.estado}
            </span>
            <span className="text-xs text-muted-foreground">
              {new Date(contrato.fecha_inicio).toLocaleDateString('es-PE')}
              {contrato.fecha_fin ? ` - ${new Date(contrato.fecha_fin).toLocaleDateString('es-PE')}` : ' - Indefinido'}
            </span>
            {contrato.dias_hasta_vencimiento != null && contrato.dias_hasta_vencimiento <= 30 && contrato.dias_hasta_vencimiento > 0 && (
              <span className="text-xs text-orange-600 font-medium">
                Vence en {contrato.dias_hasta_vencimiento} dias
              </span>
            )}
          </div>
        </div>
      </div>
      {contrato.salario_neto && (
        <div className="text-right ml-2">
          <p className="text-sm font-medium">S/ {Number(contrato.salario_neto).toLocaleString('es-PE', { minimumFractionDigits: 2 })}</p>
          <p className="text-xs text-muted-foreground">Neto</p>
        </div>
      )}
    </div>
  )
}

/* --------------------------------------------------------
   UploadDocumentoDialog
   -------------------------------------------------------- */

function sugerirNombreDocumento(tipo: string): string {
  const hoy = new Date()
  const fecha = hoy.toLocaleDateString('es-PE', { year: 'numeric', month: '2-digit', day: '2-digit' })
  const label = TIPO_DOCUMENTO_LABELS[tipo]
  return label ? `${label} - ${fecha}` : ''
}

interface UploadDialogProps {
  readonly open: boolean
  readonly empleadoId: number
  readonly isAdmin: boolean
  readonly onClose: () => void
  readonly onSuccess: () => void
}

function UploadDocumentoDialog({ open, empleadoId, isAdmin, onClose, onSuccess }: UploadDialogProps) {
  const [formData, setFormData] = useState<Partial<DocumentoFormData>>({
    empleado: empleadoId,
    estado_documento: 'activo',
    nivel_acceso: 'restringido',
  })
  const [file, setFile] = useState<File | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)

  // Tipos disponibles segun rol
  const tiposDisponibles = isAdmin
    ? Object.entries(TIPO_DOCUMENTO_LABELS)
    : Object.entries(TIPO_DOCUMENTO_LABELS).filter(
        ([key]) => !TIPOS_INSTITUCIONALES.includes(key)
      )

  const handleTipoChange = (tipo: string) => {
    const updates: Partial<DocumentoFormData> = { tipo_documento: tipo }
    if (!isAdmin) {
      updates.categoria = TIPO_CATEGORIA_MAP[tipo] || 'otros'
      updates.nombre_documento = sugerirNombreDocumento(tipo)
    }
    setFormData((p) => ({ ...p, ...updates }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.tipo_documento || !formData.nombre_documento) {
      toast.error('Complete los campos requeridos')
      return
    }
    if (isAdmin && !formData.categoria) {
      toast.error('Seleccione una categoria')
      return
    }
    if (!isAdmin && !file) {
      toast.error('Debe adjuntar un archivo')
      return
    }
    setSubmitting(true)
    try {
      const tipoDocumento = formData.tipo_documento || 'otros'
      const submitData: DocumentoFormData = {
        ...(formData as DocumentoFormData),
        empleado: empleadoId,
        categoria: formData.categoria || TIPO_CATEGORIA_MAP[tipoDocumento] || 'otros',
        archivo: file ?? undefined,
      }
      await legajoService.create(submitData)
      toast.success('Documento cargado exitosamente')
      onSuccess()
      onClose()
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Error al cargar documento')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Subir Documento</DialogTitle>
          <DialogDescription>
            {isAdmin ? 'Adjunta un documento al legajo del empleado' : 'Sube un documento a tu legajo digital'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Tipo de documento */}
          <div>
            <Label>Tipo de documento *</Label>
            <Select
              value={formData.tipo_documento ?? ''}
              onValueChange={handleTipoChange}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar tipo" />
              </SelectTrigger>
              <SelectContent>
                {tiposDisponibles.map(([val, label]) => (
                  <SelectItem key={val} value={val}>{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Categoria - solo visible para admin */}
          {isAdmin && (
            <div>
              <Label>Categoria *</Label>
              <Select
                value={formData.categoria ?? ''}
                onValueChange={(v) => setFormData((p) => ({ ...p, categoria: v }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar" />
                </SelectTrigger>
                <SelectContent>
                  {CATEGORIAS.map(([val, label]) => (
                    <SelectItem key={val} value={val}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Nombre del documento */}
          <div>
            <Label>Nombre del documento {isAdmin ? '*' : ''}</Label>
            <Input
              value={formData.nombre_documento ?? ''}
              onChange={(e) => setFormData((p) => ({ ...p, nombre_documento: e.target.value }))}
              placeholder={isAdmin ? 'Ej: DNI vigente 2025' : 'Se genera automaticamente'}
            />
          </div>

          {/* Archivo */}
          <div>
            <Label>Archivo {isAdmin ? '' : '* '}(PDF, JPG, PNG, DOC)</Label>
            <Input
              type="file"
              accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className={isAdmin || file ? '' : 'border-dashed'}
            />
            {isAdmin || file ? null : (
              <p className="text-xs text-muted-foreground mt-1">Debe adjuntar un archivo</p>
            )}
          </div>

          {/* Opciones avanzadas (colapsable para usuarios normales, siempre visible para admin) */}
          {isAdmin ? (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Fecha de emision</Label>
                  <Input
                    type="date"
                    value={formData.fecha_emision ?? ''}
                    onChange={(e) => setFormData((p) => ({ ...p, fecha_emision: e.target.value }))}
                  />
                </div>
                <div>
                  <Label>Fecha de vencimiento</Label>
                  <Input
                    type="date"
                    value={formData.fecha_vencimiento ?? ''}
                    onChange={(e) => setFormData((p) => ({ ...p, fecha_vencimiento: e.target.value }))}
                  />
                </div>
              </div>
              <div>
                <Label>Descripcion</Label>
                <Textarea
                  value={formData.descripcion_documento ?? ''}
                  onChange={(e) => setFormData((p) => ({ ...p, descripcion_documento: e.target.value }))}
                  rows={2}
                />
              </div>
            </>
          ) : (
            <>
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                {showAdvanced ? '▾ Ocultar opciones adicionales' : '▸ Mas opciones (fechas, descripcion)'}
              </button>
              {showAdvanced && (
                <div className="space-y-3 pl-3 border-l-2 border-muted">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label className="text-xs">Fecha de emision</Label>
                      <Input
                        type="date"
                        value={formData.fecha_emision ?? ''}
                        onChange={(e) => setFormData((p) => ({ ...p, fecha_emision: e.target.value }))}
                      />
                    </div>
                    <div>
                      <Label className="text-xs">Fecha de vencimiento</Label>
                      <Input
                        type="date"
                        value={formData.fecha_vencimiento ?? ''}
                        onChange={(e) => setFormData((p) => ({ ...p, fecha_vencimiento: e.target.value }))}
                      />
                    </div>
                  </div>
                  <div>
                    <Label className="text-xs">Descripcion</Label>
                    <Textarea
                      value={formData.descripcion_documento ?? ''}
                      onChange={(e) => setFormData((p) => ({ ...p, descripcion_documento: e.target.value }))}
                      rows={2}
                    />
                  </div>
                </div>
              )}
            </>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>Cancelar</Button>
            <Button
              type="submit"
              disabled={submitting || !formData.tipo_documento || (!isAdmin && !file)}
            >
              {submitting ? <LoadingSpinner size="sm" /> : <><Upload className="h-4 w-4 mr-2" />Subir</>}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

/* --------------------------------------------------------
   RechazoDialog
   -------------------------------------------------------- */

interface RechazoDialogProps {
  readonly open: boolean
  readonly onClose: () => void
  readonly onConfirm: (motivo: string) => void
}

function RechazoDialog({ open, onClose, onConfirm }: RechazoDialogProps) {
  const [motivo, setMotivo] = useState('')

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Rechazar Documento</DialogTitle>
          <DialogDescription>Indique el motivo del rechazo</DialogDescription>
        </DialogHeader>
        <Textarea
          value={motivo}
          onChange={(e) => setMotivo(e.target.value)}
          placeholder="Motivo del rechazo..."
          rows={3}
        />
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancelar</Button>
          <Button
            variant="destructive"
            onClick={() => { onConfirm(motivo); setMotivo(''); }}
            disabled={!motivo.trim()}
          >
            Rechazar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

/* --------------------------------------------------------
   LegajoPage (main)
   -------------------------------------------------------- */

export default function LegajoPage() {
  const { empleadoId: paramId } = useParams<{ empleadoId: string }>()
  const { user, isAdminOrRRHH } = useAuth()
  const queryClient = useQueryClient()
  const isAdmin = isAdminOrRRHH()

  // Si no hay parametro en URL, usar el empleado_id del usuario autenticado
  const empId = paramId
    ? Number.parseInt(paramId, 10)
    : (user?.empleado?.id ?? 0)

  const [activeTab, setActiveTab] = useState('todos')
  const [uploadOpen, setUploadOpen] = useState(false)
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [viewDoc, setViewDoc] = useState<Documento | null>(null)
  const [rechazoDocId, setRechazoDocId] = useState<number | null>(null)

  // Fetch documentos
  const { data: documentos = [], isLoading } = useQuery({
    queryKey: ['documentos', empId],
    queryFn: () => legajoService.getByEmpleado(empId),
    enabled: empId > 0,
  })

  // Fetch contratos
  const { data: contratos = [] } = useQuery({
    queryKey: ['contratos-empleado', empId],
    queryFn: () => contratosService.getByEmpleado(empId),
    enabled: empId > 0,
  })

  // Notificar si no hay documentos una vez cargado
  useEffect(() => {
    if (!isLoading && empId > 0 && documentos.length === 0) {
      toast.info('Este empleado no tiene documentos en su legajo digital. Puede subir documentos usando el boton "Subir Documento".')
    }
  }, [isLoading, empId, documentos.length])

  // Mutations
  const deleteMutation = useMutation({
    mutationFn: legajoService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documentos', empId] })
      toast.success('Documento eliminado')
      setDeleteId(null)
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : 'Error al eliminar'),
  })

  const validarMutation = useMutation({
    mutationFn: (id: number) => legajoService.validar(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documentos', empId] })
      toast.success('Documento validado')
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : 'Error al validar'),
  })

  const rechazarMutation = useMutation({
    mutationFn: ({ id, motivo }: { id: number; motivo: string }) => legajoService.rechazar(id, motivo),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documentos', empId] })
      toast.success('Documento rechazado')
      setRechazoDocId(null)
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : 'Error al rechazar'),
  })

  // Clasificacion
  const docsPersonales = documentos.filter(d => !TIPOS_INSTITUCIONALES.includes(d.tipo_documento))
  const docsInstitucionales = documentos.filter(d => TIPOS_INSTITUCIONALES.includes(d.tipo_documento))

  const docsByCategoria = documentos.reduce<Record<string, Documento[]>>((acc, doc) => {
    const cat = doc.categoria ?? 'otros'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(doc)
    return acc
  }, {})

  const categoriasConDocumentos = Object.keys(docsByCategoria)

  // Stats
  const totalDocs = documentos.length
  const pendientes = documentos.filter(d => d.estado_documento === 'pendiente_revision').length

  if (!empId) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3 text-muted-foreground">
        <FolderOpen className="h-12 w-12" />
        <p>Selecciona un empleado para ver su legajo</p>
        <p className="text-sm">URL esperada: /legajo/:empleadoId</p>
      </div>
    )
  }

  const renderDocList = (docs: Documento[]) => (
    <div className="space-y-2">
      {docs.length === 0 ? (
        <p className="text-center text-muted-foreground py-6 text-sm">No hay documentos en esta seccion</p>
      ) : (
        docs.map((doc) => (
          <DocumentoCard
            key={doc.documento_id}
            doc={doc}
            onDelete={setDeleteId}
            onView={setViewDoc}
            isAdmin={isAdmin}
            onValidar={(id) => validarMutation.mutate(id)}
            onRechazar={setRechazoDocId}
          />
        ))
      )}
    </div>
  )

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <FolderOpen className="h-6 w-6 text-blue-600" />
            Legajo Digital
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            {paramId ? `Empleado ID: ${empId}` : 'Mi legajo digital'}
          </p>
        </div>
        <Button onClick={() => setUploadOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Subir Documento
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card className="p-4">
          <p className="text-xs text-muted-foreground">Total</p>
          <p className="text-2xl font-bold">{totalDocs}</p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-muted-foreground">Personales</p>
          <p className="text-2xl font-bold text-blue-600">{docsPersonales.length}</p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-muted-foreground">Institucionales</p>
          <p className="text-2xl font-bold text-purple-600">{docsInstitucionales.length}</p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-muted-foreground">Pendientes</p>
          <p className="text-2xl font-bold text-yellow-600">{pendientes}</p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-muted-foreground">Contratos</p>
          <p className="text-2xl font-bold text-indigo-600">{contratos.length}</p>
        </Card>
      </div>

      {/* Tabs principales */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Documentos y Contratos</CardTitle>
          <CardDescription>Legajo digital completo del empleado</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && <div className="flex justify-center py-8"><LoadingSpinner /></div>}
          {!isLoading && (
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="mb-4 flex-wrap h-auto gap-1">
                <TabsTrigger value="todos">Todos ({totalDocs})</TabsTrigger>
                <TabsTrigger value="personales">
                  Mis Documentos ({docsPersonales.length})
                </TabsTrigger>
                <TabsTrigger value="institucionales">
                  Institucionales ({docsInstitucionales.length})
                </TabsTrigger>
                <TabsTrigger value="contratos">
                  Contratos ({contratos.length})
                </TabsTrigger>
                {categoriasConDocumentos.map((cat) => (
                  <TabsTrigger key={cat} value={`cat-${cat}`}>
                    {CATEGORIA_LABELS[cat] ?? cat} ({docsByCategoria[cat].length})
                  </TabsTrigger>
                ))}
              </TabsList>

              <TabsContent value="todos">{renderDocList(documentos)}</TabsContent>
              <TabsContent value="personales">{renderDocList(docsPersonales)}</TabsContent>
              <TabsContent value="institucionales">{renderDocList(docsInstitucionales)}</TabsContent>

              <TabsContent value="contratos">
                <div className="space-y-2">
                  {contratos.length === 0 ? (
                    <p className="text-center text-muted-foreground py-6 text-sm">No hay contratos registrados</p>
                  ) : (
                    contratos.map((c) => <ContratoCard key={c.contrato_id} contrato={c} />)
                  )}
                </div>
              </TabsContent>

              {categoriasConDocumentos.map((cat) => (
                <TabsContent key={cat} value={`cat-${cat}`}>
                  {renderDocList(docsByCategoria[cat])}
                </TabsContent>
              ))}
            </Tabs>
          )}
        </CardContent>
      </Card>

      {/* Dialogs */}
      {uploadOpen && (
        <UploadDocumentoDialog
          open={uploadOpen}
          empleadoId={empId}
          isAdmin={isAdmin}
          onClose={() => setUploadOpen(false)}
          onSuccess={() => queryClient.invalidateQueries({ queryKey: ['documentos', empId] })}
        />
      )}

      {viewDoc?.archivo && (
        <DocumentViewer
          url={viewDoc.archivo}
          nombre={viewDoc.nombre_documento}
          open={!!viewDoc}
          onClose={() => setViewDoc(null)}
        />
      )}

      <RechazoDialog
        open={rechazoDocId !== null}
        onClose={() => setRechazoDocId(null)}
        onConfirm={(motivo) => {
          if (rechazoDocId !== null) {
            rechazarMutation.mutate({ id: rechazoDocId, motivo })
          }
        }}
      />

      <AlertDialog open={deleteId !== null} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Eliminar documento?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta accion no se puede deshacer. El documento sera eliminado permanentemente.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteId !== null && deleteMutation.mutate(deleteId)}
              className="bg-red-600 hover:bg-red-700"
            >
              Eliminar
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
