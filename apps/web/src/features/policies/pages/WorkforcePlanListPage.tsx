import { useEffect, useState } from 'react'
import { Users, TrendingUp } from 'lucide-react'
import { toast } from 'sonner'

import { Badge } from '@/shared/ui/badge'
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle,
} from '@/shared/ui/card'

import {
  workforcePlanService,
  type WorkforcePlan,
  type SuccessionPlan,
} from '../services/workforcePlanService'

export default function WorkforcePlanListPage() {
  const [workforcePlans, setWorkforcePlans] = useState<WorkforcePlan[]>([])
  const [successionPlans, setSuccessionPlans] = useState<SuccessionPlan[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      workforcePlanService.listPlans(),
      workforcePlanService.listSuccessionPlans(),
    ])
      .then(([wp, sp]) => {
        setWorkforcePlans(wp)
        setSuccessionPlans(sp)
      })
      .catch((e) => toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="p-6 space-y-6">
      <header>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Users className="h-6 w-6" /> Dotación + sucesión
        </h1>
        <p className="text-muted-foreground">
          Planeación de headcount (Módulo 01 § 3.1) y cargos clave con candidatos sucesores (§ 3.2).
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" /> Planes de dotación
          </CardTitle>
          <CardDescription>
            {loading ? 'Cargando…' : `${workforcePlans.length} plan(es)`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {workforcePlans.length === 0 && !loading ? (
            <p className="text-muted-foreground text-sm">Sin planes registrados.</p>
          ) : (
            <div className="space-y-2">
              {workforcePlans.map((p) => (
                <div key={p.id} className="flex items-center justify-between border rounded p-3">
                  <div>
                    <div className="font-medium">{p.name}</div>
                    <div className="text-xs text-muted-foreground">
                      FY {p.fiscal_year} · {p.period_start} → {p.period_end}
                    </div>
                  </div>
                  <Badge variant="outline">{p.status_display}</Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Planes de sucesión</CardTitle>
          <CardDescription>
            {loading ? 'Cargando…' : `${successionPlans.length} plan(es)`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {successionPlans.length === 0 && !loading ? (
            <p className="text-muted-foreground text-sm">Sin planes de sucesión.</p>
          ) : (
            <div className="space-y-2">
              {successionPlans.map((p) => (
                <div key={p.id} className="flex items-center justify-between border rounded p-3">
                  <div>
                    <div className="font-medium">{p.name}</div>
                    <div className="text-xs text-muted-foreground">FY {p.fiscal_year}</div>
                  </div>
                  <Badge variant="outline">{p.status_display}</Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
