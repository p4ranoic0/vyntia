import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from '@/components/ui/dialog'
import { useAuth } from '@/hooks/useAuth'
import { legajoService, TIPO_DOCUMENTO_LABELS, CATEGORIA_LABELS } from '@/services/legajoService'
import { onboardingService, getEstadoLabel, type OnboardingStatus } from '@/services/onboardingService'
import {
  CheckCircle2, Circle, Clock, FileText, Upload, XCircle, AlertCircle, ExternalLink,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'

const REQUIRED_DOCS = [
  { grupo: 'Personal', items: [
    { tipo: 'dni', categoria: 'personal', label: 'Copia de DNI' },
    { tipo: 'declaracion_jurada', categoria: 'legal', label: 'Declaraciones Juradas firmadas' },
  ]},
  { grupo: 'Académico', items: [
    { tipo: 'certificado_estudios', categoria: 'academico', label: 'Certificados de estudios' },
    { tipo: 'titulo_profesional', categoria: 'academico', label: 'Título profesional' },
  ]},
  { grupo: 'Laboral', items: [
    { tipo: 'certificado_trabajo', categoria: 'laboral', label: 'Certificados de trabajo anteriores' },
  ]},
  { grupo: 'Familiar', items: [
    { tipo: 'dni_familiar', categoria: 'familiar', label: 'DNI de familiares directos' },
    { tipo: 'acta_matrimonio', categoria: 'familiar', label: 'Acta de matrimonio (si aplica)' },
  ]},
]

export default function OnboardingPage() {
  const { user } = useAuth()
  const [onboarding, setOnboarding] = useState<OnboardingStatus | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [uploadDocType, setUploadDocType] = useState('')
  const [uploadCategory, setUploadCategory] = useState('')
  const [uploadLabel, setUploadLabel] = useState('')

  const empleadoId = user?.empleado?.id ?? user?.empleado_id ?? null

  const fetchOnboarding = async () => {
    try {
      setIsLoading(true)
      const data = await onboardingService.getMiOnboarding()
      setOnboarding(data)
    } catch {
      setError('No tiene un proceso de onboarding activo')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchOnboarding()
  }, [])

  const handleUploadClick = (tipo: string, categoria: string, label: string) => {
    setUploadDocType(tipo)
    setUploadCategory(categoria)
    setUploadLabel(label)
    setUploadOpen(true)
  }

  const getStepStatus = (completed: boolean) => {
    if (completed) return { icon: <CheckCircle2 className="h-5 w-5 text-green-600" />, color: 'text-green-600' }
    return { icon: <Circle className="h-5 w-5 text-muted-foreground" />, color: 'text-muted-foreground' }
  }

  const getEstadoBadge = (estado: string) => {
    switch (estado) {
      case 'completado': return <Badge className="bg-green-600">Completado</Badge>
      case 'observado': return <Badge variant="destructive">Observado</Badge>
      case 'pendiente_validacion': return <Badge className="bg-blue-600">En Validacion</Badge>
      default: return <Badge variant="secondary">{getEstadoLabel(estado)}</Badge>
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
      </div>
    )
  }

  if (error || !onboarding) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4">
        <AlertCircle className="h-12 w-12 text-muted-foreground" />
        <h2 className="text-xl font-semibold">{error || 'No se encontro proceso de onboarding'}</h2>
        <Button asChild variant="outline">
          <Link to="/">Ir al Inicio</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Mi Incorporacion</h1>
        <p className="text-muted-foreground">Complete los pasos para finalizar su proceso de ingreso</p>
      </div>

      {/* Status and Progress */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Estado actual</p>
              <div className="mt-1">{getEstadoBadge(onboarding.estado_onboarding)}</div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Progreso</p>
              <div className="flex items-center gap-3 mt-1">
                <div className="w-48 h-3 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all"
                    style={{ width: `${onboarding.progreso_porcentaje}%` }}
                  />
                </div>
                <span className="text-sm font-semibold">{onboarding.progreso_porcentaje}%</span>
              </div>
            </div>
          </div>
          {onboarding.observaciones && onboarding.estado_onboarding === 'observado' && (
            <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
              <p className="text-sm font-medium text-destructive">Observaciones de RRHH:</p>
              <p className="text-sm mt-1">{onboarding.observaciones}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Step 1: Personal Data */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            {getStepStatus(onboarding.datos_personales_completos).icon}
            <div>
              <CardTitle className="text-base">Paso 1: Datos Personales</CardTitle>
              <CardDescription>Complete su informacion personal</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Button asChild variant={onboarding.datos_personales_completos ? 'outline' : 'default'} size="sm">
              <Link to="/empleados/datos-personales">
                <ExternalLink className="h-4 w-4 mr-2" />
                {onboarding.datos_personales_completos ? 'Revisar Datos' : 'Completar Datos'}
              </Link>
            </Button>
            {onboarding.datos_personales_completos && (
              <span className="text-sm text-green-600 font-medium">Completado</span>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Step 2: Labor Data */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            {getStepStatus(onboarding.datos_laborales_completos).icon}
            <div>
              <CardTitle className="text-base">Paso 2: Datos Laborales</CardTitle>
              <CardDescription>Registre su información de contrato y cargo</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Button asChild variant={onboarding.datos_laborales_completos ? 'outline' : 'default'} size="sm">
              <Link to="/empleados/datos-laborales">
                <ExternalLink className="h-4 w-4 mr-2" />
                {onboarding.datos_laborales_completos ? 'Revisar Datos' : 'Completar Datos'}
              </Link>
            </Button>
            {onboarding.datos_laborales_completos && (
              <span className="text-sm text-green-600 font-medium">Completado</span>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Step 3: Upload Documents */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            {getStepStatus(
              onboarding.dni_subido &&
              onboarding.declaraciones_juradas_subidas &&
              onboarding.certificados_academicos_subidos &&
              onboarding.certificados_trabajo_subidos &&
              onboarding.documentos_familiares_subidos
            ).icon}
            <div>
              <CardTitle className="text-base">Paso 3: Documentos del Legajo</CardTitle>
              <CardDescription>Suba los documentos requeridos para su legajo digital</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {REQUIRED_DOCS.map((grupo) => (
            <div key={grupo.grupo}>
              <h4 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wider">
                {grupo.grupo}
              </h4>
              <div className="space-y-2">
                {grupo.items.map((item) => {
                  const isPending = onboarding.documentos_pendientes?.some(
                    (d) => d.tipo_documento === item.tipo && d.categoria === item.categoria
                  )
                  return (
                    <div
                      key={`${item.tipo}-${item.categoria}-${item.label}`}
                      className="flex items-center justify-between p-3 rounded-lg border"
                    >
                      <div className="flex items-center gap-3">
                        {isPending ? (
                          <Clock className="h-4 w-4 text-amber-500" />
                        ) : (
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                        )}
                        <span className="text-sm">{item.label}</span>
                      </div>
                      <Button
                        variant={isPending ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => handleUploadClick(item.tipo, item.categoria, item.label)}
                      >
                        <Upload className="h-4 w-4 mr-1" />
                        {isPending ? 'Subir' : 'Resubir'}
                      </Button>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Step 4: Validation */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            {getStepStatus(onboarding.estado_onboarding === 'completado').icon}
            <div>
              <CardTitle className="text-base">Paso 4: Validación por RRHH</CardTitle>
              <CardDescription>
                {onboarding.estado_onboarding === 'completado'
                  ? 'Su informacion ha sido validada'
                  : onboarding.estado_onboarding === 'pendiente_validacion'
                  ? 'Sus documentos estan siendo revisados por RRHH'
                  : 'Complete los pasos anteriores para iniciar la validacion'
                }
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        {onboarding.fecha_validacion && (
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Validado el {new Date(onboarding.fecha_validacion).toLocaleDateString('es-PE')}
            </p>
          </CardContent>
        )}
      </Card>

      {/* Upload Dialog */}
      {uploadOpen && empleadoId && (
        <UploadDocDialog
          open={uploadOpen}
          empleadoId={empleadoId}
          tipoDocumento={uploadDocType}
          categoria={uploadCategory}
          label={uploadLabel}
          onClose={() => setUploadOpen(false)}
          onSuccess={() => {
            setUploadOpen(false)
            fetchOnboarding()
          }}
        />
      )}
    </div>
  )
}

function UploadDocDialog({
  open, empleadoId, tipoDocumento, categoria, label, onClose, onSuccess,
}: {
  open: boolean
  empleadoId: number
  tipoDocumento: string
  categoria: string
  label: string
  onClose: () => void
  onSuccess: () => void
}) {
  const [file, setFile] = useState<File | null>(null)
  const [nombreDocumento, setNombreDocumento] = useState(label)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      toast.error('Seleccione un archivo')
      return
    }
    setSubmitting(true)
    try {
      await legajoService.create({
        empleado: empleadoId,
        tipo_documento: tipoDocumento,
        categoria,
        nombre_documento: nombreDocumento,
        archivo: file,
        estado_documento: 'pendiente_revision',
        nivel_acceso: 'restringido',
      })
      toast.success('Documento subido exitosamente')
      onSuccess()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al subir documento')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Subir: {label}</DialogTitle>
          <DialogDescription>
            Suba un archivo escaneado en formato PDF, JPG o PNG.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Nombre del documento</Label>
            <Input value={nombreDocumento} onChange={(e) => setNombreDocumento(e.target.value)} />
          </div>
          <div>
            <Label>Archivo</Label>
            <Input
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={submitting}>
              Cancelar
            </Button>
            <Button type="submit" disabled={submitting || !file}>
              {submitting ? 'Subiendo...' : 'Subir Documento'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
