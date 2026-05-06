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
import { Users, Heart, Baby, Plus, Trash2, Phone, MapPin, User, Lock, AlertCircle } from 'lucide-react'
import { employeesService, type DatosFamiliares } from '@/services/employeesService'
import { useAuth } from '@/hooks/useAuth'
import { useEmployeePermissions } from '@/hooks/useEmployeePermissions'

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

interface DatosFamiliaresModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  empleadoId: number
  isReadOnly?: boolean
  title?: string
}

export function DatosFamiliaresModal({
  open,
  onOpenChange,
  empleadoId,
  isReadOnly = false,
  title = 'Datos Familiares'
}: DatosFamiliaresModalProps) {
  const { user } = useAuth()
  const { 
    canEditEmployeeData, 
    canAccessEmployeeData, 
    getViewMode,
    currentEmployeeId,
    isEmployee
  } = useEmployeePermissions()
  
  const [datos, setDatos] = useState<DatosFamiliares | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [accessDenied, setAccessDenied] = useState(false)
  
  // Determinar el modo de visualización basado en permisos
  const viewMode = getViewMode(empleadoId, 'familiar')
  const isReadOnlyMode = isReadOnly || viewMode === 'readonly'
  const [isEditing, setIsEditing] = useState(!isReadOnlyMode)
  const [editingFamiliar, setEditingFamiliar] = useState<Familiar | null>(null)
  const [editingContacto, setEditingContacto] = useState<ContactoEmergencia | null>(null)

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
      
      const response = await employeesService.datosFamiliares.get(empleadoId)
      setDatos(response)
      setAccessDenied(false)
    } catch (error) {
      console.error('Error loading family data:', error)
      toast.error('Error al cargar los datos familiares')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!datos) return
    
    // Verificar permisos antes de guardar
    if (!canEditEmployeeData(empleadoId, 'familiar')) {
      toast.error('No tienes permisos para editar estos datos')
      return
    }
    
    setSaving(true)
    try {
      await employeesService.datosFamiliares.update(empleadoId, datos)
      toast.success('Datos familiares actualizados correctamente')
      setIsEditing(false)
    } catch (error) {
      console.error('Error saving family data:', error)
      toast.error('Error al guardar los datos familiares')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
    setEditingFamiliar(null)
    setEditingContacto(null)
    checkAccessAndLoadDatos() // Recargar datos originales
  }

  const handleInputChange = (field: keyof DatosFamiliares, value: string | number) => {
    if (!datos) return
    setDatos({ ...datos, [field]: value })
  }

  const handleAddFamiliar = () => {
    if (!canEditEmployeeData(empleadoId, 'familiar')) {
      toast.error('No tienes permisos para agregar familiares')
      return
    }
    
    const newFamiliar: Familiar = {
      id: Date.now(), // ID temporal
      nombres: '',
      apellidos: '',
      tipo_documento: 'DNI',
      numero_documento: '',
      parentesco: '',
      fecha_nacimiento: '',
      genero: '',
      estado_civil: '',
      es_beneficiario: false,
      es_contacto_emergencia: false
    }
    setEditingFamiliar(newFamiliar)
  }

  const handleSaveFamiliar = () => {
    if (!editingFamiliar || !datos) return
    
    const updatedFamiliares = editingFamiliar.id > 1000000 // ID temporal
      ? [...datos.familiares, editingFamiliar]
      : datos.familiares.map(f => f.id === editingFamiliar.id ? editingFamiliar : f)
    
    setDatos({ ...datos, familiares: updatedFamiliares })
    setEditingFamiliar(null)
  }

  const handleDeleteFamiliar = (id: number) => {
    if (!datos || !canEditEmployeeData(empleadoId, 'familiar')) {
      toast.error('No tienes permisos para eliminar familiares')
      return
    }
    setDatos({
      ...datos,
      familiares: datos.familiares.filter(f => f.id !== id)
    })
  }

  const handleAddContacto = () => {
    if (!canEditEmployeeData(empleadoId, 'familiar')) {
      toast.error('No tienes permisos para agregar contactos')
      return
    }
    
    const newContacto: ContactoEmergencia = {
      id: Date.now(), // ID temporal
      nombres: '',
      apellidos: '',
      parentesco: '',
      telefono_principal: '',
      direccion: '',
      es_principal: false
    }
    setEditingContacto(newContacto)
  }

  const handleSaveContacto = () => {
    if (!editingContacto || !datos) return
    
    const updatedContactos = editingContacto.id > 1000000 // ID temporal
      ? [...datos.contactos_emergencia, editingContacto]
      : datos.contactos_emergencia.map(c => c.id === editingContacto.id ? editingContacto : c)
    
    setDatos({ ...datos, contactos_emergencia: updatedContactos })
    setEditingContacto(null)
  }

  const handleDeleteContacto = (id: number) => {
    if (!datos || !canEditEmployeeData(empleadoId, 'familiar')) {
      toast.error('No tienes permisos para eliminar contactos')
      return
    }
    setDatos({
      ...datos,
      contactos_emergencia: datos.contactos_emergencia.filter(c => c.id !== id)
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
                No tienes permisos para acceder a estos datos familiares.
                {isEmployee && empleadoId !== currentEmployeeId && 
                  ' Solo puedes ver tus propios datos familiares.'}
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
            <Users className="h-5 w-5" />
            {title}
            {isReadOnlyMode && <Badge variant="secondary">Solo lectura</Badge>}
            {empleadoId === currentEmployeeId && <Badge variant="outline">Mis datos</Badge>}
          </DialogTitle>
          <DialogDescription>
            {isReadOnlyMode 
              ? 'Visualización de información familiar del empleado'
              : 'Gestión de información familiar del empleado'
            }
          </DialogDescription>
        </DialogHeader>

        {datos && (
          <div className="space-y-6">
            {/* Información general */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Heart className="h-4 w-4" />
                  Información General
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="estado_civil">Estado Civil</Label>
                    <Select
                      value={datos.estado_civil || ''}
                      onValueChange={(value) => handleInputChange('estado_civil', value)}
                      disabled={isReadOnlyMode || !isEditing}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Seleccionar estado civil" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="soltero">Soltero(a)</SelectItem>
                        <SelectItem value="casado">Casado(a)</SelectItem>
                        <SelectItem value="divorciado">Divorciado(a)</SelectItem>
                        <SelectItem value="viudo">Viudo(a)</SelectItem>
                        <SelectItem value="conviviente">Conviviente</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="numero_hijos" className="flex items-center gap-2">
                      <Baby className="h-4 w-4" />
                      Número de Hijos
                    </Label>
                    <Input
                      id="numero_hijos"
                      type="number"
                      min="0"
                      value={datos.numero_hijos || 0}
                      onChange={(e) => handleInputChange('numero_hijos', parseInt(e.target.value))}
                      disabled={isReadOnlyMode || !isEditing}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="observaciones_generales">Observaciones Generales</Label>
                  <Textarea
                    id="observaciones_generales"
                    placeholder="Observaciones adicionales..."
                    value={datos.observaciones_generales || ''}
                    onChange={(e) => handleInputChange('observaciones_generales', e.target.value)}
                    disabled={isReadOnlyMode || !isEditing}
                    rows={2}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Lista de familiares */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-4 w-4" />
                    Familiares ({datos.familiares.length})
                  </CardTitle>
                  {!isReadOnlyMode && isEditing && canEditEmployeeData(empleadoId, 'familiar') && (
                    <Button onClick={handleAddFamiliar} size="sm">
                      <Plus className="h-4 w-4 mr-2" />
                      Agregar Familiar
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {datos.familiares.map((familiar) => (
                    <div key={familiar.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-medium">
                            {familiar.nombres} {familiar.apellidos}
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            {familiar.parentesco} • {familiar.tipo_documento}: {familiar.numero_documento}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          {familiar.es_beneficiario && (
                            <Badge variant="secondary">Beneficiario</Badge>
                          )}
                          {familiar.es_contacto_emergencia && (
                            <Badge variant="outline">Contacto Emergencia</Badge>
                          )}
                          {!isReadOnlyMode && isEditing && canEditEmployeeData(empleadoId, 'familiar') && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteFamiliar(familiar.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                      <div className="grid gap-2 md:grid-cols-3 text-sm">
                        <div>
                          <span className="font-medium">Fecha Nacimiento:</span>
                          <br />
                          {familiar.fecha_nacimiento}
                        </div>
                        <div>
                          <span className="font-medium">Género:</span>
                          <br />
                          {familiar.genero}
                        </div>
                        <div>
                          <span className="font-medium">Estado Civil:</span>
                          <br />
                          {familiar.estado_civil}
                        </div>
                        {familiar.ocupacion && (
                          <div>
                            <span className="font-medium">Ocupación:</span>
                            <br />
                            {familiar.ocupacion}
                          </div>
                        )}
                        {familiar.telefono && (
                          <div className="flex items-center gap-1">
                            <Phone className="h-3 w-3" />
                            {familiar.telefono}
                          </div>
                        )}
                        {familiar.direccion && (
                          <div className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {familiar.direccion}
                          </div>
                        )}
                      </div>
                      {familiar.observaciones && (
                        <div className="mt-2 text-sm text-muted-foreground">
                          <span className="font-medium">Observaciones:</span> {familiar.observaciones}
                        </div>
                      )}
                    </div>
                  ))}
                  {datos.familiares.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      No hay familiares registrados
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Lista de contactos de emergencia */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Phone className="h-4 w-4" />
                    Contactos de Emergencia ({datos.contactos_emergencia.length})
                  </CardTitle>
                  {!isReadOnlyMode && isEditing && canEditEmployeeData(empleadoId, 'familiar') && (
                    <Button onClick={handleAddContacto} size="sm">
                      <Plus className="h-4 w-4 mr-2" />
                      Agregar Contacto
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {datos.contactos_emergencia.map((contacto) => (
                    <div key={contacto.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="font-medium">
                            {contacto.nombres} {contacto.apellidos}
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            {contacto.parentesco}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          {contacto.es_principal && (
                            <Badge variant="default">Principal</Badge>
                          )}
                          {!isReadOnlyMode && isEditing && canEditEmployeeData(empleadoId, 'familiar') && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteContacto(contacto.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                      <div className="grid gap-2 md:grid-cols-2 text-sm">
                        <div className="flex items-center gap-1">
                          <Phone className="h-3 w-3" />
                          <span className="font-medium">Principal:</span> {contacto.telefono_principal}
                        </div>
                        {contacto.telefono_secundario && (
                          <div className="flex items-center gap-1">
                            <Phone className="h-3 w-3" />
                            <span className="font-medium">Secundario:</span> {contacto.telefono_secundario}
                          </div>
                        )}
                        <div className="flex items-center gap-1 md:col-span-2">
                          <MapPin className="h-3 w-3" />
                          <span className="font-medium">Dirección:</span> {contacto.direccion}
                        </div>
                      </div>
                    </div>
                  ))}
                  {datos.contactos_emergencia.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      No hay contactos de emergencia registrados
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <DialogFooter>
          {!isReadOnlyMode && (
            <>
              {isEditing ? (
                <>
                  <Button variant="outline" onClick={handleCancel} disabled={saving}>
                    Cancelar
                  </Button>
                  <Button onClick={handleSave} disabled={saving}>
                    {saving ? (
                      <>
                        <LoadingSpinner size="sm" className="mr-2" />
                        Guardando...
                      </>
                    ) : (
                      'Guardar Cambios'
                    )}
                  </Button>
                </>
              ) : (
                canEditEmployeeData(empleadoId, 'familiar') && (
                  <Button onClick={() => setIsEditing(true)}>
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
          {isEmployee && empleadoId === currentEmployeeId && isReadOnlyMode && (
            <Alert className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Algunos de tus datos familiares solo pueden ser modificados por el área de Recursos Humanos.
                Si necesitas actualizar información, contacta con RRHH.
              </AlertDescription>
            </Alert>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}