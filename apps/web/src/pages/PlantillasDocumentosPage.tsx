import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  AlertTriangle, BookOpen, Check, ChevronDown, ChevronUp,
  Copy, Download, Eye, FileText, Info, Trash2, Upload,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
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
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { toast } from 'sonner'
import {
  plantillasService,
  TIPO_PLANTILLA_BADGE,
  TIPO_PLANTILLA_LABELS,
  type PlantillaDocumento,
  type TipoPlantilla,
} from '@/services/plantillasService'

type TabValue = 'todos' | TipoPlantilla

const TABS: { value: TabValue; label: string }[] = [
  { value: 'todos', label: 'Todos' },
  { value: 'certificado_trabajo', label: 'Certificados' },
  { value: 'constancia_laboral', label: 'Constancias' },
  { value: 'contrato', label: 'Contratos' },
  { value: 'adenda', label: 'Adendas' },
]

// Variables con descripción agrupadas por categoría
interface VarDef { variable: string; descripcion: string }
interface VarGrupo { grupo: string; vars: VarDef[] }

const GRUPOS_EMPLEADO: VarDef[] = [
  { variable: '{{NOMBRE_COMPLETO}}', descripcion: 'Nombres y apellidos completos' },
  { variable: '{{NOMBRE_EMPLEADO}}', descripcion: 'Solo los nombres del empleado' },
  { variable: '{{APELLIDOS}}', descripcion: 'Apellido paterno y materno' },
  { variable: '{{DNI}}', descripcion: 'Número de documento de identidad' },
  { variable: '{{TIPO_DOCUMENTO}}', descripcion: 'Tipo de documento (DNI, CE, etc.)' },
  { variable: '{{CARGO}}', descripcion: 'Cargo del empleado' },
  { variable: '{{AREA}}', descripcion: 'Área u órgano donde labora' },
  { variable: '{{FECHA_INGRESO}}', descripcion: 'Fecha de inicio de labores (DD de mes de AAAA)' },
  { variable: '{{TELEFONO}}', descripcion: 'Teléfono celular del empleado' },
  { variable: '{{EMAIL}}', descripcion: 'Correo electrónico personal' },
]

const GRUPOS_EMPRESA: VarDef[] = [
  { variable: '{{EMPRESA_NOMBRE}}', descripcion: 'Razón social de la institución' },
  { variable: '{{EMPRESA_RUC}}', descripcion: 'RUC de la institución' },
  { variable: '{{EMPRESA_DIRECCION}}', descripcion: 'Dirección fiscal de la institución' },
  { variable: '{{CIUDAD}}', descripcion: 'Ciudad (por defecto: Lima)' },
  { variable: '{{FECHA_HOY}}', descripcion: 'Fecha actual (DD de mes de AAAA)' },
]

const GRUPOS_CERTIFICADO: VarDef[] = [
  { variable: '{{NUMERO_CERTIFICADO}}', descripcion: 'Número correlativo del documento' },
  { variable: '{{FECHA_EXPEDICION}}', descripcion: 'Fecha de expedición del certificado' },
  { variable: '{{PROPOSITO}}', descripcion: 'Propósito o destino del documento' },
  { variable: '{{SALARIO_BRUTO}}', descripcion: 'Remuneración bruta mensual (si se incluye)' },
]

const GRUPOS_CONTRATO: VarDef[] = [
  { variable: '{{NUMERO_CONTRATO}}', descripcion: 'Número de contrato (Ej: CONT-20240115120000)' },
  { variable: '{{TIPO_CONTRATO}}', descripcion: 'Modalidad contractual' },
  { variable: '{{FECHA_INICIO}}', descripcion: 'Fecha de inicio del contrato' },
  { variable: '{{FECHA_FIN}}', descripcion: 'Fecha de vencimiento del contrato' },
  { variable: '{{FECHA_FIRMA}}', descripcion: 'Fecha de suscripción del contrato' },
  { variable: '{{SALARIO_BRUTO}}', descripcion: 'Remuneración bruta mensual' },
  { variable: '{{SALARIO_NETO}}', descripcion: 'Remuneración neta mensual' },
  { variable: '{{JORNADA}}', descripcion: 'Jornada laboral (Ej: 48 horas semanales)' },
  { variable: '{{LUGAR_TRABAJO}}', descripcion: 'Dirección del lugar de trabajo' },
  { variable: '{{HORARIO_TRABAJO}}', descripcion: 'Horario de trabajo' },
  { variable: '{{FUNCIONES}}', descripcion: 'Descripción de funciones del puesto' },
]

