import { Badge } from '@/shared/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Skeleton } from '@/shared/ui/skeleton'
import { apiClient } from '@/shared/api/api'
import { cn } from '@/shared/utils/cn'
import { contractsService, TIPO_CONTRATO_LABELS } from '@/features/contracts/services/contractsService'
import { useQuery } from '@tanstack/react-query'
import {
    Activity,
    AlertTriangle,
    ArrowRight,
    Banknote,
    CheckCircle2,
    FileText,
    RefreshCw,
    TrendingDown,
    TrendingUp,
    Users,
} from 'lucide-react'
import React, { useEffect, useId, useState } from 'react'

// ─── API Response Types ────────────────────────────────────────────────────────

interface EmpleadosPagination {
  total_items: number
  total_pages: number
  current_page: number
  has_next: boolean
}

interface EmpleadosResponse {
  data?: unknown[]
  meta?: { pagination?: EmpleadosPagination }
  count?: number // fallback DRF pagination
}

interface ContratosEstadisticas {
  resumen_general: {
    total_contratos: number
    contratos_activos: number
    contratos_por_vencer: number
    empleados_con_contratos: number
  }
  distribucion_tipos: Array<{
    tipo_documento: string
    total: number
  }>
  areas_top: Array<{
    area__siglas_area: string
    area__nombre_unidad_organica: string
    total: number
  }>
  fecha_consulta: string
}

interface Area {
  id: string
  siglas_area: string
  nombre_organo: string
  nombre_unidad_organica?: string
  estado_area: string
  empleados_activos_count?: number
  empleados_count?: number
}

interface PlanillaMensual {
  id: string
  periodo: string
  estado?: string
  estado_texto?: string
  total_trabajadores?: number
  total_neto_pagar?: number
  total_remuneracion_bruta?: number
  total_ingresos?: number
  total_descuentos?: number
}

// ─── React Query hooks ─────────────────────────────────────────────────────────

function useEmpleadosStats() {
  return useQuery({
    queryKey: ['dashboard', 'empleados-stats'],
    queryFn: async () => {
      const [totalRes, activosRes] = await Promise.all([
        apiClient.get<EmpleadosResponse>('/api/v1/employees/', { page_size: 1 }),
        apiClient.get<EmpleadosResponse>('/api/v1/employees/', {
          page_size: 1,
          estado_empleado: 'activo',
        }),
      ])
      const parseCount = (res: EmpleadosResponse): number =>
        res?.meta?.pagination?.total_items ?? res?.count ?? 0

      return {
        total: parseCount(totalRes.data),
        activos: parseCount(activosRes.data),
      }
    },
    staleTime: 5 * 60 * 1000,
  })
}

function useContratosEstadisticas() {
  return useQuery<ContratosEstadisticas>({
    queryKey: ['dashboard', 'contratos-estadisticas'],
    queryFn: async () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw = (await contractsService.getEstadisticas()) as any
      return raw as ContratosEstadisticas
    },
    staleTime: 5 * 60 * 1000,
  })
}

function useAreasDistribucion() {
  return useQuery<Area[]>({
    queryKey: ['dashboard', 'areas-distribucion'],
    queryFn: async () => {
      const response = await apiClient.get<{ data?: Area[]; results?: Area[] }>(
        '/api/v1/organization/departments/',
        { page_size: 100, estado_area: 'activo' },
      )
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw = response.data as any
      const areas: Area[] = raw?.data ?? raw?.results ?? []
      return areas
        .filter((a) => a.estado_area === 'activo')
        .sort(
          (a, b) =>
            (b.empleados_activos_count ?? b.empleados_count ?? 0) -
            (a.empleados_activos_count ?? a.empleados_count ?? 0),
        )
        .slice(0, 8)
    },
    staleTime: 10 * 60 * 1000,
  })
}

