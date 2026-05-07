import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { ProfileImage } from '@/shared/components/ProfileImage'
import EmployeeLayout from '@/components/layout/EmployeeLayout'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select'
import { Textarea } from '@/shared/ui/textarea'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { employeesService } from '@/services/employeesService'
import { CreditCard, Phone, User } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { toast } from 'sonner'

interface DatosPersonales {
  id: string
  nombres_empleado: string
  apellido_paterno: string
  apellido_materno: string
  numero_documento: string
  tipo_documento: string
  genero_empleado: string
  fecha_nacimiento: string
  estado_civil: string
  telefono_fijo: string
  telefono_celular: string
  correo_personal: string
  direccion_domicilio: string
  distrito_domicilio: string
  provincia_domicilio: string
  departamento_domicilio: string
  tipo_sangre: string
  talla_empleado: number
  peso_empleado: number
  ruta_fotografia: string
  estado_empleado: string
  entidad_bancaria: string
  numero_cuenta_bancaria: string
  numero_cci: string
  sistema_pensiones: string
  numero_ruc: string
}

export function DatosPersonalesPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const [empleado, setEmpleado] = useState<DatosPersonales | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Determinar el ID del empleado: del URL param o del usuario autenticado
  const empleadoId = id ?? user?.empleado?.id

  useEffect(() => {
    if (!empleadoId) {
      setLoading(false)
      setError('No se pudo determinar el empleado')
      return
    }

    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await employeesService.getById(empleadoId)
        const data = response?.data || response
        setEmpleado({
          id: data.id,
          nombres_empleado: data.nombres_empleado || '',
          apellido_paterno: data.apellido_paterno || '',
          apellido_materno: data.apellido_materno || '',
          numero_documento: data.numero_documento || '',
          tipo_documento: data.tipo_documento || 'DNI',
          genero_empleado: data.genero_empleado || '',
          fecha_nacimiento: data.fecha_nacimiento || '',
          estado_civil: data.estado_civil || '',
          telefono_fijo: data.telefono_fijo || '',
          telefono_celular: data.telefono_celular || '',
          correo_personal: data.correo_personal || '',
          direccion_domicilio: data.direccion_domicilio || '',
          distrito_domicilio: data.distrito_domicilio || '',
          provincia_domicilio: data.provincia_domicilio || '',
          departamento_domicilio: data.departamento_domicilio || '',
          tipo_sangre: data.tipo_sangre || '',
          talla_empleado: data.talla_empleado || 0,
          peso_empleado: data.peso_empleado || 0,
          ruta_fotografia: data.ruta_fotografia || '',
          estado_empleado: data.estado_empleado || '',
          entidad_bancaria: data.entidad_bancaria || '',
          numero_cuenta_bancaria: data.numero_cuenta_bancaria || '',
          numero_cci: data.numero_cci || '',
          sistema_pensiones: data.sistema_pensiones || '',
          numero_ruc: data.numero_ruc || '',
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error al cargar datos del empleado')
        toast.error('Error al cargar datos del empleado')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [empleadoId])

  const handleSave = async () => {
    if (!empleado || !empleadoId) return

    setSaving(true)
    try {
      await employeesService.update(empleadoId, {
        nombres_empleado: empleado.nombres_empleado,
        apellido_paterno: empleado.apellido_paterno,
        apellido_materno: empleado.apellido_materno,
        numero_documento: empleado.numero_documento,
        genero_empleado: empleado.genero_empleado,
        fecha_nacimiento: empleado.fecha_nacimiento,
        estado_civil: empleado.estado_civil,
        telefono_fijo: empleado.telefono_fijo,
        telefono_celular: empleado.telefono_celular,
        correo_personal: empleado.correo_personal,
        direccion_domicilio: empleado.direccion_domicilio,
        distrito_domicilio: empleado.distrito_domicilio,
        provincia_domicilio: empleado.provincia_domicilio,
        departamento_domicilio: empleado.departamento_domicilio,
        tipo_sangre: empleado.tipo_sangre,
        talla_empleado: empleado.talla_empleado,
        peso_empleado: empleado.peso_empleado,
        entidad_bancaria: empleado.entidad_bancaria,
        numero_cuenta_bancaria: empleado.numero_cuenta_bancaria,
        numero_cci: empleado.numero_cci,
        sistema_pensiones: empleado.sistema_pensiones,
        numero_ruc: empleado.numero_ruc,
      } as any)
      toast.success('Datos personales actualizados correctamente')
      setIsEditing(false)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al guardar los datos')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
    // Recargar datos originales
    if (empleadoId) {
      setLoading(true)
      employeesService.getById(empleadoId).then((response) => {
        const data = response?.data || response
        setEmpleado((prev) => prev ? { ...prev, ...data } : null)
      }).finally(() => setLoading(false))
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  if (error || !empleado) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">{error || 'No se encontraron datos del empleado.'}</p>
      </div>
    )
  }

  return (
    <EmployeeLayout
      title="Datos Personales"
      description={`Informacion personal del empleado - ID: ${empleado.id}`}
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
              <User className="w-4 h-4 mr-2" />
              Editar
            </Button>
          )}
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
        {/* Informacion Personal */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              Informacion Personal
            </CardTitle>
            <CardDescription>
              Datos basicos de identificacion
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-center mb-4">
              <ProfileImage
                src={empleado.ruta_fotografia}
                alt={`${empleado.nombres_empleado} ${empleado.apellido_paterno}`}
                size="lg"
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="nombres">Nombres</Label>
                <Input
                  id="nombres"
                  value={empleado.nombres_empleado}
                  onChange={(e) => setEmpleado({ ...empleado, nombres_empleado: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="apellido_paterno">Apellido Paterno</Label>
                <Input
                  id="apellido_paterno"
                  value={empleado.apellido_paterno}
                  onChange={(e) => setEmpleado({ ...empleado, apellido_paterno: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="apellido_materno">Apellido Materno</Label>
                <Input
                  id="apellido_materno"
                  value={empleado.apellido_materno}
                  onChange={(e) => setEmpleado({ ...empleado, apellido_materno: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="numero_documento">Numero de Documento</Label>
                <Input
                  id="numero_documento"
                  value={empleado.numero_documento}
                  onChange={(e) => setEmpleado({ ...empleado, numero_documento: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="genero">Genero</Label>
                <Select
                  value={empleado.genero_empleado}
                  onValueChange={(value) => setEmpleado({ ...empleado, genero_empleado: value })}
                  disabled={!isEditing}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="M">Masculino</SelectItem>
                    <SelectItem value="F">Femenino</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="fecha_nacimiento">Fecha de Nacimiento</Label>
                <Input
                  id="fecha_nacimiento"
                  type="date"
                  value={empleado.fecha_nacimiento}
                  onChange={(e) => setEmpleado({ ...empleado, fecha_nacimiento: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
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
                    <SelectItem value="soltero">Soltero</SelectItem>
                    <SelectItem value="casado">Casado</SelectItem>
                    <SelectItem value="divorciado">Divorciado</SelectItem>
                    <SelectItem value="viudo">Viudo</SelectItem>
                    <SelectItem value="conviviente">Conviviente</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="tipo_sangre">Tipo de Sangre</Label>
                <Select
                  value={empleado.tipo_sangre}
                  onValueChange={(value) => setEmpleado({ ...empleado, tipo_sangre: value })}
                  disabled={!isEditing}
                >
                  <SelectTrigger>
                    <SelectValue />
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
            </div>
          </CardContent>
        </Card>

        {/* Informacion de Contacto */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Phone className="w-5 h-5" />
              Informacion de Contacto
            </CardTitle>
            <CardDescription>
              Datos de contacto y ubicacion
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4">
              <div className="space-y-2">
                <Label htmlFor="telefono_fijo">Telefono Fijo</Label>
                <Input
                  id="telefono_fijo"
                  value={empleado.telefono_fijo}
                  onChange={(e) => setEmpleado({ ...empleado, telefono_fijo: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="telefono_celular">Celular</Label>
                <Input
                  id="telefono_celular"
                  value={empleado.telefono_celular}
                  onChange={(e) => setEmpleado({ ...empleado, telefono_celular: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="correo_personal">Correo Personal</Label>
                <Input
                  id="correo_personal"
                  type="email"
                  value={empleado.correo_personal}
                  onChange={(e) => setEmpleado({ ...empleado, correo_personal: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="direccion">Direccion</Label>
                <Textarea
                  id="direccion"
                  value={empleado.direccion_domicilio}
                  onChange={(e) => setEmpleado({ ...empleado, direccion_domicilio: e.target.value })}
                  disabled={!isEditing}
                  rows={3}
                />
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor="distrito">Distrito</Label>
                  <Input
                    id="distrito"
                    value={empleado.distrito_domicilio}
                    onChange={(e) => setEmpleado({ ...empleado, distrito_domicilio: e.target.value })}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="provincia">Provincia</Label>
                  <Input
                    id="provincia"
                    value={empleado.provincia_domicilio}
                    onChange={(e) => setEmpleado({ ...empleado, provincia_domicilio: e.target.value })}
                    disabled={!isEditing}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="departamento">Departamento</Label>
                  <Input
                    id="departamento"
                    value={empleado.departamento_domicilio}
                    onChange={(e) => setEmpleado({ ...empleado, departamento_domicilio: e.target.value })}
                    disabled={!isEditing}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Informacion Bancaria y Pensiones */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="w-5 h-5" />
              Informacion Bancaria
            </CardTitle>
            <CardDescription>
              Datos bancarios y sistema de pensiones
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="entidad_bancaria">Entidad Bancaria</Label>
                <Input
                  id="entidad_bancaria"
                  value={empleado.entidad_bancaria}
                  onChange={(e) => setEmpleado({ ...empleado, entidad_bancaria: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="numero_cuenta">Numero de Cuenta</Label>
                <Input
                  id="numero_cuenta"
                  value={empleado.numero_cuenta_bancaria}
                  onChange={(e) => setEmpleado({ ...empleado, numero_cuenta_bancaria: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cci">CCI</Label>
                <Input
                  id="cci"
                  value={empleado.numero_cci}
                  onChange={(e) => setEmpleado({ ...empleado, numero_cci: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="sistema_pensiones">Sistema de Pensiones</Label>
                <Input
                  id="sistema_pensiones"
                  value={empleado.sistema_pensiones}
                  onChange={(e) => setEmpleado({ ...empleado, sistema_pensiones: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="numero_ruc">RUC</Label>
                <Input
                  id="numero_ruc"
                  value={empleado.numero_ruc}
                  onChange={(e) => setEmpleado({ ...empleado, numero_ruc: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="talla">Talla (cm)</Label>
                <Input
                  id="talla"
                  type="number"
                  value={empleado.talla_empleado || ''}
                  onChange={(e) => setEmpleado({ ...empleado, talla_empleado: parseInt(e.target.value) || 0 })}
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="peso">Peso (kg)</Label>
                <Input
                  id="peso"
                  type="number"
                  value={empleado.peso_empleado || ''}
                  onChange={(e) => setEmpleado({ ...empleado, peso_empleado: parseInt(e.target.value) || 0 })}
                  disabled={!isEditing}
                />
              </div>
            </div>
          </CardContent>
        </Card>
        </div>
      </div>
    </EmployeeLayout>
  )
}

export default DatosPersonalesPage
