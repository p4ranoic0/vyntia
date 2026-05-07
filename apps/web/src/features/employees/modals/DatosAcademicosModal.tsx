'use client'

import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog'
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
import { Textarea } from '@/shared/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'
import { LoadingSpinner } from '@/shared/ui/loading-spinner'
import { Alert, AlertDescription } from '@/shared/ui/alert'
import { toast } from 'sonner'
import { GraduationCap, BookOpen, Award, Plus, Trash2, Calendar, Building, Lock, AlertCircle, Edit, Save, X } from 'lucide-react'
import { employeesService, type DatosAcademicos } from '@/services/employeesService'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useEmployeePermissions } from '@/hooks/useEmployeePermissions'

interface EstudioAcademico {
  id: number
  institucion: string
  nivel_educativo: string
  carrera_especialidad: string
  estado: string
  fecha_inicio: string
  fecha_fin?: string
  titulo_obtenido?: string
  numero_titulo?: string
  observaciones?: string
}

interface Certificacion {
  id: number
  nombre: string
  institucion_emisora: string
  fecha_obtencion: string
  fecha_vencimiento?: string
  numero_certificado?: string
  nivel?: string
  horas_academicas?: number
  observaciones?: string
}

interface Idioma {
  id: number
  idioma: string
  nivel_oral: string
  nivel_escrito: string
  nivel_lectura: string
  certificacion?: string
  institucion_certificadora?: string
  fecha_certificacion?: string
  observaciones?: string
}

interface DatosAcademicosModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  empleadoId: number
  isReadOnly?: boolean
  title?: string
}

