import { useEffect, useState } from 'react'
import { ClipboardCheck, MessageSquare, ShieldOff } from 'lucide-react'
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
  exitFlowService,
  type ExitInterview,
  type HandoverChecklist,
  type SystemsOffboarding,
} from '../services/exitFlowService'

export default function ExitFlowListPage() {
  const [interviews, setInterviews] = useState<ExitInterview[]>([])
  const [checklists, setChecklists] = useState<HandoverChecklist[]>([])
  const [systems, setSystems] = useState<SystemsOffboarding[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  const reload = () => {
    setLoading(true)
    Promise.all([
      exitFlowService.listInterviews(),
      exitFlowService.listChecklists(),
      exitFlowService.listSystemsOffboardings(),
    ])
      .then(([i, c, s]) => {
        setInterviews(i)
        setChecklists(c)
        setSystems(s)
      })
      .catch((e) =>
        toast.error(
          `Error: ${e instanceof Error ? e.message : 'desconocido'}`,
        ),
      )
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])

  const handleDeliverItem = async (itemId: string) => {
    setBusyId(itemId)
    try {
      await exitFlowService.deliverItem(itemId)
      toast.success('Item entregado')
      reload()
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleItemNoAplica = async (itemId: string) => {
    setBusyId(itemId)
    try {
      await exitFlowService.itemNoAplica(itemId)
      toast.success('Item marcado N/A')
      reload()
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div className="p-6 space-y-8">
      <header>
        <h1 className="text-2xl font-bold">Flujo de salida</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Module 03.7 · Entrevistas + entrega de cargo + offboarding de sistemas.
        </p>
      </header>

      {loading ? (
        <p className="text-muted-foreground">Cargando…</p>
      ) : (
        <>
          <section className="space-y-3">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-blue-600" />
              Entrevistas de salida ({interviews.length})
            </h2>
            {interviews.length === 0 ? (
              <p className="text-sm text-muted-foreground">No hay entrevistas.</p>
            ) : (
              <div className="grid gap-3 md:grid-cols-2">
                {interviews.map((i) => (
                  <Card key={i.id}>
                    <CardHeader>
                      <div className="flex items-start justify-between gap-2">
                        <CardTitle className="text-sm">
                          Cese {i.termination.slice(0, 8)}
                        </CardTitle>
                        <Badge
                          variant={i.status === 'completed' ? 'default' : 'secondary'}
                        >
                          {i.status_display}
                        </Badge>
                      </div>
                      {i.sentiment && (
                        <CardDescription className="text-xs">
                          Sentimiento: {i.sentiment_display}
                        </CardDescription>
                      )}
                    </CardHeader>
                    <CardContent className="text-xs text-muted-foreground line-clamp-3">
                      {i.comments || <span className="italic">Sin comentarios</span>}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <ClipboardCheck className="h-5 w-5 text-emerald-700" />
              Entrega de cargo ({checklists.length})
            </h2>
            {checklists.length === 0 ? (
              <p className="text-sm text-muted-foreground">No hay checklists.</p>
            ) : (
              <div className="grid gap-3">
                {checklists.map((c) => (
                  <Card key={c.id}>
                    <CardHeader>
                      <div className="flex items-start justify-between gap-2">
                        <CardTitle className="text-sm">
                          Cese {c.termination.slice(0, 8)}
                        </CardTitle>
                        <Badge
                          variant={c.status === 'completed' ? 'default' : 'outline'}
                        >
                          {c.status_display}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="text-xs space-y-2">
                      {c.items.map((item) => (
                        <div
                          key={item.id}
                          className="flex items-center justify-between gap-2 border-b py-1 last:border-b-0"
                        >
                          <div className="flex-1">
                            <span className="font-medium">{item.name}</span>{' '}
                            <span className="text-muted-foreground">
                              ({item.kind_display})
                            </span>
                          </div>
                          <Badge
                            variant={
                              item.status === 'entregado'
                                ? 'default'
                                : item.status === 'no_aplica'
                                  ? 'secondary'
                                  : 'outline'
                            }
                          >
                            {item.status_display}
                          </Badge>
                          {item.status === 'pendiente' && (
                            <div className="flex gap-1">
                              <Button
                                size="sm"
                                disabled={busyId === item.id}
                                onClick={() => handleDeliverItem(item.id)}
                              >
                                Entregar
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                disabled={busyId === item.id}
                                onClick={() => handleItemNoAplica(item.id)}
                              >
                                N/A
                              </Button>
                            </div>
                          )}
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <ShieldOff className="h-5 w-5 text-rose-600" />
              Offboarding de sistemas ({systems.length})
            </h2>
            {systems.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No hay revocaciones registradas.
              </p>
            ) : (
              <div className="grid gap-3 md:grid-cols-2">
                {systems.map((s) => (
                  <Card key={s.id}>
                    <CardHeader>
                      <div className="flex items-start justify-between gap-2">
                        <CardTitle className="text-sm">
                          Cese {s.termination.slice(0, 8)}
                        </CardTitle>
                        <Badge
                          variant={s.status === 'completed' ? 'default' : 'outline'}
                        >
                          {s.status_display}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="text-xs space-y-1">
                      {Object.entries(s.checks).map(([sys, done]) => (
                        <div key={sys} className="flex justify-between">
                          <span className="capitalize">{sys}</span>
                          <span
                            className={done ? 'text-emerald-700' : 'text-rose-600'}
                          >
                            {done ? '✓' : '○'}
                          </span>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  )
}
