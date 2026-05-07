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
import { Alert, AlertDescription } from '@/shared/ui/alert'
import { Badge } from '@/shared/ui/badge'
import { toast } from 'sonner'
import { Briefcase, Calendar, DollarSign, Building2, Clock, FileText, Lock, AlertCircle } from 'lucide-react'
import { employeesService, type DatosLaborales } from '@/services/employeesService'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useEmployeePermissions } from '@/hooks/useEmployeePermissions'

interface DatosLaboralesModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  empleadoId: number
  isReadOnly?: boolean
  title?: string
}

export function DatosLaboralesModal({
  open,
  onOpenChange,
  empleadoId,
  isReadOnly = false,
  title = 'Datos Laborales'
}: DatosLaboralesModalProps) {
  const { user } = useAuth()
  const { 
    canEditEmployeeData, 
    canAccessEmployeeData, 
    getViewMode,
    currentEmployeeId,
    isEmployee,
    canViewContractData,
    canViewSalaryData
  } = useEmployeePermissions()
  
  const [datos, setDatos] = useState<DatosLaborales | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [accessDenied, setAccessDenied] = useState(false)
  
  // Determinar el modo de visualización basado en permisos
  const viewMode = getViewMode(empleadoId, 'laboral')
  const isReadOnlyMode = isReadOnly || viewMode === 'readonly'
  const [isEditing, setIsEditing] = useState(!isReadOnlyMode)

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
      
      const response = await employeesService.datosLaborales.get(empleadoId)
      setDatos(response)
      setAccessDenied(false)
    } catch (error) {
      console.error('Error loading work data:', error)
      toast.error('Error al cargar los datos laborales')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!datos) return
    
    // Verificar permisos antes de guardar
    if (!canEditEmployeeData(empleadoId, 'laboral')) {
      toast.error('No tiene permisos para editar estos datos')
      return
    }
    
    setSaving(true)
    try {
      await employeesService.datosLaborales.update(empleadoId, datos)
      toast.success('Datos laborales actualizados correctamente')
      setIsEditing(false)
    } catch (error) {
      console.error('Error saving work data:', error)
      toast.error('Error al guardar los datos laborales')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
    checkAccessAndLoadDatos() // Recargar datos originales
  }

  const handleInputChange = (field: keyof DatosLaborales, value: string | number) => {
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
                No tienes permisos para acceder a estos datos laborales.
                {isEmployee && empleadoId !== currentEmployeeId && 
                  ' Solo puedes ver tus propios datos laborales.'}
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
            <Briefcase className="h-5 w-5" />
            {title}
            {isReadOnlyMode && <Badge variant="secondary">Solo lectura</Badge>}
            {empleadoId === currentEmployeeId && <Badge variant="outline">Mis datos</Badge>}
          </DialogTitle>
          <DialogDescription>
            {isReadOnlyMode 
              ? 'Visualización de información laboral del empleado'
              : 'Gestión de información laboral del empleado'
            }
          </DialogDescription>
        </DialogHeader>

        {datos && (
          <div className="space-y-6">
            {/* Información básica laboral */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="area_id" className="flex items-center gap-2">
                  <Building2 className="h-4 w-4" />
                  Área
                </Label>
                <Select
                  value={datos.area_id || ''}
                  onValueChange={(value) => handleInputChange('area_id', value)}
                  disabled={isReadOnlyMode || !isEditing}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar área" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Recursos Humanos</SelectItem>
                    <SelectItem value="2">Tecnología</SelectItem>
                    <SelectItem value="3">Administración</SelectItem>
                    <SelectItem value="4">Ventas</SelectItem>
                    <SelectItem value="5">Marketing</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="cargo_id">Cargo</Label>
                <Select
                  value={datos.cargo_id || ''}
                  onValueChange={(value) => handleInputChange('cargo_id', value)}
                  disabled={isReadOnlyMode || !isEditing}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar cargo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Analista</SelectItem>
                    <SelectItem value="2">Especialista</SelectItem>
                    <SelectItem value="3">Coordinador</SelectItem>
                    <SelectItem value="4">Jefe</SelectItem>
                    <SelectItem value="5">Gerente</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Fechas importantes */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="fecha_ingreso" className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Fecha de Ingreso
                </Label>
                <Input
                  id="fecha_ingreso"
                  type="date"
                  value={datos.fecha_ingreso || ''}
                  onChange={(e) => handleInputChange('fecha_ingreso', e.target.value)}
                  disabled={isReadOnlyMode || !isEditing || !canViewContractData(empleadoId)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="fecha_cese">Fecha de Cese</Label>
                <Input
                  id="fecha_cese"
                  type="date"
                  value={datos.fecha_cese || ''}
                  onChange={(e) => handleInputChange('fecha_cese', e.target.value)}
                  disabled={isReadOnlyMode || !isEditing || !canViewContractData(empleadoId)}
                />
              </div>
            </div>

            {/* Tipo de contrato y modalidad */}
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="tipo_contrato">Tipo de Contrato</Label>
                <Select
                  value={datos.tipo_contrato || ''}
                  onValueChange={(value) => handleInputChange('tipo_contrato', value)}
                  disabled={isReadOnlyMode || !isEditing || !canViewContractData(empleadoId)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="indefinido">Indefinido</SelectItem>
                    <SelectItem value="temporal">Temporal</SelectItem>
                    <SelectItem value="practicas">Prácticas</SelectItem>
                    <SelectItem value="consultoria">Consultoría</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="modalidad_trabajo">Modalidad de Trabajo</Label>
                <Select
                  value={datos.modalidad_trabajo || ''}
                  onValueChange={(value) => handleInputChange('modalidad_trabajo', value)}
                  disabled={isReadOnlyMode || !isEditing}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar modalidad" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="presencial">Presencial</SelectItem>
                    <SelectItem value="remoto">Remoto</SelectItem>
                    <SelectItem value="hibrido">Híbrido</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="estado">Estado Laboral</Label>
                <Select
                  value={datos.estado || ''}
                  onValueChange={(value) => handleInputChange('estado', value)}
                  disabled={isReadOnlyMode || !isEditing}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar estado" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="activo">Activo</SelectItem>
                    <SelectItem value="inactivo">Inactivo</SelectItem>
                    <SelectItem value="cesado">Cesado</SelectItem>
                    <SelectItem value="suspendido">Suspendido</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Horario y supervisor */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="horario_trabajo" className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Horario de Trabajo
                </Label>
                <Input
                  id="horario_trabajo"
                  placeholder="Ej: 08:00 - 17:00"
                  value={datos.horario_trabajo || ''}
                  onChange={(e) => handleInputChange('horario_trabajo', e.target.value)}
                  disabled={isReadOnlyMode || !isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="supervisor_id">Supervisor</Label>
                <Select
                  value={datos.supervisor_id || ''}
                  onValueChange={(value) => handleInputChange('supervisor_id', value)}
                  disabled={isReadOnlyMode || !isEditing}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar supervisor" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">María González</SelectItem>
                    <SelectItem value="2">Carlos Rodríguez</SelectItem>
                    <SelectItem value="3">Ana López</SelectItem>
                    <SelectItem value="4">Luis Martínez</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Información salarial */}
            <div className="space-y-4">
              <Label className="flex items-center gap-2">
                <DollarSign className="h-4 w-4" />
                Información Salarial
              </Label>
              <div className="grid gap-4 md:grid-cols-1">
                <div className="space-y-2">
                  <Label htmlFor="salario_base">Salario Base</Label>
                  <Input
                    id="salario_base"
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    value={datos.salario_base || ''}
                    onChange={(e) => handleInputChange('salario_base', parseFloat(e.target.value))}
                    disabled={isReadOnlyMode || !isEditing || !canViewSalaryData(empleadoId)}
                  />
                </div>
              </div>
            </div>

            {/* Motivo de cese */}
            {datos.fecha_cese && (
              <div className="space-y-2">
                <Label htmlFor="motivo_cese" className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Motivo de Cese
                </Label>
                <Textarea
                  id="motivo_cese"
                  placeholder="Describir el motivo del cese..."
                  value={datos.motivo_cese || ''}
                  onChange={(e) => handleInputChange('motivo_cese', e.target.value)}
                  disabled={isReadOnlyMode || !isEditing}
                  rows={3}
                />
              </div>
            )}
          </div>
        )}

        <DialogFooter className="flex-col gap-4">
          <div className="flex justify-end gap-2">
            {!isReadOnlyMode && canEditEmployeeData(empleadoId, 'laboral') && (
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
                  <Button onClick={() => setIsEditing(true)}>
                    Editar
                  </Button>
                )}
              </>
            )}
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cerrar
            </Button>
          </div>
          
          {/* Información de permisos para empleados */}
          {isEmployee && empleadoId === currentEmployeeId && isReadOnlyMode && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Algunos de tus datos laborales solo pueden ser modificados por el área de Recursos Humanos.
                Si necesitas actualizar información, contacta con RRHH.
              </AlertDescription>
            </Alert>
          )}
          
          {/* Información sobre datos restringidos */}
          {isEmployee && empleadoId === currentEmployeeId && !canViewSalaryData(empleadoId) && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Algunos datos salariales están restringidos según las políticas de la empresa.
              </AlertDescription>
            </Alert>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}