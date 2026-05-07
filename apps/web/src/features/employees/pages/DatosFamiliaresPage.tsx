import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { employeesService } from '@/services/employeesService'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select'
import { Textarea } from '@/shared/ui/textarea'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { toast } from '@/shared/ui/use-toast'
import { Users, Heart, Baby, Plus, Trash2, Phone, MapPin } from 'lucide-react'
import { Badge } from '@/shared/ui/badge'
import EmployeeLayout from '@/components/layout/EmployeeLayout'

interface Familiar {
  id: number
  nombres: string
  apellidos: string
  tipo_documento: string
  numero_documento: string
  parentesco: string
  fecha_nacimiento: string
  genero: string
  estado_civil: string
  ocupacion?: string
  telefono?: string
  email?: string
  direccion?: string
  es_beneficiario: boolean
  es_contacto_emergencia: boolean
  observaciones?: string
}

interface ContactoEmergencia {
  id: number
  nombres: string
  apellidos: string
  parentesco: string
  telefono_principal: string
  telefono_secundario?: string
  direccion: string
  es_principal: boolean
}

interface DatosFamiliares {
  id: number
  estado_civil: string
  numero_hijos: number
  familiares: Familiar[]
  contactos_emergencia: ContactoEmergencia[]
  observaciones_generales?: string
}

