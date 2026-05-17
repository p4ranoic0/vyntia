import { useEffect, useState } from 'react'
import { Target, Play, CheckCircle, Archive } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle,
} from '@/shared/ui/card'

import {
  strategicPlanService,
  type HRStrategicPlan,
  type StrategicPlanStatus,
} from '../services/strategicPlanService'

const STATUS_VARIANT: Record<StrategicPlanStatus, 'secondary' | 'default' | 'outline' | 'destructive'> = {
  draft: 'secondary',
  active: 'default',
  completed: 'outline',
  archived: 'destructive',
}

export default function StrategicPlanListPage() {
  const [items, setItems] = useState<HRStrategicPlan[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  const reload = () => {
    setLoading(true)
    strategicPlanService.listPlans()
      .then(setItems)
      .catch((e) => toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`))
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])

  const handle = async (id: string, fn: () => Promise<unknown>, msg: string) => {
    setBusyId(id)
    try {
      await fn()
      toast.success(msg)
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
          <Target className="h-6 w-6" /> Plan estratégico de RRHH
        </h1>
        <p className="text-muted-foreground">
          Planes anuales con objetivos estratégicos y KPIs medibles (Módulo 01 § 2).
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Planes</CardTitle>
          <CardDescription>
            {loading ? 'Cargando…' : `${items.length} plan(es)`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {items.length === 0 && !loading ? (
            <p className="text-muted-foreground text-sm">No hay planes registrados aún.</p>
          ) : (
            <div className="space-y-3">
              {items.map((p) => (
                <div key={p.id} className="flex items-start justify-between gap-4 border rounded-lg p-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium truncate">{p.name}</h3>
                      <Badge variant={STATUS_VARIANT[p.status]}>{p.status_display}</Badge>
                      <Badge variant="outline">FY {p.fiscal_year}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">
                      {p.period_start} → {p.period_end}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    {p.status === 'draft' && (
                      <Button
                        variant="default" size="sm"
                        disabled={busyId === p.id}
                        onClick={() => handle(p.id, () => strategicPlanService.activate(p.id), 'Plan activado')}
                      >
                        <Play className="h-4 w-4 mr-1" /> Activar
                      </Button>
                    )}
                    {p.status === 'active' && (
                      <Button
                        variant="outline" size="sm"
                        disabled={busyId === p.id}
                        onClick={() => handle(p.id, () => strategicPlanService.complete(p.id), 'Plan completado')}
                      >
                        <CheckCircle className="h-4 w-4 mr-1" /> Completar
                      </Button>
                    )}
                    {p.status !== 'archived' && (
                      <Button
                        variant="outline" size="sm"
                        disabled={busyId === p.id}
                        onClick={() => handle(p.id, () => strategicPlanService.archive(p.id), 'Plan archivado')}
                      >
                        <Archive className="h-4 w-4 mr-1" /> Archivar
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
