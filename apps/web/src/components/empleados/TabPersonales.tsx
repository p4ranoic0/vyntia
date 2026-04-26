import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { employeesService } from '@/services/employeesService'
import { ChangeEvent, useEffect, useState } from 'react'
import { toast } from 'sonner'

interface Empleado {
  empleado_id: number
  nombres_empleado: string
  apellido_paterno: string
  apellido_materno: string
  telefono_celular?: string
  correo_personal?: string
  estado_civil?: string
  fecha_nacimiento?: string
  distrito_domicilio?: string
  provincia_domicilio?: string
  departamento_domicilio?: string
  estado_empleado: string
  genero_empleado?: string
}

interface TabPersonalesProps {
  empleadoId: number
  initialData: Empleado
}

const BANCOS_PERU = [
  { value: 'BCP - Banco de Crédito del Perú', label: 'BCP - Banco de Crédito del Perú' },
  { value: 'Interbank', label: 'Interbank' },
  { value: 'BBVA Perú', label: 'BBVA Perú' },
  { value: 'Scotiabank Perú', label: 'Scotiabank Perú' },
  { value: 'Banco de la Nación', label: 'Banco de la Nación' },
  { value: 'BanBif', label: 'BanBif' },
  { value: 'Mibanco', label: 'Mibanco' },
  { value: 'Banco GNB', label: 'Banco GNB' },
  { value: 'Banco Pichincha', label: 'Banco Pichincha' },
  { value: 'Citibank Perú', label: 'Citibank Perú' },
  { value: 'Banco Falabella', label: 'Banco Falabella' },
  { value: 'Banco Ripley', label: 'Banco Ripley' },
  { value: 'Caja Cusco', label: 'Caja Cusco' },
  { value: 'Caja Arequipa', label: 'Caja Arequipa' },
  { value: 'Caja Piura', label: 'Caja Piura' },
  { value: 'Caja Sullana', label: 'Caja Sullana' },
  { value: 'Otro', label: 'Otro' },
]

const TIPO_SANGRE_OPTIONS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

const AFP_LIST = ['AFP PRIMA', 'AFP INTEGRA', 'AFP PROFUTURO', 'AFP HABITAT']

const SISTEMA_PENSIONES_OPTIONS = [
  'ONP',
  'AFP PRIMA',
  'AFP INTEGRA',
  'AFP PROFUTURO',
  'AFP HABITAT',
  'PENSIONISTA-SPP',
  'PENSIONISTA-CMP',
  'PENSIONISTA-OTRO',
  'SIN PENSION',
]