export function DatosAcademicosModal({
  open,
  onOpenChange,
  empleadoId,
  isReadOnly = false,
  title = 'Datos Académicos'
}: DatosAcademicosModalProps) {
  const { user } = useAuth()
  const { 
    canEditEmployeeData, 
    canAccessEmployeeData, 
    getViewMode,
    currentEmployeeId,
    isEmployee
  } = useEmployeePermissions()
  
  const [datos, setDatos] = useState<DatosAcademicos | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [accessDenied, setAccessDenied] = useState(false)
  
  // Determinar el modo de visualización basado en permisos
  const viewMode = getViewMode(empleadoId, 'academic')
  const effectiveReadOnly = isReadOnly || viewMode === 'readonly'
  const [isEditing, setIsEditing] = useState(!effectiveReadOnly)

  // Cargar datos cuando se abre el modal
  useEffect(() => {
    if (open && empleadoId) {
      checkAccessAndLoadDatos()
    }
  }, [open, empleadoId])

  const checkAccessAndLoadDatos = async () => {
    try {
      setLoading(true)
      
      // Verificar permisos de acceso
      if (!canAccessEmployeeData(empleadoId)) {
        setAccessDenied(true)
        return
      }
      
      const response = await employeesService.datosAcademicos.get(empleadoId)
      setDatos(response)
      setAccessDenied(false)
    } catch (error) {
      console.error('Error loading academic data:', error)
      toast.error('Error al cargar los datos académicos')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!datos) return
    
    // Verificar permisos antes de guardar
    if (!canEditEmployeeData(empleadoId, 'academic')) {
      toast.error('No tienes permisos para editar estos datos')
      return
    }
    
    setSaving(true)
    try {
      await employeesService.datosAcademicos.update(empleadoId, datos)
      toast.success('Datos académicos actualizados correctamente')
      setIsEditing(false)
    } catch (error) {
      console.error('Error saving academic data:', error)
      toast.error('Error al guardar los datos académicos')
    } finally {
      setSaving(false)
    }
  }

  const handleEdit = () => {
    if (canEditEmployeeData(empleadoId, 'academic')) {
      setIsEditing(true)
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
    checkAccessAndLoadDatos() // Recargar datos originales
  }

  const handleAddEstudio = () => {
    if (!datos || !canEditEmployeeData(empleadoId, 'academic')) return
    const newEstudio: EstudioAcademico = {
      id: Date.now(),
      institucion: '',
      nivel_educativo: '',
      carrera_especialidad: '',
      estado: 'en_curso',
      fecha_inicio: ''
    }
    setDatos({
      ...datos,
      estudios_academicos: [...datos.estudios_academicos, newEstudio]
    })
  }

  const handleDeleteEstudio = (id: number) => {
    if (!datos || !canEditEmployeeData(empleadoId, 'academic')) return
    setDatos({
      ...datos,
      estudios_academicos: datos.estudios_academicos.filter(e => e.id !== id)
    })
  }

  const handleUpdateEstudio = (id: number, field: keyof EstudioAcademico, value: string) => {
    if (!datos) return
    setDatos({
      ...datos,
      estudios_academicos: datos.estudios_academicos.map(e => 
        e.id === id ? { ...e, [field]: value } : e
      )
    })
  }

  const handleAddCertificacion = () => {
    if (!datos || !canEditEmployeeData(empleadoId, 'academic')) return
    const newCertificacion: Certificacion = {
      id: Date.now(),
      nombre: '',
      institucion_emisora: '',
      fecha_obtencion: ''
    }
    setDatos({
      ...datos,
      certificaciones: [...datos.certificaciones, newCertificacion]
    })
  }

  const handleDeleteCertificacion = (id: number) => {
    if (!datos || !canEditEmployeeData(empleadoId, 'academic')) return
    setDatos({
      ...datos,
      certificaciones: datos.certificaciones.filter(c => c.id !== id)
    })
  }

  const handleUpdateCertificacion = (id: number, field: keyof Certificacion, value: string | number) => {
    if (!datos) return
    setDatos({
      ...datos,
      certificaciones: datos.certificaciones.map(c => 
        c.id === id ? { ...c, [field]: value } : c
      )
    })
  }

  const handleAddIdioma = () => {
    if (!datos || !canEditEmployeeData(empleadoId, 'academic')) return
    const newIdioma: Idioma = {
      id: Date.now(),
      idioma: '',
      nivel_oral: '',
      nivel_escrito: '',
      nivel_lectura: ''
    }
    setDatos({
      ...datos,
      idiomas: [...datos.idiomas, newIdioma]
    })
  }

  const handleDeleteIdioma = (id: number) => {
    if (!datos || !canEditEmployeeData(empleadoId, 'academic')) return
    setDatos({
      ...datos,
      idiomas: datos.idiomas.filter(i => i.id !== id)
    })
  }

  const handleUpdateIdioma = (id: number, field: keyof Idioma, value: string) => {
    if (!datos) return
    setDatos({
      ...datos,
      idiomas: datos.idiomas.map(i => 
        i.id === id ? { ...i, [field]: value } : i
      )
    })
  }

  // Mostrar mensaje de acceso denegado
  if (accessDenied) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-yellow-500" />
              Acceso Denegado
            </DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <Alert>
              <Lock className="h-4 w-4" />
              <AlertDescription>
                No tienes permisos para acceder a estos datos académicos.
                {isEmployee && empleadoId !== currentEmployeeId && 
                  ' Solo puedes ver tus propios datos académicos.'}
              </AlertDescription>
            </Alert>
          </div>
          <div className="flex justify-end">
            <Button onClick={() => onOpenChange(false)} variant="outline">
              Cerrar
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  if (loading) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-6xl max-h-[80vh] overflow-y-auto">
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner size="lg" />
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <GraduationCap className="h-5 w-5" />
            {title}
            {effectiveReadOnly && <Badge variant="secondary">Solo lectura</Badge>}
            {empleadoId === currentEmployeeId && <Badge variant="outline">Mis datos</Badge>}
          </DialogTitle>
          <DialogDescription>
            {effectiveReadOnly 
              ? 'Visualización de información académica del empleado'
              : 'Gestión de información académica del empleado'
            }
          </DialogDescription>
        </DialogHeader>

        {datos && (
          <div className="space-y-6">
            {/* Estudios Académicos */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-4 w-4" />
                    Estudios Académicos ({datos.estudios_academicos.length})
                  </CardTitle>
                  {!effectiveReadOnly && canEditEmployeeData(empleadoId, 'academic') && (
                    <Button onClick={handleAddEstudio} size="sm">
                      <Plus className="h-4 w-4 mr-2" />
                      Agregar Estudio
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {datos.estudios_academicos.map((estudio) => (
                    <div key={estudio.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h4 className="font-medium">{estudio.carrera_especialidad || 'Sin especificar'}</h4>
                          <p className="text-sm text-muted-foreground">
                            {estudio.institucion} • {estudio.nivel_educativo}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant={estudio.estado === 'completado' ? 'default' : 'secondary'}>
                            {estudio.estado === 'completado' ? 'Completado' : 
                             estudio.estado === 'en_curso' ? 'En Curso' : 'Trunco'}
                          </Badge>
                          {!effectiveReadOnly && canEditEmployeeData(empleadoId, 'academic') && isEditing && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteEstudio(estudio.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                      
                      {isEditing && !isReadOnly ? (
                        <div className="grid gap-4 md:grid-cols-2">
                          <div className="space-y-2">
                            <Label>Institución</Label>
                            <Input
                              value={estudio.institucion}
                              onChange={(e) => handleUpdateEstudio(estudio.id, 'institucion', e.target.value)}
                              placeholder="Nombre de la institución"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Nivel Educativo</Label>
                            <Select
                              value={estudio.nivel_educativo}
                              onValueChange={(value) => handleUpdateEstudio(estudio.id, 'nivel_educativo', value)}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="Seleccionar nivel" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="primaria">Primaria</SelectItem>
                                <SelectItem value="secundaria">Secundaria</SelectItem>
                                <SelectItem value="tecnico">Técnico</SelectItem>
                                <SelectItem value="universitario">Universitario</SelectItem>
                                <SelectItem value="postgrado">Postgrado</SelectItem>
                                <SelectItem value="maestria">Maestría</SelectItem>
                                <SelectItem value="doctorado">Doctorado</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label>Carrera/Especialidad</Label>
                            <Input
                              value={estudio.carrera_especialidad}
                              onChange={(e) => handleUpdateEstudio(estudio.id, 'carrera_especialidad', e.target.value)}
                              placeholder="Nombre de la carrera"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Estado</Label>
                            <Select
                              value={estudio.estado}
                              onValueChange={(value) => handleUpdateEstudio(estudio.id, 'estado', value)}
                            >
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="en_curso">En Curso</SelectItem>
                                <SelectItem value="completado">Completado</SelectItem>
                                <SelectItem value="trunco">Trunco</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label>Fecha Inicio</Label>
                            <Input
                              type="date"
                              value={estudio.fecha_inicio}
                              onChange={(e) => handleUpdateEstudio(estudio.id, 'fecha_inicio', e.target.value)}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Fecha Fin</Label>
                            <Input
                              type="date"
                              value={estudio.fecha_fin || ''}
                              onChange={(e) => handleUpdateEstudio(estudio.id, 'fecha_fin', e.target.value)}
                            />
                          </div>
                          {estudio.estado === 'completado' && (
                            <>
                              <div className="space-y-2">
                                <Label>Título Obtenido</Label>
                                <Input
                                  value={estudio.titulo_obtenido || ''}
                                  onChange={(e) => handleUpdateEstudio(estudio.id, 'titulo_obtenido', e.target.value)}
                                  placeholder="Título obtenido"
                                />
                              </div>
                              <div className="space-y-2">
                                <Label>Número de Título</Label>
                                <Input
                                  value={estudio.numero_titulo || ''}
                                  onChange={(e) => handleUpdateEstudio(estudio.id, 'numero_titulo', e.target.value)}
                                  placeholder="Número del título"
                                />
                              </div>
                            </>
                          )}
                          <div className="space-y-2 md:col-span-2">
                            <Label>Observaciones</Label>
                            <Textarea
                              value={estudio.observaciones || ''}
                              onChange={(e) => handleUpdateEstudio(estudio.id, 'observaciones', e.target.value)}
                              placeholder="Observaciones adicionales..."
                              rows={2}
                            />
                          </div>
                        </div>
                      ) : (
                        <div className="grid gap-2 md:grid-cols-3 text-sm">
                          <div>
                            <span className="font-medium">Período:</span>
                            <br />
                            {estudio.fecha_inicio} {estudio.fecha_fin && `- ${estudio.fecha_fin}`}
                          </div>
                          {estudio.titulo_obtenido && (
                            <div>
                              <span className="font-medium">Título:</span>
                              <br />
                              {estudio.titulo_obtenido}
                            </div>
                          )}
                          {estudio.numero_titulo && (
                            <div>
                              <span className="font-medium">N° Título:</span>
                              <br />
                              {estudio.numero_titulo}
                            </div>
                          )}
                          {estudio.observaciones && (
                            <div className="md:col-span-3">
                              <span className="font-medium">Observaciones:</span>
                              <br />
                              {estudio.observaciones}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                  {datos.estudios_academicos.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      No hay estudios académicos registrados
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Certificaciones */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Award className="h-4 w-4" />
                    Certificaciones ({datos.certificaciones.length})
                  </CardTitle>
                  {!effectiveReadOnly && canEditEmployeeData(empleadoId, 'academic') && (
                    <Button onClick={handleAddCertificacion} size="sm">
                      <Plus className="h-4 w-4 mr-2" />
                      Agregar Certificación
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {datos.certificaciones.map((cert) => (
                    <div key={cert.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h4 className="font-medium">{cert.nombre || 'Sin especificar'}</h4>
                          <p className="text-sm text-muted-foreground">
                            {cert.institucion_emisora}
                          </p>
                        </div>
                        {!effectiveReadOnly && canEditEmployeeData(empleadoId, 'academic') && isEditing && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteCertificacion(cert.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                      
                      {isEditing && !isReadOnly ? (
                        <div className="grid gap-4 md:grid-cols-2">
                          <div className="space-y-2">
                            <Label>Nombre de la Certificación</Label>
                            <Input
                              value={cert.nombre}
                              onChange={(e) => handleUpdateCertificacion(cert.id, 'nombre', e.target.value)}
                              placeholder="Nombre de la certificación"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Institución Emisora</Label>
                            <Input
                              value={cert.institucion_emisora}
                              onChange={(e) => handleUpdateCertificacion(cert.id, 'institucion_emisora', e.target.value)}
                              placeholder="Institución que emite"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Fecha de Obtención</Label>
                            <Input
                              type="date"
                              value={cert.fecha_obtencion}
                              onChange={(e) => handleUpdateCertificacion(cert.id, 'fecha_obtencion', e.target.value)}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Fecha de Vencimiento</Label>
                            <Input
                              type="date"
                              value={cert.fecha_vencimiento || ''}
                              onChange={(e) => handleUpdateCertificacion(cert.id, 'fecha_vencimiento', e.target.value)}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Número de Certificado</Label>
                            <Input
                              value={cert.numero_certificado || ''}
                              onChange={(e) => handleUpdateCertificacion(cert.id, 'numero_certificado', e.target.value)}
                              placeholder="Número del certificado"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Horas Académicas</Label>
                            <Input
                              type="number"
                              value={cert.horas_academicas || ''}
                              onChange={(e) => handleUpdateCertificacion(cert.id, 'horas_academicas', parseInt(e.target.value))}
                              placeholder="Número de horas"
                            />
                          </div>
                        </div>
                      ) : (
                        <div className="grid gap-2 md:grid-cols-3 text-sm">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            <span className="font-medium">Obtenido:</span> {cert.fecha_obtencion}
                          </div>
                          {cert.fecha_vencimiento && (
                            <div className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              <span className="font-medium">Vence:</span> {cert.fecha_vencimiento}
                            </div>
                          )}
                          {cert.horas_academicas && (
                            <div>
                              <span className="font-medium">Horas:</span> {cert.horas_academicas}h
                            </div>
                          )}
                          {cert.numero_certificado && (
                            <div>
                              <span className="font-medium">N° Certificado:</span> {cert.numero_certificado}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                  {datos.certificaciones.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      No hay certificaciones registradas
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Idiomas */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Building className="h-4 w-4" />
                    Idiomas ({datos.idiomas.length})
                  </CardTitle>
                  {!effectiveReadOnly && canEditEmployeeData(empleadoId, 'academic') && (
                    <Button onClick={handleAddIdioma} size="sm">
                      <Plus className="h-4 w-4 mr-2" />
                      Agregar Idioma
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {datos.idiomas.map((idioma) => (
                    <div key={idioma.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h4 className="font-medium">{idioma.idioma || 'Sin especificar'}</h4>
                          {idioma.certificacion && (
                            <p className="text-sm text-muted-foreground">
                              Certificación: {idioma.certificacion}
                            </p>
                          )}
                        </div>
                        {!effectiveReadOnly && canEditEmployeeData(empleadoId, 'academic') && isEditing && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteIdioma(idioma.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                      
                      {isEditing && !isReadOnly ? (
                        <div className="grid gap-4 md:grid-cols-2">
                          <div className="space-y-2">
                            <Label>Idioma</Label>
                            <Select
                              value={idioma.idioma}
                              onValueChange={(value) => handleUpdateIdioma(idioma.id, 'idioma', value)}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="Seleccionar idioma" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="español">Español</SelectItem>
                                <SelectItem value="ingles">Inglés</SelectItem>
                                <SelectItem value="frances">Francés</SelectItem>
                                <SelectItem value="portugues">Portugués</SelectItem>
                                <SelectItem value="italiano">Italiano</SelectItem>
                                <SelectItem value="aleman">Alemán</SelectItem>
                                <SelectItem value="chino">Chino</SelectItem>
                                <SelectItem value="japones">Japonés</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label>Nivel Oral</Label>
                            <Select
                              value={idioma.nivel_oral}
                              onValueChange={(value) => handleUpdateIdioma(idioma.id, 'nivel_oral', value)}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="Seleccionar nivel" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="basico">Básico</SelectItem>
                                <SelectItem value="intermedio">Intermedio</SelectItem>
                                <SelectItem value="avanzado">Avanzado</SelectItem>
                                <SelectItem value="nativo">Nativo</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label>Nivel Escrito</Label>
                            <Select
                              value={idioma.nivel_escrito}
                              onValueChange={(value) => handleUpdateIdioma(idioma.id, 'nivel_escrito', value)}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="Seleccionar nivel" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="basico">Básico</SelectItem>
                                <SelectItem value="intermedio">Intermedio</SelectItem>
                                <SelectItem value="avanzado">Avanzado</SelectItem>
                                <SelectItem value="nativo">Nativo</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label>Nivel Lectura</Label>
                            <Select
                              value={idioma.nivel_lectura}
                              onValueChange={(value) => handleUpdateIdioma(idioma.id, 'nivel_lectura', value)}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="Seleccionar nivel" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="basico">Básico</SelectItem>
                                <SelectItem value="intermedio">Intermedio</SelectItem>
                                <SelectItem value="avanzado">Avanzado</SelectItem>
                                <SelectItem value="nativo">Nativo</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                      ) : (
                        <div className="grid gap-2 md:grid-cols-3 text-sm">
                          <div>
                            <span className="font-medium">Oral:</span> {idioma.nivel_oral}
                          </div>
                          <div>
                            <span className="font-medium">Escrito:</span> {idioma.nivel_escrito}
                          </div>
                          <div>
                            <span className="font-medium">Lectura:</span> {idioma.nivel_lectura}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  {datos.idiomas.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      No hay idiomas registrados
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <DialogFooter>
          {!effectiveReadOnly && (
            <>
              {isEditing ? (
                <>
                  <Button variant="outline" onClick={handleCancel} disabled={saving}>
                    <X className="h-4 w-4 mr-2" />
                    Cancelar
                  </Button>
                  <Button onClick={handleSave} disabled={saving}>
                    {saving ? (
                      <>
                        <LoadingSpinner size="sm" className="mr-2" />
                        Guardando...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Guardar Cambios
                      </>
                    )}
                  </Button>
                </>
              ) : (
                canEditEmployeeData(empleadoId, 'academic') && (
                  <Button onClick={handleEdit}>
                    <Edit className="h-4 w-4 mr-2" />
                    Editar
                  </Button>
                )
              )}
            </>
          )}
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cerrar
          </Button>
          
          {/* Información de permisos para empleados */}
          {isEmployee && empleadoId === currentEmployeeId && effectiveReadOnly && (
            <Alert className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Algunos de tus datos académicos solo pueden ser modificados por el área de Recursos Humanos.
                Si necesitas actualizar información, contacta con RRHH.
              </AlertDescription>
            </Alert>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}