import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from '@/shared/ui/accordion'
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
import { employeesService } from '@/services/employeesService'
import { Documento, legajoService } from '@/services/legajoService'
import { Award, BookOpen, Edit, GraduationCap, Plus, Trash2 } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { AdminDocUpload } from './AdminDocUpload'

const NIVEL_EDUCATIVO_OPTIONS = [
  { value: 'PRIMARIA', label: 'Primaria' },
  { value: 'SECUNDARIA', label: 'Secundaria' },
  { value: 'TECNICO', label: 'Tecnico' },
  { value: 'UNIVERSITARIO', label: 'Universitario' },
  { value: 'POSTGRADO', label: 'Postgrado' },
  { value: 'MAESTRIA', label: 'Maestria' },
  { value: 'DOCTORADO', label: 'Doctorado' },
]

const ACADEMICO_EMPTY = {
  nivel_educativo: '',
  nombre_institucion: '',
  nombre_carrera: '',
  fecha_inicio: '',
  fecha_fin: '',
  estado_estudios: 'CONCLUIDO',
}

interface TabAcademicosProps {
  empleadoId: string
}

export function TabAcademicos({ empleadoId }: TabAcademicosProps) {
  const [academicos, setAcademicos] = useState<any[]>([])
  const [editingId, setEditingId] = useState<number | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ ...ACADEMICO_EMPTY })
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)
  const [acadDocs, setAcadDocs] = useState<Documento[]>([])

  const reload = useCallback(() => {
    setFetching(true)
    employeesService.datosAcademicos.getAll(empleadoId).then((data: any) => {
      const raw = data?.data?.results ?? data?.results ?? data?.data ?? data
      setAcademicos(Array.isArray(raw) ? raw : [])
    }).catch(() => setAcademicos([])).finally(() => setFetching(false))
  }, [empleadoId])

  const loadDocs = useCallback(() => {
    legajoService.getByEmpleado(empleadoId, 'academico').then(docs => {
      setAcadDocs(docs)
    }).catch(() => setAcadDocs([]))
    // Also load capacitacion docs
    legajoService.getByEmpleado(empleadoId, 'capacitacion').then(docs => {
      setAcadDocs(prev => [...prev, ...docs])
    }).catch(() => {/* silent */})
  }, [empleadoId])

  useEffect(() => { reload(); loadDocs() }, [reload, loadDocs])

  const startEdit = (acad: any) => {
    setEditingId(acad.id)
    setFormData({
      nivel_educativo: acad.nivel_educativo || '',
      nombre_institucion: acad.nombre_institucion || '',
      nombre_carrera: acad.nombre_carrera || '',
      fecha_inicio: acad.fecha_inicio || '',
      fecha_fin: acad.fecha_fin || '',
      estado_estudios: acad.estado_estudios || 'CONCLUIDO',
    })
    setShowForm(true)
  }

  const startNew = () => {
    setEditingId(null)
    setFormData({ ...ACADEMICO_EMPTY })
    setShowForm(true)
  }

  const handleSave = async () => {
    if (!formData.nivel_educativo || !formData.nombre_institucion) {
      toast.error('Nivel educativo e institución son obligatorios')
      return
    }
    setLoading(true)
    try {
      if (editingId) {
        await employeesService.datosAcademicos.update(empleadoId, editingId, formData as any)
        toast.success('Formacion actualizada')
      } else {
        await employeesService.datosAcademicos.create(empleadoId, formData as any)
        toast.success('Formacion agregada')
      }
      setShowForm(false)
      reload()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al guardar')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!globalThis.confirm('¿Eliminar este registro academico?')) return
    try {
      await employeesService.datosAcademicos.delete(empleadoId, id)
      toast.success('Registro eliminado')
      reload()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al eliminar')
    }
  }

  // Helper: find matching doc by tipo and institution/name hint
  const findDoc = (tipo: string, nameHint?: string) => {
    return acadDocs.find(d =>
      d.tipo_documento === tipo &&
      (!nameHint || (d.nombre_documento || '').toLowerCase().includes(nameHint.toLowerCase().slice(0, 8)))
    ) || null
  }

  if (fetching) return <div className="py-8 text-center text-sm text-muted-foreground">Cargando...</div>

  // Classify academicos
  const certificados = academicos.filter(a =>
    ['PRIMARIA', 'SECUNDARIA', 'TECNICO', 'UNIVERSITARIO'].includes(a.nivel_educativo)
  )
  const postgrados = academicos.filter(a =>
    ['POSTGRADO', 'MAESTRIA', 'DOCTORADO'].includes(a.nivel_educativo)
  )

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">{academicos.length} registro(s) academico(s)</p>
        <Button size="sm" variant="outline" onClick={startNew}>
          <Plus className="h-4 w-4 mr-1" /> Agregar
        </Button>
      </div>

      <Accordion type="multiple" defaultValue={['certificados', 'titulos', 'docs']} className="space-y-2">
        {/* Certificados y Estudios */}
        <AccordionItem value="certificados" className="border rounded-md">
          <AccordionTrigger className="px-3 py-2 hover:no-underline">
            <div className="flex items-center gap-2 text-sm font-medium">
              <BookOpen className="h-4 w-4" />
              Certificados de Estudios ({certificados.length})
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-3 pb-3">
            {certificados.length === 0 ? (
              <p className="text-xs text-muted-foreground py-2">Sin registros</p>
            ) : (
              <div className="space-y-2">
                {certificados.map((acad: any) => {
                  const acadId = acad.id
                  const existingDoc = findDoc('certificado_estudios', acad.nombre_institucion)
                  return (
                    <div key={acadId} className="border rounded p-2 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium">{acad.nivel_educativo} — {acad.nombre_institucion}</p>
                          <p className="text-xs text-muted-foreground">
                            {acad.nombre_carrera || ''} {acad.fecha_inicio && acad.fecha_fin ? `(${acad.fecha_inicio} - ${acad.fecha_fin})` : ''}
                          </p>
                        </div>
                        <div className="flex gap-1">
                          <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => startEdit(acad)}>
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button size="icon" variant="ghost" className="h-7 w-7 text-destructive" onClick={() => handleDelete(acadId)}>
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                      <AdminDocUpload
                        empleadoId={empleadoId}
                        tipoDocumento="certificado_estudios"
                        categoria="academico"
                        label={`Certificado - ${acad.nombre_institucion}`}
                        existing={existingDoc ? {
                          documento_id: existingDoc.id,
                          nombre_documento: existingDoc.nombre_documento,
                          archivo: existingDoc.archivo,
                        } : null}
                        onUploaded={loadDocs}
                        onDeleted={loadDocs}
                        compact
                      />
                    </div>
                  )
                })}
              </div>
            )}
          </AccordionContent>
        </AccordionItem>

        {/* Títulos profesionales / Posgrados */}
        <AccordionItem value="titulos" className="border rounded-md">
          <AccordionTrigger className="px-3 py-2 hover:no-underline">
            <div className="flex items-center gap-2 text-sm font-medium">
              <GraduationCap className="h-4 w-4" />
              Titulos Profesionales y Posgrados ({postgrados.length})
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-3 pb-3">
            {postgrados.length === 0 ? (
              <p className="text-xs text-muted-foreground py-2">Sin registros</p>
            ) : (
              <div className="space-y-2">
                {postgrados.map((acad: any) => {
                  const acadId = acad.id
                  const existingDoc = findDoc('titulo_profesional', acad.nombre_institucion)
                  return (
                    <div key={acadId} className="border rounded p-2 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium">{acad.nivel_educativo} — {acad.nombre_institucion}</p>
                          <p className="text-xs text-muted-foreground">
                            {acad.nombre_carrera || ''} {acad.fecha_inicio && acad.fecha_fin ? `(${acad.fecha_inicio} - ${acad.fecha_fin})` : ''}
                          </p>
                        </div>
                        <div className="flex gap-1">
                          <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => startEdit(acad)}>
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button size="icon" variant="ghost" className="h-7 w-7 text-destructive" onClick={() => handleDelete(acadId)}>
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                      <AdminDocUpload
                        empleadoId={empleadoId}
                        tipoDocumento="titulo_profesional"
                        categoria="academico"
                        label={`Titulo - ${acad.nombre_carrera || acad.nombre_institucion}`}
                        existing={existingDoc ? {
                          documento_id: existingDoc.id,
                          nombre_documento: existingDoc.nombre_documento,
                          archivo: existingDoc.archivo,
                        } : null}
                        onUploaded={loadDocs}
                        onDeleted={loadDocs}
                        compact
                      />
                    </div>
                  )
                })}
              </div>
            )}
          </AccordionContent>
        </AccordionItem>

        {/* Capacitaciones / Cursos -- upload zone */}
        <AccordionItem value="docs" className="border rounded-md">
          <AccordionTrigger className="px-3 py-2 hover:no-underline">
            <div className="flex items-center gap-2 text-sm font-medium">
              <Award className="h-4 w-4" />
              Capacitaciones y Cursos
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-3 pb-3">
            {/* List existing capacitacion docs */}
            {acadDocs.some(d => d.tipo_documento === 'certificado_capacitacion') && (
              <div className="space-y-1.5 mb-3">
                {acadDocs.filter(d => d.tipo_documento === 'certificado_capacitacion').map(doc => (
                  <AdminDocUpload
                    key={doc.id}
                    empleadoId={empleadoId}
                    tipoDocumento="certificado_capacitacion"
                    categoria="capacitacion"
                    label={doc.nombre_documento}
                    existing={{
                      documento_id: doc.id,
                      nombre_documento: doc.nombre_documento,
                      archivo: doc.archivo,
                    }}
                    onUploaded={loadDocs}
                    onDeleted={loadDocs}
                    compact
                  />
                ))}
              </div>
            )}
            <AdminDocUpload
              empleadoId={empleadoId}
              tipoDocumento="certificado_capacitacion"
              categoria="capacitacion"
              label="Nuevo certificado de capacitacion"
              onUploaded={loadDocs}
              compact
            />
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      {showForm && (
        <div className="border rounded-md p-3 space-y-3 bg-muted/20">
          <p className="text-sm font-medium">{editingId ? 'Editar formacion' : 'Nueva formacion'}</p>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label>Nivel Educativo <span className="text-destructive">*</span></Label>
              <Select value={formData.nivel_educativo} onValueChange={v => setFormData(s => ({ ...s, nivel_educativo: v }))}>
                <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
                <SelectContent>
                  {NIVEL_EDUCATIVO_OPTIONS.map(o => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label>Estado</Label>
              <Select value={formData.estado_estudios} onValueChange={v => setFormData(s => ({ ...s, estado_estudios: v }))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="EN_CURSO">En curso</SelectItem>
                  <SelectItem value="CONCLUIDO">Concluido</SelectItem>
                  <SelectItem value="INCOMPLETO">Incompleto</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5 col-span-2">
              <Label>Institucion <span className="text-destructive">*</span></Label>
              <Input value={formData.nombre_institucion} onChange={e => setFormData(s => ({ ...s, nombre_institucion: e.target.value }))} placeholder="UNMSM, PUCP, Senati..." />
            </div>
            <div className="grid gap-1.5 col-span-2">
              <Label>Carrera / Titulo Obtenido</Label>
              <Input value={formData.nombre_carrera} onChange={e => setFormData(s => ({ ...s, nombre_carrera: e.target.value }))} placeholder="Administracion de Empresas" />
            </div>
            <div className="grid gap-1.5">
              <Label>Fecha de Inicio</Label>
              <Input type="date" value={formData.fecha_inicio} onChange={e => setFormData(s => ({ ...s, fecha_inicio: e.target.value }))} />
            </div>
            <div className="grid gap-1.5">
              <Label>Fecha de Fin</Label>
              <Input type="date" value={formData.fecha_fin} onChange={e => setFormData(s => ({ ...s, fecha_fin: e.target.value }))} />
            </div>
          </div>
          <div className="flex gap-2 justify-end pt-1">
            <Button size="sm" variant="outline" onClick={() => setShowForm(false)}>Cancelar</Button>
            <Button size="sm" onClick={handleSave} disabled={loading}>
              {loading ? 'Guardando...' : 'Guardar'}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