export function TabPersonales({ empleadoId, initialData }: TabPersonalesProps) {
  const [form, setForm] = useState({
    nombres_empleado: initialData.nombres_empleado || '',
    apellido_paterno: initialData.apellido_paterno || '',
    apellido_materno: initialData.apellido_materno || '',
    telefono_celular: initialData.telefono_celular || '',
    telefono_fijo: '',
    correo_personal: initialData.correo_personal || '',
    estado_civil: initialData.estado_civil || '',
    genero_empleado: initialData.genero_empleado || '',
    fecha_nacimiento: initialData.fecha_nacimiento || '',
    tipo_sangre: '',
    talla_empleado: '',
    peso_empleado: '',
    direccion_domicilio: '',
    distrito_domicilio: initialData.distrito_domicilio || '',
    provincia_domicilio: initialData.provincia_domicilio || '',
    departamento_domicilio: initialData.departamento_domicilio || '',
    numero_ruc: '',
    entidad_bancaria: '',
    numero_cuenta_bancaria: '',
    numero_cci: '',
    sistema_pensiones: '',
    tipo_comision: '',
    codigo_cuspp: '',
    estado_empleado: initialData.estado_empleado || 'activo',
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    employeesService.getById(empleadoId).then((data: any) => {
      const d = data?.data ?? data
      setForm(f => ({
        ...f,
        telefono_fijo: d?.telefono_fijo || '',
        tipo_sangre: d?.tipo_sangre || '',
        talla_empleado: d?.talla_empleado || '',
        peso_empleado: d?.peso_empleado || '',
        direccion_domicilio: d?.direccion_domicilio || '',
        numero_ruc: d?.numero_ruc || '',
        entidad_bancaria: d?.entidad_bancaria || '',
        numero_cuenta_bancaria: d?.numero_cuenta_bancaria || '',
        numero_cci: d?.numero_cci || '',
        sistema_pensiones: d?.sistema_pensiones || '',
        tipo_comision: d?.tipo_comision || '',
        codigo_cuspp: d?.codigo_cuspp || '',
        genero_empleado: d?.genero_empleado || initialData.genero_empleado || '',
      }))
    }).catch(() => {/* silent */})
  }, [empleadoId, initialData.genero_empleado])

  const f = (key: keyof typeof form) => ({
    value: form[key],
    onChange: (e: ChangeEvent<HTMLInputElement>) => setForm(s => ({ ...s, [key]: e.target.value })),
  })

  const isAfpSelected = AFP_LIST.includes(form.sistema_pensiones)

  const handleSave = async () => {
    setLoading(true)
    try {
      await employeesService.update(empleadoId, {
        nombres_empleado: form.nombres_empleado,
        apellido_paterno: form.apellido_paterno,
        apellido_materno: form.apellido_materno,
        telefono_celular: form.telefono_celular,
        telefono_fijo: form.telefono_fijo,
        correo_personal: form.correo_personal,
        estado_civil: form.estado_civil,
        genero_empleado: form.genero_empleado,
        fecha_nacimiento: form.fecha_nacimiento || undefined,
        tipo_sangre: form.tipo_sangre,
        talla_empleado: form.talla_empleado,
        peso_empleado: form.peso_empleado,
        direccion_domicilio: form.direccion_domicilio,
        distrito_domicilio: form.distrito_domicilio,
        provincia_domicilio: form.provincia_domicilio,
        departamento_domicilio: form.departamento_domicilio,
        numero_ruc: form.numero_ruc,
        entidad_bancaria: form.entidad_bancaria,
        numero_cuenta_bancaria: form.numero_cuenta_bancaria,
        numero_cci: form.numero_cci,
        sistema_pensiones: form.sistema_pensiones,
        tipo_comision: isAfpSelected ? form.tipo_comision : '',
        codigo_cuspp: isAfpSelected ? form.codigo_cuspp : '',
        estado_empleado: form.estado_empleado,
      } as any)
      toast.success('Datos personales guardados')
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al guardar')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Identidad */}
      <fieldset className="space-y-3">
        <legend className="text-sm font-semibold text-muted-foreground mb-1">Identidad</legend>
        <div className="grid grid-cols-2 gap-3">
          <div className="grid gap-1.5 col-span-2">
            <Label>Nombres</Label>
            <Input {...f('nombres_empleado')} placeholder="Nombres" />
          </div>
          <div className="grid gap-1.5">
            <Label>Apellido Paterno</Label>
            <Input {...f('apellido_paterno')} placeholder="Apellido Paterno" />
          </div>
          <div className="grid gap-1.5">
            <Label>Apellido Materno</Label>
            <Input {...f('apellido_materno')} placeholder="Apellido Materno" />
          </div>
          <div className="grid gap-1.5">
            <Label>Genero</Label>
            <Select value={form.genero_empleado} onValueChange={(v) => setForm(s => ({ ...s, genero_empleado: v }))}>
              <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="masculino">Masculino</SelectItem>
                <SelectItem value="femenino">Femenino</SelectItem>
                <SelectItem value="otro">Otro</SelectItem>
                <SelectItem value="no_especifica">No especifica</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label>Estado Civil</Label>
            <Select value={form.estado_civil} onValueChange={(v) => setForm(s => ({ ...s, estado_civil: v }))}>
              <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="soltero">Soltero/a</SelectItem>
                <SelectItem value="casado">Casado/a</SelectItem>
                <SelectItem value="conviviente">Conviviente</SelectItem>
                <SelectItem value="divorciado">Divorciado/a</SelectItem>
                <SelectItem value="viudo">Viudo/a</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label>Fecha de Nacimiento</Label>
            <Input type="date" {...f('fecha_nacimiento')} />
          </div>
          <div className="grid gap-1.5">
            <Label>N° RUC</Label>
            <Input {...f('numero_ruc')} placeholder="20123456789" maxLength={20} />
          </div>
        </div>
      </fieldset>

      {/* Datos físicos */}
      <fieldset className="space-y-3">
        <legend className="text-sm font-semibold text-muted-foreground mb-1">Datos fisicos</legend>
        <div className="grid grid-cols-3 gap-3">
          <div className="grid gap-1.5">
            <Label>Tipo de Sangre</Label>
            <Select value={form.tipo_sangre} onValueChange={(v) => setForm(s => ({ ...s, tipo_sangre: v }))}>
              <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
              <SelectContent>
                {TIPO_SANGRE_OPTIONS.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label>Talla</Label>
            <Input {...f('talla_empleado')} placeholder="1.70 m" />
          </div>
          <div className="grid gap-1.5">
            <Label>Peso</Label>
            <Input {...f('peso_empleado')} placeholder="70 kg" />
          </div>
        </div>
      </fieldset>

      {/* Contacto */}
      <fieldset className="space-y-3">
        <legend className="text-sm font-semibold text-muted-foreground mb-1">Contacto</legend>
        <div className="grid grid-cols-2 gap-3">
          <div className="grid gap-1.5">
            <Label>Telefono Celular</Label>
            <Input {...f('telefono_celular')} placeholder="987654321" />
          </div>
          <div className="grid gap-1.5">
            <Label>Telefono Fijo</Label>
            <Input {...f('telefono_fijo')} placeholder="014567890" />
          </div>
          <div className="grid gap-1.5 col-span-2">
            <Label>Correo Personal</Label>
            <Input type="email" {...f('correo_personal')} placeholder="correo@ejemplo.com" />
          </div>
        </div>
      </fieldset>

      {/* Domicilio */}
      <fieldset className="space-y-3">
        <legend className="text-sm font-semibold text-muted-foreground mb-1">Domicilio</legend>
        <div className="grid grid-cols-2 gap-3">
          <div className="grid gap-1.5 col-span-2">
            <Label>Direccion Domicilio</Label>
            <Input {...f('direccion_domicilio')} placeholder="Av. Principal 123" />
          </div>
          <div className="grid gap-1.5">
            <Label>Distrito</Label>
            <Input {...f('distrito_domicilio')} placeholder="Miraflores" />
          </div>
          <div className="grid gap-1.5">
            <Label>Provincia</Label>
            <Input {...f('provincia_domicilio')} placeholder="Lima" />
          </div>
          <div className="grid gap-1.5">
            <Label>Departamento</Label>
            <Input {...f('departamento_domicilio')} placeholder="Lima" />
          </div>
        </div>
      </fieldset>

      {/* Datos bancarios y pensiones */}
      <fieldset className="space-y-3">
        <legend className="text-sm font-semibold text-muted-foreground mb-1">Datos bancarios y pensiones</legend>
        <div className="grid grid-cols-2 gap-3">
          <div className="grid gap-1.5">
            <Label>Entidad Bancaria</Label>
            <Select value={form.entidad_bancaria} onValueChange={(v) => setForm(s => ({ ...s, entidad_bancaria: v }))}>
              <SelectTrigger><SelectValue placeholder="Seleccionar banco" /></SelectTrigger>
              <SelectContent>
                {BANCOS_PERU.map(b => <SelectItem key={b.value} value={b.value}>{b.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label>Numero de Cuenta</Label>
            <Input {...f('numero_cuenta_bancaria')} placeholder="123-456789-0-12" />
          </div>
          <div className="grid gap-1.5">
            <Label>Numero CCI</Label>
            <Input {...f('numero_cci')} placeholder="002-123-004567890123-45" />
          </div>
          <div className="grid gap-1.5">
            <Label>Sistema de Pensiones</Label>
            <Select value={form.sistema_pensiones} onValueChange={(v) => setForm(s => ({ ...s, sistema_pensiones: v }))}>
              <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
              <SelectContent>
                {SISTEMA_PENSIONES_OPTIONS.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          {isAfpSelected && (
            <>
              <div className="grid gap-1.5">
                <Label>Tipo de Comision</Label>
                <Select value={form.tipo_comision} onValueChange={(v) => setForm(s => ({ ...s, tipo_comision: v }))}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="FLUJO">Flujo</SelectItem>
                    <SelectItem value="MIXTA">Mixta</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-1.5">
                <Label>Codigo CUSPP</Label>
                <Input {...f('codigo_cuspp')} placeholder="123456ABCD" maxLength={20} />
              </div>
            </>
          )}
        </div>
      </fieldset>

      {/* Estado */}
      <fieldset className="space-y-3">
        <legend className="text-sm font-semibold text-muted-foreground mb-1">Estado del empleado</legend>
        <div className="grid grid-cols-2 gap-3">
          <div className="grid gap-1.5">
            <Label>Estado</Label>
            <Select value={form.estado_empleado} onValueChange={(v) => setForm(s => ({ ...s, estado_empleado: v }))}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="activo">Activo</SelectItem>
                <SelectItem value="inactivo">Inactivo</SelectItem>
                <SelectItem value="suspendido">Suspendido</SelectItem>
                <SelectItem value="cesado">Cesado</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </fieldset>

      <div className="flex justify-end pt-2">
        <Button onClick={handleSave} disabled={loading} size="sm">
          {loading ? 'Guardando...' : 'Guardar datos personales'}
        </Button>
      </div>
    </div>
  )
}