const GRUPOS_ADENDA: VarDef[] = [
  { variable: '{{NUMERO_ADENDA}}', descripcion: 'Número de adenda' },
  { variable: '{{NUMERO_CONTRATO}}', descripcion: 'Número del contrato que se modifica' },
  { variable: '{{FECHA_INICIO}}', descripcion: 'Inicio de vigencia de la adenda' },
  { variable: '{{FECHA_FIN}}', descripcion: 'Fin de vigencia de la adenda' },
  { variable: '{{FECHA_FIRMA}}', descripcion: 'Fecha de suscripción de la adenda' },
  { variable: '{{SALARIO_BRUTO}}', descripcion: 'Nueva remuneración bruta (si cambia)' },
  { variable: '{{FUNCIONES}}', descripcion: 'Nuevas funciones o modificaciones' },
]

const VARIABLES_POR_TIPO: Record<TipoPlantilla, VarGrupo[]> = {
  certificado_trabajo: [
    { grupo: 'Datos del Empleado', vars: GRUPOS_EMPLEADO },
    { grupo: 'Datos de la Empresa', vars: GRUPOS_EMPRESA },
    { grupo: 'Datos del Certificado', vars: GRUPOS_CERTIFICADO },
  ],
  constancia_laboral: [
    { grupo: 'Datos del Empleado', vars: GRUPOS_EMPLEADO },
    { grupo: 'Datos de la Empresa', vars: GRUPOS_EMPRESA },
    { grupo: 'Datos del Documento', vars: GRUPOS_CERTIFICADO },
  ],
  contrato: [
    { grupo: 'Datos del Empleado', vars: GRUPOS_EMPLEADO },
    { grupo: 'Datos de la Empresa', vars: GRUPOS_EMPRESA },
    { grupo: 'Datos del Contrato', vars: GRUPOS_CONTRATO },
  ],
  adenda: [
    { grupo: 'Datos del Empleado', vars: GRUPOS_EMPLEADO },
    { grupo: 'Datos de la Empresa', vars: GRUPOS_EMPRESA },
    { grupo: 'Datos de la Adenda', vars: GRUPOS_ADENDA },
  ],
}

interface UploadForm {
  nombre: string
  tipo: TipoPlantilla | ''
  descripcion: string
  archivo: File | null
}

function formatDate(iso: string): string {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('es-PE', {
    year: 'numeric', month: '2-digit', day: '2-digit',
  })
}

function CopyableVar({ variable }: { variable: string }) {
  const [copied, setCopied] = useState(false)

  function handleCopy() {
    navigator.clipboard.writeText(variable).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }

  return (
    <button
      type="button"
      onClick={handleCopy}
      title="Copiar al portapapeles"
      className="inline-flex items-center gap-1 bg-muted border hover:bg-accent hover:border-primary/30 text-foreground text-xs px-2 py-1 rounded font-mono transition-colors cursor-pointer group"
    >
      <span>{variable}</span>
      {copied
        ? <Check className="w-3 h-3 text-green-500 flex-shrink-0" />
        : <Copy className="w-3 h-3 opacity-0 group-hover:opacity-60 flex-shrink-0 transition-opacity" />
      }
    </button>
  )
}

// Card colapsable de guía de uso
function GuiaUso() {
  const [open, setOpen] = useState(false)

  return (
    <Card className="border-blue-200 bg-blue-50/50">
      <button
        type="button"
        className="w-full text-left"
        onClick={() => setOpen(v => !v)}
      >
        <CardHeader className="pb-2 pt-4 px-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-blue-600" />
              <CardTitle className="text-sm font-semibold text-blue-800">
                ¿Cómo crear y usar una plantilla?
              </CardTitle>
            </div>
            {open
              ? <ChevronUp className="w-4 h-4 text-blue-600" />
              : <ChevronDown className="w-4 h-4 text-blue-600" />
            }
          </div>
        </CardHeader>
      </button>

      {open && (
        <CardContent className="px-4 pb-4 text-sm text-blue-900 space-y-3">
          <ol className="space-y-2 list-decimal list-inside">
            <li>
              <strong>Descarga una plantilla base</strong> haciendo clic en el ícono
              <Download className="w-3.5 h-3.5 inline mx-1" />
              de cualquier plantilla existente. Abrela en Microsoft Word.
            </li>
            <li>
              <strong>Edita el contenido</strong> con el texto que necesitas. Donde quieras insertar
              datos del empleado, escribe el marcador correspondiente, por ejemplo{' '}
              <code className="bg-white border border-blue-200 px-1 rounded font-mono">{'{{NOMBRE_COMPLETO}}'}</code>.
            </li>
            <li>
              <strong>Importante:</strong> escribe cada marcador en un solo bloque de texto sin
              interrupciones. No uses formato diferente dentro del marcador
              (todo el <code className="bg-white border border-blue-200 px-1 rounded font-mono">{'{{VARIABLE}}'}</code> debe tener el mismo estilo).
            </li>
            <li>
              <strong>Guarda el archivo como .docx</strong> (no PDF ni .doc).
            </li>
            <li>
              Haz clic en <strong>Subir Plantilla</strong>, elige el tipo correcto y sube el archivo.
            </li>
            <li>
              Desde <strong>Contratos</strong> o el módulo correspondiente podrás generar el
              documento real seleccionando esta plantilla y el empleado.
            </li>
          </ol>
          <div className="rounded bg-white border border-blue-200 p-2 text-xs text-blue-700">
            <strong>Consejo:</strong> Usa el botón <Eye className="w-3 h-3 inline mx-0.5" />
            {' '}de cada plantilla para ver todos los marcadores disponibles y hacer clic en ellos para copiarlos.
          </div>
        </CardContent>
      )}
    </Card>
  )
}