function usePlanillasMes() {
  return useQuery<PlanillaMensual[]>({
    queryKey: ['dashboard', 'planillas-mes'],
    queryFn: async () => {
      const response = await apiClient.get<{ data?: PlanillaMensual[]; results?: PlanillaMensual[] }>(
        '/api/v1/payroll/monthly-runs/',
        { page_size: 6, ordering: '-periodo' },
      )
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw = response.data as any
      return raw?.data ?? raw?.results ?? []
    },
    staleTime: 5 * 60 * 1000,
  })
}

// ─── Helpers ───────────────────────────────────────────────────────────────────

const CHART_COLORS = [
  'hsl(var(--chart-2))',
  'hsl(var(--chart-1))',
  'hsl(var(--chart-4))',
  'hsl(var(--chart-5))',
  'hsl(var(--chart-3))',
  'hsl(var(--chart-2))',
  'hsl(var(--chart-1))',
  'hsl(var(--chart-4))',
]

const PLANILLA_ESTADO_PCT: Record<string, number> = {
  borrador: 10,
  generada: 35,
  calculada: 65,
  aprobada: 85,
  pagada: 100,
  anulado: 0,
}

const PLANILLA_ESTADO_COLOR: Record<string, string> = {
  borrador: 'hsl(var(--muted-foreground))',
  generada: 'hsl(var(--chart-4))',
  calculada: 'hsl(var(--chart-5))',
  aprobada: 'hsl(var(--chart-2))',
  pagada: 'hsl(var(--chart-2))',
  anulado: 'hsl(var(--destructive))',
}

function formatPeriodo(periodo: string): string {
  if (!periodo) return '-'
  const [year, month] = periodo.split('-')
  const meses = [
    '', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic',
  ]
  return `${meses[parseInt(month)] ?? month} ${year}`
}

function shortTipoLabel(tipo: string): string {
  const label = TIPO_CONTRATO_LABELS[tipo] ?? tipo
  // Shorten common labels for chart display
  return label
    .replace('Contrato ', '')
    .replace('Adenda ', 'Ad. ')
    .replace('de Practicas', 'Prácticas')
    .replace('a Plazo Fijo', 'Plazo Fijo')
    .replace('por Obra o Servicio', 'Obra/Servicio')
}

// ─── Animated Counter ──────────────────────────────────────────────────────────

