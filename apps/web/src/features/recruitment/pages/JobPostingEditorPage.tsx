import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Briefcase, CheckCircle2, FileText, Plus } from 'lucide-react'
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
  type JobPosting,
} from '../services/selectionService'

const STATUS_VARIANT: Record<
  JobPosting['status'],
  'secondary' | 'default' | 'outline' | 'destructive'
> = {
  draft: 'secondary',
  published: 'default',
  in_evaluation: 'default',
  closed: 'outline',
  cancelled: 'outline',
  declared_void: 'destructive',
}

export default function JobPostingEditorPage() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const requisitionId = params.get('requisition') ?? undefined

  const [postings, setPostings] = useState<JobPosting[]>([])
  const [loading, setLoading] = useState(true)
  const [working, setWorking] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    selectionService
      .listPostings(requisitionId)
      .then((rows) => {
        if (cancelled) return
        setPostings(rows)
        setLoading(false)
      })
      .catch((e) => {
        if (cancelled) return
        toast.error(
          `Error cargando convocatorias: ${e instanceof Error ? e.message : 'desconocido'}`,
        )
        setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [requisitionId])

  async function handlePublish(p: JobPosting) {
    setWorking(p.id)
    try {
      const updated = await selectionService.publishPosting(p.id)
      setPostings(postings.map((x) => (x.id === p.id ? updated : x)))
      toast.success('Convocatoria publicada')
    } catch (e) {
      toast.error(
        `Error publicando: ${e instanceof Error ? e.message : 'desconocido'}`,
      )
    } finally {
      setWorking(null)
    }
  }

  async function handleClose(p: JobPosting) {
    setWorking(p.id)
    try {
      const updated = await selectionService.closePosting(p.id, 'Candidato seleccionado')
      setPostings(postings.map((x) => (x.id === p.id ? updated : x)))
      toast.success('Convocatoria cerrada')
    } catch (e) {
      toast.error(
        `Error cerrando: ${e instanceof Error ? e.message : 'desconocido'}`,
      )
    } finally {
      setWorking(null)
    }
  }

  const sectorBadge = (mode: JobPosting['sector_mode']) =>
    mode === 'public_servir' ? (
      <Badge variant="secondary" className="text-xs">SERVIR</Badge>
    ) : (
      <Badge variant="outline" className="text-xs">Privado</Badge>
    )

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Briefcase className="h-6 w-6 text-blue-600" />
            Convocatorias {requisitionId && '(filtradas por requisición)'}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Convocatorias privadas (Ley 728 / DL 1057-CAS) o públicas
            (concurso SERVIR Ley 30057). Crear vía API hasta B.9.1.
          </p>
        </div>
        <Button disabled title="Creación desde aquí en B.9.1">
          <Plus className="h-4 w-4 mr-2" />
          Nueva convocatoria
        </Button>
      </header>

      {loading ? (
        <p className="text-muted-foreground">Cargando convocatorias…</p>
      ) : postings.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No hay convocatorias todavía.
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {postings.length} convocatoria(s)
            </CardTitle>
            <CardDescription>
              Acciones disponibles según estado actual de cada convocatoria.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Título</TableHead>
                  <TableHead>Sector</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Postulaciones</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {postings.map((p) => (
                  <TableRow key={p.id}>
                    <TableCell>
                      <div className="font-medium">{p.title}</div>
                      <div className="text-xs text-muted-foreground">
                        {p.code || p.id}
                      </div>
                    </TableCell>
                    <TableCell>{sectorBadge(p.sector_mode)}</TableCell>
                    <TableCell>
                      <Badge variant={STATUS_VARIANT[p.status]}>
                        {p.status_display}
                      </Badge>
                    </TableCell>
                    <TableCell>{p.application_count ?? 0}</TableCell>
                    <TableCell className="text-right space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => navigate(`/seleccion/convocatorias/${p.id}/candidatos`)}
                      >
                        <FileText className="h-3 w-3 mr-1" />
                        Candidatos
                      </Button>
                      {p.status === 'draft' && (
                        <Button
                          size="sm"
                          onClick={() => handlePublish(p)}
                          disabled={working === p.id}
                        >
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                          Publicar
                        </Button>
                      )}
                      {(p.status === 'published' || p.status === 'in_evaluation') && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleClose(p)}
                          disabled={working === p.id}
                        >
                          Cerrar
                        </Button>
                      )}
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
