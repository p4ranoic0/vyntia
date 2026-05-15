import { useEffect, useState } from 'react'
import { Download, MoveRight, Workflow } from 'lucide-react'
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
  displacementService,
  type Displacement,
  type DisplacementStatus,
} from '../services/displacementService'

const STATUS_VARIANT: Record<
  DisplacementStatus,
  'secondary' | 'default' | 'outline' | 'destructive'
> = {
  draft: 'secondary',
  pending_supervisor: 'outline',
  pending_hr: 'outline',
  pending_titular: 'outline',
  approved: 'default',
  active: 'default',
  completed: 'default',
  cancelled: 'destructive',
}

function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(url)
}

export default function DisplacementListPage() {
  const [items, setItems] = useState<Displacement[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  const reload = () => {
    setLoading(true)
    displacementService
      .list()
      .then(setItems)
      .catch((e) =>
        toast.error(
          `Error cargando desplazamientos: ${e instanceof Error ? e.message : 'desconocido'}`,
        ),
      )
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])

  const handleSubmit = async (id: string) => {
    setBusyId(id)
    try {
      await displacementService.submit(id)
      toast.success('Desplazamiento enviado a aprobación')
      reload()
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleActivate = async (id: string) => {
    setBusyId(id)
    try {
      await displacementService.activate(id)
      toast.success('Desplazamiento activo')
      reload()
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleDownload = async (id: string) => {
    setBusyId(id)
    try {
      const blob = await displacementService.downloadResolutionPdf(id)
      downloadBlob(blob, `desplazamiento_${id}.pdf`)
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <header>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Workflow className="h-6 w-6 text-blue-600" />
          Desplazamientos
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Module 03.6 · 7 modalidades (rotación, encargatura, destaque, comisión,
          designación, transferencia, permuta) con workflow supervisor → RRHH → titular.
        </p>
      </header>

      {loading ? (
        <p className="text-muted-foreground">Cargando…</p>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No hay desplazamientos registrados.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {items.map((d) => (
            <Card key={d.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base leading-snug flex items-center gap-2">
                    {d.kind_display}
                  </CardTitle>
                  <Badge variant={STATUS_VARIANT[d.status]}>
                    {d.status_display}
                  </Badge>
                </div>
                <CardDescription className="text-xs flex items-center gap-1">
                  <MoveRight className="h-3 w-3" />
                  {new Date(d.start_date).toLocaleDateString()}
                  {d.end_date && ` → ${new Date(d.end_date).toLocaleDateString()}`}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {d.resolution_number && (
                  <div className="text-xs text-muted-foreground">
                    Resolución {d.resolution_number}
                  </div>
                )}
                {d.cancelled_reason && (
                  <div className="text-xs text-red-700 line-clamp-2">
                    {d.cancelled_reason}
                  </div>
                )}
                <div className="flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    disabled={busyId === d.id || d.status !== 'draft'}
                    onClick={() => handleSubmit(d.id)}
                  >
                    Enviar aprobación
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={busyId === d.id || d.status !== 'approved'}
                    onClick={() => handleActivate(d.id)}
                  >
                    Activar
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={busyId === d.id}
                    onClick={() => handleDownload(d.id)}
                  >
                    <Download className="h-3.5 w-3.5 mr-1" />
                    Resolución
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
