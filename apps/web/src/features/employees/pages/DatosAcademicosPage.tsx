import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { employeesService } from '@/features/employees/services/employeesService'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select'
import { Textarea } from '@/shared/ui/textarea'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { toast } from '@/shared/ui/use-toast'
import { GraduationCap, BookOpen, Award, Plus, Trash2 } from 'lucide-react'
import { Badge } from '@/shared/ui/badge'
import EmployeeLayout from '@/shared/layout/EmployeeLayout'

interface FormacionAcademica {
  id: number
  nivel_educativo: string
  institucion: string
  carrera_especialidad: string
  fecha_inicio: string
  fecha_fin?: string
  estado: string
  titulo_obtenido?: string
  numero_titulo?: string
  observaciones?: string
}

interface Certificacion {
  id: number
  nombre_certificacion: string
  institucion_emisora: string
  fecha_obtencion: string
  fecha_vencimiento?: string
  numero_certificado?: string
  estado: string
}

interface Idioma {
  id: number
  idioma: string
  nivel_oral: string
  nivel_escrito: string
  nivel_lectura: string
  certificacion?: string
}

interface DatosAcademicos {
  id: number
  formacion_academica: FormacionAcademica[]
  certificaciones: Certificacion[]
  idiomas: Idioma[]
}

