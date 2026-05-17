import { useEffect, useState } from 'react'
import { AlertTriangle, FileX, UserX } from 'lucide-react'
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
  terminationService,
  type Termination,
  type TerminationStatus,
} from '../services/terminationService'

const STATUS_VARIANT: Record<
  TerminationStatus,
  'secondary' | 'default' | 'outline' | 'destructive'
> = {
  draft: 'secondary',
  in_progress: 'outline',
  completed: 'default',
  liquidated: 'default',
  baja_t_registro_done: 'default',
  cancelled: 'destructive',
}

export default function TerminationListPage() {
  const [items, setItems] = useState<Termination[]>([])
  const [alertas, setAlertas] = useState<Termination[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  const reload = () => {
    setLoading(true)
    Promise.all([terminationService.list(), terminationService.alertas48hSLA()])
      .then(([all, slas]) => {
        setItems(all)
        setAlertas(slas)
      })
      .catch((e) =>
        toast.error(
          `Error cargando ceses: ${e instanceof Error ? e.message : 'desconocido'}`,
        ),
      )
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])

  const handleComplete = async (id: string) => {
    setBusyId(id)
    try {
      await terminationService.complete(id)
      toast.success('Cese completado')
      reload()
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleLiquidate = async (id: string) => {
    setBusyId(id)
    try {
      await terminationService.liquidate(id)
      toast.success('Liquidación cerrada')
      reload()
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleCancel = async (id: string) => {
    const reason = window.prompt('Motivo de cancelación:')
    if (!reason) return
    setBusyId(id)
    try {
      await terminationService.cancel(id, reason)
      toast.success('Cese cancelado')
      reload()
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
          <UserX className="h-6 w-6 text-rose-600" />
          Desvinculación
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Module 03.7 · Causales 728/276/CAS + liquidación mínima legal (ADR-B.9).
        </p>
      </header>

      {alertas.length > 0 && (
        <Card className="border-amber-300 bg-amber-50">
          <CardHeader className="pb-2">
            <CardTitle className="text-amber-900 text-sm flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              Alertas SLA Baja T-Registro &gt; 48h ({alertas.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-amber-900 space-y-1">
            {alertas.map((t) => (
              <div key={t.id}>
                Cese {t.id.slice(0, 8)} · {t.causal_display} · cesado{' '}
                {new Date(t.fecha_cese).toLocaleDateString()}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {loading ? (
        <p className="text-muted-foreground">Cargando…</p>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No hay ceses registrados.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {items.map((t) => (
            <Card key={t.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base leading-snug">
                    {t.causal_display}
                  </CardTitle>
                  <Badge variant={STATUS_VARIANT[t.status]}>
                    {t.status_display}
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  Régimen {t.regimen_display} · cese{' '}
                  {new Date(t.fecha_cese).toLocaleDateString()}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {t.motivo && (
                  <p className="text-xs text-muted-foreground line-clamp-3">
                    {t.motivo}
                  </p>
                )}
                <div className="flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    disabled={busyId === t.id || t.status !== 'in_progress'}
                    onClick={() => handleComplete(t.id)}
                  >
                    Completar
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={busyId === t.id || t.status !== 'completed'}
                    onClick={() => handleLiquidate(t.id)}
                  >
                    Marcar liquidado
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={
                      busyId === t.id ||
                      t.status === 'baja_t_registro_done' ||
                      t.status === 'cancelled'
                    }
                    onClick={() => handleCancel(t.id)}
                  >
                    <FileX className="h-3.5 w-3.5 mr-1" />
                    Cancelar
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