function useCounter(target: number, duration = 1100) {
  const [value, setValue] = useState(0)
  useEffect(() => {
    if (target === 0) return
    const start = performance.now()
    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setValue(Math.round(target * eased))
      if (progress < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  }, [target, duration])
  return value
}

// ─── SVG Sparkline (decorativa, basada en datos reales cuando están disponibles)

function Sparkline({ data, color, height = 32 }: { data: number[]; color: string; height?: number }) {
  const id = useId()
  const gradId = `spark-grad-${id.replace(/:/g, '')}`
  const W = 100
  if (data.length < 2) return null
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const step = W / (data.length - 1)
  const points = data.map((v, i) => ({
    x: i * step,
    y: height - ((v - min) / range) * (height - 2) - 1,
  }))
  const linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
  const fillPath = `${linePath} L ${points[points.length - 1].x} ${height} L 0 ${height} Z`
  const last = points[points.length - 1]
  return (
    <svg viewBox={`0 0 ${W} ${height}`} width="100%" height={height} preserveAspectRatio="none" className="overflow-visible">
      <defs>
        <linearGradient id={gradId} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={fillPath} fill={`url(#${gradId})`} />
      <path d={linePath} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={last.x} cy={last.y} r="3" fill={color} />
    </svg>
  )
}

// ─── Donut Chart ───────────────────────────────────────────────────────────────

function DonutChart({
  slices,
  total,
}: {
  slices: Array<{ label: string; value: number; color: string }>
  total: number
}) {
  const r = 56
  const circ = 2 * Math.PI * r
  const gap = 3
  let accumulated = 0
  const rendered = slices.map((s) => {
    const dash = (s.value / total) * (circ - slices.length * gap)
    const item = { ...s, dash, offset: accumulated }
    accumulated += dash + gap
    return item
  })

  return (
    <div className="flex items-center gap-5">
      <div className="relative flex-shrink-0">
        <svg width={140} height={140} viewBox="0 0 140 140">
          <circle cx={70} cy={70} r={r} fill="none" stroke="hsl(var(--border))" strokeWidth={16} />
          {rendered.map((s, i) => (
            <circle
              key={i}
              cx={70} cy={70} r={r}
              fill="none"
              stroke={s.color}
              strokeWidth={16}
              strokeDasharray={`${s.dash} ${circ - s.dash}`}
              strokeDashoffset={circ / 4 - s.offset}
              strokeLinecap="butt"
            />
          ))}
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-mono font-bold leading-none">{total.toLocaleString('es-PE')}</span>
          <span className="text-[10px] text-muted-foreground uppercase tracking-wider mt-0.5">total</span>
        </div>
      </div>
      <div className="space-y-2.5 flex-1">
        {slices.map((s) => {
          const pct = total > 0 ? Math.round((s.value / total) * 100) : 0
          return (
            <div key={s.label} className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: s.color }} />
              <div className="flex-1 min-w-0">
                <div className="flex items-baseline justify-between">
                  <span className="text-xs text-muted-foreground truncate">{s.label}</span>
                  <span className="text-xs font-mono font-semibold ml-2">{s.value.toLocaleString('es-PE')}</span>
                </div>
                <div className="mt-1 h-1 bg-muted rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${pct}%`, backgroundColor: s.color }} />
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─── KPI Card ──────────────────────────────────────────────────────────────────

interface KpiCardProps {
  icon: React.ReactNode
  label: string
  value: number
  suffix?: string
  trend?: number
  trendLabel?: string
  sub?: string
  accent: string
  sparkData?: number[]
  delay?: number
  loading?: boolean
}

function KpiCard({ icon, label, value, suffix = '', trend, trendLabel, sub, accent, sparkData, delay = 0, loading }: KpiCardProps) {
  const count = useCounter(value, 1000 + delay)
  const isPositive = (trend ?? 0) >= 0

  if (loading) {
    return (
      <Card className="relative overflow-hidden">
        <div className="absolute left-0 top-0 bottom-0 w-[3px]" style={{ backgroundColor: accent }} />
        <CardContent className="pl-5 pt-5 pb-4 space-y-2">
          <Skeleton className="h-3 w-28" />
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-3 w-36" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card
      className="relative overflow-hidden animate-fade-in-up group hover:shadow-md hover:-translate-y-0.5 transition-all duration-200"
      style={{ animationDelay: `${delay}ms`, animationFillMode: 'both' }}
    >
      <div className="absolute left-0 top-0 bottom-0 w-[3px] rounded-r-full" style={{ backgroundColor: accent }} />
      <CardContent className="pl-5 pt-5 pb-4">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1 min-w-0 flex-1">
            <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">{label}</p>
            <div className="flex items-baseline gap-0.5">
              <span className="text-3xl font-mono font-bold tabular-nums tracking-tight leading-none">
                {count.toLocaleString('es-PE')}
              </span>
              {suffix && <span className="text-sm font-mono text-muted-foreground">{suffix}</span>}
            </div>
            {sub && <p className="text-[11px] text-muted-foreground leading-snug">{sub}</p>}
          </div>
          <div className="flex flex-col items-end gap-2 flex-shrink-0">
            <div className="p-2 rounded-lg" style={{ backgroundColor: `${accent}1a` }}>
              <div style={{ color: accent }}>{icon}</div>
            </div>
            {trend !== undefined && (
              <div className={cn('flex items-center gap-0.5 text-[11px] font-mono font-medium', isPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500')}>
                {isPositive ? <TrendingUp size={11} /> : <TrendingDown size={11} />}
                <span>{Math.abs(trend)}% {trendLabel ?? 'vs mes ant.'}</span>
              </div>
            )}
          </div>
        </div>
        {sparkData && sparkData.length >= 2 && (
          <div className="mt-3 h-8">
            <Sparkline data={sparkData} color={accent} height={32} />
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ─── Area Bars ─────────────────────────────────────────────────────────────────

function AreaBars({ areas, loading }: { areas: Area[]; loading: boolean }) {
  if (loading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i}>
            <div className="flex items-center gap-3 mb-1.5">
              <Skeleton className="h-3 w-8" />
              <Skeleton className="h-3 flex-1" />
              <Skeleton className="h-3 w-8" />
            </div>
            <Skeleton className="h-1.5 w-full" />
          </div>
        ))}
      </div>
    )
  }

  const max = Math.max(...areas.map((a) => a.empleados_activos_count ?? a.empleados_count ?? 0), 1)
  const totalEmpleados = areas.reduce((s, a) => s + (a.empleados_activos_count ?? a.empleados_count ?? 0), 0)

  return (
    <div className="space-y-3">
      {areas.map((area, i) => {
        const count = area.empleados_activos_count ?? area.empleados_count ?? 0
        const pct = totalEmpleados > 0 ? Math.round((count / totalEmpleados) * 100) : 0
        const nombre = area.nombre_unidad_organica || area.nombre_organo
        return (
          <div key={area.id}>
            <div className="flex items-center gap-3 mb-1.5">
              <span className="text-[10px] font-mono font-bold w-8 text-muted-foreground uppercase">
                {area.siglas_area}
              </span>
              <span className="text-xs text-foreground flex-1 truncate">{nombre}</span>
              <span className="text-xs font-mono font-bold tabular-nums">{count}</span>
              <span className="text-[10px] text-muted-foreground w-8 text-right">{pct}%</span>
            </div>
            <div className="h-1.5 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700 ease-out"
                style={{
                  width: `${(count / max) * 100}%`,
                  backgroundColor: CHART_COLORS[i % CHART_COLORS.length],
                  transitionDelay: `${i * 60 + 200}ms`,
                }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}

// ─── Planillas List ────────────────────────────────────────────────────────────

function PlanillasList({ planillas, loading }: { planillas: PlanillaMensual[]; loading: boolean }) {
  if (loading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i}>
            <div className="flex justify-between mb-1.5">
              <Skeleton className="h-3 w-24" />
              <Skeleton className="h-3 w-12" />
            </div>
            <Skeleton className="h-1.5 w-full" />
          </div>
        ))}
      </div>
    )
  }

  if (!planillas.length) {
    return <p className="text-xs text-muted-foreground text-center py-4">Sin planillas registradas</p>
  }

  return (
    <div className="space-y-4">
      {planillas.slice(0, 5).map((p) => {
        const estado = (p.status ?? 'borrador').toLowerCase()
        const pct = PLANILLA_ESTADO_PCT[estado] ?? 10
        const color = PLANILLA_ESTADO_COLOR[estado] ?? 'hsl(var(--muted-foreground))'
        return (
          <div key={p.id}>
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <span className="text-xs text-foreground">{formatPeriodo(p.periodo)}</span>
                {p.total_trabajadores && (
                  <span className="text-[10px] text-muted-foreground font-mono">
                    {p.total_trabajadores} trab.
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold">{pct}%</span>
                <span className="text-[10px] text-muted-foreground uppercase tracking-wide font-mono">
                  {p.estado_texto ?? p.status ?? '—'}
                </span>
              </div>
            </div>
            <div className="h-1.5 bg-muted rounded-full overflow-hidden">
              <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, backgroundColor: color }} />
            </div>
            {p.total_neto_pagar && (
              <p className="text-[10px] text-muted-foreground mt-0.5 font-mono">
                Neto: S/ {p.total_neto_pagar.toLocaleString('es-PE', { maximumFractionDigits: 0 })}
              </p>
            )}
          </div>
        )
      })}
    </div>
  )
}

// ─── Alert Row ─────────────────────────────────────────────────────────────────

const ALERT_STYLES = {
  warning: {
    icon: <AlertTriangle size={13} />,
    className: 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800/40',
  },
  info: {
    icon: <Activity size={13} />,
    className: 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 border-blue-200 dark:border-blue-800/40',
  },
  error: {
    icon: <AlertTriangle size={13} />,
    className: 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-800/40',
  },
  success: {
    icon: <CheckCircle2 size={13} />,
    className: 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800/40',
  },
} as const

type AlertTipo = keyof typeof ALERT_STYLES

function AlertRow({ tipo, mensaje, modulo }: { tipo: AlertTipo; mensaje: string; modulo: string }) {
  const s = ALERT_STYLES[tipo]
  return (
    <div className={cn('flex items-start gap-2.5 px-3 py-2.5 rounded-md border', s.className)}>
      <div className="mt-0.5 flex-shrink-0">{s.icon}</div>
      <div className="flex-1 min-w-0">
        <p className="text-xs leading-snug">{mensaje}</p>
        <p className="text-[10px] opacity-70 mt-0.5 font-mono uppercase tracking-wider">{modulo}</p>
      </div>
    </div>
  )
}

// Derive real alerts from actual data
function buildAlertas(
  contratos?: ContratosEstadisticas,
  planillas?: PlanillaMensual[],
  empleados?: { total: number; activos: number },
): Array<{ tipo: AlertTipo; mensaje: string; modulo: string }> {
  const alerts: Array<{ tipo: AlertTipo; mensaje: string; modulo: string }> = []

  if (contratos) {
    const { contratos_por_vencer, contratos_activos, empleados_con_contratos } = contratos.resumen_general
    if (contratos_por_vencer > 0) {
      alerts.push({
        tipo: 'warning',
        mensaje: `${contratos_por_vencer} contrato${contratos_por_vencer !== 1 ? 's' : ''} vence${contratos_por_vencer !== 1 ? 'n' : ''} en los próximos 30 días`,
        modulo: 'Contratos',
      })
    }
    if (empleados && empleados.total > 0) {
      const sinContrato = empleados.total - empleados_con_contratos
      if (sinContrato > 0) {
        alerts.push({
          tipo: 'info',
          mensaje: `${sinContrato} empleado${sinContrato !== 1 ? 's' : ''} sin contrato activo`,
          modulo: 'Empleados',
        })
      }
    }
    if (contratos_activos > 0) {
      alerts.push({
        tipo: 'success',
        mensaje: `${contratos_activos.toLocaleString('es-PE')} contratos activos en el sistema`,
        modulo: 'Contratos',
      })
    }
  }

  if (planillas && planillas.length > 0) {
    const latest = planillas[0]
    const estado = (latest.status ?? '').toLowerCase()
    if (estado === 'aprobada' || estado === 'pagada') {
      alerts.push({
        tipo: 'success',
        mensaje: `Planilla ${formatPeriodo(latest.periodo)} ${estado === 'pagada' ? 'pagada' : 'aprobada'} correctamente`,
        modulo: 'Planillas',
      })
    } else if (estado === 'calculada' || estado === 'generada') {
      alerts.push({
        tipo: 'info',
        mensaje: `Planilla ${formatPeriodo(latest.periodo)} pendiente de aprobación`,
        modulo: 'Planillas',
      })
    } else if (estado === 'borrador') {
      alerts.push({
        tipo: 'warning',
        mensaje: `Planilla ${formatPeriodo(latest.periodo)} en borrador, requiere procesamiento`,
        modulo: 'Planillas',
      })
    } else if (estado === 'anulado') {
      alerts.push({
        tipo: 'error',
        mensaje: `Planilla ${formatPeriodo(latest.periodo)} fue anulada`,
        modulo: 'Planillas',
      })
    }
  }

  return alerts
}

// ─── Main Dashboard ────────────────────────────────────────────────────────────

export default function HROverviewDashboard() {
  const empleadosQuery = useEmpleadosStats()
  const contratosQuery = useContratosEstadisticas()
  const areasQuery = useAreasDistribucion()
  const planillasQuery = usePlanillasMes()

  const today = new Date().toLocaleDateString('es-PE', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })

  const empleados = empleadosQuery.data
  const contratos = contratosQuery.data
  const areas = areasQuery.data ?? []
  const planillas = planillasQuery.data ?? []

  // Derived values
  const contratosActivos = contratos?.resumen_general.contratos_activos ?? 0
  const contratosPorVencer = contratos?.resumen_general.contratos_por_vencer ?? 0
  const empleadosConContratos = contratos?.resumen_general.empleados_con_contratos ?? 0

  // Donut slices from real data
  const contratoSlices = (contratos?.distribucion_tipos ?? [])
    .filter((d) => d.total > 0)
    .slice(0, 5)
    .map((d, i) => ({
      label: shortTipoLabel(d.tipo_documento),
      value: d.total,
      color: CHART_COLORS[i % CHART_COLORS.length],
    }))
  const contratoTotal = contratoSlices.reduce((s, d) => s + d.value, 0)

  // Latest planilla progress for KPI card
  const latestPlanilla = planillas[0]
  const planillaEstado = (latestPlanilla?.status ?? 'borrador').toLowerCase()
  const planillaPct = PLANILLA_ESTADO_PCT[planillaEstado] ?? 0

  // Alerts derived from real data
  const alertas = buildAlertas(contratos, planillas, empleados)

  // Global loading / error state
  const isAnyLoading = empleadosQuery.isLoading || contratosQuery.isLoading || areasQuery.isLoading || planillasQuery.isLoading
  const hasError = empleadosQuery.isError || contratosQuery.isError

  return (
    <div className="min-h-full p-6 space-y-8">

      {/* ── Header ── */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p className="text-[11px] font-mono uppercase tracking-[0.15em] text-muted-foreground mb-1 capitalize">
            {today}
          </p>
          <h1 className="text-2xl font-bold tracking-tight">Panel de Control RRHH</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Indicadores generales del capital humano
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isAnyLoading && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800/40">
              <RefreshCw size={12} className="animate-spin text-blue-500" />
              <span className="text-xs font-mono text-blue-600 dark:text-blue-400">Cargando datos</span>
            </div>
          )}
          {!isAnyLoading && !hasError && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/40">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-mono text-emerald-700 dark:text-emerald-400">Datos actualizados</span>
            </div>
          )}
          {hasError && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800/40">
              <AlertTriangle size={12} className="text-red-500" />
              <span className="text-xs font-mono text-red-600 dark:text-red-400">Error al cargar</span>
            </div>
          )}
        </div>
      </div>

      {/* ── KPI Row ── */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          icon={<Users size={18} />}
          label="Total empleados"
          value={empleados?.total ?? 0}
          sub={`${(empleados?.activos ?? 0).toLocaleString('es-PE')} activos`}
          accent="hsl(var(--chart-2))"
          delay={0}
          loading={empleadosQuery.isLoading}
        />
        <KpiCard
          icon={<FileText size={18} />}
          label="Contratos activos"
          value={contratosActivos}
          sub={`${contratosPorVencer} vencen en 30 días`}
          accent="hsl(var(--chart-1))"
          delay={80}
          loading={contratosQuery.isLoading}
        />
        <KpiCard
          icon={<AlertTriangle size={18} />}
          label="Por vencer (30 días)"
          value={contratosPorVencer}
          sub={`De ${contratosActivos.toLocaleString('es-PE')} contratos activos`}
          accent="hsl(var(--chart-4))"
          delay={160}
          loading={contratosQuery.isLoading}
        />
        <KpiCard
          icon={<Banknote size={18} />}
          label="Planilla más reciente"
          value={planillaPct}
          suffix="%"
          sub={latestPlanilla ? `${formatPeriodo(latestPlanilla.periodo)} · ${latestPlanilla.estado_texto ?? latestPlanilla.status ?? '—'}` : 'Sin planillas'}
          accent="hsl(var(--chart-5))"
          delay={240}
          loading={planillasQuery.isLoading}
        />
      </div>

      {/* ── Middle Row ── */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">

        {/* Area Distribution — 3 cols */}
        <Card className="lg:col-span-3 animate-fade-in-up" style={{ animationDelay: '320ms', animationFillMode: 'both' }}>
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                Empleados por área
              </CardTitle>
              <Badge variant="outline" className="text-[10px] font-mono h-5">
                {areasQuery.isLoading ? '…' : `${areas.length} áreas`}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <AreaBars areas={areas} loading={areasQuery.isLoading} />
            {areasQuery.isError && (
              <p className="text-xs text-muted-foreground text-center py-4">Error al cargar áreas</p>
            )}
          </CardContent>
        </Card>

        {/* Contract Types Donut — 2 cols */}
        <Card className="lg:col-span-2 animate-fade-in-up" style={{ animationDelay: '380ms', animationFillMode: 'both' }}>
          <CardHeader className="pb-4">
            <CardTitle className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
              Tipos de contrato
            </CardTitle>
          </CardHeader>
          <CardContent>
            {contratosQuery.isLoading ? (
              <div className="flex items-center gap-5">
                <Skeleton className="w-[140px] h-[140px] rounded-full" />
                <div className="space-y-3 flex-1">
                  {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-8 w-full" />)}
                </div>
              </div>
            ) : contratoSlices.length > 0 ? (
              <DonutChart slices={contratoSlices} total={contratoTotal} />
            ) : (
              <p className="text-xs text-muted-foreground text-center py-8">Sin datos de contratos</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ── Bottom Row ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        {/* Areas Top (from contratos) */}
        <Card className="animate-fade-in-up" style={{ animationDelay: '440ms', animationFillMode: 'both' }}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                Áreas con más contratos
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            {contratosQuery.isLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <Skeleton className="h-3 w-8" />
                    <Skeleton className="h-3 flex-1" />
                    <Skeleton className="h-3 w-8" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-2.5">
                {(contratos?.areas_top ?? []).slice(0, 7).map((area, i) => {
                  const totalAreas = (contratos?.areas_top ?? []).reduce((s, a) => s + a.total, 0)
                  const pct = totalAreas > 0 ? Math.round((area.total / totalAreas) * 100) : 0
                  return (
                    <div key={i}>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-mono font-bold w-8 text-muted-foreground">
                          {area.area__siglas_area}
                        </span>
                        <span className="text-xs text-foreground flex-1 truncate">
                          {area.area__nombre_unidad_organica}
                        </span>
                        <span className="text-xs font-mono font-bold">{area.total}</span>
                      </div>
                      <div className="h-1 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${pct}%`,
                            backgroundColor: CHART_COLORS[i % CHART_COLORS.length],
                          }}
                        />
                      </div>
                    </div>
                  )
                })}
                <div className="pt-2 flex items-center gap-1.5 text-[11px] text-muted-foreground border-t">
                  <ArrowRight size={11} />
                  <span>
                    Total: {empleadosConContratos.toLocaleString('es-PE')} empleados con contratos activos
                  </span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Planillas */}
        <Card className="animate-fade-in-up" style={{ animationDelay: '500ms', animationFillMode: 'both' }}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                Planillas recientes
              </CardTitle>
              <Badge variant="outline" className="text-[10px] font-mono h-5">
                {planillasQuery.isLoading ? '…' : `${planillas.length} periodos`}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <PlanillasList planillas={planillas} loading={planillasQuery.isLoading} />
          </CardContent>
        </Card>

        {/* Alerts */}
        <Card className="animate-fade-in-up" style={{ animationDelay: '560ms', animationFillMode: 'both' }}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                Alertas y avisos
              </CardTitle>
              {alertas.length > 0 && (
                <Badge variant="destructive" className="text-[10px] font-mono h-5">
                  {alertas.length}
                </Badge>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            {isAnyLoading ? (
              Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-12 w-full rounded-md" />)
            ) : alertas.length > 0 ? (
              alertas.map((a, i) => (
                <AlertRow key={i} tipo={a.tipo} mensaje={a.mensaje} modulo={a.modulo} />
              ))
            ) : (
              <div className="flex flex-col items-center justify-center py-6 gap-2">
                <CheckCircle2 size={24} className="text-emerald-500" />
                <p className="text-xs text-muted-foreground">Sin alertas activas</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
