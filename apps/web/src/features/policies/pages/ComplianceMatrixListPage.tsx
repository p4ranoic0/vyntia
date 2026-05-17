import { useEffect, useState } from 'react'
import { ShieldCheck, AlertTriangle, Clock } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle,
} from '@/shared/ui/card'

import {
  complianceService,
  type ComplianceMatrix,
  type ComplianceObligation,
} from '../services/complianceService'

export default function ComplianceMatrixListPage() {
  const [matrices, setMatrices] = useState<ComplianceMatrix[]>([])
  const [overdue, setOverdue] = useState<ComplianceObligation[]>([])
  const [dueSoon, setDueSoon] = useState<ComplianceObligation[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)

  const reload = () => {
    setLoading(true)
    Promise.all([
      complianceService.listMatrices(),
      complianceService.getAlerts(30),
    ])
      .then(([ms, alerts]) => {
        setMatrices(ms)
        setOverdue(alerts.overdue)
        setDueSoon(alerts.due_soon)
      })
      .catch((e) => toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`))
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])

  const handleMarkOverdue = async () => {
    setBusy(true)
    try {
      const out = await complianceService.markOverdue()
      toast.success(`${out.flagged_overdue} obligación(es) marcada(s) como vencida(s)`)
      reload()
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusy(false)
    }
  }

  const handleMarkCompleted = async (id: string) => {
    setBusy(true)
    try {
      await complianceService.markCompleted(id)
      toast.success('Obligación marcada como cumplida')
      reload()
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <ShieldCheck className="h-6 w-6" /> Matriz de cumplimiento
          </h1>
          <p className="text-muted-foreground">
            Obligaciones legales y normativas (SUNAT, SUNAFIL, MINTRA, SERVIR…) con vencimientos (Módulo 01 § 4).
          </p>
        </div>
        <Button variant="outline" onClick={handleMarkOverdue} disabled={busy}>
          Marcar vencidos
        </Button>
      </header>

      {overdue.length > 0 && (
        <Card className="border-destructive/40">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" /> Obligaciones vencidas ({overdue.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {overdue.map((o) => (
              <div key={o.id} className="flex items-center justify-between border border-destructive/30 rounded p-3">
                <div>
                  <div className="font-medium">
                    {o.code} — {o.title}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {o.source_display} · vence {o.next_due_date} · {Math.abs(o.days_to_due)} días vencida
                  </div>
                </div>
                <Button
                  size="sm" variant="default" disabled={busy}
                  onClick={() => handleMarkCompleted(o.id)}
                >
                  Marcar cumplida
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {dueSoon.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" /> Próximas a vencer ({dueSoon.length})
            </CardTitle>
            <CardDescription>Próximos 30 días</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {dueSoon.map((o) => (
              <div key={o.id} className="flex items-center justify-between border rounded p-3">
                <div>
                  <div className="font-medium">{o.code} — {o.title}</div>
                  <div className="text-xs text-muted-foreground">
                    {o.source_display} · vence {o.next_due_date} ({o.days_to_due} días)
                  </div>
                </div>
                <Badge variant="outline">{o.severity_display}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Matrices</CardTitle>
          <CardDescription>
            {loading ? 'Cargando…' : `${matrices.length} matriz(ces)`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {matrices.length === 0 && !loading ? (
            <p className="text-muted-foreground text-sm">Sin matrices registradas.</p>
          ) : (
            <div className="space-y-2">
              {matrices.map((m) => (
                <div key={m.id} className="flex items-center justify-between border rounded p-3">
                  <div>
                    <div className="font-medium">{m.name}</div>
                    <div className="text-xs text-muted-foreground">FY {m.fiscal_year}</div>
                  </div>
                  <Badge variant="outline">{m.status_display}</Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
