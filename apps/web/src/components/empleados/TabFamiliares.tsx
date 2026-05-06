import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
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
import { Documento, legajoService } from '@/services/legajoService'
import { Edit, Plus, Trash2 } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { AdminDocUpload } from './AdminDocUpload'

const PARENTESCO_OPTIONS = [
  { value: 'conyuge', label: 'Conyuge' },
  { value: 'conviviente', label: 'Conviviente' },
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

function getRequiredDocTypes(parentesco: string): Array<{ tipo: string; label: string }> {
  const base = [{ tipo: 'dni_familiar', label: 'DNI del familiar' }]
  if (parentesco === 'hijo' || parentesco === 'padre' || parentesco === 'madre') {
    return [...base, { tipo: 'certificado_nacimiento', label: 'Partida de nacimiento' }]
  }
  if (parentesco === 'conyuge' || parentesco === 'conviviente') {
    return [...base, { tipo: 'acta_matrimonio', label: 'Acta de matrimonio / Cert. union de hecho' }]
  }
  return base
}

interface TabFamiliaresProps {
  empleadoId: string
}

export function TabFamiliares({ empleadoId }: TabFamiliaresProps) {
  const [familiares, setFamiliares] = useState<any[]>([])
  const [editingId, setEditingId] = useState<number | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ ...FAMILIAR_EMPTY })
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)
  // Documentos existentes por familiar
  const [familiarDocs, setFamiliarDocs] = useState<Record<number, Documento[]>>({})

  const reload = useCallback(() => {
    setFetching(true)
    employeesService.datosFamiliares.getAll(empleadoId).then((data: any) => {
      const raw = data?.data?.results ?? data?.results ?? data?.data ?? data
      setFamiliares(Array.isArray(raw) ? raw : [])
    }).catch(() => setFamiliares([])).finally(() => setFetching(false))
  }, [empleadoId])

  const loadDocs = useCallback(() => {
    legajoService.getByEmpleado(empleadoId, 'personal').then(docs => {
      // Agrupar docs por familiar_id (si el backend lo provee) o por tipo
      const grouped: Record<string, Documento[]> = {}
      for (const doc of docs) {
        // Los docs familiares usan un campo referencia libre o el nombre contiene info
        const refId = (doc as Documento & { familiar_id?: string }).familiar_id || ''
        if (!grouped[refId]) grouped[refId] = []
        grouped[refId].push(doc)
      }
      setFamiliarDocs(grouped)
    }).catch(() => {/* silent */})
  }, [empleadoId])

  useEffect(() => { reload(); loadDocs() }, [reload, loadDocs])

  const startEdit = (fam: any) => {
    setEditingId(fam.id)
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

  const handleDelete = async (id: string) => {
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
        <div className="space-y-2">
          {familiares.map((fam: any) => {
            const famId = fam.id
            const requiredDocs = getRequiredDocTypes(fam.parentesco || '')
            return (
              <div key={famId} className="border rounded-md p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">
                      {fam.nombres_familiar} {fam.apellido_paterno} {fam.apellido_materno}
                    </p>
                    <p className="text-xs text-muted-foreground capitalize">
                      {fam.parentesco} {fam.numero_documento ? `• DNI: ${fam.numero_documento}` : ''}
                    </p>
                  </div>
                  <div className="flex gap-1">
                    <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => startEdit(fam)}>
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button size="icon" variant="ghost" className="h-7 w-7 text-destructive" onClick={() => handleDelete(famId)}>
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
                {/* Document uploads per familiar */}
                <div className="space-y-1.5 pt-1 border-t">
                  <p className="text-xs font-medium text-muted-foreground">Documentos requeridos</p>
                  {requiredDocs.map(docType => {
                    // Match existing doc: search in all docs for this empleado that match tipo
                    const allDocs = familiarDocs[0] || []
                    const existingDoc = allDocs.find(d =>
                      d.tipo_documento === docType.tipo &&
                      (d.nombre_documento || '').toLowerCase().includes((fam.nombres_familiar || '').toLowerCase().slice(0, 5))
                    ) || null
                    return (
                      <AdminDocUpload
                        key={`${famId}-${docType.tipo}`}
                        empleadoId={empleadoId}
                        tipoDocumento={docType.tipo}
                        categoria="personal"
                        label={`${docType.label} - ${fam.nombres_familiar || 'Familiar'}`}
                        existing={existingDoc ? {
                          documento_id: existingDoc.id,
                          nombre_documento: existingDoc.nombre_documento,
                          archivo: existingDoc.archivo,
                        } : null}
                        onUploaded={loadDocs}
                        onDeleted={loadDocs}
                        compact
                      />
                    )
                  })}
                </div>
              </div>
            )
          })}
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