export function DatosAcademicosPage() {
  const { id } = useParams<{ id: string }>()
  const [empleado, setEmpleado] = useState<DatosAcademicos | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [isEditing, setIsEditing] = useState(false)

  useEffect(() => {
    if (!id) return
    const empleadoId = parseInt(id)

    employeesService.datosAcademicos.getAll(empleadoId)
      .then((response: any) => {
        const items = response?.data || response?.results || []
        const records = Array.isArray(items) ? items : []
        const formacion = records.map((r: any) => ({
          id: r.id,
          nivel_educativo: r.nivel_educativo || r.tipo_formacion || '',
          institucion: r.nombre_institucion || '',
          carrera_especialidad: r.carrera_especialidad || '',
          fecha_inicio: r.fecha_inicio_estudios || '',
          fecha_fin: r.fecha_termino_estudios || undefined,
          estado: r.estado_estudios || '',
          titulo_obtenido: r.titulo_obtenido || undefined,
          numero_titulo: undefined,
          observaciones: undefined,
        }))
        setEmpleado({
          id: empleadoId,
          formacion_academica: formacion,
          certificaciones: [],
          idiomas: [],
        })
      })
      .catch(() => {
        setEmpleado({ id: empleadoId, formacion_academica: [], certificaciones: [], idiomas: [] })
      })
      .finally(() => setLoading(false))
  }, [id])

  const handleSave = async () => {
    if (!empleado) return

    setSaving(true)
    try {
      const empleadoId = parseInt(id!)
      await Promise.all(
        empleado.formacion_academica.map((f) =>
          f.id < 1_000_000_000
            ? employeesService.datosAcademicos.update(empleadoId, f.id, {
                nivel_educativo: f.nivel_educativo,
                nombre_institucion: f.institucion,
                carrera_especialidad: f.carrera_especialidad,
                fecha_inicio_estudios: f.fecha_inicio,
                fecha_termino_estudios: f.fecha_fin,
                estado_estudios: f.estado,
                titulo_obtenido: f.titulo_obtenido,
              } as any)
            : employeesService.datosAcademicos.create(empleadoId, {
                nivel_educativo: f.nivel_educativo,
                nombre_institucion: f.institucion,
                carrera_especialidad: f.carrera_especialidad,
                fecha_inicio_estudios: f.fecha_inicio,
                fecha_termino_estudios: f.fecha_fin,
                estado_estudios: f.estado,
                titulo_obtenido: f.titulo_obtenido,
              } as any)
        )
      )
      toast({
        title: 'Datos guardados',
        description: 'Los datos académicos han sido actualizados correctamente.',
      })
      setIsEditing(false)
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudieron guardar los datos. Inténtalo de nuevo.',
        variant: 'destructive',
      })
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
  }

  const agregarFormacion = () => {
    if (!empleado) return
    const nuevaFormacion: FormacionAcademica = {
      id: Date.now(),
      nivel_educativo: '',
      institucion: '',
      carrera_especialidad: '',
      fecha_inicio: '',
      estado: 'En curso'
    }
    setEmpleado({
      ...empleado,
      formacion_academica: [...empleado.formacion_academica, nuevaFormacion]
    })
  }

  const eliminarFormacion = (id: number) => {
    if (!empleado) return
    setEmpleado({
      ...empleado,
      formacion_academica: empleado.formacion_academica.filter(f => f.id !== id)
    })
  }

  const agregarCertificacion = () => {
    if (!empleado) return
    const nuevaCertificacion: Certificacion = {
      id: Date.now(),
      nombre_certificacion: '',
      institucion_emisora: '',
      fecha_obtencion: '',
      estado: 'Vigente'
    }
    setEmpleado({
      ...empleado,
      certificaciones: [...empleado.certificaciones, nuevaCertificacion]
    })
  }

  const eliminarCertificacion = (id: number) => {
    if (!empleado) return
    setEmpleado({
      ...empleado,
      certificaciones: empleado.certificaciones.filter(c => c.id !== id)
    })
  }

  const agregarIdioma = () => {
    if (!empleado) return
    const nuevoIdioma: Idioma = {
      id: Date.now(),
      idioma: '',
      nivel_oral: 'Básico',
      nivel_escrito: 'Básico',
      nivel_lectura: 'Básico'
    }
    setEmpleado({
      ...empleado,
      idiomas: [...empleado.idiomas, nuevoIdioma]
    })
  }

  const eliminarIdioma = (id: number) => {
    if (!empleado) return
    setEmpleado({
      ...empleado,
      idiomas: empleado.idiomas.filter(i => i.id !== id)
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  if (!empleado) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">No se encontraron datos académicos del empleado.</p>
      </div>
    )
  }

  return (
    <EmployeeLayout 
      title="Datos Académicos" 
      description="Formación académica, certificaciones e idiomas del empleado"
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-end">
          <div className="flex gap-2">
          {isEditing ? (
            <>
              <Button variant="outline" onClick={handleCancel} disabled={saving}>
                Cancelar
              </Button>
              <Button onClick={handleSave} disabled={saving}>
                {saving ? 'Guardando...' : 'Guardar'}
              </Button>
            </>
          ) : (
            <Button onClick={() => setIsEditing(true)}>
              <GraduationCap className="w-4 h-4 mr-2" />
              Editar
            </Button>
          )}
          </div>
        </div>

      {/* Formación Académica */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <GraduationCap className="w-5 h-5" />
                Formación Académica
              </CardTitle>
              <CardDescription>
                Estudios realizados y títulos obtenidos
              </CardDescription>
            </div>
            {isEditing && (
              <Button onClick={agregarFormacion} size="sm">
                <Plus className="w-4 h-4 mr-2" />
                Agregar
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {empleado.formacion_academica.map((formacion, index) => (
            <div key={formacion.id} className="border rounded-lg p-4 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium">Formación {index + 1}</h4>
                {isEditing && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => eliminarFormacion(formacion.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Nivel Educativo</Label>
                  <Select
                    value={formacion.nivel_educativo}
                    onValueChange={(value) => {
                      const nuevaFormacion = empleado.formacion_academica.map(f => 
                        f.id === formacion.id ? { ...f, nivel_educativo: value } : f
                      )
                      setEmpleado({ ...empleado, formacion_academica: nuevaFormacion })
                    }}
                    disabled={!isEditing}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Primaria">Primaria</SelectItem>
                      <SelectItem value="Secundaria">Secundaria</SelectItem>
                      <SelectItem value="Técnico">Técnico</SelectItem>
                      <SelectItem value="Universitario">Universitario</SelectItem>
                      <SelectItem value="Postgrado">Postgrado</SelectItem>
                      <SelectItem value="Maestría">Maestría</SelectItem>
                      <SelectItem value="Doctorado">Doctorado</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Institución</Label>
                  <Input
                    value={formacion.institucion}
                    onChange={(e) => {
                      const nuevaFormacion = empleado.formacion_academica.map(f => 
                        f.id === formacion.id ? { ...f, institucion: e.target.value } : f
                      )
                      setEmpleado({ ...empleado, formacion_academica: nuevaFormacion })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Carrera/Especialidad</Label>
                  <Input
                    value={formacion.carrera_especialidad}
                    onChange={(e) => {
                      const nuevaFormacion = empleado.formacion_academica.map(f => 
                        f.id === formacion.id ? { ...f, carrera_especialidad: e.target.value } : f
                      )
                      setEmpleado({ ...empleado, formacion_academica: nuevaFormacion })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Estado</Label>
                  <Select
                    value={formacion.estado}
                    onValueChange={(value) => {
                      const nuevaFormacion = empleado.formacion_academica.map(f => 
                        f.id === formacion.id ? { ...f, estado: value } : f
                      )
                      setEmpleado({ ...empleado, formacion_academica: nuevaFormacion })
                    }}
                    disabled={!isEditing}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="En curso">En curso</SelectItem>
                      <SelectItem value="Completo">Completo</SelectItem>
                      <SelectItem value="Incompleto">Incompleto</SelectItem>
                      <SelectItem value="Abandonado">Abandonado</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Fecha de Inicio</Label>
                  <Input
                    type="date"
                    value={formacion.fecha_inicio}
                    onChange={(e) => {
                      const nuevaFormacion = empleado.formacion_academica.map(f => 
                        f.id === formacion.id ? { ...f, fecha_inicio: e.target.value } : f
                      )
                      setEmpleado({ ...empleado, formacion_academica: nuevaFormacion })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Fecha de Fin</Label>
                  <Input
                    type="date"
                    value={formacion.fecha_fin || ''}
                    onChange={(e) => {
                      const nuevaFormacion = empleado.formacion_academica.map(f => 
                        f.id === formacion.id ? { ...f, fecha_fin: e.target.value || undefined } : f
                      )
                      setEmpleado({ ...empleado, formacion_academica: nuevaFormacion })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Título Obtenido</Label>
                  <Input
                    value={formacion.titulo_obtenido || ''}
                    onChange={(e) => {
                      const nuevaFormacion = empleado.formacion_academica.map(f => 
                        f.id === formacion.id ? { ...f, titulo_obtenido: e.target.value || undefined } : f
                      )
                      setEmpleado({ ...empleado, formacion_academica: nuevaFormacion })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Número de Título</Label>
                  <Input
                    value={formacion.numero_titulo || ''}
                    onChange={(e) => {
                      const nuevaFormacion = empleado.formacion_academica.map(f => 
                        f.id === formacion.id ? { ...f, numero_titulo: e.target.value || undefined } : f
                      )
                      setEmpleado({ ...empleado, formacion_academica: nuevaFormacion })
                    }}
                    disabled={!isEditing}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Observaciones</Label>
                <Textarea
                  value={formacion.observaciones || ''}
                  onChange={(e) => {
                    const nuevaFormacion = empleado.formacion_academica.map(f => 
                      f.id === formacion.id ? { ...f, observaciones: e.target.value || undefined } : f
                    )
                    setEmpleado({ ...empleado, formacion_academica: nuevaFormacion })
                  }}
                  disabled={!isEditing}
                  rows={2}
                />
              </div>
            </div>
          ))}
          {empleado.formacion_academica.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No hay formación académica registrada
            </div>
          )}
        </CardContent>
      </Card>

      {/* Certificaciones */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Award className="w-5 h-5" />
                Certificaciones
              </CardTitle>
              <CardDescription>
                Certificaciones profesionales y técnicas
              </CardDescription>
            </div>
            {isEditing && (
              <Button onClick={agregarCertificacion} size="sm">
                <Plus className="w-4 h-4 mr-2" />
                Agregar
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {empleado.certificaciones.map((cert, index) => (
            <div key={cert.id} className="border rounded-lg p-4 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium">Certificación {index + 1}</h4>
                {isEditing && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => eliminarCertificacion(cert.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Nombre de la Certificación</Label>
                  <Input
                    value={cert.nombre_certificacion}
                    onChange={(e) => {
                      const nuevasCert = empleado.certificaciones.map(c => 
                        c.id === cert.id ? { ...c, nombre_certificacion: e.target.value } : c
                      )
                      setEmpleado({ ...empleado, certificaciones: nuevasCert })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Institución Emisora</Label>
                  <Input
                    value={cert.institucion_emisora}
                    onChange={(e) => {
                      const nuevasCert = empleado.certificaciones.map(c => 
                        c.id === cert.id ? { ...c, institucion_emisora: e.target.value } : c
                      )
                      setEmpleado({ ...empleado, certificaciones: nuevasCert })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Fecha de Obtención</Label>
                  <Input
                    type="date"
                    value={cert.fecha_obtencion}
                    onChange={(e) => {
                      const nuevasCert = empleado.certificaciones.map(c => 
                        c.id === cert.id ? { ...c, fecha_obtencion: e.target.value } : c
                      )
                      setEmpleado({ ...empleado, certificaciones: nuevasCert })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Fecha de Vencimiento</Label>
                  <Input
                    type="date"
                    value={cert.fecha_vencimiento || ''}
                    onChange={(e) => {
                      const nuevasCert = empleado.certificaciones.map(c => 
                        c.id === cert.id ? { ...c, fecha_vencimiento: e.target.value || undefined } : c
                      )
                      setEmpleado({ ...empleado, certificaciones: nuevasCert })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Número de Certificado</Label>
                  <Input
                    value={cert.numero_certificado || ''}
                    onChange={(e) => {
                      const nuevasCert = empleado.certificaciones.map(c => 
                        c.id === cert.id ? { ...c, numero_certificado: e.target.value || undefined } : c
                      )
                      setEmpleado({ ...empleado, certificaciones: nuevasCert })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Estado</Label>
                  <Select
                    value={cert.estado}
                    onValueChange={(value) => {
                      const nuevasCert = empleado.certificaciones.map(c => 
                        c.id === cert.id ? { ...c, estado: value } : c
                      )
                      setEmpleado({ ...empleado, certificaciones: nuevasCert })
                    }}
                    disabled={!isEditing}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Vigente">Vigente</SelectItem>
                      <SelectItem value="Vencido">Vencido</SelectItem>
                      <SelectItem value="En proceso">En proceso</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          ))}
          {empleado.certificaciones.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No hay certificaciones registradas
            </div>
          )}
        </CardContent>
      </Card>

      {/* Idiomas */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="w-5 h-5" />
                Idiomas
              </CardTitle>
              <CardDescription>
                Conocimientos de idiomas y niveles de competencia
              </CardDescription>
            </div>
            {isEditing && (
              <Button onClick={agregarIdioma} size="sm">
                <Plus className="w-4 h-4 mr-2" />
                Agregar
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {empleado.idiomas.map((idioma, index) => (
            <div key={idioma.id} className="border rounded-lg p-4 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium">Idioma {index + 1}</h4>
                {isEditing && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => eliminarIdioma(idioma.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Idioma</Label>
                  <Input
                    value={idioma.idioma}
                    onChange={(e) => {
                      const nuevosIdiomas = empleado.idiomas.map(i => 
                        i.id === idioma.id ? { ...i, idioma: e.target.value } : i
                      )
                      setEmpleado({ ...empleado, idiomas: nuevosIdiomas })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Certificación</Label>
                  <Input
                    value={idioma.certificacion || ''}
                    onChange={(e) => {
                      const nuevosIdiomas = empleado.idiomas.map(i => 
                        i.id === idioma.id ? { ...i, certificacion: e.target.value || undefined } : i
                      )
                      setEmpleado({ ...empleado, idiomas: nuevosIdiomas })
                    }}
                    disabled={!isEditing}
                    placeholder="Ej: TOEFL, IELTS, etc."
                  />
                </div>
                <div className="space-y-2">
                  <Label>Nivel Oral</Label>
                  <Select
                    value={idioma.nivel_oral}
                    onValueChange={(value) => {
                      const nuevosIdiomas = empleado.idiomas.map(i => 
                        i.id === idioma.id ? { ...i, nivel_oral: value } : i
                      )
                      setEmpleado({ ...empleado, idiomas: nuevosIdiomas })
                    }}
                    disabled={!isEditing}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Básico">Básico</SelectItem>
                      <SelectItem value="Intermedio">Intermedio</SelectItem>
                      <SelectItem value="Avanzado">Avanzado</SelectItem>
                      <SelectItem value="Nativo">Nativo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Nivel Escrito</Label>
                  <Select
                    value={idioma.nivel_escrito}
                    onValueChange={(value) => {
                      const nuevosIdiomas = empleado.idiomas.map(i => 
                        i.id === idioma.id ? { ...i, nivel_escrito: value } : i
                      )
                      setEmpleado({ ...empleado, idiomas: nuevosIdiomas })
                    }}
                    disabled={!isEditing}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Básico">Básico</SelectItem>
                      <SelectItem value="Intermedio">Intermedio</SelectItem>
                      <SelectItem value="Avanzado">Avanzado</SelectItem>
                      <SelectItem value="Nativo">Nativo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Nivel de Lectura</Label>
                  <Select
                    value={idioma.nivel_lectura}
                    onValueChange={(value) => {
                      const nuevosIdiomas = empleado.idiomas.map(i => 
                        i.id === idioma.id ? { ...i, nivel_lectura: value } : i
                      )
                      setEmpleado({ ...empleado, idiomas: nuevosIdiomas })
                    }}
                    disabled={!isEditing}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Básico">Básico</SelectItem>
                      <SelectItem value="Intermedio">Intermedio</SelectItem>
                      <SelectItem value="Avanzado">Avanzado</SelectItem>
                      <SelectItem value="Nativo">Nativo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          ))}
          {empleado.idiomas.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No hay idiomas registrados
            </div>
          )}
        </CardContent>
      </Card>
      </div>
    </EmployeeLayout>
  )
}

export default DatosAcademicosPage