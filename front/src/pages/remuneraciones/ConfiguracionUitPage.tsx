import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useToast } from '@/components/ui/use-toast'
import {
  useActivarUit,
  useConfiguracionUit,
  useCreateUit,
  useDeleteUit,
  useUpdateUit,
} from '@/hooks/useRemuneraciones'
import { ConfiguracionUitPayload } from '@/services/remuneracionesService'
import { CheckCircle2, Landmark, Pencil, Plus, Save, Trash2 } from 'lucide-react'
import { useMemo, useState, type ReactNode } from 'react'

type FormState = {
  anio: string
  valor_uit: string
  tope_renta_cuarta_uit: string
  porcentaje_renta_cuarta: string
  estado: 'activo' | 'inactivo'
}

const EMPTY_FORM: FormState = {
  anio: String(new Date().getFullYear()),
  valor_uit: '5150.00',
  tope_renta_cuarta_uit: '45',
  porcentaje_renta_cuarta: '8.00',
  estado: 'activo',
}

function toPayload(form: FormState): ConfiguracionUitPayload {
  return {
    anio: Number(form.anio),
    valor_uit: Number(form.valor_uit || 0),
    tope_renta_cuarta_uit: Number(form.tope_renta_cuarta_uit || 45),
    porcentaje_renta_cuarta: Number(form.porcentaje_renta_cuarta || 8),
    estado: form.estado,
  }
}

