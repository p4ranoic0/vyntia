import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/components/ui/use-toast'
import {
    ConceptoRemuneracion,
    ConceptoRemuneracionPayload,
    ConfiguracionAfp,
    ConfiguracionAfpPayload,
    TipoConceptoRemuneracion,
    payrollService,
} from '@/services/payrollService'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Landmark, Pencil, Plus, Save, Trash2 } from 'lucide-react'
import { useMemo, useState, type ReactNode } from 'react'

type TabTipo = 'afp' | TipoConceptoRemuneracion

const TIPO_LABEL: Record<TabTipo, string> = {
  afp: 'AFP',
  ingreso: 'Ingresos',
  descuento: 'Descuentos',
}

type FormState = {
  tipo: TipoConceptoRemuneracion
  codigo: string
  nombre: string
  descripcion: string
  porcentaje: string
  monto_fijo: string
  aplica_base_imponible: boolean
  orden: string
  estado: 'activo' | 'inactivo'
}

const EMPTY_FORM: FormState = {
  tipo: 'ingreso',
  codigo: '',
  nombre: '',
  descripcion: '',
  porcentaje: '0',
  monto_fijo: '0',
  aplica_base_imponible: true,
  orden: '1',
  estado: 'activo',
}

function toPayload(form: FormState): ConceptoRemuneracionPayload {
  return {
    tipo: form.tipo,
    codigo: form.codigo.trim().toUpperCase(),
    nombre: form.nombre.trim(),
    descripcion: form.descripcion.trim(),
    porcentaje: Number(form.porcentaje || 0),
    monto_fijo: Number(form.monto_fijo || 0),
    aplica_base_imponible: form.aplica_base_imponible,
    orden: Number(form.orden || 1),
    status: form.estado,
  }
}

type AfpFormState = {
  afp_nombre: string
  vigencia_mes: string
  aporte_obligatorio_pct: string
  comision_flujo_pct: string
  comision_mixta_pct: string
  prima_seguro_pct: string
  remuneracion_max_asegurable: string
  estado: 'activo' | 'inactivo'
}

const EMPTY_AFP_FORM: AfpFormState = {
  afp_nombre: '',
  vigencia_mes: new Date().toISOString().slice(0, 7),
  aporte_obligatorio_pct: '10.000',
  comision_flujo_pct: '0.000',
  comision_mixta_pct: '0.000',
  prima_seguro_pct: '1.370',
  remuneracion_max_asegurable: '0.00',
  estado: 'activo',
}

function toAfpPayload(form: AfpFormState): ConfiguracionAfpPayload {
  return {
    afp_nombre: form.afp_nombre.trim().toUpperCase(),
    vigencia_mes: form.vigencia_mes,
    aporte_obligatorio_pct: Number(form.aporte_obligatorio_pct || 0),
    comision_flujo_pct: Number(form.comision_flujo_pct || 0),
    comision_mixta_pct: Number(form.comision_mixta_pct || 0),
    prima_seguro_pct: Number(form.prima_seguro_pct || 0),
    remuneracion_max_asegurable: Number(form.remuneracion_max_asegurable || 0),
    status: form.estado,
  }
}

