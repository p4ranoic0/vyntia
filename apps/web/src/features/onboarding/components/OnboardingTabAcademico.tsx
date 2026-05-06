import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Plus, BookOpen, GraduationCap, Award, Upload, X } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui/select'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/shared/ui/dialog'
import { Card, CardContent, CardHeader } from '@/shared/ui/card'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/shared/ui/accordion'
import { DocumentUploadZone } from './DocumentUploadZone'
import { DocumentPreviewModal } from './DocumentPreviewModal'
import {
  getAcademicos,
  createAcademico,
  getCursos,
  createCurso,
  deleteCurso,
} from '../services/onboardingDataService'
import { subirDocumento } from '../services/onboardingUploadService'
import { cn } from '@/shared/utils/cn'

interface OnboardingTabAcademicoProps {
  empleadoId: number
  docs?: import('../types/onboarding').DocumentInfo[]
}

const CERTIFICADO_NIVELES = ['secundaria', 'tecnico', 'universitario']
const TITULO_NIVELES = ['bachiller', 'titulo_profesional', 'maestria', 'doctorado', 'especializacion']

interface CertificadoForm {
  institucion: string
  nivel_educativo: string
  fecha_inicio: string
  fecha_fin: string
}

interface CursoForm {
  nombre_curso: string
  institucion: string
  fecha_inicio: string
  fecha_fin: string
  horas: string
}

interface TituloForm {
  carrera: string
  institucion: string
  nivel_educativo: string
  fecha_inicio: string
  fecha_fin: string
}

const EMPTY_CERT: CertificadoForm = { institucion: '', nivel_educativo: '', fecha_inicio: '', fecha_fin: '' }
const EMPTY_CURSO: CursoForm = { nombre_curso: '', institucion: '', fecha_inicio: '', fecha_fin: '', horas: '' }
const EMPTY_TITULO: TituloForm = { carrera: '', institucion: '', nivel_educativo: '', fecha_inicio: '', fecha_fin: '' }

interface PendingDoc {
  file: File
  tipo: string
  label: string
}

interface CompactDropZoneProps {
  onFileSelected: (file: File) => void
  disabled?: boolean
}