export default function ConfiguracionUitPage() {
  const { toast } = useToast()
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState<FormState>(EMPTY_FORM)

  const { data: configs = [], isLoading } = useConfiguracionUit()

  const createMutation = useCreateUit()
  const updateMutation = useUpdateUit()
  const deleteMutation = useDeleteUit()
  const activarMutation = useActivarUit()

  const resumen = useMemo(() => {
    const activos = configs.filter((item) => item.estado === 'activo').length
    return { total: configs.length, activos }
  }, [configs])

  const handleEdit = (item: typeof configs[0]) => {
    setEditingId(item.configuracion_uit_id)
    setForm({
      anio: String(item.anio),
      valor_uit: String(item.valor_uit),
      tope_renta_cuarta_uit: String(item.tope_renta_cuarta_uit),
      porcentaje_renta_cuarta: String(item.porcentaje_renta_cuarta),
      estado: item.estado,
    })
  }

  const handleSubmit = () => {
    const payload = toPayload(form)

    if (!payload.anio || payload.anio < 2020 || payload.anio > 2100) {
      toast({
        title: 'Validación',
        description: 'El año debe estar entre 2020 y 2100.',
        variant: 'destructive',
      })
      return
    }

    if (payload.valor_uit <= 0) {
      toast({
        title: 'Validación',
        description: 'El valor UIT debe ser mayor a cero.',
        variant: 'destructive',
      })
      return
    }

    if (editingId) {
      updateMutation.mutate(
        { id: editingId, data: payload },
        {
          onSuccess: () => {
            toast({ title: 'UIT actualizada', description: 'Los cambios fueron guardados.' })
            setEditingId(null)
            setForm(EMPTY_FORM)
          },
          onError: () => {
            toast({
              title: 'Error',
              description: 'No se pudo actualizar la configuración UIT.',
              variant: 'destructive',
            })
          },
        }
      )
      return
    }

    createMutation.mutate(payload, {
      onSuccess: () => {
        toast({ title: 'UIT creada', description: 'Se registró correctamente.' })
        setForm(EMPTY_FORM)
      },
      onError: (error) => {
        const message =
          error?.response?.data?.message || 'No se pudo crear la configuración UIT.'
        toast({ title: 'Error', description: message, variant: 'destructive' })
      },
    })
  }

  const handleActivar = (id: number, anio: number) => {
    activarMutation.mutate(id, {
      onSuccess: () => {
        toast({
          title: 'UIT activada',
          description: `La UIT del año ${anio} fue activada. Otras UIT del mismo año se desactivaron.`,
        })
      },
      onError: () => {
        toast({
          title: 'Error',
          description: 'No se pudo activar la configuración UIT.',
          variant: 'destructive',
        })
      },
    })
  }

  const handleDelete = (id: number) => {
    if (!confirm('¿Estás seguro de eliminar esta configuración UIT?')) return

    deleteMutation.mutate(id, {
      onSuccess: () => {
        toast({ title: 'UIT eliminada', description: 'Se eliminó del catálogo.' })
      },
      onError: () => {
        toast({
          title: 'Error',
          description: 'No se pudo eliminar la configuración UIT.',
          variant: 'destructive',
        })
      },
    })
  }

  const loadingSave = createMutation.isPending || updateMutation.isPending
  const editorTitle = editingId ? 'Editar configuración UIT' : 'Nueva configuración UIT'
  const editorDescription = editingId
    ? 'Modifica los valores de la Unidad Impositiva Tributaria.'
    : 'Define los valores de la Unidad Impositiva Tributaria para cálculos de planilla.'

  let tableContent: ReactNode

  if (isLoading) {
    tableContent = (
      <TableRow>
        <TableCell colSpan={8} className="text-center text-muted-foreground">
          Cargando configuración UIT...
        </TableCell>
      </TableRow>
    )
  } else if (configs.length === 0) {
    tableContent = (
      <TableRow>
        <TableCell colSpan={8} className="text-center text-muted-foreground">
          No hay configuración UIT registrada.
        </TableCell>
      </TableRow>
    )
  } else {
    tableContent = configs.map((item) => (
      <TableRow key={item.configuracion_uit_id}>
        <TableCell className="font-semibold">{item.anio}</TableCell>
        <TableCell className="text-right">S/ {Number(item.valor_uit).toFixed(2)}</TableCell>
        <TableCell className="text-center">{item.tope_renta_cuarta_uit}</TableCell>
        <TableCell className="text-right">S/ {Number(item.tope_renta_cuarta_soles).toFixed(2)}</TableCell>
        <TableCell className="text-center">{Number(item.porcentaje_renta_cuarta).toFixed(2)}%</TableCell>
        <TableCell className="text-right">S/ {Number(item.essalud_cas_mensual).toFixed(2)}</TableCell>
        <TableCell>
          <Badge variant={item.estado === 'activo' ? 'default' : 'secondary'}>
            {item.estado}
          </Badge>
        </TableCell>
        <TableCell className="text-right">
          <div className="flex justify-end gap-2">
            {item.estado === 'inactivo' && (
              <Button
                size="icon"
                variant="outline"
                className="border-emerald-300 bg-emerald-50 text-emerald-700 hover:bg-emerald-100"
                onClick={() => handleActivar(item.configuracion_uit_id, item.anio)}
                disabled={activarMutation.isPending}
                title="Activar esta UIT"
              >
                <CheckCircle2 className="h-4 w-4" />
              </Button>
            )}
            <Button size="icon" variant="outline" onClick={() => handleEdit(item)}>
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="destructive"
              onClick={() => handleDelete(item.configuracion_uit_id)}
              disabled={deleteMutation.isPending}
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
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Configuración de UIT
            </h1>
            <p className="text-sm text-slate-600">
              Gestiona los valores anuales de la Unidad Impositiva Tributaria para cálculos
              de planilla.
            </p>
          </div>
          <div className="flex gap-2">
            <Badge variant="secondary" className="bg-white/80 text-slate-700">
              Total: {resumen.total}
            </Badge>
            <Badge variant="secondary" className="bg-emerald-100 text-emerald-800">
              Activos: {resumen.activos}
            </Badge>
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Valores de UIT registrados</CardTitle>
            <CardDescription>
              Solo puede haber una UIT activa por año. El valor UIT se usa para calcular ESSALUD
              CAS y límites de Renta de 4ta categoría.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Año</TableHead>
                  <TableHead className="text-right">Valor UIT</TableHead>
                  <TableHead className="text-center">Tope Renta 4ta (UITs)</TableHead>
                  <TableHead className="text-right">Tope (soles)</TableHead>
                  <TableHead className="text-center">% Renta 4ta</TableHead>
                  <TableHead className="text-right">ESSALUD CAS</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>{tableContent}</TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{editorTitle}</CardTitle>
            <CardDescription>{editorDescription}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="anio">Año</Label>
              <Input
                id="anio"
                type="number"
                min="2020"
                max="2100"
                value={form.anio}
                onChange={(e) => setForm((prev) => ({ ...prev, anio: e.target.value }))}
                placeholder="2026"
              />
              <p className="text-xs text-muted-foreground">Rango permitido: 2020 - 2100</p>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="valor_uit">Valor UIT (S/)</Label>
              <Input
                id="valor_uit"
                type="number"
                step="0.01"
                min="0.01"
                value={form.valor_uit}
                onChange={(e) => setForm((prev) => ({ ...prev, valor_uit: e.target.value }))}
                placeholder="5150.00"
              />
              <p className="text-xs text-muted-foreground">
                Valor oficial de la UIT establecido por el gobierno
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="grid gap-2">
                <Label htmlFor="tope_renta_cuarta_uit">Tope Renta 4ta (UITs)</Label>
                <Input
                  id="tope_renta_cuarta_uit"
                  type="number"
                  step="1"
                  min="1"
                  value={form.tope_renta_cuarta_uit}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, tope_renta_cuarta_uit: e.target.value }))
                  }
                  placeholder="45"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="porcentaje_renta_cuarta">% Renta 4ta</Label>
                <Input
                  id="porcentaje_renta_cuarta"
                  type="number"
                  step="0.01"
                  min="0"
                  max="100"
                  value={form.porcentaje_renta_cuarta}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, porcentaje_renta_cuarta: e.target.value }))
                  }
                  placeholder="8.00"
                />
              </div>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="estado">Estado</Label>
              <Select
                value={form.estado}
                onValueChange={(value) =>
                  setForm((prev) => ({ ...prev, estado: value as 'activo' | 'inactivo' }))
                }
              >
                <SelectTrigger id="estado">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="activo">Activo</SelectItem>
                  <SelectItem value="inactivo">Inactivo</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex gap-2 pt-2">
              <Button className="flex-1" onClick={handleSubmit} disabled={loadingSave}>
                {editingId ? <Save className="mr-2 h-4 w-4" /> : <Plus className="mr-2 h-4 w-4" />}
                {editingId ? 'Guardar cambios' : 'Crear configuración UIT'}
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setEditingId(null)
                  setForm(EMPTY_FORM)
                }}
              >
                Limpiar
              </Button>
            </div>

            <div className="rounded-lg bg-slate-50 p-3 text-xs text-slate-600">
              <div className="mb-1 flex items-center gap-2 font-medium text-slate-800">
                <Landmark className="h-4 w-4" />
                Sobre la UIT
              </div>
              <ul className="ml-6 list-disc space-y-1">
                <li>La UIT se usa para calcular ESSALUD de trabajadores CAS (9% de 45% UIT mensual)</li>
                <li>
                  El tope de Renta 4ta categoría determina cuándo aplicar el {form.porcentaje_renta_cuarta}% de
                  retención
                </li>
                <li>Solo puede haber una UIT activa por año para evitar inconsistencias</li>
                <li>Los valores computados (tope en soles, ESSALUD CAS) se calculan automáticamente</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