// eslint-disable-next-line sonarjs/cognitive-complexity
export default function ConfiguracionRemuneracionesPage() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [tipo, setTipo] = useState<TabTipo>('afp')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editingAfpId, setEditingAfpId] = useState<number | null>(null)
  const [form, setForm] = useState<FormState>({ ...EMPTY_FORM, tipo: 'ingreso' })
  const [afpForm, setAfpForm] = useState<AfpFormState>(EMPTY_AFP_FORM)

  const { data: conceptos = [], isLoading } = useQuery({
    queryKey: ['config-remuneraciones', tipo],
    queryFn: () => payrollService.list({ tipo: tipo as TipoConceptoRemuneracion }),
    enabled: tipo !== 'afp',
  })

  const { data: afpConfigs = [], isLoading: isLoadingAfp } = useQuery({
    queryKey: ['config-afp'],
    queryFn: () => payrollService.listAfp(),
    enabled: tipo === 'afp',
  })

  const createMutation = useMutation({
    mutationFn: (payload: ConceptoRemuneracionPayload) => payrollService.create(payload),
    onSuccess: () => {
      toast({ title: 'Concepto creado', description: 'Se registró correctamente.' })
      setForm({ ...EMPTY_FORM, tipo: tipo as TipoConceptoRemuneracion })
      queryClient.invalidateQueries({ queryKey: ['config-remuneraciones'] })
    },
    onError: () => {
      toast({ title: 'Error', description: 'No se pudo crear el concepto.', variant: 'destructive' })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: ConceptoRemuneracionPayload }) => payrollService.update(id, payload),
    onSuccess: () => {
      toast({ title: 'Concepto actualizado', description: 'Los cambios fueron guardados.' })
      setEditingId(null)
      setForm({ ...EMPTY_FORM, tipo: tipo as TipoConceptoRemuneracion })
      queryClient.invalidateQueries({ queryKey: ['config-remuneraciones'] })
    },
    onError: () => {
      toast({ title: 'Error', description: 'No se pudo actualizar el concepto.', variant: 'destructive' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => payrollService.remove(id),
    onSuccess: () => {
      toast({ title: 'Concepto eliminado', description: 'Se eliminó del catálogo.' })
      queryClient.invalidateQueries({ queryKey: ['config-remuneraciones'] })
    },
    onError: () => {
      toast({ title: 'Error', description: 'No se pudo eliminar el concepto.', variant: 'destructive' })
    },
  })

  const resumen = useMemo(() => {
    if (tipo === 'afp') {
      const activos = afpConfigs.filter((item) => item.status === 'activo').length
      return { total: afpConfigs.length, activos }
    }
    const activos = conceptos.filter((item) => item.status === 'activo').length
    return { total: conceptos.length, activos }
  }, [afpConfigs, conceptos, tipo])

  const createAfpMutation = useMutation({
    mutationFn: (payload: ConfiguracionAfpPayload) => payrollService.createAfp(payload),
    onSuccess: () => {
      toast({ title: 'Configuración AFP creada', description: 'Se registró correctamente.' })
      setAfpForm(EMPTY_AFP_FORM)
      queryClient.invalidateQueries({ queryKey: ['config-afp'] })
    },
    onError: () => {
      toast({ title: 'Error', description: 'No se pudo crear la configuración AFP.', variant: 'destructive' })
    },
  })

  const updateAfpMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<ConfiguracionAfpPayload> }) => payrollService.updateAfp(id, payload),
    onSuccess: () => {
      toast({ title: 'Configuración AFP actualizada', description: 'Los cambios fueron guardados.' })
      setEditingAfpId(null)
      setAfpForm(EMPTY_AFP_FORM)
      queryClient.invalidateQueries({ queryKey: ['config-afp'] })
    },
    onError: () => {
      toast({ title: 'Error', description: 'No se pudo actualizar la configuración AFP.', variant: 'destructive' })
    },
  })

  const deleteAfpMutation = useMutation({
    mutationFn: (id: string) => payrollService.removeAfp(id),
    onSuccess: () => {
      toast({ title: 'Configuración AFP eliminada', description: 'Se eliminó del catálogo.' })
      queryClient.invalidateQueries({ queryKey: ['config-afp'] })
    },
    onError: () => {
      toast({ title: 'Error', description: 'No se pudo eliminar la configuración AFP.', variant: 'destructive' })
    },
  })

  const handleTipoChange = (value: string) => {
    const nuevoTipo = value as TabTipo
    setTipo(nuevoTipo)
    setEditingId(null)
    setEditingAfpId(null)
    if (nuevoTipo !== 'afp') {
      setForm({ ...EMPTY_FORM, tipo: nuevoTipo })
    }
  }

  const handleEdit = (item: ConceptoRemuneracion) => {
    setEditingId(item.id)
    setForm({
      tipo: item.tipo,
      codigo: item.codigo,
      nombre: item.nombre,
      descripcion: item.descripcion || '',
      porcentaje: String(item.porcentaje),
      monto_fijo: String(item.monto_fijo),
      aplica_base_imponible: item.aplica_base_imponible,
      orden: String(item.orden),
      estado: item.status,
    })
  }

  const handleSubmit = () => {
    if (tipo === 'afp') return

    const payload = toPayload(form)
    if (!payload.codigo || !payload.nombre) {
      toast({ title: 'Campos requeridos', description: 'Código y nombre son obligatorios.', variant: 'destructive' })
      return
    }

    if (editingId) {
      updateMutation.mutate({ id: editingId, payload })
      return
    }

    createMutation.mutate(payload)
  }

  const handleEditAfp = (item: ConfiguracionAfp) => {
    setEditingAfpId(item.id)
    setAfpForm({
      afp_nombre: item.afp_nombre,
      vigencia_mes: item.vigencia_mes,
      aporte_obligatorio_pct: String(item.aporte_obligatorio_pct),
      comision_flujo_pct: String(item.comision_flujo_pct),
      comision_mixta_pct: String(item.comision_mixta_pct),
      prima_seguro_pct: String(item.prima_seguro_pct),
      remuneracion_max_asegurable: String(item.remuneracion_max_asegurable),
      estado: item.status,
    })
  }

  const handleSubmitAfp = () => {
    const payload = toAfpPayload(afpForm)
    if (!payload.afp_nombre || !payload.vigencia_mes) {
      toast({ title: 'Campos requeridos', description: 'AFP y mes de vigencia son obligatorios.', variant: 'destructive' })
      return
    }
    if (payload.remuneracion_max_asegurable <= 0) {
      toast({ title: 'Validación', description: 'La remuneración máxima asegurable debe ser mayor a cero.', variant: 'destructive' })
      return
    }

    if (editingAfpId) {
      updateAfpMutation.mutate({ id: editingAfpId, payload })
      return
    }

    createAfpMutation.mutate(payload)
  }

  const loadingSave = createMutation.isPending || updateMutation.isPending
  const loadingAfpSave = createAfpMutation.isPending || updateAfpMutation.isPending
  let editorTitle = 'Nuevo concepto'
  let editorDescription = 'Configura porcentaje, monto fijo y comportamiento de base imponible.'

  if (tipo === 'afp') {
    editorTitle = editingAfpId ? 'Editar parámetros AFP' : 'Nuevo parámetro AFP'
    editorDescription = 'La AFP se mantiene en datos laborales; aquí se configuran sus porcentajes y topes.'
  } else if (editingId) {
    editorTitle = 'Editar concepto'
  }

  let tableContent: ReactNode
  let afpTableContent: ReactNode

  if (isLoading) {
    tableContent = (
      <TableRow>
        <TableCell colSpan={6} className="text-center text-muted-foreground">Cargando conceptos...</TableCell>
      </TableRow>
    )
  } else if (conceptos.length === 0) {
    tableContent = (
      <TableRow>
        <TableCell colSpan={6} className="text-center text-muted-foreground">No hay conceptos registrados para este tipo.</TableCell>
      </TableRow>
    )
  } else {
    tableContent = conceptos.map((item) => (
      <TableRow key={item.id}>
        <TableCell className="font-semibold">{item.codigo}</TableCell>
        <TableCell>
          <div className="font-medium">{item.nombre}</div>
          {item.descripcion && <div className="text-xs text-muted-foreground">{item.descripcion}</div>}
        </TableCell>
        <TableCell>{Number(item.porcentaje).toFixed(3)}</TableCell>
        <TableCell>{Number(item.monto_fijo).toFixed(2)}</TableCell>
        <TableCell>
          <Badge variant={item.status === 'activo' ? 'default' : 'secondary'}>
            {item.status}
          </Badge>
        </TableCell>
        <TableCell className="text-right">
          <div className="flex justify-end gap-2">
            <Button size="icon" variant="outline" onClick={() => handleEdit(item)}>
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="destructive"
              onClick={() => deleteMutation.mutate(item.id)}
              disabled={deleteMutation.isPending}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </TableCell>
      </TableRow>
    ))
  }

  if (isLoadingAfp) {
    afpTableContent = (
      <TableRow>
        <TableCell colSpan={9} className="text-center text-muted-foreground">Cargando configuración AFP...</TableCell>
      </TableRow>
    )
  } else if (afpConfigs.length === 0) {
    afpTableContent = (
      <TableRow>
        <TableCell colSpan={9} className="text-center text-muted-foreground">No hay configuración AFP registrada.</TableCell>
      </TableRow>
    )
  } else {
    afpTableContent = afpConfigs.map((item) => (
      <TableRow key={item.id}>
        <TableCell className="font-semibold">{item.afp_nombre}</TableCell>
        <TableCell>{item.vigencia_mes}</TableCell>
        <TableCell>{Number(item.aporte_obligatorio_pct).toFixed(3)}%</TableCell>
        <TableCell>{Number(item.comision_flujo_pct).toFixed(3)}%</TableCell>
        <TableCell>{Number(item.comision_mixta_pct).toFixed(3)}%</TableCell>
        <TableCell>{Number(item.prima_seguro_pct).toFixed(3)}%</TableCell>
        <TableCell>{Number(item.remuneracion_max_asegurable).toFixed(2)}</TableCell>
        <TableCell>
          <Badge variant={item.status === 'activo' ? 'default' : 'secondary'}>{item.status}</Badge>
        </TableCell>
        <TableCell className="text-right">
          <div className="flex justify-end gap-2">
            <Button size="icon" variant="outline" onClick={() => handleEditAfp(item)}>
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="destructive"
              onClick={() => deleteAfpMutation.mutate(item.id)}
              disabled={deleteAfpMutation.isPending}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </TableCell>
      </TableRow>
    ))
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-cyan-100 bg-gradient-to-r from-cyan-50 via-white to-emerald-50 p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Configuración de Remuneraciones</h1>
            <p className="text-sm text-slate-600">
              Tabla maestra para AFP, ingresos y descuentos aplicables a la planilla.
            </p>
          </div>
          <div className="flex gap-2">
            <Badge variant="secondary" className="bg-white/80 text-slate-700">Total: {resumen.total}</Badge>
            <Badge variant="secondary" className="bg-emerald-100 text-emerald-800">Activos: {resumen.activos}</Badge>
          </div>
        </div>
      </div>

      <Tabs value={tipo} onValueChange={handleTipoChange}>
        <TabsList className="grid w-full max-w-md grid-cols-3">
          <TabsTrigger value="afp">AFP</TabsTrigger>
          <TabsTrigger value="ingreso">Ingresos</TabsTrigger>
          <TabsTrigger value="descuento">Descuentos</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="grid gap-6 xl:grid-cols-[1.35fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>{tipo === 'afp' ? 'Parámetros AFP' : `Conceptos de ${TIPO_LABEL[tipo]}`}</CardTitle>
            <CardDescription>
              {tipo === 'afp'
                ? 'Define aporte obligatorio, comisiones, prima de seguro y remuneración máxima asegurable.'
                : 'Administra los conceptos visibles en cálculos y reportes.'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                {tipo === 'afp' ? (
                  <TableRow>
                    <TableHead>AFP</TableHead>
                    <TableHead>Vigencia</TableHead>
                    <TableHead>Aporte</TableHead>
                    <TableHead>Comisión Flujo</TableHead>
                    <TableHead>Comisión Mixta</TableHead>
                    <TableHead>Prima Seguro</TableHead>
                    <TableHead>Rem. Máx. Asegurable</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead className="text-right">Acciones</TableHead>
                  </TableRow>
                ) : (
                  <TableRow>
                    <TableHead>Código</TableHead>
                    <TableHead>Nombre</TableHead>
                    <TableHead>%</TableHead>
                    <TableHead>Monto</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead className="text-right">Acciones</TableHead>
                  </TableRow>
                )}
              </TableHeader>
              <TableBody>{tipo === 'afp' ? afpTableContent : tableContent}</TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{editorTitle}</CardTitle>
            <CardDescription>{editorDescription}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {tipo === 'afp' ? (
              <>
                <div className="grid gap-2">
                  <Label htmlFor="afp_nombre">AFP</Label>
                  <Input id="afp_nombre" value={afpForm.afp_nombre} onChange={(e) => setAfpForm((prev) => ({ ...prev, afp_nombre: e.target.value }))} placeholder="Ej. HABITAT" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="vigencia_mes">Mes de Vigencia (YYYY-MM)</Label>
                  <Input id="vigencia_mes" value={afpForm.vigencia_mes} onChange={(e) => setAfpForm((prev) => ({ ...prev, vigencia_mes: e.target.value }))} placeholder="2026-03" />
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="grid gap-2">
                    <Label htmlFor="aporte_obligatorio_pct">Aporte Obligatorio %</Label>
                    <Input id="aporte_obligatorio_pct" type="number" step="0.001" value={afpForm.aporte_obligatorio_pct} onChange={(e) => setAfpForm((prev) => ({ ...prev, aporte_obligatorio_pct: e.target.value }))} />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="prima_seguro_pct">Prima Seguro %</Label>
                    <Input id="prima_seguro_pct" type="number" step="0.001" value={afpForm.prima_seguro_pct} onChange={(e) => setAfpForm((prev) => ({ ...prev, prima_seguro_pct: e.target.value }))} />
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="grid gap-2">
                    <Label htmlFor="comision_flujo_pct">Comisión Flujo %</Label>
                    <Input id="comision_flujo_pct" type="number" step="0.001" value={afpForm.comision_flujo_pct} onChange={(e) => setAfpForm((prev) => ({ ...prev, comision_flujo_pct: e.target.value }))} />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="comision_mixta_pct">Comisión Mixta %</Label>
                    <Input id="comision_mixta_pct" type="number" step="0.001" value={afpForm.comision_mixta_pct} onChange={(e) => setAfpForm((prev) => ({ ...prev, comision_mixta_pct: e.target.value }))} />
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="grid gap-2">
                    <Label htmlFor="remuneracion_max_asegurable">Remuneración Máx. Asegurable</Label>
                    <Input id="remuneracion_max_asegurable" type="number" step="0.01" value={afpForm.remuneracion_max_asegurable} onChange={(e) => setAfpForm((prev) => ({ ...prev, remuneracion_max_asegurable: e.target.value }))} />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="estado_afp">Estado</Label>
                    <Select value={afpForm.estado} onValueChange={(value) => setAfpForm((prev) => ({ ...prev, estado: value as 'activo' | 'inactivo' }))}>
                      <SelectTrigger id="estado_afp"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="activo">Activo</SelectItem>
                        <SelectItem value="inactivo">Inactivo</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <Button className="flex-1" onClick={handleSubmitAfp} disabled={loadingAfpSave}>
                    {editingAfpId ? <Save className="mr-2 h-4 w-4" /> : <Plus className="mr-2 h-4 w-4" />}
                    {editingAfpId ? 'Guardar parámetros' : 'Crear parámetros AFP'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setEditingAfpId(null)
                      setAfpForm(EMPTY_AFP_FORM)
                    }}
                  >
                    Limpiar
                  </Button>
                </div>
              </>
            ) : (
              <>
                <div className="grid gap-2">
                  <Label htmlFor="codigo">Código</Label>
                  <Input id="codigo" value={form.codigo} onChange={(e) => setForm((prev) => ({ ...prev, codigo: e.target.value }))} placeholder="Ej. BONO_PRODUCTIVIDAD" />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="nombre">Nombre</Label>
                  <Input id="nombre" value={form.nombre} onChange={(e) => setForm((prev) => ({ ...prev, nombre: e.target.value }))} placeholder="Nombre del concepto" />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="descripcion">Descripción</Label>
                  <Input id="descripcion" value={form.descripcion} onChange={(e) => setForm((prev) => ({ ...prev, descripcion: e.target.value }))} placeholder="Opcional" />
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="grid gap-2">
                    <Label htmlFor="porcentaje">Porcentaje</Label>
                    <Input id="porcentaje" type="number" step="0.001" value={form.porcentaje} onChange={(e) => setForm((prev) => ({ ...prev, porcentaje: e.target.value }))} />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="monto_fijo">Monto fijo</Label>
                    <Input id="monto_fijo" type="number" step="0.01" value={form.monto_fijo} onChange={(e) => setForm((prev) => ({ ...prev, monto_fijo: e.target.value }))} />
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="grid gap-2">
                    <Label htmlFor="orden">Orden</Label>
                    <Input id="orden" type="number" min="1" value={form.orden} onChange={(e) => setForm((prev) => ({ ...prev, orden: e.target.value }))} />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="estado">Estado</Label>
                    <Select value={form.estado} onValueChange={(value) => setForm((prev) => ({ ...prev, estado: value as 'activo' | 'inactivo' }))}>
                      <SelectTrigger id="estado"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="activo">Activo</SelectItem>
                        <SelectItem value="inactivo">Inactivo</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <p className="text-sm font-medium">Aplica a base imponible</p>
                    <p className="text-xs text-muted-foreground">Útil para distinguir deducibles y no deducibles.</p>
                  </div>
                  <Switch
                    checked={form.aplica_base_imponible}
                    onCheckedChange={(checked) => setForm((prev) => ({ ...prev, aplica_base_imponible: checked }))}
                  />
                </div>

                <div className="flex gap-2 pt-2">
                  <Button className="flex-1" onClick={handleSubmit} disabled={loadingSave}>
                    {editingId ? <Save className="mr-2 h-4 w-4" /> : <Plus className="mr-2 h-4 w-4" />}
                    {editingId ? 'Guardar cambios' : 'Crear concepto'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setEditingId(null)
                      setForm({ ...EMPTY_FORM, tipo: tipo === 'afp' ? 'ingreso' : tipo })
                    }}
                  >
                    Limpiar
                  </Button>
                </div>
              </>
            )}

            <div className="rounded-lg bg-slate-50 p-3 text-xs text-slate-600">
              <div className="mb-1 flex items-center gap-2 font-medium text-slate-800">
                <Landmark className="h-4 w-4" />
                Recomendación
              </div>
              Mantén alineada esta configuración con los valores vigentes publicados por SBS para evitar diferencias en nómina.
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
