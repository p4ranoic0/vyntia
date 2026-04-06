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
import { useAreas } from '@/hooks/useApi'
import { employeesService } from '@/services/employeesService'
import { Documento, legajoService } from '@/services/legajoService'
import { Briefcase } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { AdminDocUpload } from './AdminDocUpload'

interface TabLaboralesProps {
  empleadoId: number
}

export function TabLaborales({ empleadoId }: TabLaboralesProps) {
  const { data: areasData } = useAreas()
  const areasRaw: any = (areasData as any)?.data ?? areasData
  const areas: any[] = areasRaw?.results ?? (Array.isArray(areasRaw) ? areasRaw : [])

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
  const [laboralDocs, setLaboralDocs] = useState<Documento[]>([])

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

  const loadDocs = useCallback(() => {
    legajoService.getByEmpleado(empleadoId, 'laboral').then(docs => {
      setLaboralDocs(docs.filter(d =>
        ['constancia_trabajo', 'certificado_trabajo', 'carta_recomendacion'].includes(d.tipo_documento)
      ))
    }).catch(() => setLaboralDocs([]))
  }, [empleadoId])

  useEffect(() => { loadDocs() }, [loadDocs])

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

      {/* Documentos laborales: Constancias / Certificados de trabajo */}
      <div className="border-t pt-4 space-y-3">
        <div className="flex items-center gap-2">
          <Briefcase className="h-4 w-4 text-muted-foreground" />
          <p className="text-sm font-semibold text-muted-foreground">Documentos laborales (experiencia previa)</p>
        </div>
        <p className="text-xs text-muted-foreground">
          Adjunte constancias de trabajo, certificados laborales o cartas de recomendacion de empleos anteriores (PDF).
        </p>

        {laboralDocs.length > 0 && (
          <div className="space-y-1.5">
            {laboralDocs.map(doc => (
              <AdminDocUpload
                key={doc.documento_id}
                empleadoId={empleadoId}
                tipoDocumento={doc.tipo_documento}
                categoria="laboral"
                label={doc.nombre_documento}
                existing={{
                  documento_id: doc.documento_id,
                  nombre_documento: doc.nombre_documento,
                  archivo: doc.archivo,
                }}
                onUploaded={loadDocs}
                onDeleted={loadDocs}
                compact
              />
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 gap-2">
          <AdminDocUpload
            empleadoId={empleadoId}
            tipoDocumento="constancia_trabajo"
            categoria="laboral"
            label="Constancia de trabajo"
            onUploaded={loadDocs}
            compact
          />
          <AdminDocUpload
            empleadoId={empleadoId}
            tipoDocumento="certificado_trabajo"
            categoria="laboral"
            label="Certificado de trabajo"
            onUploaded={loadDocs}
            compact
          />
          <AdminDocUpload
            empleadoId={empleadoId}
            tipoDocumento="carta_recomendacion"
            categoria="laboral"
            label="Carta de recomendacion"
            onUploaded={loadDocs}
            compact
          />
        </div>
      </div>
    </div>
  )
}
