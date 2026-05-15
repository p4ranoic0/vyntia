import { useEffect, useState } from 'react'
import { Award, BookOpen, Download, Play } from 'lucide-react'
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
  inductionService,
  type InductionPlan,
  type InductionStatus,
} from '../services/inductionService'

const STATUS_VARIANT: Record<
  InductionStatus,
  'secondary' | 'default' | 'outline'
> = {
  draft: 'secondary',
  in_progress: 'outline',
  completed: 'default',
  certified: 'default',
}

function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(url)
}

export default function InductionPlanListPage() {
  const [plans, setPlans] = useState<InductionPlan[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  const reload = () => {
    setLoading(true)
    inductionService
      .listPlans()
      .then(setPlans)
      .catch((e) =>
        toast.error(
          `Error cargando planes: ${e instanceof Error ? e.message : 'desconocido'}`,
        ),
      )
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])

  const handleStart = async (id: string) => {
    setBusyId(id)
    try {
      await inductionService.start(id)
      toast.success('Plan iniciado')
      reload()
    } catch (e) {
      toast.error(`Error iniciando: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleComplete = async (id: string) => {
    setBusyId(id)
    try {
      await inductionService.complete(id)
      toast.success('Plan completado')
      reload()
    } catch (e) {
      toast.error(`Error completando: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleCertify = async (id: string) => {
    setBusyId(id)
    try {
      await inductionService.certify(id)
      toast.success('Plan certificado')
      reload()
    } catch (e) {
      toast.error(`Error certificando: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleDownload = async (id: string) => {
    setBusyId(id)
    try {
      const blob = await inductionService.downloadCertificatePdf(id)
      downloadBlob(blob, `induccion_${id}.pdf`)
    } catch (e) {
      toast.error(`Error descargando: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <header>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <BookOpen className="h-6 w-6 text-blue-600" />
          Inducción
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Module 03.3 · planes RPE 265-2017-SERVIR-PE con checklist por día/semana/mes,
          mentor, evaluación y certificado obligatorio.
        </p>
      </header>

      {loading ? (
        <p className="text-muted-foreground">Cargando planes…</p>
      ) : plans.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No hay planes de inducción todavía.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {plans.map((p) => {
            const doneCount = p.tasks.filter((t) => t.is_done).length
            return (
              <Card key={p.id}>
                <CardHeader>
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-base leading-snug">
                      {p.title}
                    </CardTitle>
                    <Badge variant={STATUS_VARIANT[p.status]}>
                      {p.status_display}
                    </Badge>
                  </div>
                  <CardDescription className="text-xs">
                    {p.kind_display} · {doneCount}/{p.tasks.length} tareas
                    {p.lengua_originaria && ` · idioma ${p.lengua_originaria}`}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex flex-wrap gap-2">
                    <Button
                      size="sm"
                      disabled={busyId === p.id || p.status !== 'draft'}
                      onClick={() => handleStart(p.id)}
                    >
                      <Play className="h-3.5 w-3.5 mr-1" />
                      Iniciar
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={busyId === p.id || p.status !== 'in_progress'}
                      onClick={() => handleComplete(p.id)}
                    >
                      Completar
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={busyId === p.id || p.status !== 'completed'}
                      onClick={() => handleCertify(p.id)}
                    >
                      <Award className="h-3.5 w-3.5 mr-1" />
                      Certificar
                    </Button>
                  </div>
                  {(p.status === 'completed' || p.status === 'certified') && (
                    <Button
                      size="sm"
                      variant="ghost"
                      disabled={busyId === p.id}
                      onClick={() => handleDownload(p.id)}
                    >
                      <Download className="h-3.5 w-3.5 mr-1" />
                      Certificado PDF
                    </Button>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