export function DatosFamiliaresPage() {
  const { id } = useParams<{ id: string }>()
  const [empleado, setEmpleado] = useState<DatosFamiliares | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [isEditing, setIsEditing] = useState(false)

  useEffect(() => {
    if (!id) return
    const empleadoId = parseInt(id)

    employeesService.datosFamiliares.getAll(empleadoId)
      .then((response: any) => {
        const items = response?.data || response?.results || []
        const records = Array.isArray(items) ? items : []
        const familiares = records.map((r: any) => ({
          id: r.id,
          nombres: r.nombres_familiar || '',
          apellidos: [r.apellido_paterno, r.apellido_materno].filter(Boolean).join(' '),
          tipo_documento: r.tipo_documento || 'DNI',
          numero_documento: r.numero_documento || '',
          parentesco: r.parentesco || '',
          fecha_nacimiento: r.fecha_nacimiento || '',
          genero: r.genero_familiar || '',
          estado_civil: 'Soltero',
          es_beneficiario: r.es_beneficiario || false,
          es_contacto_emergencia: false,
        }))
        setEmpleado({
          id: empleadoId,
          estado_civil: '',
          numero_hijos: 0,
          familiares,
          contactos_emergencia: [],
          observaciones_generales: '',
        })
      })
      .catch(() => {
        setEmpleado({ id: empleadoId, estado_civil: '', numero_hijos: 0, familiares: [], contactos_emergencia: [], observaciones_generales: '' })
      })
      .finally(() => setLoading(false))
  }, [id])

  const handleSave = async () => {
    if (!empleado) return

    setSaving(true)
    try {
      const empleadoId = parseInt(id!)
      await Promise.all(
        empleado.familiares.map((f) =>
          f.id < 1_000_000_000
            ? employeesService.datosFamiliares.update(empleadoId, f.id, {
                nombres_familiar: f.nombres,
                parentesco: f.parentesco,
                tipo_documento: f.tipo_documento,
                numero_documento: f.numero_documento,
                fecha_nacimiento: f.fecha_nacimiento,
                genero_familiar: f.genero,
                es_beneficiario: f.es_beneficiario,
              } as any)
            : employeesService.datosFamiliares.create(empleadoId, {
                nombres_familiar: f.nombres,
                parentesco: f.parentesco,
                tipo_documento: f.tipo_documento,
                numero_documento: f.numero_documento,
                fecha_nacimiento: f.fecha_nacimiento,
                genero_familiar: f.genero,
                es_beneficiario: f.es_beneficiario,
              } as any)
        )
      )
      toast({
        title: 'Datos guardados',
        description: 'Los datos familiares han sido actualizados correctamente.',
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

  const agregarFamiliar = () => {
    if (!empleado) return
    const nuevoFamiliar: Familiar = {
      id: Date.now(),
      nombres: '',
      apellidos: '',
      tipo_documento: 'DNI',
      numero_documento: '',
      parentesco: '',
      fecha_nacimiento: '',
      genero: '',
      estado_civil: 'Soltero',
      es_beneficiario: false,
      es_contacto_emergencia: false
    }
    setEmpleado({
      ...empleado,
      familiares: [...empleado.familiares, nuevoFamiliar]
    })
  }

  const eliminarFamiliar = (id: number) => {
    if (!empleado) return
    setEmpleado({
      ...empleado,
      familiares: empleado.familiares.filter(f => f.id !== id)
    })
  }

  const agregarContactoEmergencia = () => {
    if (!empleado) return
    const nuevoContacto: ContactoEmergencia = {
      id: Date.now(),
      nombres: '',
      apellidos: '',
      parentesco: '',
      telefono_principal: '',
      direccion: '',
      es_principal: false
    }
    setEmpleado({
      ...empleado,
      contactos_emergencia: [...empleado.contactos_emergencia, nuevoContacto]
    })
  }

  const eliminarContactoEmergencia = (id: number) => {
    if (!empleado) return
    setEmpleado({
      ...empleado,
      contactos_emergencia: empleado.contactos_emergencia.filter(c => c.id !== id)
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
        <p className="text-muted-foreground">No se encontraron datos familiares del empleado.</p>
      </div>
    )
  }

  return (
    <EmployeeLayout 
      title="Datos Familiares" 
      description="Información familiar y contactos de emergencia del empleado"
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
              <Users className="w-4 h-4 mr-2" />
              Editar
            </Button>
          )}
          </div>
        </div>

        {/* Información General */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="w-5 h-5" />
            Información General
          </CardTitle>
          <CardDescription>
            Datos generales sobre el estado familiar
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="estado_civil">Estado Civil</Label>
              <Select
                value={empleado.estado_civil}
                onValueChange={(value) => setEmpleado({ ...empleado, estado_civil: value })}
                disabled={!isEditing}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Soltero">Soltero(a)</SelectItem>
                  <SelectItem value="Casado">Casado(a)</SelectItem>
                  <SelectItem value="Conviviente">Conviviente</SelectItem>
                  <SelectItem value="Divorciado">Divorciado(a)</SelectItem>
                  <SelectItem value="Viudo">Viudo(a)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="numero_hijos">Número de Hijos</Label>
              <Input
                id="numero_hijos"
                type="number"
                min="0"
                value={empleado.numero_hijos}
                onChange={(e) => setEmpleado({ ...empleado, numero_hijos: parseInt(e.target.value) || 0 })}
                disabled={!isEditing}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Familiares */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                Familiares
              </CardTitle>
              <CardDescription>
                Información de familiares y dependientes
              </CardDescription>
            </div>
            {isEditing && (
              <Button onClick={agregarFamiliar} size="sm">
                <Plus className="w-4 h-4 mr-2" />
                Agregar
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {empleado.familiares.map((familiar, index) => (
            <div key={familiar.id} className="border rounded-lg p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <h4 className="font-medium">Familiar {index + 1}</h4>
                  <div className="flex gap-1">
                    {familiar.es_beneficiario && (
                      <Badge variant="secondary">Beneficiario</Badge>
                    )}
                    {familiar.es_contacto_emergencia && (
                      <Badge variant="outline">Contacto Emergencia</Badge>
                    )}
                  </div>
                </div>
                {isEditing && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => eliminarFamiliar(familiar.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label>Nombres</Label>
                  <Input
                    value={familiar.nombres}
                    onChange={(e) => {
                      const nuevosFamiliares = empleado.familiares.map(f => 
                        f.id === familiar.id ? { ...f, nombres: e.target.value } : f
                      )
                      setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Apellidos</Label>
                  <Input
                    value={familiar.apellidos}
                    onChange={(e) => {
                      const nuevosFamiliares = empleado.familiares.map(f => 
                        f.id === familiar.id ? { ...f, apellidos: e.target.value } : f
                      )
                      setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Parentesco</Label>
                  <Select
                    value={familiar.parentesco}
                    onValueChange={(value) => {
                      const nuevosFamiliares = empleado.familiares.map(f => 
                        f.id === familiar.id ? { ...f, parentesco: value } : f
                      )
                      setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                    }}
                    disabled={!isEditing}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Cónyuge">Cónyuge</SelectItem>
                      <SelectItem value="Conviviente">Conviviente</SelectItem>
                      <SelectItem value="Hijo">Hijo(a)</SelectItem>
                      <SelectItem value="Padre">Padre</SelectItem>
                      <SelectItem value="Madre">Madre</SelectItem>
                      <SelectItem value="Hermano">Hermano(a)</SelectItem>
                      <SelectItem value="Abuelo">Abuelo(a)</SelectItem>
                      <SelectItem value="Tío">Tío(a)</SelectItem>
                      <SelectItem value="Primo">Primo(a)</SelectItem>
                      <SelectItem value="Otro">Otro</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Tipo de Documento</Label>
                  <Select
                    value={familiar.tipo_documento}
                    onValueChange={(value) => {
                      const nuevosFamiliares = empleado.familiares.map(f => 
                        f.id === familiar.id ? { ...f, tipo_documento: value } : f
                      )
                      setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                    }}
                    disabled={!isEditing}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="DNI">DNI</SelectItem>
                      <SelectItem value="Pasaporte">Pasaporte</SelectItem>
                      <SelectItem value="Carnet de Extranjería">Carnet de Extranjería</SelectItem>
                      <SelectItem value="Partida de Nacimiento">Partida de Nacimiento</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Número de Documento</Label>
                  <Input
                    value={familiar.numero_documento}
                    onChange={(e) => {
                      const nuevosFamiliares = empleado.familiares.map(f => 
                        f.id === familiar.id ? { ...f, numero_documento: e.target.value } : f
                      )
                      setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Fecha de Nacimiento</Label>
                  <Input
                    type="date"
                    value={familiar.fecha_nacimiento}
                    onChange={(e) => {
                      const nuevosFamiliares = empleado.familiares.map(f => 
                        f.id === familiar.id ? { ...f, fecha_nacimiento: e.target.value } : f
                      )
                      setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Género</Label>
                  <Select
                    value={familiar.genero}
                    onValueChange={(value) => {
                      const nuevosFamiliares = empleado.familiares.map(f => 
                        f.id === familiar.id ? { ...f, genero: value } : f
                      )
                      setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                    }}
                    disabled={!isEditing}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Masculino">Masculino</SelectItem>
                      <SelectItem value="Femenino">Femenino</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Estado Civil</Label>
                  <Select
                    value={familiar.estado_civil}
                    onValueChange={(value) => {
                      const nuevosFamiliares = empleado.familiares.map(f => 
                        f.id === familiar.id ? { ...f, estado_civil: value } : f
                      )
                      setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                    }}
                    disabled={!isEditing}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Soltero">Soltero(a)</SelectItem>
                      <SelectItem value="Casado">Casado(a)</SelectItem>
                      <SelectItem value="Conviviente">Conviviente</SelectItem>
                      <SelectItem value="Divorciado">Divorciado(a)</SelectItem>
                      <SelectItem value="Viudo">Viudo(a)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Ocupación</Label>
                  <Input
                    value={familiar.ocupacion || ''}
                    onChange={(e) => {
                      const nuevosFamiliares = empleado.familiares.map(f => 
                        f.id === familiar.id ? { ...f, ocupacion: e.target.value || undefined } : f
                      )
                      setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Teléfono</Label>
                  <Input
                    value={familiar.telefono || ''}
                    onChange={(e) => {
                      const nuevosFamiliares = empleado.familiares.map(f => 
                        f.id === familiar.id ? { ...f, telefono: e.target.value || undefined } : f
                      )
                      setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Email</Label>
                  <Input
                    type="email"
                    value={familiar.email || ''}
                    onChange={(e) => {
                      const nuevosFamiliares = empleado.familiares.map(f => 
                        f.id === familiar.id ? { ...f, email: e.target.value || undefined } : f
                      )
                      setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                    }}
                    disabled={!isEditing}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Dirección</Label>
                <Input
                  value={familiar.direccion || ''}
                  onChange={(e) => {
                    const nuevosFamiliares = empleado.familiares.map(f => 
                      f.id === familiar.id ? { ...f, direccion: e.target.value || undefined } : f
                    )
                    setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                  }}
                  disabled={!isEditing}
                />
              </div>
              <div className="flex gap-4">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id={`beneficiario-${familiar.id}`}
                    checked={familiar.es_beneficiario}
                    onChange={(e) => {
                      const nuevosFamiliares = empleado.familiares.map(f => 
                        f.id === familiar.id ? { ...f, es_beneficiario: e.target.checked } : f
                      )
                      setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                    }}
                    disabled={!isEditing}
                  />
                  <Label htmlFor={`beneficiario-${familiar.id}`}>Es beneficiario</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id={`emergencia-${familiar.id}`}
                    checked={familiar.es_contacto_emergencia}
                    onChange={(e) => {
                      const nuevosFamiliares = empleado.familiares.map(f => 
                        f.id === familiar.id ? { ...f, es_contacto_emergencia: e.target.checked } : f
                      )
                      setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                    }}
                    disabled={!isEditing}
                  />
                  <Label htmlFor={`emergencia-${familiar.id}`}>Contacto de emergencia</Label>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Observaciones</Label>
                <Textarea
                  value={familiar.observaciones || ''}
                  onChange={(e) => {
                    const nuevosFamiliares = empleado.familiares.map(f => 
                      f.id === familiar.id ? { ...f, observaciones: e.target.value || undefined } : f
                    )
                    setEmpleado({ ...empleado, familiares: nuevosFamiliares })
                  }}
                  disabled={!isEditing}
                  rows={2}
                />
              </div>
            </div>
          ))}
          {empleado.familiares.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No hay familiares registrados
            </div>
          )}
        </CardContent>
      </Card>

      {/* Contactos de Emergencia */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Phone className="w-5 h-5" />
                Contactos de Emergencia
              </CardTitle>
              <CardDescription>
                Personas a contactar en caso de emergencia
              </CardDescription>
            </div>
            {isEditing && (
              <Button onClick={agregarContactoEmergencia} size="sm">
                <Plus className="w-4 h-4 mr-2" />
                Agregar
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {empleado.contactos_emergencia.map((contacto, index) => (
            <div key={contacto.id} className="border rounded-lg p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <h4 className="font-medium">Contacto {index + 1}</h4>
                  {contacto.es_principal && (
                    <Badge variant="default">Principal</Badge>
                  )}
                </div>
                {isEditing && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => eliminarContactoEmergencia(contacto.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Nombres</Label>
                  <Input
                    value={contacto.nombres}
                    onChange={(e) => {
                      const nuevosContactos = empleado.contactos_emergencia.map(c => 
                        c.id === contacto.id ? { ...c, nombres: e.target.value } : c
                      )
                      setEmpleado({ ...empleado, contactos_emergencia: nuevosContactos })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Apellidos</Label>
                  <Input
                    value={contacto.apellidos}
                    onChange={(e) => {
                      const nuevosContactos = empleado.contactos_emergencia.map(c => 
                        c.id === contacto.id ? { ...c, apellidos: e.target.value } : c
                      )
                      setEmpleado({ ...empleado, contactos_emergencia: nuevosContactos })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Parentesco</Label>
                  <Input
                    value={contacto.parentesco}
                    onChange={(e) => {
                      const nuevosContactos = empleado.contactos_emergencia.map(c => 
                        c.id === contacto.id ? { ...c, parentesco: e.target.value } : c
                      )
                      setEmpleado({ ...empleado, contactos_emergencia: nuevosContactos })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Teléfono Principal</Label>
                  <Input
                    value={contacto.telefono_principal}
                    onChange={(e) => {
                      const nuevosContactos = empleado.contactos_emergencia.map(c => 
                        c.id === contacto.id ? { ...c, telefono_principal: e.target.value } : c
                      )
                      setEmpleado({ ...empleado, contactos_emergencia: nuevosContactos })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Teléfono Secundario</Label>
                  <Input
                    value={contacto.telefono_secundario || ''}
                    onChange={(e) => {
                      const nuevosContactos = empleado.contactos_emergencia.map(c => 
                        c.id === contacto.id ? { ...c, telefono_secundario: e.target.value || undefined } : c
                      )
                      setEmpleado({ ...empleado, contactos_emergencia: nuevosContactos })
                    }}
                    disabled={!isEditing}
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id={`principal-${contacto.id}`}
                    checked={contacto.es_principal}
                    onChange={(e) => {
                      const nuevosContactos = empleado.contactos_emergencia.map(c => 
                        c.id === contacto.id ? { ...c, es_principal: e.target.checked } : c
                      )
                      setEmpleado({ ...empleado, contactos_emergencia: nuevosContactos })
                    }}
                    disabled={!isEditing}
                  />
                  <Label htmlFor={`principal-${contacto.id}`}>Contacto principal</Label>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Dirección</Label>
                <Textarea
                  value={contacto.direccion}
                  onChange={(e) => {
                    const nuevosContactos = empleado.contactos_emergencia.map(c => 
                      c.id === contacto.id ? { ...c, direccion: e.target.value } : c
                    )
                    setEmpleado({ ...empleado, contactos_emergencia: nuevosContactos })
                  }}
                  disabled={!isEditing}
                  rows={2}
                />
              </div>
            </div>
          ))}
          {empleado.contactos_emergencia.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No hay contactos de emergencia registrados
            </div>
          )}
        </CardContent>
      </Card>

      {/* Observaciones Generales */}
      <Card>
        <CardHeader>
          <CardTitle>Observaciones Generales</CardTitle>
          <CardDescription>
            Notas adicionales sobre la situación familiar
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="observaciones_generales">Observaciones</Label>
            <Textarea
              id="observaciones_generales"
              value={empleado.observaciones_generales || ''}
              onChange={(e) => setEmpleado({ ...empleado, observaciones_generales: e.target.value || undefined })}
              disabled={!isEditing}
              rows={4}
              placeholder="Ingrese observaciones generales sobre la situación familiar..."
            />
          </div>
        </CardContent>
      </Card>
      </div>
    </EmployeeLayout>
  )
}

export default DatosFamiliaresPage