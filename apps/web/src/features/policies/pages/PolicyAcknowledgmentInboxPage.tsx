import { useEffect, useState } from 'react'
import { ClipboardCheck, FileText, XCircle } from 'lucide-react'
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
  policiesService,
  type PolicyAcknowledgment,
} from '../services/policiesService'

/**
 * Bandeja de acuses — vista admin (filtra por status=pending).
 * El flujo employee-facing (firma canvas) se construirá sobre esta misma
 * data en una vista per-empleado posterior; aquí mostramos lo pendiente
 * a nivel organización para que RRHH monitoree adopción.
 */
export default function PolicyAcknowledgmentInboxPage() {
  const [items, setItems] = useState<PolicyAcknowledgment[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  const reload = () => {
    setLoading(true)
    policiesService
      .listAcknowledgments({ status: 'pending' })
      .then(setItems)
      .catch((e) =>
        toast.error(
          `Error cargando acuses: ${e instanceof Error ? e.message : 'desconocido'}`,
        ),
      )
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])

  const handleAcknowledge = async (id: string) => {
    setBusyId(id)
    try {
      await policiesService.acknowledge(id, {
        signature_kind: 'checkbox',
        signature_payload: 'true',
      })
      toast.success('Acuse registrado')
      reload()
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleDecline = async (id: string) => {
    const reason = window.prompt('Motivo del rechazo:')
    if (!reason) return
    setBusyId(id)
    try {
      await policiesService.decline(id, reason)
      toast.success('Acuse rechazado')
      reload()
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleExpireOverdue = async () => {
    try {
      const r = await policiesService.expireOverdue()
      toast.success(`${r.expired} acuse(s) vencido(s)`)
      reload()
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <ClipboardCheck className="h-6 w-6" /> Acuses de políticas
          </h1>
          <p className="text-muted-foreground">
            Bandeja de acuses pendientes. RRHH puede correr expire-overdue para
            cerrar los vencidos.
          </p>
        </div>
        <Button onClick={handleExpireOverdue} variant="outline">
          Vencer pendientes con deadline pasado
        </Button>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Pendientes</CardTitle>
          <CardDescription>
            {loading ? 'Cargando…' : `${items.length} acuse(s) pendientes`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {items.length === 0 && !loading ? (
            <p className="text-muted-foreground text-sm">
              No hay acuses pendientes.
            </p>
          ) : (
            <div className="space-y-3">
              {items.map((a) => (
                <div
                  key={a.id}
                  className="flex items-start justify-between gap-4 border rounded-lg p-4"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">
                        Publicación {a.publication.slice(0, 8)}…
                      </span>
                      <Badge variant="secondary">{a.status_display}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      Empleado {a.employee.slice(0, 8)}… · Creado:{' '}
                      {new Date(a.created_at).toLocaleString('es-PE')}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="default"
                      size="sm"
                      onClick={() => handleAcknowledge(a.id)}
                      disabled={busyId === a.id}
                    >
                      Marcar acusado
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDecline(a.id)}
                      disabled={busyId === a.id}
                    >
                      <XCircle className="h-4 w-4 mr-1" /> Rechazar
                    </Button>
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
