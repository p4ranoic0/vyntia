import { useEffect, useState } from 'react'
import { AlertTriangle, CheckCircle2, RefreshCw, TrendingDown, TrendingUp } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui/table'
import { toast } from 'sonner'

import { ccfService, type SalaryGapAudit } from '../services/ccfService'

interface SalaryGapAuditPanelProps {
  ccfId?: string
  /** Optional: when true, autoloads on mount; default true. */
  autoload?: boolean
}

export function SalaryGapAuditPanel({
  ccfId,
  autoload = true,
}: SalaryGapAuditPanelProps) {
  const [audit, setAudit] = useState<SalaryGapAudit | null>(null)
  const [loading, setLoading] = useState(autoload)

  async function load() {
    setLoading(true)
    try {
      const a = await ccfService.getSalaryGapAudit(ccfId)
      setAudit(a)
    } catch (e) {
      toast.error(`Error generando audit: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (autoload) load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ccfId, autoload])

  if (loading) {
    return (
      <Card>
        <CardContent className="py-6 text-center text-muted-foreground">
          Calculando brechas salariales…
        </CardContent>
      </Card>
    )
  }
  if (!audit) {
    return (
      <Card>
        <CardContent className="py-6 text-center">
          <Button onClick={load}>Generar audit</Button>
        </CardContent>
      </Card>
    )
  }

  const { rows, summary } = audit
  const overall = parseFloat(summary.overall_brecha_pct)

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <SummaryCard
          label="Categorías totales"
          value={String(summary.total_categories)}
        />
        <SummaryCard
          label="Con alerta"
          value={String(summary.alerted_categories)}
          alert={summary.alerted_categories > 0}
        />
        <SummaryCard
          label="Brecha global"
          value={`${summary.overall_brecha_pct}%`}
          alert={Math.abs(overall) > 5}
        />
        <SummaryCard
          label="Empleados (M / F)"
          value={`${summary.total_male_employees} / ${summary.total_female_employees}`}
        />
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle className="text-base">Brecha salarial por categoría</CardTitle>
            <CardDescription>
              Ley 30709 § 8. Alerta cuando |brecha| {'>'}  5%.
            </CardDescription>
          </div>
          <Button size="sm" variant="outline" onClick={load}>
            <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
            Recalcular
          </Button>
        </CardHeader>
        <CardContent>
          {rows.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-6">
              No hay categorías para auditar todavía.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Categoría</TableHead>
                  <TableHead className="text-right">Hombres</TableHead>
                  <TableHead className="text-right">Mujeres</TableHead>
                  <TableHead className="text-right">Brecha %</TableHead>
                  <TableHead>Estado</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((row) => {
                  const brecha = parseFloat(row.brecha_pct)
                  return (
                    <TableRow key={row.category_id}>
                      <TableCell>
                        <div className="font-medium">{row.category_name}</div>
                        <div className="text-xs text-muted-foreground font-mono">
                          {row.category_code}
                        </div>
                      </TableCell>
                      <TableCell className="text-right tabular-nums">
                        {row.group_male.count} ·{' '}
                        <span className="text-muted-foreground">
                          S/ {row.group_male.avg_salary}
                        </span>
                      </TableCell>
                      <TableCell className="text-right tabular-nums">
                        {row.group_female.count} ·{' '}
                        <span className="text-muted-foreground">
                          S/ {row.group_female.avg_salary}
                        </span>
                      </TableCell>
                      <TableCell className="text-right tabular-nums">
                        <span
                          className={
                            row.alert
                              ? brecha > 0
                                ? 'text-red-700 font-semibold inline-flex items-center gap-1'
                                : 'text-orange-700 font-semibold inline-flex items-center gap-1'
                              : ''
                          }
                        >
                          {row.alert && brecha > 0 && <TrendingUp className="h-3 w-3" />}
                          {row.alert && brecha < 0 && <TrendingDown className="h-3 w-3" />}
                          {row.brecha_pct}%
                        </span>
                      </TableCell>
                      <TableCell>
                        {row.alert ? (
                          <Badge variant="destructive" className="gap-1">
                            <AlertTriangle className="h-3 w-3" />
                            Investigar
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="gap-1 text-green-700">
                            <CheckCircle2 className="h-3 w-3" />
                            OK
                          </Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

interface SummaryCardProps {
  label: string
  value: string
  alert?: boolean
}

function SummaryCard({ label, value, alert }: SummaryCardProps) {
  return (
    <Card className={alert ? 'border-red-300' : ''}>
      <CardContent className="py-4">
        <div className="text-xs text-muted-foreground uppercase tracking-wide">
          {label}
        </div>
        <div
          className={`text-2xl font-bold mt-1 ${alert ? 'text-red-700' : ''}`}
        >
          {value}
        </div>
      </CardContent>
    </Card>
  )
}
