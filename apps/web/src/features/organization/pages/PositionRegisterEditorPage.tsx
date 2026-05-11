import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, Download, ShieldCheck } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui/table'

import {
  publicPositionService,
  type PositionRegister,
  type PositionRegisterEntry,
  type RegisterType,
} from '../services/publicPositionService'
import { useTenantSector } from '../hooks/useTenantSector'

const STATUS_VARIANT: Record<
  PositionRegister['status'],
  'secondary' | 'default' | 'outline'
> = {
  draft: 'secondary',
  approved: 'default',
  registered_servir: 'default',
  superseded: 'outline',
  archived: 'outline',
}

interface Props {
  defaultType?: RegisterType
}

export default function PositionRegisterEditorPage({ defaultType }: Readonly<Props>) {
  const { id, type: routeType } = useParams<{ id: string; type?: string }>()
  const navigate = useNavigate()
  const sector = useTenantSector()
  const type: RegisterType = defaultType ?? (routeType === 'cap' ? 'cap' : 'cpe')

  const [register, setRegister] = useState<PositionRegister | null>(null)
  const [entries, setEntries] = useState<PositionRegisterEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [approving, setApproving] = useState(false)
  const [servirOpen, setServirOpen] = useState(false)
  const [servirRef, setServirRef] = useState('')
  const [servirSubmitting, setServirSubmitting] = useState(false)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    if (!id) return
    let cancelled = false
    ;(async () => {
      try {
        const [reg, ent] = await Promise.all([
          publicPositionService.getRegister(id),
          publicPositionService.listEntries(id),
        ])
        if (cancelled) return
        setRegister(reg)
        setEntries(ent)
      } catch (e) {
        if (cancelled) return
        toast.error(
          `Error cargando registro: ${e instanceof Error ? e.message : 'desconocido'}`,
        )
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [id])

  if (sector !== 'public') {
    return (
      <Card className="m-6">
        <CardHeader>
          <CardTitle>CPE/CAP no aplicable</CardTitle>
          <CardDescription>
            Su tenant es sector privado. Use el módulo CCF (B.7) en su lugar.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (loading) {
    return <p className="p-6 text-muted-foreground">Cargando registro…</p>
  }
  if (!register) {
    return (
      <Card className="m-6">
        <CardContent className="py-6 text-center text-muted-foreground">
          Registro no encontrado.
        </CardContent>
      </Card>
    )
  }

  async function handleApprove() {
    if (!register) return
    setApproving(true)
    try {
      const updated = await publicPositionService.approveRegister(register.id)
      setRegister(updated)
      toast.success(`${updated.register_type_display} aprobado`)
    } catch (e) {
      toast.error(`Error aprobando: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setApproving(false)
    }
  }

  async function handleRegisterServir() {
    if (!register || !servirRef.trim()) {
      toast.error('La referencia SERVIR es requerida')
      return
    }
    setServirSubmitting(true)
    try {
      const updated = await publicPositionService.registerInServir(
        register.id,
        servirRef.trim(),
      )
      setRegister(updated)
      setServirOpen(false)
      setServirRef('')
      toast.success('CPE registrado en SERVIR')
    } catch (e) {
      toast.error(
        `Error registrando en SERVIR: ${e instanceof Error ? e.message : 'desconocido'}`,
      )
    } finally {
      setServirSubmitting(false)
    }
  }

  async function handleDownloadMPP() {
    if (!register) return
    setDownloading(true)
    try {
      const blob = await publicPositionService.downloadMPP(register.id)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `mpp_${register.title.replace(/\s+/g, '_')}_v${register.version}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (e) {
      toast.error(
        `Error descargando MPP: ${e instanceof Error ? e.message : 'desconocido'}`,
      )
    } finally {
      setDownloading(false)
    }
  }

  const isCpe = register.register_type === 'cpe'
  const canApprove = register.status === 'draft'
  const canRegisterServir =
    isCpe && register.status === 'approved' && !register.servir_registered_at
  const canDownloadMpp = isCpe

  return (
    <div className="p-6 space-y-6">
      <Button variant="ghost" onClick={() => navigate(`/organizacion/registros/${type}`)}>
        <ArrowLeft className="h-4 w-4 mr-2" />
        Volver al listado
      </Button>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div>
              <CardTitle className="text-xl">{register.title}</CardTitle>
              <CardDescription>
                {register.register_type_display} · v{register.version}
                {register.effective_date && ` · efectivo desde ${register.effective_date}`}
              </CardDescription>
              {register.description && (
                <p className="text-sm text-muted-foreground mt-2 max-w-3xl">
                  {register.description}
                </p>
              )}
            </div>
            <div className="flex flex-col items-end gap-2">
              <Badge variant={STATUS_VARIANT[register.status]}>
                {register.status_display}
              </Badge>
              {register.servir_registration_ref && (
                <span className="text-xs text-muted-foreground">
                  SERVIR ref: {register.servir_registration_ref}
                </span>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-2">
            {canApprove && (
              <Button onClick={handleApprove} disabled={approving}>
                <CheckCircle2 className="h-4 w-4 mr-2" />
                {approving ? 'Aprobando…' : 'Aprobar'}
              </Button>
            )}
            {canRegisterServir && (
              <Dialog open={servirOpen} onOpenChange={setServirOpen}>
                <Button variant="outline" onClick={() => setServirOpen(true)}>
                  <ShieldCheck className="h-4 w-4 mr-2" />
                  Registrar en SERVIR
                </Button>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Registrar CPE en SERVIR</DialogTitle>
                    <DialogDescription>
                      Una vez registrado en SERVIR (proceso manual), ingrese la
                      referencia oficial para trazabilidad.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-2 py-2">
                    <Label htmlFor="servir-ref">Referencia SERVIR *</Label>
                    <Input
                      id="servir-ref"
                      value={servirRef}
                      onChange={(e) => setServirRef(e.target.value)}
                      placeholder="SERVIR-2026-MEF-001"
                    />
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setServirOpen(false)}>
                      Cancelar
                    </Button>
                    <Button onClick={handleRegisterServir} disabled={servirSubmitting}>
                      {servirSubmitting ? 'Registrando…' : 'Registrar'}
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            )}
            {canDownloadMpp && (
              <Button variant="outline" onClick={handleDownloadMPP} disabled={downloading}>
                <Download className="h-4 w-4 mr-2" />
                {downloading ? 'Generando…' : 'Descargar MPP (PDF)'}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            Puestos del {register.register_type.toUpperCase()} ({entries.length})
          </CardTitle>
          <CardDescription>
            {isCpe
              ? 'Cada fila representa un puesto del Cuadro de Puestos de la Entidad — Ley 30057 SERVIR.'
              : 'Cada fila representa un cargo del Cuadro de Asignación de Personal — DL 276 / 728.'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {entries.length === 0 ? (
            <p className="text-sm text-muted-foreground py-6 text-center">
              No hay puestos en este registro. Agregue puestos vía API o
              importación masiva (próximamente desde esta interfaz).
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">#</TableHead>
                  <TableHead>Plaza</TableHead>
                  <TableHead>Puesto</TableHead>
                  {isCpe && <TableHead>Nivel organizacional</TableHead>}
                  {isCpe && <TableHead>Nivel remunerativo</TableHead>}
                  {!isCpe && <TableHead>Clasificación CAP</TableHead>}
                  <TableHead>Plazas</TableHead>
                  <TableHead>Situación</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {entries.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell className="font-mono">{entry.sequence}</TableCell>
                    <TableCell className="font-mono text-xs">
                      {entry.plaza_code || '—'}
                    </TableCell>
                    <TableCell>
                      <div className="font-medium">{entry.position_name}</div>
                      <div className="text-xs text-muted-foreground">
                        {entry.position_code}
                      </div>
                    </TableCell>
                    {isCpe && (
                      <TableCell className="text-sm">
                        {entry.nivel_organizacional || '—'}
                      </TableCell>
                    )}
                    {isCpe && (
                      <TableCell className="text-sm">
                        {entry.nivel_remunerativo || '—'}
                      </TableCell>
                    )}
                    {!isCpe && (
                      <TableCell className="text-sm">
                        {entry.clasificacion_cap_display || '—'}
                      </TableCell>
                    )}
                    <TableCell>{entry.plaza_count}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{entry.situacion_display}</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
