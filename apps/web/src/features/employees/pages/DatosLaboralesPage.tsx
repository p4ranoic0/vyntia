import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select'
import { Textarea } from '@/shared/ui/textarea'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { toast } from '@/shared/ui/use-toast'
import { Briefcase, DollarSign, Building2, FileText } from 'lucide-react'
import EmployeeLayout from '@/components/layout/EmployeeLayout'
import { employeesService } from '@/features/employees/services/employeesService'

interface DatosLaboralesForm {
  id: number
  codigo_empleado: string
  fecha_ingreso: string
  fecha_cese?: string
  cargo: string
  area: string
  jefe_inmediato: string
  tipo_contrato: string
  modalidad_trabajo: string
  horario_trabajo: string
  sueldo_basico: number
  bonificaciones: number
  descuentos: number
  banco: string
  numero_cuenta: string
  numero_cci: string
  afp_pension: string
  cuspp: string
  tipo_seguro: string
  estado_laboral: string
  observaciones: string
  tiene_suspension_renta_cuarta_vigente: boolean
  fecha_inicio_suspension_renta?: string
  fecha_fin_suspension_renta?: string
  documento_suspension_renta?: string
}

export function DatosLaboralesPage() {
  const { id } = useParams<{ id: string }>()
  const [empleado, setEmpleado] = useState<DatosLaboralesForm | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [isEditing, setIsEditing] = useState(false)

  useEffect(() => {
    if (!id) return
    const empleadoId = Number.parseInt(id, 10)

    Promise.all([
      employeesService.datosLaborales.get(empleadoId),
      employeesService.getById(empleadoId),
    ])
      .then(([response, empleadoResponse]: [unknown, unknown]) => {
        const items = (response as Record<string, unknown>)?.data || (response as Record<string, unknown>)?.results || []
        const records = Array.isArray(items) ? items : []
        const record = records.find((r: unknown) => (r as Record<string, unknown>)?.es_activo) || records[0]

        const empleadoPayload = empleadoResponse?.data || empleadoResponse || {}

        if (record) {
          setEmpleado({
            id: record.id,
            codigo_empleado: '',
            fecha_ingreso: record.fecha_ingreso || '',
            fecha_cese: record.fecha_cese || undefined,
            cargo: record.cargo_empleado || '',
            area: record.area_nombre || '',
            jefe_inmediato: '',
            tipo_contrato: record.tipo_contrato || '',
            modalidad_trabajo: record.modalidad_trabajo || '',
            horario_trabajo: record.jornada_laboral || '',
            sueldo_basico: record.sueldo_basico || 0,
            bonificaciones: 0,
            descuentos: 0,
            banco: '',
            numero_cuenta: '',
            numero_cci: '',
            afp_pension: '',
            cuspp: '',
            tipo_seguro: '',
            estado_laboral: record.es_activo ? 'Activo' : 'Cesado',
            observaciones: '',
            tiene_suspension_renta_cuarta_vigente: Boolean(empleadoPayload.tiene_suspension_renta_cuarta_vigente),
            fecha_inicio_suspension_renta: empleadoPayload.fecha_inicio_suspension_renta || undefined,
            fecha_fin_suspension_renta: empleadoPayload.fecha_fin_suspension_renta || undefined,
            documento_suspension_renta: empleadoPayload.documento_suspension_renta || undefined,
          })
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [id])

  const handleSave = async () => {
    if (!empleado) return

    setSaving(true)
    try {
      await employeesService.datosLaborales.update(empleado.id, {
        cargo_empleado: empleado.cargo,
        tipo_contrato: empleado.tipo_contrato,
        modalidad_trabajo: empleado.modalidad_trabajo,
        jornada_laboral: empleado.horario_trabajo,
        sueldo_basico: empleado.sueldo_basico,
        fecha_ingreso: empleado.fecha_ingreso,
        fecha_cese: empleado.fecha_cese,
      } as unknown as Record<string, unknown>)

      if (id) {
        await employeesService.update(Number.parseInt(id, 10), {
          tiene_suspension_renta_cuarta_vigente: empleado.tiene_suspension_renta_cuarta_vigente,
          fecha_inicio_suspension_renta: empleado.fecha_inicio_suspension_renta,
          fecha_fin_suspension_renta: empleado.fecha_fin_suspension_renta,
          documento_suspension_renta: empleado.documento_suspension_renta,
        })
      }

      toast({
        title: 'Datos guardados',
        description: 'Los datos laborales han sido actualizados correctamente.',
      })
      setIsEditing(false)
    } catch {
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
        <p className="text-muted-foreground">No se encontraron datos laborales del empleado.</p>
      </div>
    )
  }

  return (
    <EmployeeLayout 
      title="Datos Laborales" 
      description="Información laboral y contractual del empleado"
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
              <Briefcase className="w-4 h-4 mr-2" />
              Editar
            </Button>
          )}
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
        {/* Información del Puesto */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Briefcase className="w-5 h-5" />
              Información del Puesto
            </CardTitle>
            <CardDescription>
              Datos del cargo y área de trabajo
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4">
              <div className="space-y-2">
                <Label htmlFor="codigo_empleado">Código de Empleado</Label>
                <Input
                  id="codigo_empleado"
                  value={empleado.codigo_empleado}
                  onChange={(e) => setEmpleado({ ...empleado, codigo_empleado: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cargo">Cargo</Label>
                <Input
                  id="cargo"
                  value={empleado.cargo}
                  onChange={(e) => setEmpleado({ ...empleado, cargo: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="area">Área</Label>
                <Input
                  id="area"
                  value={empleado.area}
                  onChange={(e) => setEmpleado({ ...empleado, area: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="jefe_inmediato">Jefe Inmediato</Label>
                <Input
                  id="jefe_inmediato"
                  value={empleado.jefe_inmediato}
                  onChange={(e) => setEmpleado({ ...empleado, jefe_inmediato: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="estado_laboral">Estado Laboral</Label>
                <Select
                  value={empleado.estado_laboral}
                  onValueChange={(value) => setEmpleado({ ...empleado, estado_laboral: value })}
                  disabled={!isEditing}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Activo">Activo</SelectItem>
                    <SelectItem value="Inactivo">Inactivo</SelectItem>
                    <SelectItem value="Suspendido">Suspendido</SelectItem>
                    <SelectItem value="Cesado">Cesado</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Información Contractual */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Información Contractual
            </CardTitle>
            <CardDescription>
              Datos del contrato y modalidad de trabajo
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4">
              <div className="space-y-2">
                <Label htmlFor="fecha_ingreso">Fecha de Ingreso</Label>
                <Input
                  id="fecha_ingreso"
                  type="date"
                  value={empleado.fecha_ingreso}
                  onChange={(e) => setEmpleado({ ...empleado, fecha_ingreso: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="fecha_cese">Fecha de Cese</Label>
                <Input
                  id="fecha_cese"
                  type="date"
                  value={empleado.fecha_cese || ''}
                  onChange={(e) => setEmpleado({ ...empleado, fecha_cese: e.target.value || undefined })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="tipo_contrato">Tipo de Contrato</Label>
                <Select
                  value={empleado.tipo_contrato}
                  onValueChange={(value) => setEmpleado({ ...empleado, tipo_contrato: value })}
                  disabled={!isEditing}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Indefinido">Indefinido</SelectItem>
                    <SelectItem value="Temporal">Temporal</SelectItem>
                    <SelectItem value="CAS">CAS</SelectItem>
                    <SelectItem value="Locación">Locación de Servicios</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="modalidad_trabajo">Modalidad de Trabajo</Label>
                <Select
                  value={empleado.modalidad_trabajo}
                  onValueChange={(value) => setEmpleado({ ...empleado, modalidad_trabajo: value })}
                  disabled={!isEditing}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Presencial">Presencial</SelectItem>
                    <SelectItem value="Remoto">Remoto</SelectItem>
                    <SelectItem value="Híbrido">Híbrido</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="horario_trabajo">Horario de Trabajo</Label>
                <Input
                  id="horario_trabajo"
                  value={empleado.horario_trabajo}
                  onChange={(e) => setEmpleado({ ...empleado, horario_trabajo: e.target.value })}
                  disabled={!isEditing}
                  placeholder="08:00 - 17:00"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Información Salarial */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="w-5 h-5" />
              Información Salarial
            </CardTitle>
            <CardDescription>
              Datos de remuneración y beneficios
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4">
              <div className="space-y-2">
                <Label htmlFor="sueldo_basico">Sueldo Básico</Label>
                <Input
                  id="sueldo_basico"
                  type="number"
                  step="0.01"
                  value={empleado.sueldo_basico}
                  onChange={(e) => setEmpleado({ ...empleado, sueldo_basico: Number.parseFloat(e.target.value) || 0 })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="bonificaciones">Bonificaciones</Label>
                <Input
                  id="bonificaciones"
                  type="number"
                  step="0.01"
                  value={empleado.bonificaciones}
                  onChange={(e) => setEmpleado({ ...empleado, bonificaciones: Number.parseFloat(e.target.value) || 0 })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="descuentos">Descuentos</Label>
                <Input
                  id="descuentos"
                  type="number"
                  step="0.01"
                  value={empleado.descuentos}
                  onChange={(e) => setEmpleado({ ...empleado, descuentos: Number.parseFloat(e.target.value) || 0 })}
                  disabled={!isEditing}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Suspensión Renta 4ta */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Suspensión Renta 4ta
            </CardTitle>
            <CardDescription>
              Registra la vigencia de suspensión para la retención del 8% de renta de cuarta categoría.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4">
              <div className="flex items-center justify-between rounded-lg border px-3 py-2">
                <Label htmlFor="tiene_suspension_renta_cuarta_vigente">Suspensión vigente</Label>
                <Input
                  id="tiene_suspension_renta_cuarta_vigente"
                  type="checkbox"
                  checked={empleado.tiene_suspension_renta_cuarta_vigente}
                  onChange={(e) => setEmpleado({ ...empleado, tiene_suspension_renta_cuarta_vigente: e.target.checked })}
                  disabled={!isEditing}
                  className="h-4 w-4"
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="fecha_inicio_suspension_renta">Fecha inicio</Label>
                  <Input
                    id="fecha_inicio_suspension_renta"
                    type="date"
                    value={empleado.fecha_inicio_suspension_renta || ''}
                    onChange={(e) => setEmpleado({ ...empleado, fecha_inicio_suspension_renta: e.target.value || undefined })}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="fecha_fin_suspension_renta">Fecha fin</Label>
                  <Input
                    id="fecha_fin_suspension_renta"
                    type="date"
                    value={empleado.fecha_fin_suspension_renta || ''}
                    onChange={(e) => setEmpleado({ ...empleado, fecha_fin_suspension_renta: e.target.value || undefined })}
                    disabled={!isEditing}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="documento_suspension_renta">Documento de suspensión</Label>
                <Input
                  id="documento_suspension_renta"
                  value={empleado.documento_suspension_renta || ''}
                  onChange={(e) => setEmpleado({ ...empleado, documento_suspension_renta: e.target.value || undefined })}
                  disabled={!isEditing}
                  placeholder="Nro. expediente o referencia del documento"
                />
                <p className="text-xs text-muted-foreground">
                  La retención se evalúa contra el tope anual configurado en UIT.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Información Bancaria y Previsional */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              Información Bancaria y Previsional
            </CardTitle>
            <CardDescription>
              Datos bancarios y de seguridad social
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4">
              <div className="space-y-2">
                <Label htmlFor="banco">Banco</Label>
                <Input
                  id="banco"
                  value={empleado.banco}
                  onChange={(e) => setEmpleado({ ...empleado, banco: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="numero_cuenta">Número de Cuenta</Label>
                <Input
                  id="numero_cuenta"
                  value={empleado.numero_cuenta}
                  onChange={(e) => setEmpleado({ ...empleado, numero_cuenta: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="numero_cci">Número CCI</Label>
                <Input
                  id="numero_cci"
                  value={empleado.numero_cci}
                  onChange={(e) => setEmpleado({ ...empleado, numero_cci: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="afp_pension">AFP/Pensión</Label>
                <Select
                  value={empleado.afp_pension}
                  onValueChange={(value) => setEmpleado({ ...empleado, afp_pension: value })}
                  disabled={!isEditing}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="AFP Prima">AFP Prima</SelectItem>
                    <SelectItem value="AFP Integra">AFP Integra</SelectItem>
                    <SelectItem value="AFP Profuturo">AFP Profuturo</SelectItem>
                    <SelectItem value="AFP Habitat">AFP Habitat</SelectItem>
                    <SelectItem value="ONP">ONP</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="cuspp">CUSPP</Label>
                <Input
                  id="cuspp"
                  value={empleado.cuspp}
                  onChange={(e) => setEmpleado({ ...empleado, cuspp: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="tipo_seguro">Tipo de Seguro</Label>
                <Select
                  value={empleado.tipo_seguro}
                  onValueChange={(value) => setEmpleado({ ...empleado, tipo_seguro: value })}
                  disabled={!isEditing}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="EsSalud">EsSalud</SelectItem>
                    <SelectItem value="EPS">EPS</SelectItem>
                    <SelectItem value="Ninguno">Ninguno</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Observaciones */}
      <Card>
        <CardHeader>
          <CardTitle>Observaciones</CardTitle>
          <CardDescription>
            Notas adicionales sobre el empleado
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="observaciones">Observaciones</Label>
            <Textarea
              id="observaciones"
              value={empleado.observaciones}
              onChange={(e) => setEmpleado({ ...empleado, observaciones: e.target.value })}
              disabled={!isEditing}
              rows={4}
              placeholder="Ingrese observaciones adicionales..."
            />
          </div>
        </CardContent>
      </Card>
      </div>
    </EmployeeLayout>
  )
}

export default DatosLaboralesPage