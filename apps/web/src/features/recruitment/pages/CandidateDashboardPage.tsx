import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Award, BarChart3, Trash2, Users } from 'lucide-react'
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui/table'

import {
  selectionService,
  type JobApplication,
  type JobPosting,
  type MeritRanking,
  type SelectionStage,
} from '../services/selectionService'

const STATUS_VARIANT: Record<
  JobApplication['status'],
  'secondary' | 'default' | 'outline' | 'destructive'
> = {
  received: 'secondary',
  reviewing: 'secondary',
  in_evaluation: 'secondary',
  eliminated: 'destructive',
  finalist: 'default',
  offered: 'default',
  accepted: 'default',
  hired: 'default',
  rejected: 'destructive',
  withdrawn: 'outline',
}

const OUTCOME_VARIANT: Record<
  MeritRanking['outcome'],
  'secondary' | 'default' | 'destructive'
> = {
  winner: 'default',
  waiting_list: 'secondary',
  eliminated: 'destructive',
}

export default function CandidateDashboardPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [posting, setPosting] = useState<JobPosting | null>(null)
  const [stages, setStages] = useState<SelectionStage[]>([])
  const [applications, setApplications] = useState<JobApplication[]>([])
  const [rankings, setRankings] = useState<MeritRanking[]>([])
  const [loading, setLoading] = useState(true)
  const [computing, setComputing] = useState(false)

  useEffect(() => {
    if (!id) return
    let cancelled = false
    ;(async () => {
      try {
        const [p, st, apps, rnk] = await Promise.all([
          selectionService.getPosting(id),
          selectionService.listStages(id),
          selectionService.listApplications(id),
          selectionService.listRanking(id),
        ])
        if (cancelled) return
        setPosting(p)
        setStages(st)
        setApplications(apps)
        setRankings(rnk)
      } catch (e) {
        if (cancelled) return
        toast.error(
          `Error cargando convocatoria: ${e instanceof Error ? e.message : 'desconocido'}`,
        )
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [id])

  async function handleEliminate(app: JobApplication) {
    try {
      const updated = await selectionService.eliminateApplication(app.id, {
        reason: 'Eliminado desde dashboard',
      })
      setApplications(applications.map((x) => (x.id === app.id ? updated : x)))
      toast.success('Postulación eliminada')
    } catch (e) {
      toast.error(
        `Error eliminando: ${e instanceof Error ? e.message : 'desconocido'}`,
      )
    }
  }

  async function handleComputeRanking() {
    if (!id) return
    setComputing(true)
    try {
      const rows = await selectionService.computeRanking(id)
      setRankings(rows)
      toast.success(`Cuadro de méritos calculado (${rows.length} candidatos)`)
    } catch (e) {
      toast.error(
        `Error calculando ranking: ${e instanceof Error ? e.message : 'desconocido'}`,
      )
    } finally {
      setComputing(false)
    }
  }

  if (loading) return <p className="p-6 text-muted-foreground">Cargando…</p>
  if (!posting) {
    return (
      <Card className="m-6">
        <CardContent className="py-6 text-center text-muted-foreground">
          Convocatoria no encontrada.
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <Button variant="ghost" onClick={() => navigate('/seleccion/convocatorias')}>
        <ArrowLeft className="h-4 w-4 mr-2" />
        Volver
      </Button>

      <Card>
        <CardHeader>
          <CardTitle className="text-xl">{posting.title}</CardTitle>
          <CardDescription>
            {posting.sector_mode_display} · {posting.status_display}
            {posting.applications_close_at && ` · cierre ${posting.applications_close_at}`}
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          {posting.summary || 'Sin descripción.'}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-3">
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                <Users className="h-4 w-4" />
                Postulaciones ({applications.length})
              </CardTitle>
              <CardDescription>
                {stages.length} etapa(s) configurada(s) · evalúa por API o
                interfaz por etapa (próximamente).
              </CardDescription>
            </div>
            <Button onClick={handleComputeRanking} disabled={computing}>
              <BarChart3 className="h-4 w-4 mr-2" />
              {computing ? 'Calculando…' : 'Calcular cuadro de méritos'}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {applications.length === 0 ? (
            <p className="text-sm text-muted-foreground py-6 text-center">
              Aún no hay postulaciones.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Candidato</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Postulado</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {applications.map((app) => (
                  <TableRow key={app.id}>
                    <TableCell>{app.candidate_name}</TableCell>
                    <TableCell>
                      <Badge variant={STATUS_VARIANT[app.status]}>
                        {app.status_display}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {new Date(app.applied_at).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right">
                      {app.status !== 'eliminated' && app.status !== 'hired' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEliminate(app)}
                        >
                          <Trash2 className="h-3 w-3 mr-1" />
                          Eliminar
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {rankings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Award className="h-4 w-4 text-amber-500" />
              Cuadro de méritos ({rankings.length})
            </CardTitle>
            <CardDescription>
              Snapshot calculado el{' '}
              {rankings[0]?.snapshot_at &&
                new Date(rankings[0].snapshot_at).toLocaleString()}
              . SERVIR transparency: detalle por etapa disponible en
              score_breakdown.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">#</TableHead>
                  <TableHead>Candidato</TableHead>
                  <TableHead>Puntaje</TableHead>
                  <TableHead>Outcome</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rankings.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="font-mono">{r.rank}</TableCell>
                    <TableCell>{r.candidate_name}</TableCell>
                    <TableCell className="font-mono">{r.total_score}</TableCell>
                    <TableCell>
                      <Badge variant={OUTCOME_VARIANT[r.outcome]}>
                        {r.outcome_display}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
