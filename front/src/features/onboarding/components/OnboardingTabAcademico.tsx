import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Plus, BookOpen, GraduationCap, Award } from 'lucide-react'
import { Button } from '@/components/ui/button'
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
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { DocumentUploadZone } from './DocumentUploadZone'
import {
  getAcademicos,
  createAcademico,
  getCursos,
  createCurso,
  deleteCurso,
} from '../services/onboardingDataService'

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

export function OnboardingTabAcademico({ empleadoId }: OnboardingTabAcademicoProps) {
  const queryClient = useQueryClient()

  const [isCertDialogOpen, setIsCertDialogOpen] = useState(false)
  const [isCursoDialogOpen, setIsCursoDialogOpen] = useState(false)
  const [isTituloDialogOpen, setIsTituloDialogOpen] = useState(false)

  const [certForm, setCertForm] = useState<CertificadoForm>(EMPTY_CERT)
  const [cursoForm, setCursoForm] = useState<CursoForm>(EMPTY_CURSO)
  const [tituloForm, setTituloForm] = useState<TituloForm>(EMPTY_TITULO)

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
  }

  const certMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => createAcademico(data),
    onSuccess: () => {
      invalidateAll()
      toast.success('Certificado agregado exitosamente')
      setCertForm(EMPTY_CERT)
      setIsCertDialogOpen(false)
    },
    onError: () => toast.error('Error al agregar certificado'),
  })

  const cursoMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => createCurso(data),
    onSuccess: () => {
      invalidateAll()
      toast.success('Curso agregado exitosamente')
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
    onSuccess: () => {
      invalidateAll()
      toast.success('Titulo agregado exitosamente')
      setTituloForm(EMPTY_TITULO)
      setIsTituloDialogOpen(false)
    },
    onError: () => toast.error('Error al agregar titulo'),
  })

  const handleUploadSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
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
                <Card key={cert.academico_id as number} className="border">
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
                <Card key={curso.curso_id as number} className="border">
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
                        onClick={() => deleteCursoMutation.mutate(curso.curso_id as number)}
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
                <Card key={titulo.academico_id as number} className="border">
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
      <Dialog open={isCertDialogOpen} onOpenChange={setIsCertDialogOpen}>
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
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setIsCertDialogOpen(false); setCertForm(EMPTY_CERT) }}>
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
      <Dialog open={isCursoDialogOpen} onOpenChange={setIsCursoDialogOpen}>
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
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setIsCursoDialogOpen(false); setCursoForm(EMPTY_CURSO) }}>
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
      <Dialog open={isTituloDialogOpen} onOpenChange={setIsTituloDialogOpen}>
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
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setIsTituloDialogOpen(false); setTituloForm(EMPTY_TITULO) }}>
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
    </div>
  )
}
