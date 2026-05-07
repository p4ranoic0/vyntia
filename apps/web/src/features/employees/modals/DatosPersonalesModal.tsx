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
import { LoadingSpinner } from '@/shared/ui/loading-spinner'
import { Badge } from '@/shared/ui/badge'
import { Alert, AlertDescription } from '@/shared/ui/alert'
import { toast } from 'sonner'
import { User, Calendar, MapPin, Phone, Mail, CreditCard, Lock, AlertCircle, Edit } from 'lucide-react'
import { employeesService, type DatosPersonales } from '@/features/employees/services/employeesService'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useEmployeePermissions } from '@/features/employees/hooks/useEmployeePermissions'

interface DatosPersonalesModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  empleadoId: number
  isReadOnly?: boolean
  title?: string
}

export function DatosPersonalesModal({
  open,
  onOpenChange,
  empleadoId,
  isReadOnly = false,
  title = 'Datos Personales'
}: DatosPersonalesModalProps) {
  const { user } = useAuth()
  const { 
    canEditEmployeeData, 
    canAccessEmployeeData, 
    getViewMode,
    currentEmployeeId,
    isEmployee
  } = useEmployeePermissions()
  
  const [datos, setDatos] = useState<DatosPersonales | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [accessDenied, setAccessDenied] = useState(false)
  
  // Determinar el modo de visualización basado en permisos
  const viewMode = getViewMode(empleadoId, 'personal')
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
      
      const response = await employeesService.datosPersonales.get(empleadoId)
      setDatos(response)
      setAccessDenied(false)
    } catch (error) {
      console.error('Error loading personal data:', error)
      toast.error('Error al cargar los datos personales')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!datos) return
    
    // Verificar permisos antes de guardar
    if (!canEditEmployeeData(empleadoId, 'personal')) {
      toast.error('No tienes permisos para editar estos datos')
      return
    }
    
    setSaving(true)
    try {
      await employeesService.datosPersonales.update(empleadoId, datos)
      toast.success('Datos personales actualizados correctamente')
      setIsEditing(false)
    } catch (error) {
      console.error('Error saving personal data:', error)
      toast.error('Error al guardar los datos personales')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
    checkAccessAndLoadDatos() // Recargar datos originales
  }

  const handleEdit = () => {
    if (canEditEmployeeData(empleadoId, 'personal')) {
      setIsEditing(true)
    }
  }

  const handleInputChange = (field: keyof DatosPersonales, value: string | number) => {
    if (!datos) return
    setDatos({ ...datos, [field]: value })
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
                No tienes permisos para acceder a estos datos personales.
                {isEmployee && empleadoId !== currentEmployeeId && 
                  ' Solo puedes ver tus propios datos personales.'}
              </AlertDescription>
            </Alert>
          </div>
          <DialogFooter>
            <Button onClick={() => onOpenChange(false)} variant="outline">
              Cerrar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    )
  }

  if (loading) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner size="lg" />
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            {title}
            {effectiveReadOnly && <Badge variant="secondary">Solo lectura</Badge>}
            {empleadoId === currentEmployeeId && <Badge variant="outline">Mis datos</Badge>}
          </DialogTitle>
          <DialogDescription>
            {effectiveReadOnly 
              ? 'Visualización de información personal del empleado'
              : 'Gestión de información personal del empleado'}
          </DialogDescription>
        </DialogHeader>

        {datos && (
          <div className="space-y-6">
            {/* Información básica */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="nombres">Nombres</Label>
                <Input
                  id="nombres"
                  value={datos.nombres || ''}
                  onChange={(e) => handleInputChange('nombres', e.target.value)}
                  disabled={effectiveReadOnly || !isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ape_paterno">Apellido Paterno</Label>
                <Input
                  id="ape_paterno"
                  value={datos.ape_paterno || ''}
                  onChange={(e) => handleInputChange('ape_paterno', e.target.value)}
                  disabled={effectiveReadOnly || !isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ape_materno">Apellido Materno</Label>
                <Input
                  id="ape_materno"
                  value={datos.ape_materno || ''}
                  onChange={(e) => handleInputChange('ape_materno', e.target.value)}
                  disabled={effectiveReadOnly || !isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="dni">DNI</Label>
                <Input
                  id="dni"
                  value={datos.dni || ''}
                  onChange={(e) => handleInputChange('dni', e.target.value)}
                  disabled={effectiveReadOnly || !isEditing}
                  className="font-mono"
                />
              </div>
            </div>

            {/* Información de contacto */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="telefono" className="flex items-center gap-2">
                  <Phone className="h-4 w-4" />
                  Teléfono
                </Label>
                <Input
                  id="telefono"
                  value={datos.telefono || ''}
                  onChange={(e) => handleInputChange('telefono', e.target.value)}
                  disabled={effectiveReadOnly || !isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email_personal" className="flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Email Personal
                </Label>
                <Input
                  id="email_personal"
                  type="email"
                  value={datos.email_personal || ''}
                  onChange={(e) => handleInputChange('email_personal', e.target.value)}
                  disabled={effectiveReadOnly || !isEditing}
                />
              </div>
            </div>

            {/* Información personal */}
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="fecha_nacimiento" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Fecha de Nacimiento
                </Label>
                <Input
                  id="fecha_nacimiento"
                  type="date"
                  value={datos.fecha_nacimiento || ''}
                  onChange={(e) => handleInputChange('fecha_nacimiento', e.target.value)}
                  disabled={effectiveReadOnly || !isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="genero">Género</Label>
                <Select
                  value={datos.genero || ''}
                  onValueChange={(value) => handleInputChange('genero', value)}
                  disabled={effectiveReadOnly || !isEditing}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar género" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="M">Masculino</SelectItem>
                    <SelectItem value="F">Femenino</SelectItem>
                    <SelectItem value="O">Otro</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="estado_civil">Estado Civil</Label>
                <Select
                  value={datos.estado_civil || ''}
                  onValueChange={(value) => handleInputChange('estado_civil', value)}
                  disabled={effectiveReadOnly || !isEditing}
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
            </div>

            {/* Dirección */}
            <div className="space-y-4">
              <Label className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                Dirección
              </Label>
              <div className="space-y-2">
                <Textarea
                  placeholder="Dirección completa"
                  value={datos.direccion || ''}
                  onChange={(e) => handleInputChange('direccion', e.target.value)}
                  disabled={effectiveReadOnly || !isEditing}
                  rows={2}
                />
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor="distrito">Distrito</Label>
                  <Input
                    id="distrito"
                    value={datos.distrito || ''}
                    onChange={(e) => handleInputChange('distrito', e.target.value)}
                    disabled={effectiveReadOnly || !isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="provincia">Provincia</Label>
                  <Input
                    id="provincia"
                    value={datos.provincia || ''}
                    onChange={(e) => handleInputChange('provincia', e.target.value)}
                    disabled={effectiveReadOnly || !isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="departamento">Departamento</Label>
                  <Input
                    id="departamento"
                    value={datos.departamento || ''}
                    onChange={(e) => handleInputChange('departamento', e.target.value)}
                    disabled={effectiveReadOnly || !isEditing}
                  />
                </div>
              </div>
            </div>

            {/* Información adicional */}
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="nacionalidad">Nacionalidad</Label>
                <Input
                  id="nacionalidad"
                  value={datos.nacionalidad || ''}
                  onChange={(e) => handleInputChange('nacionalidad', e.target.value)}
                  disabled={effectiveReadOnly || !isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="tipo_sangre">Tipo de Sangre</Label>
                <Select
                  value={datos.tipo_sangre || ''}
                  onValueChange={(value) => handleInputChange('tipo_sangre', value)}
                  disabled={effectiveReadOnly || !isEditing}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="A+">A+</SelectItem>
                    <SelectItem value="A-">A-</SelectItem>
                    <SelectItem value="B+">B+</SelectItem>
                    <SelectItem value="B-">B-</SelectItem>
                    <SelectItem value="AB+">AB+</SelectItem>
                    <SelectItem value="AB-">AB-</SelectItem>
                    <SelectItem value="O+">O+</SelectItem>
                    <SelectItem value="O-">O-</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="lugar_nacimiento">Lugar de Nacimiento</Label>
                <Input
                  id="lugar_nacimiento"
                  value={datos.lugar_nacimiento || ''}
                  onChange={(e) => handleInputChange('lugar_nacimiento', e.target.value)}
                  disabled={effectiveReadOnly || !isEditing}
                />
              </div>
            </div>

            {/* Contacto de emergencia */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="contacto_emergencia">Contacto de Emergencia</Label>
                <Input
                  id="contacto_emergencia"
                  value={datos.contacto_emergencia || ''}
                  onChange={(e) => handleInputChange('contacto_emergencia', e.target.value)}
                  disabled={effectiveReadOnly || !isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="telefono_emergencia">Teléfono de Emergencia</Label>
                <Input
                  id="telefono_emergencia"
                  value={datos.telefono_emergencia || ''}
                  onChange={(e) => handleInputChange('telefono_emergencia', e.target.value)}
                  disabled={effectiveReadOnly || !isEditing}
                />
              </div>
            </div>
          </div>
        )}

        <DialogFooter className="flex-col gap-4">
          <div className="flex justify-end gap-2">
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
              <>
                <Button variant="outline" onClick={() => onOpenChange(false)}>
                  Cerrar
                </Button>
                {!effectiveReadOnly && canEditEmployeeData(empleadoId, 'personal') && (
                  <Button onClick={handleEdit}>
                    <Edit className="h-4 w-4 mr-2" />
                    Editar
                  </Button>
                )}
              </>
            )}
          </div>
          
          {/* Información de permisos para empleados */}
          {isEmployee && empleadoId === currentEmployeeId && effectiveReadOnly && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Algunos de tus datos personales solo pueden ser modificados por el área de Recursos Humanos.
                Si necesitas actualizar información, contacta con RRHH.
              </AlertDescription>
            </Alert>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}