function CompactDropZone({ onFileSelected, disabled }: CompactDropZoneProps) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'], 'image/*': ['.jpg', '.jpeg', '.png'] },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
    disabled,
    onDropAccepted: ([file]) => onFileSelected(file),
    onDropRejected: ([rejection]) => {
      const code = rejection.errors[0]?.code
      if (code === 'file-too-large') toast.error('El archivo supera los 10 MB permitidos')
      else toast.error('Solo se permiten PDF o imagenes')
    },
  })

  return (
    <div
      {...getRootProps()}
      className={cn(
        'rounded border border-dashed p-3 text-center cursor-pointer transition-colors',
        isDragActive ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50 hover:bg-muted/50',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <input {...getInputProps()} />
      <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
        <Upload className="h-3 w-3" />
        <span>{isDragActive ? 'Suelte el archivo aqui' : 'Arrastra el archivo aqui o haz clic'}</span>
      </div>
    </div>
  )
}

export function OnboardingTabAcademico({ empleadoId }: OnboardingTabAcademicoProps) {
  const queryClient = useQueryClient()

  const [isCertDialogOpen, setIsCertDialogOpen] = useState(false)
  const [isCursoDialogOpen, setIsCursoDialogOpen] = useState(false)
  const [isTituloDialogOpen, setIsTituloDialogOpen] = useState(false)

  const [certForm, setCertForm] = useState<CertificadoForm>(EMPTY_CERT)
  const [cursoForm, setCursoForm] = useState<CursoForm>(EMPTY_CURSO)
  const [tituloForm, setTituloForm] = useState<TituloForm>(EMPTY_TITULO)

  // Two-phase upload state — cert dialog
  const [certPendingDoc, setCertPendingDoc] = useState<PendingDoc | null>(null)
  const [certStagedFile, setCertStagedFile] = useState<File | null>(null)
  const [isCertPreviewOpen, setIsCertPreviewOpen] = useState(false)

  // Two-phase upload state — curso dialog
  const [cursoPendingDoc, setCursoPendingDoc] = useState<PendingDoc | null>(null)
  const [cursoStagedFile, setCursoStagedFile] = useState<File | null>(null)
  const [isCursoPreviewOpen, setIsCursoPreviewOpen] = useState(false)

  // Two-phase upload state — titulo dialog
  const [tituloPendingDoc, setTituloPendingDoc] = useState<PendingDoc | null>(null)
  const [tituloStagedFile, setTituloStagedFile] = useState<File | null>(null)
  const [isTituloPreviewOpen, setIsTituloPreviewOpen] = useState(false)

  const { data: academicos = [] } = useQuery({
    queryKey: ['academicos', empleadoId],
    queryFn: () => getAcademicos(empleadoId),
  })

  const { data: cursos = [] } = useQuery({
    queryKey: ['cursos', empleadoId],
    queryFn: () => getCursos(empleadoId),
  })

  const certificados = (academicos as Record<string, unknown>[]).filter(
    (a) => CERTIFICADO_NIVELES.includes(a.nivel_educativo as string)
  )
  const titulos = (academicos as Record<string, unknown>[]).filter(
    (a) => TITULO_NIVELES.includes(a.nivel_educativo as string)
  )

  const invalidateAll = () => {
    queryClient.invalidateQueries({ queryKey: ['academicos', empleadoId] })
    queryClient.invalidateQueries({ queryKey: ['cursos', empleadoId] })
    queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
    queryClient.invalidateQueries({ queryKey: ['legajo-docs', empleadoId] })
  }

  const certMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => createAcademico(data),
    onSuccess: async () => {
      invalidateAll()
      if (certPendingDoc) {
        try {
          await subirDocumento(empleadoId, certPendingDoc.tipo, 'academico', certPendingDoc.label, certPendingDoc.file)
          toast.success('Certificado y documento guardados')
        } catch {
          toast.warning('Certificado guardado. Error al subir documento — puede subirlo luego.')
        }
        setCertPendingDoc(null)
      } else {
        toast.success('Certificado agregado exitosamente')
      }
      setCertForm(EMPTY_CERT)
      setIsCertDialogOpen(false)
    },
    onError: () => toast.error('Error al agregar certificado'),
  })

  const cursoMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => createCurso(data),
    onSuccess: async () => {
      invalidateAll()
      if (cursoPendingDoc) {
        try {
          await subirDocumento(empleadoId, cursoPendingDoc.tipo, 'academico', cursoPendingDoc.label, cursoPendingDoc.file)
          toast.success('Curso y documento guardados')
        } catch {
          toast.warning('Curso guardado. Error al subir documento — puede subirlo luego.')
        }
        setCursoPendingDoc(null)
      } else {
        toast.success('Curso agregado exitosamente')
      }
      setCursoForm(EMPTY_CURSO)
      setIsCursoDialogOpen(false)
    },
    onError: () => toast.error('Error al agregar curso'),
  })

  const deleteCursoMutation = useMutation({
    mutationFn: (id: number) => deleteCurso(id),
    onSuccess: () => {
      invalidateAll()
      toast.success('Curso eliminado')
    },
    onError: () => toast.error('Error al eliminar curso'),
  })

  const tituloMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => createAcademico(data),
    onSuccess: async () => {
      invalidateAll()
      if (tituloPendingDoc) {
        try {
          await subirDocumento(empleadoId, tituloPendingDoc.tipo, 'academico', tituloPendingDoc.label, tituloPendingDoc.file)
          toast.success('Titulo y documento guardados')
        } catch {
          toast.warning('Titulo guardado. Error al subir documento — puede subirlo luego.')
        }
        setTituloPendingDoc(null)
      } else {
        toast.success('Titulo agregado exitosamente')
      }
      setTituloForm(EMPTY_TITULO)
      setIsTituloDialogOpen(false)
    },
    onError: () => toast.error('Error al agregar titulo'),
  })

  const handleUploadSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
    queryClient.invalidateQueries({ queryKey: ['legajo-docs', empleadoId] })
  }

  // Cert dialog handlers
  const handleCertFileSelected = (file: File) => {
    setCertStagedFile(file)
    setIsCertPreviewOpen(true)
  }
  const handleCertPreviewConfirm = () => {
    if (certStagedFile) setCertPendingDoc({ file: certStagedFile, tipo: 'certificado_estudios', label: 'Certificado de estudios' })
    setCertStagedFile(null)
    setIsCertPreviewOpen(false)
  }
  const handleCertPreviewCancel = () => {
    setCertStagedFile(null)
    setIsCertPreviewOpen(false)
  }
  const handleCertDialogClose = () => {
    setCertPendingDoc(null)
    setCertStagedFile(null)
    setIsCertPreviewOpen(false)
    setCertForm(EMPTY_CERT)
    setIsCertDialogOpen(false)
  }

  // Curso dialog handlers
  const handleCursoFileSelected = (file: File) => {
    setCursoStagedFile(file)
    setIsCursoPreviewOpen(true)
  }
  const handleCursoPreviewConfirm = () => {
    if (cursoStagedFile) setCursoPendingDoc({ file: cursoStagedFile, tipo: 'certificado_capacitacion', label: 'Certificado del curso' })
    setCursoStagedFile(null)
    setIsCursoPreviewOpen(false)
  }
  const handleCursoPreviewCancel = () => {
    setCursoStagedFile(null)
    setIsCursoPreviewOpen(false)
  }
  const handleCursoDialogClose = () => {
    setCursoPendingDoc(null)
    setCursoStagedFile(null)
    setIsCursoPreviewOpen(false)
    setCursoForm(EMPTY_CURSO)
    setIsCursoDialogOpen(false)
  }

  // Titulo dialog handlers
  const handleTituloFileSelected = (file: File) => {
    setTituloStagedFile(file)
    setIsTituloPreviewOpen(true)
  }
  const handleTituloPreviewConfirm = () => {
    if (tituloStagedFile) setTituloPendingDoc({ file: tituloStagedFile, tipo: 'titulo_profesional', label: 'Titulo / Diploma' })
    setTituloStagedFile(null)
    setIsTituloPreviewOpen(false)
  }
  const handleTituloPreviewCancel = () => {
    setTituloStagedFile(null)
    setIsTituloPreviewOpen(false)
  }
  const handleTituloDialogClose = () => {
    setTituloPendingDoc(null)
    setTituloStagedFile(null)
    setIsTituloPreviewOpen(false)
    setTituloForm(EMPTY_TITULO)
    setIsTituloDialogOpen(false)
  }

  return (
    <div className="space-y-4">
      <Accordion type="multiple" className="w-full">

        {/* --- Certificados de Estudio --- */}
        <AccordionItem value="certificados">
          <AccordionTrigger>
            <div className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Certificados de Estudio
              {certificados.length > 0 && (
                <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">
                  {certificados.length}
                </span>
              )}
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-3">
              {certificados.length === 0 && (
                <p className="text-sm text-muted-foreground">No ha agregado certificados aun.</p>
              )}
              {certificados.map((cert: Record<string, unknown>) => (
                <Card key={cert.id as string} className="border">
                  <CardHeader className="pb-2">
                    <p className="font-medium text-sm">{cert.institucion as string}</p>
                    <p className="text-xs text-muted-foreground capitalize">
                      {cert.nivel_educativo as string}
                      {cert.fecha_fin ? ` · Egreso: ${cert.fecha_fin as string}` : ''}
                    </p>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <DocumentUploadZone
                      tipoDocumento="certificado_estudios"
                      label="Certificado de estudios (PDF)"
                      empleadoId={empleadoId}
                      onUploadSuccess={handleUploadSuccess}
                    />
                  </CardContent>
                </Card>
              ))}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsCertDialogOpen(true)}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Agregar certificado
              </Button>
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* --- Cursos y Diplomados --- */}
        <AccordionItem value="cursos">
          <AccordionTrigger>
            <div className="flex items-center gap-2">
              <Award className="h-4 w-4" />
              Cursos y Diplomados
              {(cursos as Record<string, unknown>[]).length > 0 && (
                <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">
                  {(cursos as Record<string, unknown>[]).length}
                </span>
              )}
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-3">
              {(cursos as Record<string, unknown>[]).length === 0 && (
                <p className="text-sm text-muted-foreground">No ha agregado cursos aun.</p>
              )}
              {(cursos as Record<string, unknown>[]).map((curso: Record<string, unknown>) => (
                <Card key={curso.id as string} className="border">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">{curso.nombre_curso as string}</p>
                        <p className="text-xs text-muted-foreground">
                          {curso.institucion as string}
                          {curso.horas ? ` · ${curso.horas as number} horas` : ''}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-destructive hover:text-destructive"
                        onClick={() => deleteCursoMutation.mutate(curso.id as string)}
                        disabled={deleteCursoMutation.isPending}
                      >
                        <span className="sr-only">Eliminar</span>
                        &times;
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <DocumentUploadZone
                      tipoDocumento="certificado_capacitacion"
                      label="Certificado del curso (PDF)"
                      empleadoId={empleadoId}
                      onUploadSuccess={handleUploadSuccess}
                    />
                  </CardContent>
                </Card>
              ))}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsCursoDialogOpen(true)}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Agregar curso
              </Button>
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* --- Titulos Profesionales --- */}
        <AccordionItem value="titulos">
          <AccordionTrigger>
            <div className="flex items-center gap-2">
              <GraduationCap className="h-4 w-4" />
              Titulos Profesionales
              {titulos.length > 0 && (
                <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">
                  {titulos.length}
                </span>
              )}
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-3">
              {titulos.length === 0 && (
                <p className="text-sm text-muted-foreground">No ha agregado titulos aun.</p>
              )}
              {titulos.map((titulo: Record<string, unknown>) => (
                <Card key={titulo.id as string} className="border">
                  <CardHeader className="pb-2">
                    <p className="font-medium text-sm">{(titulo.carrera as string | undefined) ?? (titulo.institucion as string)}</p>
                    <p className="text-xs text-muted-foreground capitalize">
                      {titulo.nivel_educativo as string} · {titulo.institucion as string}
                    </p>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <DocumentUploadZone
                      tipoDocumento="titulo_profesional"
                      label="Titulo profesional (PDF)"
                      empleadoId={empleadoId}
                      onUploadSuccess={handleUploadSuccess}
                    />
                  </CardContent>
                </Card>
              ))}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsTituloDialogOpen(true)}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Agregar titulo
              </Button>
            </div>
          </AccordionContent>
        </AccordionItem>

      </Accordion>

      {/* Certificado Dialog */}
      <Dialog open={isCertDialogOpen} onOpenChange={(open) => { if (!open) handleCertDialogClose() }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Agregar certificado de estudio</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label htmlFor="cert-institucion">Institucion *</Label>
              <Input
                id="cert-institucion"
                value={certForm.institucion}
                onChange={(e) => setCertForm(f => ({ ...f, institucion: e.target.value }))}
                placeholder="Nombre de la institucion"
              />
            </div>
            <div>
              <Label htmlFor="cert-nivel">Nivel educativo *</Label>
              <Select
                value={certForm.nivel_educativo}
                onValueChange={(val) => setCertForm(f => ({ ...f, nivel_educativo: val }))}
              >
                <SelectTrigger id="cert-nivel">
                  <SelectValue placeholder="Seleccionar nivel" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="secundaria">Secundaria</SelectItem>
                  <SelectItem value="tecnico">Tecnico</SelectItem>
                  <SelectItem value="universitario">Universitario</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="cert-inicio">Fecha inicio</Label>
                <Input
                  id="cert-inicio"
                  type="date"
                  value={certForm.fecha_inicio}
                  onChange={(e) => setCertForm(f => ({ ...f, fecha_inicio: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="cert-fin">Fecha fin</Label>
                <Input
                  id="cert-fin"
                  type="date"
                  value={certForm.fecha_fin}
                  onChange={(e) => setCertForm(f => ({ ...f, fecha_fin: e.target.value }))}
                />
              </div>
            </div>
            {/* Documento (opcional) */}
            <div className="space-y-1">
              <Label className="text-sm font-medium">Documento (opcional)</Label>
              {certPendingDoc ? (
                <div className="flex items-center gap-2 rounded border border-primary/30 bg-primary/5 px-3 py-2">
                  <span className="flex-1 text-xs truncate">{certPendingDoc.file.name}</span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-5 w-5 p-0"
                    onClick={() => setCertPendingDoc(null)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              ) : (
                <CompactDropZone
                  onFileSelected={handleCertFileSelected}
                  disabled={certMutation.isPending}
                />
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={handleCertDialogClose}>
              Cancelar
            </Button>
            <Button
              onClick={() => {
                if (!certForm.institucion || !certForm.nivel_educativo) {
                  toast.error('Complete los campos requeridos')
                  return
                }
                certMutation.mutate({
                  empleado: empleadoId,
                  institucion: certForm.institucion,
                  nivel_educativo: certForm.nivel_educativo,
                  fecha_inicio: certForm.fecha_inicio || null,
                  fecha_fin: certForm.fecha_fin || null,
                })
              }}
              disabled={certMutation.isPending}
            >
              {certMutation.isPending ? 'Guardando...' : 'Guardar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Curso Dialog */}
      <Dialog open={isCursoDialogOpen} onOpenChange={(open) => { if (!open) handleCursoDialogClose() }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Agregar curso o diplomado</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label htmlFor="curso-nombre">Nombre del curso *</Label>
              <Input
                id="curso-nombre"
                value={cursoForm.nombre_curso}
                onChange={(e) => setCursoForm(f => ({ ...f, nombre_curso: e.target.value }))}
                placeholder="Nombre del curso"
              />
            </div>
            <div>
              <Label htmlFor="curso-inst">Institucion *</Label>
              <Input
                id="curso-inst"
                value={cursoForm.institucion}
                onChange={(e) => setCursoForm(f => ({ ...f, institucion: e.target.value }))}
                placeholder="Institucion organizadora"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="curso-inicio">Fecha inicio</Label>
                <Input
                  id="curso-inicio"
                  type="date"
                  value={cursoForm.fecha_inicio}
                  onChange={(e) => setCursoForm(f => ({ ...f, fecha_inicio: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="curso-fin">Fecha fin</Label>
                <Input
                  id="curso-fin"
                  type="date"
                  value={cursoForm.fecha_fin}
                  onChange={(e) => setCursoForm(f => ({ ...f, fecha_fin: e.target.value }))}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="curso-horas">Horas</Label>
              <Input
                id="curso-horas"
                type="number"
                min="1"
                value={cursoForm.horas}
                onChange={(e) => setCursoForm(f => ({ ...f, horas: e.target.value }))}
                placeholder="Numero de horas"
              />
            </div>
            {/* Documento (opcional) */}
            <div className="space-y-1">
              <Label className="text-sm font-medium">Documento (opcional)</Label>
              {cursoPendingDoc ? (
                <div className="flex items-center gap-2 rounded border border-primary/30 bg-primary/5 px-3 py-2">
                  <span className="flex-1 text-xs truncate">{cursoPendingDoc.file.name}</span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-5 w-5 p-0"
                    onClick={() => setCursoPendingDoc(null)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              ) : (
                <CompactDropZone
                  onFileSelected={handleCursoFileSelected}
                  disabled={cursoMutation.isPending}
                />
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={handleCursoDialogClose}>
              Cancelar
            </Button>
            <Button
              onClick={() => {
                if (!cursoForm.nombre_curso || !cursoForm.institucion) {
                  toast.error('Complete los campos requeridos')
                  return
                }
                cursoMutation.mutate({
                  empleado: empleadoId,
                  nombre_curso: cursoForm.nombre_curso,
                  institucion: cursoForm.institucion,
                  fecha_inicio: cursoForm.fecha_inicio || null,
                  fecha_fin: cursoForm.fecha_fin || null,
                  horas: cursoForm.horas ? parseInt(cursoForm.horas, 10) : null,
                })
              }}
              disabled={cursoMutation.isPending}
            >
              {cursoMutation.isPending ? 'Guardando...' : 'Guardar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Titulo Dialog */}
      <Dialog open={isTituloDialogOpen} onOpenChange={(open) => { if (!open) handleTituloDialogClose() }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Agregar titulo profesional</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label htmlFor="titulo-carrera">Carrera *</Label>
              <Input
                id="titulo-carrera"
                value={tituloForm.carrera}
                onChange={(e) => setTituloForm(f => ({ ...f, carrera: e.target.value }))}
                placeholder="Nombre de la carrera"
              />
            </div>
            <div>
              <Label htmlFor="titulo-inst">Institucion *</Label>
              <Input
                id="titulo-inst"
                value={tituloForm.institucion}
                onChange={(e) => setTituloForm(f => ({ ...f, institucion: e.target.value }))}
                placeholder="Universidad o instituto"
              />
            </div>
            <div>
              <Label htmlFor="titulo-nivel">Nivel *</Label>
              <Select
                value={tituloForm.nivel_educativo}
                onValueChange={(val) => setTituloForm(f => ({ ...f, nivel_educativo: val }))}
              >
                <SelectTrigger id="titulo-nivel">
                  <SelectValue placeholder="Seleccionar nivel" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="bachiller">Bachiller</SelectItem>
                  <SelectItem value="titulo_profesional">Titulo profesional</SelectItem>
                  <SelectItem value="maestria">Maestria</SelectItem>
                  <SelectItem value="doctorado">Doctorado</SelectItem>
                  <SelectItem value="especializacion">Especializacion</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="titulo-inicio">Fecha inicio</Label>
                <Input
                  id="titulo-inicio"
                  type="date"
                  value={tituloForm.fecha_inicio}
                  onChange={(e) => setTituloForm(f => ({ ...f, fecha_inicio: e.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="titulo-fin">Fecha fin</Label>
                <Input
                  id="titulo-fin"
                  type="date"
                  value={tituloForm.fecha_fin}
                  onChange={(e) => setTituloForm(f => ({ ...f, fecha_fin: e.target.value }))}
                />
              </div>
            </div>
            {/* Documento (opcional) */}
            <div className="space-y-1">
              <Label className="text-sm font-medium">Documento (opcional)</Label>
              {tituloPendingDoc ? (
                <div className="flex items-center gap-2 rounded border border-primary/30 bg-primary/5 px-3 py-2">
                  <span className="flex-1 text-xs truncate">{tituloPendingDoc.file.name}</span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-5 w-5 p-0"
                    onClick={() => setTituloPendingDoc(null)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              ) : (
                <CompactDropZone
                  onFileSelected={handleTituloFileSelected}
                  disabled={tituloMutation.isPending}
                />
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={handleTituloDialogClose}>
              Cancelar
            </Button>
            <Button
              onClick={() => {
                if (!tituloForm.carrera || !tituloForm.institucion || !tituloForm.nivel_educativo) {
                  toast.error('Complete los campos requeridos')
                  return
                }
                tituloMutation.mutate({
                  empleado: empleadoId,
                  carrera: tituloForm.carrera,
                  institucion: tituloForm.institucion,
                  nivel_educativo: tituloForm.nivel_educativo,
                  fecha_inicio: tituloForm.fecha_inicio || null,
                  fecha_fin: tituloForm.fecha_fin || null,
                })
              }}
              disabled={tituloMutation.isPending}
            >
              {tituloMutation.isPending ? 'Guardando...' : 'Guardar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Document Preview Modals (one per dialog type) */}
      <DocumentPreviewModal
        file={certStagedFile}
        archivoUrl={null}
        label="Certificado de estudios"
        isOpen={isCertPreviewOpen}
        onConfirm={handleCertPreviewConfirm}
        onCancel={handleCertPreviewCancel}
      />
      <DocumentPreviewModal
        file={cursoStagedFile}
        archivoUrl={null}
        label="Certificado del curso"
        isOpen={isCursoPreviewOpen}
        onConfirm={handleCursoPreviewConfirm}
        onCancel={handleCursoPreviewCancel}
      />
      <DocumentPreviewModal
        file={tituloStagedFile}
        archivoUrl={null}
        label="Titulo / Diploma"
        isOpen={isTituloPreviewOpen}
        onConfirm={handleTituloPreviewConfirm}
        onCancel={handleTituloPreviewCancel}
      />
    </div>
  )
}
