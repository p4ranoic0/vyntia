import { useEffect, useState } from 'react'
import { AlertTriangle, CheckCircle2, ShieldOff, Timer } from 'lucide-react'
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
  probationPeriodService,
  type ProbationPeriod,
  type ProbationStatus,
} from '../services/probationPeriodService'

const STATUS_VARIANT: Record<
  ProbationStatus,
  'secondary' | 'default' | 'outline' | 'destructive'
> = {
  pending: 'secondary',
  in_progress: 'outline',
  evaluated: 'default',
  ratified: 'default',
  not_renewed: 'destructive',
}

export default function ProbationPeriodListPage() {
  const [periods, setPeriods] = useState<ProbationPeriod[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  const reload = () => {
    setLoading(true)
    probationPeriodService
      .list()
      .then(setPeriods)
      .catch((e) =>
        toast.error(
          `Error cargando períodos: ${e instanceof Error ? e.message : 'desconocido'}`,
        ),
      )
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])

  const handleRatify = async (id: string) => {
    setBusyId(id)
    try {
      await probationPeriodService.ratify(id)
      toast.success('Trabajador ratificado')
      reload()
    } catch (e) {
      toast.error(`Error ratificando: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleNotRenew = async (id: string) => {
    const reason = window.prompt('Razón de no renovación:')
    if (!reason) return
    setBusyId(id)
    try {
      await probationPeriodService.notRenew(id, reason)
      toast.success('Trabajador no renovado')
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
          <Timer className="h-6 w-6 text-blue-600" />
          Período de prueba
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Module 03.4 · seguimiento por régimen laboral (728 común 3m / calificado 6m
          / dirección 12m / MYPE 3m / 276 carrera 3 años) con alertas 30/15 días.
        </p>
      </header>

      {loading ? (
        <p className="text-muted-foreground">Cargando períodos…</p>
      ) : periods.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No hay períodos de prueba registrados.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {periods.map((p) => (
            <Card key={p.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base leading-snug">
                    {p.regimen_display}
                  </CardTitle>
                  <Badge variant={STATUS_VARIANT[p.status]}>
                    {p.status_display}
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  {p.plazo_dias} días · termina {new Date(p.end_date).toLocaleDateString()}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-xs flex items-center gap-2">
                  {p.is_within_15_days && (
                    <span className="flex items-center gap-1 text-red-700">
                      <AlertTriangle className="h-3 w-3" />
                      Vence en {p.days_remaining}d
                    </span>
                  )}
                  {p.is_within_30_days && !p.is_within_15_days && (
                    <span className="flex items-center gap-1 text-amber-700">
                      <AlertTriangle className="h-3 w-3" />
                      {p.days_remaining}d restantes
                    </span>
                  )}
                  {!p.is_within_30_days && (
                    <span className="text-muted-foreground">
                      {p.days_remaining > 0
                        ? `${p.days_remaining} días`
                        : 'Vencido'}
                    </span>
                  )}
                </div>
                {p.evaluation_score !== null && (
                  <div className="text-xs">Score: {p.evaluation_score}/100</div>
                )}
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    disabled={busyId === p.id || p.status !== 'evaluated'}
                    onClick={() => handleRatify(p.id)}
                  >
                    <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                    Ratificar
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    disabled={busyId === p.id || p.status !== 'evaluated'}
                    onClick={() => handleNotRenew(p.id)}
                  >
                    <ShieldOff className="h-3.5 w-3.5 mr-1" />
                    No renovar
                  </Button>
                </div>
                {p.decision_reason && (
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {p.decision_reason}
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
