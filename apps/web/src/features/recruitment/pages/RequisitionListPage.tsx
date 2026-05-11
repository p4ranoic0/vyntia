import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle2, ClipboardList, Plus } from 'lucide-react'
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
  selectionService,
  type PersonnelRequisition,
} from '../services/selectionService'

const STATUS_VARIANT: Record<
  PersonnelRequisition['status'],
  'secondary' | 'default' | 'outline' | 'destructive'
> = {
  draft: 'secondary',
  pending_approval: 'secondary',
  approved: 'default',
  rejected: 'destructive',
  cancelled: 'outline',
  fulfilled: 'default',
}

export default function RequisitionListPage() {
  const navigate = useNavigate()
  const [requisitions, setRequisitions] = useState<PersonnelRequisition[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    selectionService
      .listRequisitions()
      .then((rows) => {
        if (cancelled) return
        setRequisitions(rows)
        setLoading(false)
      })
      .catch((e) => {
        if (cancelled) return
        toast.error(
          `Error cargando requisiciones: ${e instanceof Error ? e.message : 'desconocido'}`,
        )
        setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <ClipboardList className="h-6 w-6 text-blue-600" />
            Requisiciones de Personal
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Selección Module 03.1 · alta autorizada (HR + Finanzas) para crear
            convocatorias.
          </p>
        </div>
        <Button disabled title="Creación desde aquí en B.9.1">
          <Plus className="h-4 w-4 mr-2" />
          Nueva requisición
        </Button>
      </header>

      {loading ? (
        <p className="text-muted-foreground">Cargando requisiciones…</p>
      ) : requisitions.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No hay requisiciones todavía. Cree una vía API o desde el módulo
            de planificación.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {requisitions.map((req) => (
            <Card
              key={req.id}
              className="cursor-pointer hover:shadow-md transition"
              onClick={() => navigate(`/seleccion/convocatorias?requisition=${req.id}`)}
            >
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base leading-snug">
                    {req.code || req.position_name || 'Requisición'}
                  </CardTitle>
                  <Badge variant={STATUS_VARIANT[req.status]}>
                    {req.status_display}
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  {req.department_name} · {req.justification_display}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground line-clamp-2 mb-3">
                  {req.justification_notes || 'Sin notas adicionales.'}
                </div>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span>{req.requested_count} plaza(s)</span>
                  {req.is_fully_approved && (
                    <span className="flex items-center gap-1 text-green-700">
                      <CheckCircle2 className="h-3 w-3" />
                      HR + Finanzas
                    </span>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
