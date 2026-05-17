import { useEffect, useState } from 'react'
import { Calculator, CheckCircle2, Wallet } from 'lucide-react'
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
  severanceSettlementService,
  type SeveranceSettlement,
  type SeveranceStatus,
} from '../services/severanceSettlementService'

const STATUS_VARIANT: Record<
  SeveranceStatus,
  'secondary' | 'default' | 'outline' | 'destructive'
> = {
  draft: 'secondary',
  computed: 'outline',
  paid: 'default',
  void: 'destructive',
}

export default function SeveranceSettlementListPage() {
  const [items, setItems] = useState<SeveranceSettlement[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)
  const [openId, setOpenId] = useState<string | null>(null)

  const reload = () => {
    setLoading(true)
    severanceSettlementService
      .list()
      .then(setItems)
      .catch((e) =>
        toast.error(
          `Error cargando liquidaciones: ${e instanceof Error ? e.message : 'desconocido'}`,
        ),
      )
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])

  const handleCompute = async (id: string) => {
    setBusyId(id)
    try {
      await severanceSettlementService.compute(id)
      toast.success('Liquidación recomputada')
      reload()
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleMarkPaid = async (id: string, expectedTotal: string) => {
    const raw = window.prompt(
      `Total pagado al trabajador (computado: S/ ${expectedTotal}):`,
      expectedTotal,
    )
    if (!raw) return
    setBusyId(id)
    try {
      await severanceSettlementService.markPaid(id, { paid_total: raw })
      toast.success('Pago registrado')
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
          <Wallet className="h-6 w-6 text-emerald-700" />
          Liquidaciones
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Module 03.7 · Cálculo mínimo legal (ADR-B.9): CTS proporcional + vacaciones
          truncas + gratificación trunca + indemnización (cuando aplica).
        </p>
      </header>

      {loading ? (
        <p className="text-muted-foreground">Cargando…</p>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No hay liquidaciones registradas.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {items.map((s) => (
            <Card key={s.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base leading-snug">
                    Liquidación {s.id.slice(0, 8)}
                  </CardTitle>
                  <Badge variant={STATUS_VARIANT[s.status]}>
                    {s.status_display}
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  Sueldo base S/ {s.sueldo_base} · Total computado{' '}
                  <strong>S/ {s.total_amount}</strong>
                  {s.paid_at && ` · Pagado S/ ${s.paid_amount}`}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={busyId === s.id}
                    onClick={() => handleCompute(s.id)}
                  >
                    <Calculator className="h-3.5 w-3.5 mr-1" />
                    Recomputar
                  </Button>
                  <Button
                    size="sm"
                    disabled={busyId === s.id || s.status !== 'computed'}
                    onClick={() => handleMarkPaid(s.id, s.total_amount)}
                  >
                    <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                    Marcar pagado
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setOpenId(openId === s.id ? null : s.id)}
                  >
                    {openId === s.id ? 'Ocultar' : 'Ver detalle'}
                  </Button>
                </div>
                {openId === s.id && s.lines.length > 0 && (
                  <div className="bg-muted/30 rounded-md p-3 text-xs space-y-2">
                    {s.lines.map((line) => (
                      <div key={line.id} className="flex justify-between gap-2">
                        <div>
                          <div className="font-semibold">
                            {line.component_display}
                          </div>
                          <div className="text-muted-foreground">
                            {line.formula_note}
                          </div>
                        </div>
                        <div className="text-right font-mono">
                          S/ {line.amount}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
