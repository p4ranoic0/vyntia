import { Skeleton } from '@/components/common/LoadingSkeleton'
import { ProfileImage } from '@/components/common/ProfileImage'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useAreas, useEmpleados } from '@/hooks/useApi'
import { useDebounce } from '@/hooks/useDebounce'
import { contratosService } from '@/services/contratosService'
import { employeesService } from '@/services/employeesService'
import { OnboardingCreateData, onboardingService } from '@/services/onboardingService'
import {
    Award,
    ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight,
    Download,
    Edit,
    FileText,
    FolderOpen,
    GraduationCap,
    Mail,
    MoreHorizontal,
    Phone,
    Plus,
    Search,
    Trash2,
    UserPlus,
    Users
} from 'lucide-react'
import { ChangeEvent, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

// Interfaz que refleja los campos reales del backend
interface Empleado {
  empleado_id: number
  nombres_empleado: string
  apellido_paterno: string
  apellido_materno: string
  numero_documento: string
  tipo_documento?: string
  genero_empleado: string
  estado_empleado: string
  nombre_completo: string
  edad: number | null
  telefono_celular?: string
  correo_personal?: string
  estado_civil?: string
  fecha_nacimiento?: string
  distrito_domicilio?: string
  provincia_domicilio?: string
  departamento_domicilio?: string
  ruta_fotografia?: string
  ubicacion_actual?: {
    area_id: number
    area_siglas: string
    area_nombre: string
  } | null
}

// ─── Dialog: Editar empleado (tabbed) ───────────────────────────────────────

interface EditarEmpleadoDialogProps {
  empleado: Empleado | null
  open: boolean
  onClose: () => void
  onSaved: () => void
}

// ── Tab 1: Datos Personales ──────────────────────────────────────────────────

interface TabPersonalesProps {
  empleadoId: number
  initialData: Empleado
}

function TabPersonales({ empleadoId, initialData }: TabPersonalesProps) {
  const [form, setForm] = useState({
    nombres_empleado: initialData.nombres_empleado || '',
    apellido_paterno: initialData.apellido_paterno || '',
    apellido_materno: initialData.apellido_materno || '',
    telefono_celular: initialData.telefono_celular || '',
    correo_personal: initialData.correo_personal || '',
    estado_civil: initialData.estado_civil || '',
    fecha_nacimiento: initialData.fecha_nacimiento || '',
    direccion_domicilio: '',
    distrito_domicilio: initialData.distrito_domicilio || '',
    provincia_domicilio: initialData.provincia_domicilio || '',
    departamento_domicilio: initialData.departamento_domicilio || '',
    estado_empleado: initialData.estado_empleado || 'activo',
    entidad_bancaria: '',
    numero_cuenta_bancaria: '',
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Load full employee detail to get fields not included in list response
    employeesService.getById(empleadoId).then((data: any) => {
      const d = data?.data ?? data
      setForm(f => ({
        ...f,
        direccion_domicilio: d?.direccion_domicilio || '',
        entidad_bancaria: d?.entidad_bancaria || '',
        numero_cuenta_bancaria: d?.numero_cuenta_bancaria || '',
      }))
    }).catch(() => {/* silent */})
  }, [empleadoId])

  const f = (key: keyof typeof form) => ({
    value: form[key],
    onChange: (e: ChangeEvent<HTMLInputElement>) => setForm(s => ({ ...s, [key]: e.target.value })),
  })

  const handleSave = async () => {
    setLoading(true)
    try {
      await employeesService.update(empleadoId, {
        nombres_empleado: form.nombres_empleado,
        apellido_paterno: form.apellido_paterno,
        apellido_materno: form.apellido_materno,
        telefono_celular: form.telefono_celular,
        correo_personal: form.correo_personal,
        estado_civil: form.estado_civil,
        direccion_domicilio: form.direccion_domicilio,
        distrito_domicilio: form.distrito_domicilio,
        estado_empleado: form.estado_empleado,
        entidad_bancaria: form.entidad_bancaria,
        numero_cuenta_bancaria: form.numero_cuenta_bancaria,
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
          <Label>Telefono Celular</Label>
          <Input {...f('telefono_celular')} placeholder="987654321" />
        </div>
        <div className="grid gap-1.5">
          <Label>Correo Personal</Label>
          <Input type="email" {...f('correo_personal')} placeholder="correo@ejemplo.com" />
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
          <Label>Entidad Bancaria</Label>
          <Select value={form.entidad_bancaria} onValueChange={(v) => setForm(s => ({ ...s, entidad_bancaria: v }))}>
            <SelectTrigger><SelectValue placeholder="Seleccionar banco" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="BCP">BCP</SelectItem>
              <SelectItem value="BBVA">BBVA</SelectItem>
              <SelectItem value="INTERBANK">Interbank</SelectItem>
              <SelectItem value="SCOTIABANK">Scotiabank</SelectItem>
              <SelectItem value="BN">Banco de la Nacion</SelectItem>
              <SelectItem value="OTRO">Otro</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Numero de Cuenta</Label>
          <Input {...f('numero_cuenta_bancaria')} placeholder="123-456789-0-12" />
        </div>
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
      <div className="flex justify-end pt-2">
        <Button onClick={handleSave} disabled={loading} size="sm">
          {loading ? 'Guardando...' : 'Guardar datos personales'}
        </Button>
      </div>
    </div>
  )
}

// ── Tab 2: Datos Laborales ───────────────────────────────────────────────────

interface TabLaboralesProps {
  empleadoId: number
}

function TabLaborales({ empleadoId }: TabLaboralesProps) {
  const { data: areasData } = useAreas()
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const areasRaw: any = (areasData as any)?.data ?? areasData
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const areas: any[] = areasRaw?.results ?? (Array.isArray(areasRaw) ? areasRaw : [])

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [laboral, setLaboral] = useState<any>(null)
  const [form, setForm] = useState({
    area_id: '',
    cargo_empleado: '',
    fecha_ingreso: '',
    tipo_contrato: '',
    modalidad_trabajo: '',
    salario_base: '',
    horario_trabajo: '',
  })
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)

  useEffect(() => {
    setFetching(true)
    employeesService.datosLaborales.get(empleadoId).then((data: any) => {
      const raw = data?.data?.results ?? data?.results ?? data?.data ?? data
      const record = Array.isArray(raw) ? raw[0] : raw
      if (record) {
        setLaboral(record)
        setForm({
          area_id: String(record.area ?? record.area_id ?? ''),
          cargo_empleado: record.cargo_empleado || record.cargo || '',
          fecha_ingreso: record.fecha_ingreso || '',
          tipo_contrato: record.tipo_contrato || '',
          modalidad_trabajo: record.modalidad_trabajo || '',
          salario_base: String(record.sueldo_basico ?? record.salario_base ?? ''),
          horario_trabajo: record.jornada_laboral || record.horario_trabajo || '',
        })
      }
    }).catch(() => {/* silent */}).finally(() => setFetching(false))
  }, [empleadoId])

  const handleSave = async () => {
    const recordId = laboral?.dato_laboral_id ?? laboral?.id ?? laboral?.datos_laborales_id
    if (!recordId) {
      toast.error('No se encontraron datos laborales para actualizar')
      return
    }
    setLoading(true)
    try {
      await employeesService.datosLaborales.update(recordId, {
        area: form.area_id ? Number(form.area_id) : undefined,
        cargo_empleado: form.cargo_empleado,
        fecha_ingreso: form.fecha_ingreso,
        tipo_contrato: form.tipo_contrato,
        modalidad_trabajo: form.modalidad_trabajo,
        sueldo_basico: form.salario_base ? Number(form.salario_base) : undefined,
        jornada_laboral: form.horario_trabajo || undefined,
      } as any)
      toast.success('Datos laborales guardados')
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al guardar')
    } finally {
      setLoading(false)
    }
  }

  if (fetching) return <div className="py-8 text-center text-sm text-muted-foreground">Cargando datos laborales...</div>

  return (
    <div className="space-y-4">
      {!laboral && (
        <p className="text-sm text-muted-foreground py-4">No se encontraron datos laborales registrados.</p>
      )}
      <div className="grid grid-cols-2 gap-3">
        <div className="grid gap-1.5 col-span-2">
          <Label>Area / Unidad Organica</Label>
          <Select value={form.area_id} onValueChange={(v) => setForm(s => ({ ...s, area_id: v }))}>
            <SelectTrigger><SelectValue placeholder="Seleccionar area" /></SelectTrigger>
            <SelectContent>
              {areas.map((a: any) => (
                <SelectItem key={a.area_id ?? a.id} value={String(a.area_id ?? a.id)}>
                  {a.siglas_area ?? a.siglas} — {a.nombre_unidad_organica ?? a.nombre}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5 col-span-2">
          <Label>Cargo</Label>
          <Input
            value={form.cargo_empleado}
            onChange={(e) => setForm(s => ({ ...s, cargo_empleado: e.target.value }))}
            placeholder="Analista, Especialista, etc."
          />
        </div>
        <div className="grid gap-1.5">
          <Label>Fecha de Ingreso</Label>
          <Input
            type="date"
            value={form.fecha_ingreso}
            onChange={(e) => setForm(s => ({ ...s, fecha_ingreso: e.target.value }))}
          />
        </div>
        <div className="grid gap-1.5">
          <Label>Tipo de Contrato</Label>
          <Select value={form.tipo_contrato} onValueChange={(v) => setForm(s => ({ ...s, tipo_contrato: v }))}>
            <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="INDEFINIDO">Indefinido</SelectItem>
              <SelectItem value="PLAZO_FIJO">Plazo Fijo</SelectItem>
              <SelectItem value="CAS">CAS</SelectItem>
              <SelectItem value="LOCACION">Locacion de Servicios</SelectItem>
              <SelectItem value="PRACTICAS">Practicas</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Modalidad de Trabajo</Label>
          <Select value={form.modalidad_trabajo} onValueChange={(v) => setForm(s => ({ ...s, modalidad_trabajo: v }))}>
            <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="PRESENCIAL">Presencial</SelectItem>
              <SelectItem value="REMOTO">Remoto</SelectItem>
              <SelectItem value="HIBRIDO">Hibrido</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1.5">
          <Label>Salario Base</Label>
          <Input
            type="number"
            value={form.salario_base}
            onChange={(e) => setForm(s => ({ ...s, salario_base: e.target.value }))}
            placeholder="2000.00"
          />
        </div>
        <div className="grid gap-1.5 col-span-2">
          <Label>Horario de Trabajo</Label>
          <Input
            value={form.horario_trabajo}
            onChange={(e) => setForm(s => ({ ...s, horario_trabajo: e.target.value }))}
            placeholder="Lun-Vie 8:00-17:00"
          />
        </div>
      </div>
      <div className="flex justify-end pt-2">
        <Button onClick={handleSave} disabled={loading || !laboral} size="sm">
          {loading ? 'Guardando...' : 'Guardar datos laborales'}
        </Button>
      </div>
    </div>
  )
}

// ── Tab 3: Datos Familiares ──────────────────────────────────────────────────

interface TabFamiliaresProps {
  empleadoId: number
}

const PARENTESCO_OPTIONS = [
  { value: 'conyuge', label: 'Conyuge' },
  { value: 'hijo', label: 'Hijo/a' },
  { value: 'padre', label: 'Padre' },
  { value: 'madre', label: 'Madre' },
  { value: 'hermano', label: 'Hermano/a' },
  { value: 'otro', label: 'Otro' },
]

const FAMILIAR_EMPTY = {
  nombres_familiar: '',
  apellido_paterno: '',
  apellido_materno: '',
  parentesco: '',
  numero_documento: '',
  fecha_nacimiento: '',
  genero_familiar: 'masculino',
  es_beneficiario: false,
  es_dependiente: false,
}

function TabFamiliares({ empleadoId }: TabFamiliaresProps) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [familiares, setFamiliares] = useState<any[]>([])
  const [editingId, setEditingId] = useState<number | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ ...FAMILIAR_EMPTY })
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)

  const reload = () => {
    setFetching(true)
    employeesService.datosFamiliares.getAll(empleadoId).then((data: any) => {
      const raw = data?.data?.results ?? data?.results ?? data?.data ?? data
      setFamiliares(Array.isArray(raw) ? raw : [])
    }).catch(() => setFamiliares([])).finally(() => setFetching(false))
  }

  useEffect(() => { reload() }, [empleadoId])

  const startEdit = (fam: any) => {
    setEditingId(fam.familiar_id ?? fam.id)
    setFormData({
      nombres_familiar: fam.nombres_familiar || '',
      apellido_paterno: fam.apellido_paterno || '',
      apellido_materno: fam.apellido_materno || '',
      parentesco: fam.parentesco || '',
      numero_documento: fam.numero_documento || '',
      fecha_nacimiento: fam.fecha_nacimiento || '',
      genero_familiar: fam.genero_familiar || 'masculino',
      es_beneficiario: !!fam.es_beneficiario,
      es_dependiente: !!fam.es_dependiente,
    })
    setShowForm(true)
  }

  const startNew = () => {
    setEditingId(null)
    setFormData({ ...FAMILIAR_EMPTY })
    setShowForm(true)
  }

  const handleSave = async () => {
    if (!formData.nombres_familiar || !formData.parentesco) {
      toast.error('Nombre y parentesco son obligatorios')
      return
    }
    setLoading(true)
    try {
      if (editingId) {
        await employeesService.datosFamiliares.update(empleadoId, editingId, formData as any)
        toast.success('Familiar actualizado')
      } else {
        await employeesService.datosFamiliares.create(empleadoId, formData as any)
        toast.success('Familiar agregado')
      }
      setShowForm(false)
      reload()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al guardar')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!globalThis.confirm('¿Eliminar este familiar?')) return
    try {
      await employeesService.datosFamiliares.delete(empleadoId, id)
      toast.success('Familiar eliminado')
      reload()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al eliminar')
    }
  }

  if (fetching) return <div className="py-8 text-center text-sm text-muted-foreground">Cargando...</div>

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">{familiares.length} familiar(es) registrado(s)</p>
        <Button size="sm" variant="outline" onClick={startNew}>
          <Plus className="h-4 w-4 mr-1" /> Agregar
        </Button>
      </div>

      {familiares.length > 0 && (
        <div className="border rounded-md overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-3 py-2">Nombre</th>
                <th className="text-left px-3 py-2">Parentesco</th>
                <th className="text-left px-3 py-2 hidden sm:table-cell">DNI</th>
                <th className="w-20 px-2 py-2"></th>
              </tr>
            </thead>
            <tbody>
              {familiares.map((fam: any) => {
                const famId = fam.familiar_id ?? fam.id
                return (
                  <tr key={famId} className="border-t">
                    <td className="px-3 py-2">{fam.nombres_familiar} {fam.apellido_paterno}</td>
                    <td className="px-3 py-2 capitalize">{fam.parentesco}</td>
                    <td className="px-3 py-2 hidden sm:table-cell">{fam.numero_documento || '—'}</td>
                    <td className="px-2 py-2">
                      <div className="flex gap-1">
                        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => startEdit(fam)}>
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button size="icon" variant="ghost" className="h-7 w-7 text-destructive" onClick={() => handleDelete(famId)}>
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <div className="border rounded-md p-3 space-y-3 bg-muted/20">
          <p className="text-sm font-medium">{editingId ? 'Editar familiar' : 'Nuevo familiar'}</p>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label>Nombres <span className="text-destructive">*</span></Label>
              <Input value={formData.nombres_familiar} onChange={e => setFormData(s => ({ ...s, nombres_familiar: e.target.value }))} />
            </div>
            <div className="grid gap-1.5">
              <Label>Parentesco <span className="text-destructive">*</span></Label>
              <Select value={formData.parentesco} onValueChange={v => setFormData(s => ({ ...s, parentesco: v }))}>
                <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
                <SelectContent>
                  {PARENTESCO_OPTIONS.map(o => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label>Apellido Paterno</Label>
              <Input value={formData.apellido_paterno} onChange={e => setFormData(s => ({ ...s, apellido_paterno: e.target.value }))} />
            </div>
            <div className="grid gap-1.5">
              <Label>Apellido Materno</Label>
              <Input value={formData.apellido_materno} onChange={e => setFormData(s => ({ ...s, apellido_materno: e.target.value }))} />
            </div>
            <div className="grid gap-1.5">
              <Label>N° Documento</Label>
              <Input value={formData.numero_documento} onChange={e => setFormData(s => ({ ...s, numero_documento: e.target.value }))} maxLength={12} />
            </div>
            <div className="grid gap-1.5">
              <Label>Fecha de Nacimiento</Label>
              <Input type="date" value={formData.fecha_nacimiento} onChange={e => setFormData(s => ({ ...s, fecha_nacimiento: e.target.value }))} />
            </div>
            <div className="grid gap-1.5">
              <Label>Genero</Label>
              <Select value={formData.genero_familiar} onValueChange={v => setFormData(s => ({ ...s, genero_familiar: v }))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="masculino">Masculino</SelectItem>
                  <SelectItem value="femenino">Femenino</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex flex-col gap-2 pt-2">
              <div className="flex items-center gap-2">
                <Checkbox
                  id="beneficiario"
                  checked={formData.es_beneficiario}
                  onCheckedChange={v => setFormData(s => ({ ...s, es_beneficiario: !!v }))}
                />
                <Label htmlFor="beneficiario" className="font-normal">Es beneficiario</Label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="dependiente"
                  checked={formData.es_dependiente}
                  onCheckedChange={v => setFormData(s => ({ ...s, es_dependiente: !!v }))}
                />
                <Label htmlFor="dependiente" className="font-normal">Es dependiente</Label>
              </div>
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

// ── Tab 4: Formacion Academica ───────────────────────────────────────────────

interface TabAcademicosProps {
  empleadoId: number
}

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

function TabAcademicos({ empleadoId }: TabAcademicosProps) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [academicos, setAcademicos] = useState<any[]>([])
  const [editingId, setEditingId] = useState<number | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ ...ACADEMICO_EMPTY })
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)

  const reload = () => {
    setFetching(true)
    employeesService.datosAcademicos.getAll(empleadoId).then((data: any) => {
      const raw = data?.data?.results ?? data?.results ?? data?.data ?? data
      setAcademicos(Array.isArray(raw) ? raw : [])
    }).catch(() => setAcademicos([])).finally(() => setFetching(false))
  }

  useEffect(() => { reload() }, [empleadoId])

  const startEdit = (acad: any) => {
    setEditingId(acad.academico_id ?? acad.id)
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

  const handleDelete = async (id: number) => {
    if (!globalThis.confirm('¿Eliminar este registro academico?')) return
    try {
      await employeesService.datosAcademicos.delete(empleadoId, id)
      toast.success('Registro eliminado')
      reload()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al eliminar')
    }
  }

  if (fetching) return <div className="py-8 text-center text-sm text-muted-foreground">Cargando...</div>

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">{academicos.length} registro(s) academico(s)</p>
        <Button size="sm" variant="outline" onClick={startNew}>
          <Plus className="h-4 w-4 mr-1" /> Agregar
        </Button>
      </div>

      {academicos.length > 0 && (
        <div className="border rounded-md overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-3 py-2">Nivel</th>
                <th className="text-left px-3 py-2">Institucion</th>
                <th className="text-left px-3 py-2 hidden sm:table-cell">Titulo</th>
                <th className="w-20 px-2 py-2"></th>
              </tr>
            </thead>
            <tbody>
              {academicos.map((acad: any) => {
                const acadId = acad.academico_id ?? acad.id
                return (
                  <tr key={acadId} className="border-t">
                    <td className="px-3 py-2">{acad.nivel_educativo}</td>
                    <td className="px-3 py-2">{acad.nombre_institucion}</td>
                    <td className="px-3 py-2 hidden sm:table-cell">{acad.nombre_carrera || '—'}</td>
                    <td className="px-2 py-2">
                      <div className="flex gap-1">
                        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => startEdit(acad)}>
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button size="icon" variant="ghost" className="h-7 w-7 text-destructive" onClick={() => handleDelete(acadId)}>
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

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

// ── Main dialog ──────────────────────────────────────────────────────────────

function EditarEmpleadoDialog({ empleado, open, onClose, onSaved }: EditarEmpleadoDialogProps) {
  if (!empleado) return null

  const handleClose = () => {
    onSaved()
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={(v) => !v && handleClose()}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Editar Empleado</DialogTitle>
          <DialogDescription>
            {empleado.nombre_completo} — DNI {empleado.numero_documento}
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="personales" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="personales">Personales</TabsTrigger>
            <TabsTrigger value="laborales">Laborales</TabsTrigger>
            <TabsTrigger value="familiares">Familiares</TabsTrigger>
            <TabsTrigger value="academicos">
              <GraduationCap className="h-3.5 w-3.5 mr-1" />
              Academico
            </TabsTrigger>
          </TabsList>

          <TabsContent value="personales" className="mt-4">
            <TabPersonales empleadoId={empleado.empleado_id} initialData={empleado} />
          </TabsContent>

          <TabsContent value="laborales" className="mt-4">
            <TabLaborales empleadoId={empleado.empleado_id} />
          </TabsContent>

          <TabsContent value="familiares" className="mt-4">
            <TabFamiliares empleadoId={empleado.empleado_id} />
          </TabsContent>

          <TabsContent value="academicos" className="mt-4">
            <TabAcademicos empleadoId={empleado.empleado_id} />
          </TabsContent>
        </Tabs>

        <DialogFooter className="mt-2">
          <Button variant="outline" onClick={handleClose}>Cerrar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ─── Dialog: Nuevo empleado (vía onboarding) ────────────────────────────────

interface NuevoEmpleadoDialogProps {
  open: boolean
  onClose: () => void
  onCreated: () => void
}

const GENERO_OPTIONS = [
  { value: 'masculino', label: 'Masculino' },
  { value: 'femenino', label: 'Femenino' },
  { value: 'otro', label: 'Otro' },
]

function NuevoEmpleadoDialog({ open, onClose, onCreated }: NuevoEmpleadoDialogProps) {
  const emptyForm: OnboardingCreateData = {
    nombres_empleado: '',
    apellido_paterno: '',
    apellido_materno: '',
    numero_documento: '',
    correo_personal: '',
    genero_empleado: 'masculino',
  }
  const [form, setForm] = useState<OnboardingCreateData>(emptyForm)
  const [loading, setLoading] = useState(false)

  const handleCreate = async () => {
    if (!form.nombres_empleado || !form.apellido_paterno || !form.numero_documento || !form.correo_personal) {
      toast.error('Completa los campos obligatorios')
      return
    }
    setLoading(true)
    try {
      const result = await onboardingService.crear(form)
      toast.success(`Empleado creado. Usuario: ${result.username}`)
      setForm(emptyForm)
      onCreated()
      onClose()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al crear el empleado')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setForm(emptyForm)
    onClose()
  }

  const field = (key: keyof OnboardingCreateData) => ({
    value: (form[key] as string) || '',
    onChange: (e: ChangeEvent<HTMLInputElement>) =>
      setForm(f => ({ ...f, [key]: e.target.value })),
  })

  return (
    <Dialog open={open} onOpenChange={(v) => !v && handleClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Nuevo Empleado</DialogTitle>
          <DialogDescription>
            Se creara el empleado y se generaran sus credenciales de acceso al sistema.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-2">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor="n-nombres">Nombres <span className="text-destructive">*</span></Label>
              <Input id="n-nombres" placeholder="Juan Carlos" {...field('nombres_empleado')} />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="n-genero">Genero</Label>
              <Select value={form.genero_empleado || 'masculino'} onValueChange={(v) => setForm(f => ({ ...f, genero_empleado: v }))}>
                <SelectTrigger id="n-genero"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {GENERO_OPTIONS.map(o => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor="n-pat">Apellido Paterno <span className="text-destructive">*</span></Label>
              <Input id="n-pat" placeholder="Garcia" {...field('apellido_paterno')} />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="n-mat">Apellido Materno</Label>
              <Input id="n-mat" placeholder="Lopez" {...field('apellido_materno')} />
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor="n-dni">Numero de Documento <span className="text-destructive">*</span></Label>
            <Input id="n-dni" placeholder="12345678" maxLength={12} {...field('numero_documento')} />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor="n-email">Correo Personal <span className="text-destructive">*</span></Label>
            <Input id="n-email" type="email" placeholder="empleado@correo.com" {...field('correo_personal')} />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={loading}>Cancelar</Button>
          <Button onClick={handleCreate} disabled={loading}>
            {loading ? 'Creando...' : 'Crear Empleado'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ─── Componente principal ────────────────────────────────────────────────────

export function Empleados() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(15)
  const [searchTerm, setSearchTerm] = useState('')
  const [showInactive, setShowInactive] = useState(false)
  const [editTarget, setEditTarget] = useState<Empleado | null>(null)
  const [showNuevo, setShowNuevo] = useState(false)

  const debouncedSearchTerm = useDebounce(searchTerm, 500)

  const { data: empleadosData, isLoading, error, refetch } = useEmpleados({
    page,
    page_size: pageSize,
    search: debouncedSearchTerm || undefined,
    estado: showInactive ? undefined : 'true'
  })

  const empleados: Empleado[] = empleadosData?.results || []
  const totalCount = empleadosData?.count || 0
  const totalPages = Math.ceil(totalCount / pageSize)

  useEffect(() => {
    setPage(1)
  }, [debouncedSearchTerm, showInactive])

  const handleVerDetalle = (id: number) => {
    navigate(`/empleados/reporte/${id}`)
  }

  const handleDescargarPdf = async (id: number, nombre: string) => {
    try {
      await employeesService.reportes.descargarReporteIntegral(id)
      toast.success(`PDF descargado: ${nombre}`)
    } catch {
      toast.error('Error al descargar el PDF')
    }
  }

  const handleVerLegajo = (id: number) => {
    navigate(`/legajo/${id}`)
  }

  const handleGenerarDocumento = async (empleado: Empleado, tipo: 'constancia' | 'certificado') => {
    try {
      await contratosService.generarCertificado({
        empleado_id: empleado.empleado_id,
        tipo_certificado: tipo === 'certificado' ? 'trabajo' : 'constancia',
        guardar_documento: true,
      })
      toast.success(`${tipo === 'certificado' ? 'Certificado' : 'Constancia'} generado para ${empleado.nombre_completo}`)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al generar el documento')
    }
  }

  const getEstadoBadge = (estado: string) => {
    switch (estado) {
      case 'activo':
        return <Badge variant="default" className="bg-green-600">Activo</Badge>
      case 'inactivo':
        return <Badge variant="secondary">Inactivo</Badge>
      case 'suspendido':
        return <Badge variant="destructive">Suspendido</Badge>
      case 'cesado':
        return <Badge variant="outline">Cesado</Badge>
      default:
        return <Badge variant="secondary">{estado}</Badge>
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-4 w-72" />
          </div>
          <Skeleton className="h-10 w-36" />
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="flex items-center space-x-4">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <Skeleton className="h-4 flex-1" />
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-20" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4">
        <Users className="h-12 w-12 text-muted-foreground" />
        <h2 className="text-xl font-semibold">Error al cargar los empleados</h2>
        <p className="text-muted-foreground text-center max-w-md">
          No se pudo obtener la lista de empleados. Verifica tu conexion e intenta nuevamente.
        </p>
        <Button onClick={() => refetch()} variant="outline">
          Reintentar
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Dialogs */}
      <EditarEmpleadoDialog
        empleado={editTarget}
        open={!!editTarget}
        onClose={() => setEditTarget(null)}
        onSaved={() => refetch()}
      />
      <NuevoEmpleadoDialog
        open={showNuevo}
        onClose={() => setShowNuevo(false)}
        onCreated={() => refetch()}
      />

      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestion de Empleados</h1>
          <p className="text-muted-foreground">
            {totalCount} empleado{totalCount !== 1 ? 's' : ''} registrado{totalCount !== 1 ? 's' : ''}
          </p>
        </div>
        <Button onClick={() => setShowNuevo(true)}>
          <UserPlus className="mr-2 h-4 w-4" />
          Nuevo Empleado
        </Button>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-4 pb-4">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por nombre o DNI..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="show-inactive"
                checked={showInactive}
                onCheckedChange={(checked) => setShowInactive(checked as boolean)}
              />
              <Label htmlFor="show-inactive" className="text-sm">
                Incluir inactivos
              </Label>
            </div>
            <Select value={String(pageSize)} onValueChange={(v) => { setPageSize(Number(v)); setPage(1) }}>
              <SelectTrigger className="w-[130px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="10">10 por pag.</SelectItem>
                <SelectItem value="15">15 por pag.</SelectItem>
                <SelectItem value="25">25 por pag.</SelectItem>
                <SelectItem value="50">50 por pag.</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabla */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[60px]">ID</TableHead>
                  <TableHead className="w-[80px]">DNI</TableHead>
                  <TableHead>Empleado</TableHead>
                  <TableHead className="hidden md:table-cell">Area</TableHead>
                  <TableHead className="hidden lg:table-cell">Contacto</TableHead>
                  <TableHead className="hidden sm:table-cell w-[80px]">Edad</TableHead>
                  <TableHead className="w-[90px]">Estado</TableHead>
                  <TableHead className="w-[50px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {empleados.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-12">
                      <Users className="h-10 w-10 mx-auto mb-3 text-muted-foreground" />
                      <p className="text-muted-foreground">No se encontraron empleados</p>
                      {searchTerm && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Intenta con otro termino de busqueda
                        </p>
                      )}
                    </TableCell>
                  </TableRow>
                ) : (
                  empleados.map((emp) => (
                    <TableRow
                      key={emp.empleado_id}
                      className="cursor-pointer hover:bg-accent/50"
                      onClick={() => handleVerDetalle(emp.empleado_id)}
                    >
                      <TableCell className="text-xs text-muted-foreground">
                        {emp.empleado_id}
                      </TableCell>
                      <TableCell className="font-mono text-sm">
                        {emp.numero_documento}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-3 min-w-0">
                          <ProfileImage
                            src={emp.ruta_fotografia || ''}
                            alt={emp.nombre_completo}
                            size="md"
                            className="shrink-0"
                          />
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium truncate">
                              {emp.nombre_completo}
                            </p>
                            <p className="text-xs text-muted-foreground truncate">
                              {[emp.distrito_domicilio, emp.provincia_domicilio].filter(Boolean).join(', ')}
                            </p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="hidden md:table-cell">
                        {emp.ubicacion_actual ? (
                          <div>
                            <p className="text-sm font-medium">{emp.ubicacion_actual.area_siglas}</p>
                            <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                              {emp.ubicacion_actual.area_nombre}
                            </p>
                          </div>
                        ) : (
                          <span className="text-xs text-muted-foreground">Sin asignar</span>
                        )}
                      </TableCell>
                      <TableCell className="hidden lg:table-cell">
                        <div className="space-y-1">
                          {emp.correo_personal && (
                            <div className="flex items-center space-x-1 text-xs">
                              <Mail className="w-3 h-3 text-muted-foreground" />
                              <span className="truncate max-w-[180px]">{emp.correo_personal}</span>
                            </div>
                          )}
                          {emp.telefono_celular && (
                            <div className="flex items-center space-x-1 text-xs">
                              <Phone className="w-3 h-3 text-muted-foreground" />
                              <span>{emp.telefono_celular}</span>
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="hidden sm:table-cell text-center">
                        {emp.edad ?? '-'}
                      </TableCell>
                      <TableCell>
                        {getEstadoBadge(emp.estado_empleado)}
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
                            <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                            <DropdownMenuItem onClick={() => setEditTarget(emp)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Editar
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleDescargarPdf(emp.empleado_id, emp.nombre_completo)}>
                              <Download className="mr-2 h-4 w-4" />
                              Descargar PDF
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => handleVerLegajo(emp.empleado_id)}>
                              <FolderOpen className="mr-2 h-4 w-4" />
                              Legajo Digital
                            </DropdownMenuItem>
                            {/* Documentos condicionales por estado */}
                            {emp.estado_empleado === 'activo' && (
                              <>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={() => handleGenerarDocumento(emp, 'constancia')}>
                                  <FileText className="mr-2 h-4 w-4" />
                                  Constancia de Trabajo
                                </DropdownMenuItem>
                              </>
                            )}
                            {emp.estado_empleado === 'cesado' && (
                              <>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={() => handleGenerarDocumento(emp, 'certificado')}>
                                  <Award className="mr-2 h-4 w-4" />
                                  Certificado de Trabajo
                                </DropdownMenuItem>
                              </>
                            )}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          {/* Paginacion */}
          {totalCount > 0 && (
            <div className="flex items-center justify-between px-4 py-3 border-t">
              <p className="text-sm text-muted-foreground">
                Mostrando {((page - 1) * pageSize) + 1} - {Math.min(page * pageSize, totalCount)} de {totalCount}
              </p>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  disabled={page <= 1}
                  onClick={() => setPage(1)}
                >
                  <ChevronsLeft className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  disabled={page <= 1}
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-sm px-2">
                  Pagina {page} de {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  disabled={page >= totalPages}
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  disabled={page >= totalPages}
                  onClick={() => setPage(totalPages)}
                >
                  <ChevronsRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