export default function PlantillasDocumentosPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<TabValue>('todos')
  const [uploadOpen, setUploadOpen] = useState(false)
  const [variablesOpen, setVariablesOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [selectedPlantilla, setSelectedPlantilla] = useState<PlantillaDocumento | null>(null)
  const [form, setForm] = useState<UploadForm>({ nombre: '', tipo: '', descripcion: '', archivo: null })
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { data: plantillas = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['plantillas-word', activeTab],
    queryFn: () => plantillasService.getAll(activeTab === 'todos' ? undefined : (activeTab as TipoPlantilla)),
  })

  const uploadMutation = useMutation({
    mutationFn: () => {
      if (!form.archivo || !form.tipo) throw new Error('Archivo y tipo son requeridos')
      return plantillasService.subir({
        nombre: form.nombre, tipo: form.tipo as TipoPlantilla,
        descripcion: form.descripcion, archivo: form.archivo,
      })
    },
    onSuccess: () => {
      toast.success('Plantilla subida correctamente')
      queryClient.invalidateQueries({ queryKey: ['plantillas-word'] })
      setUploadOpen(false)
      setForm({ nombre: '', tipo: '', descripcion: '', archivo: null })
      if (fileInputRef.current) fileInputRef.current.value = ''
    },
    onError: (e: Error) => toast.error(e.message || 'Error al subir la plantilla'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => plantillasService.eliminar(id),
    onSuccess: () => {
      toast.success('Plantilla eliminada correctamente')
      queryClient.invalidateQueries({ queryKey: ['plantillas-word'] })
      setDeleteOpen(false)
      setSelectedPlantilla(null)
    },
    onError: (e: Error) => toast.error(e.message || 'Error al eliminar la plantilla'),
  })

  const downloadMutation = useMutation({
    mutationFn: ({ id, nombre }: { id: number; nombre: string }) =>
      plantillasService.descargar(id, nombre),
    onSuccess: () => toast.success('Descarga iniciada'),
    onError: (e: Error) => toast.error(e.message || 'Error al descargar'),
  })

  function handleUploadSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.nombre.trim()) { toast.error('El nombre es requerido'); return }
    if (!form.tipo) { toast.error('El tipo de documento es requerido'); return }
    if (!form.archivo) { toast.error('Debe seleccionar un archivo .docx'); return }
    uploadMutation.mutate()
  }

  const gruposActivos = selectedPlantilla
    ? VARIABLES_POR_TIPO[selectedPlantilla.tipo] ?? []
    : []

  return (
    <div className="space-y-5 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Plantillas de Documentos</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Gestiona las plantillas Word (.docx) para generar documentos de RRHH automáticamente
          </p>
        </div>
        <Button onClick={() => setUploadOpen(true)} className="gap-2">
          <Upload className="w-4 h-4" />
          Subir Plantilla
        </Button>
      </div>

      {/* Guía de uso colapsable */}
      <GuiaUso />

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Plantillas Registradas</CardTitle>
          <CardDescription>
            Las plantillas base vienen pre-cargadas. Descárgalas, edítalas y vuelve a subirlas con tu propia versión.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as TabValue)} className="mb-4">
            <TabsList>
              {TABS.map(t => (
                <TabsTrigger key={t.value} value={t.value}>{t.label}</TabsTrigger>
              ))}
            </TabsList>
          </Tabs>

          {isLoading ? (
            <div className="flex justify-center py-12"><LoadingSpinner /></div>
          ) : isError ? (
            <div className="flex flex-col items-center gap-3 py-12 text-destructive">
              <AlertTriangle className="w-8 h-8" />
              <p className="text-sm">Error al cargar las plantillas</p>
              <Button variant="outline" size="sm" onClick={() => refetch()}>Reintentar</Button>
            </div>
          ) : plantillas.length === 0 ? (
            <div className="flex flex-col items-center gap-4 py-16 text-muted-foreground">
              <FileText className="w-12 h-12 opacity-40" />
              <div className="text-center">
                <p className="font-medium">No hay plantillas registradas</p>
                <p className="text-xs mt-1">Sube tu primera plantilla Word para comenzar</p>
              </div>
              <Button variant="outline" size="sm" onClick={() => setUploadOpen(true)}>
                <Upload className="w-4 h-4 mr-2" />Subir plantilla
              </Button>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nombre</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead className="hidden lg:table-cell">Descripción</TableHead>
                    <TableHead className="hidden sm:table-cell whitespace-nowrap">Fecha alta</TableHead>
                    <TableHead className="text-right">Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {plantillas.map(p => (
                    <TableRow key={p.plantilla_id}>
                      <TableCell className="font-medium">{p.nombre}</TableCell>
                      <TableCell>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${TIPO_PLANTILLA_BADGE[p.tipo] ?? 'bg-gray-100 text-gray-800'}`}>
                          {p.tipo_texto || TIPO_PLANTILLA_LABELS[p.tipo]}
                        </span>
                      </TableCell>
                      <TableCell className="hidden lg:table-cell max-w-sm">
                        <span className="text-sm text-muted-foreground line-clamp-2">
                          {p.descripcion || <span className="italic">Sin descripción</span>}
                        </span>
                      </TableCell>
                      <TableCell className="hidden sm:table-cell text-sm text-muted-foreground whitespace-nowrap">
                        {formatDate(p.created_at)}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            variant="ghost" size="sm"
                            title="Ver variables disponibles"
                            onClick={() => { setSelectedPlantilla(p); setVariablesOpen(true) }}
                            className="h-8 w-8 p-0"
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost" size="sm"
                            title="Descargar archivo .docx"
                            onClick={() => downloadMutation.mutate({ id: p.plantilla_id, nombre: p.archivo_nombre || `plantilla_${p.plantilla_id}.docx` })}
                            disabled={downloadMutation.isPending}
                            className="h-8 w-8 p-0"
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost" size="sm"
                            title="Eliminar plantilla"
                            onClick={() => { setSelectedPlantilla(p); setDeleteOpen(true) }}
                            className="h-8 w-8 p-0 text-destructive hover:text-destructive hover:bg-destructive/10"
                          >
                            <Trash2 className="w-4 h-4" />
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

      {/* ── Upload Dialog ── */}
      <Dialog open={uploadOpen} onOpenChange={(v) => {
        if (!v && !uploadMutation.isPending) {
          setUploadOpen(false)
          setForm({ nombre: '', tipo: '', descripcion: '', archivo: null })
        }
      }}>
        <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Subir Plantilla Word</DialogTitle>
            <DialogDescription>
              Sube un archivo .docx con marcadores como{' '}
              <code className="font-mono bg-muted px-1 rounded">{'{{NOMBRE_EMPLEADO}}'}</code>{' '}
              que serán reemplazados al generar documentos.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleUploadSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label>Nombre <span className="text-destructive">*</span></Label>
              <Input
                placeholder="Ej: Certificado de trabajo 2024"
                value={form.nombre}
                onChange={e => setForm(p => ({ ...p, nombre: e.target.value }))}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Tipo de documento <span className="text-destructive">*</span></Label>
              <Select value={form.tipo} onValueChange={v => setForm(p => ({ ...p, tipo: v as TipoPlantilla }))}>
                <SelectTrigger><SelectValue placeholder="Selecciona un tipo" /></SelectTrigger>
                <SelectContent>
                  {(Object.keys(TIPO_PLANTILLA_LABELS) as TipoPlantilla[]).map(k => (
                    <SelectItem key={k} value={k}>{TIPO_PLANTILLA_LABELS[k]}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {form.tipo !== '' && (
              <div className="rounded-md bg-blue-50 border border-blue-200 p-3">
                <div className="flex items-start gap-2">
                  <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div className="min-w-0 w-full">
                    <p className="text-xs font-semibold text-blue-800 mb-1">
                      Variables para {TIPO_PLANTILLA_LABELS[form.tipo as TipoPlantilla]} — haz clic para copiar
                    </p>
                    {VARIABLES_POR_TIPO[form.tipo as TipoPlantilla].map(grupo => (
                      <div key={grupo.grupo} className="mb-2">
                        <p className="text-[11px] font-medium text-blue-700 mb-1">{grupo.grupo}</p>
                        <div className="flex flex-wrap gap-1">
                          {grupo.vars.map(v => (
                            <CopyableVar key={v.variable} variable={v.variable} />
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-1.5">
              <Label>Descripción</Label>
              <Textarea
                placeholder="Describe el uso de esta plantilla..."
                value={form.descripcion}
                onChange={e => setForm(p => ({ ...p, descripcion: e.target.value }))}
                rows={2}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Archivo (.docx) <span className="text-destructive">*</span></Label>
              <Input
                type="file"
                accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ref={fileInputRef}
                onChange={e => setForm(p => ({ ...p, archivo: e.target.files?.[0] ?? null }))}
              />
              {form.archivo && (
                <p className="text-xs text-muted-foreground">
                  {form.archivo.name} — {(form.archivo.size / 1024).toFixed(1)} KB
                </p>
              )}
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setUploadOpen(false)} disabled={uploadMutation.isPending}>
                Cancelar
              </Button>
              <Button type="submit" disabled={uploadMutation.isPending} className="gap-2">
                {uploadMutation.isPending
                  ? <><LoadingSpinner size="sm" />Subiendo...</>
                  : <><Upload className="w-4 h-4" />Subir Plantilla</>
                }
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* ── Variables Dialog ── */}
      <Dialog open={variablesOpen} onOpenChange={setVariablesOpen}>
        <DialogContent className="sm:max-w-lg max-h-[85vh] flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Eye className="w-5 h-5" />Variables disponibles
            </DialogTitle>
            <DialogDescription className="flex items-center gap-2">
              {selectedPlantilla && (
                <>
                  <span>{selectedPlantilla.nombre}</span>
                  <span className={`inline-flex items-center px-1.5 py-0.5 rounded-full text-[11px] font-medium ${TIPO_PLANTILLA_BADGE[selectedPlantilla.tipo] ?? 'bg-gray-100 text-gray-800'}`}>
                    {selectedPlantilla.tipo_texto || TIPO_PLANTILLA_LABELS[selectedPlantilla.tipo]}
                  </span>
                </>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="text-xs text-muted-foreground flex items-center gap-1.5 -mt-1">
            <Copy className="w-3 h-3" />
            Haz clic en cualquier marcador para copiarlo al portapapeles
          </div>

          <div className="overflow-y-auto flex-1 space-y-4 pr-1">
            {gruposActivos.map(grupo => (
              <div key={grupo.grupo}>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  {grupo.grupo}
                </p>
                <div className="space-y-1.5">
                  {grupo.vars.map(v => (
                    <div key={v.variable} className="flex items-start gap-2">
                      <CopyableVar variable={v.variable} />
                      <span className="text-xs text-muted-foreground pt-1">{v.descripcion}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <DialogFooter className="mt-2">
            <Button variant="outline" onClick={() => setVariablesOpen(false)}>Cerrar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Delete Dialog ── */}
      <Dialog open={deleteOpen} onOpenChange={(v) => {
        if (!v && !deleteMutation.isPending) setDeleteOpen(false)
      }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-destructive" />Eliminar plantilla
            </DialogTitle>
            <DialogDescription>
              Esta acción desactivará la plantilla. Los documentos ya generados no se verán afectados.
            </DialogDescription>
          </DialogHeader>
          {selectedPlantilla && (
            <div className="rounded-md bg-muted p-3 space-y-1">
              <p className="text-sm font-semibold">{selectedPlantilla.nombre}</p>
              <p className="text-xs text-muted-foreground">
                {selectedPlantilla.tipo_texto || TIPO_PLANTILLA_LABELS[selectedPlantilla.tipo]}
              </p>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)} disabled={deleteMutation.isPending}>
              Cancelar
            </Button>
            <Button
              variant="destructive"
              onClick={() => selectedPlantilla && deleteMutation.mutate(selectedPlantilla.plantilla_id)}
              disabled={deleteMutation.isPending}
              className="gap-2"
            >
              {deleteMutation.isPending
                ? <><LoadingSpinner size="sm" />Eliminando...</>
                : <><Trash2 className="w-4 h-4" />Eliminar</>
              }
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
