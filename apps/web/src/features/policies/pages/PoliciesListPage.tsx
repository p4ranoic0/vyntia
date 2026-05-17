import { useEffect, useState } from 'react'
import { BookCheck, Plus, Archive } from 'lucide-react'
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
  type Policy,
  type PolicyStatus,
} from '../services/policiesService'

const STATUS_VARIANT: Record<
  PolicyStatus,
  'secondary' | 'default' | 'outline' | 'destructive'
> = {
  draft: 'secondary',
  in_review: 'outline',
  approved: 'outline',
  published: 'default',
  retired: 'destructive',
}

export default function PoliciesListPage() {
  const [items, setItems] = useState<Policy[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  const reload = () => {
    setLoading(true)
    policiesService
      .listPolicies()
      .then(setItems)
      .catch((e) =>
        toast.error(
          `Error cargando políticas: ${e instanceof Error ? e.message : 'desconocido'}`,
        ),
      )
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])

  const handleRetire = async (id: string) => {
    if (!window.confirm('¿Retirar esta política? La versión vigente quedará retirada.')) {
      return
    }
    setBusyId(id)
    try {
      await policiesService.retirePolicy(id)
      toast.success('Política retirada')
      reload()
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <BookCheck className="h-6 w-6" /> Políticas y reglamentos
          </h1>
          <p className="text-muted-foreground">
            Gestión documental Módulo 01 — RIT, Código de Ética, Reglamento SST, políticas internas.
          </p>
        </div>
        <Button disabled title="Crear política — formulario en próxima iteración">
          <Plus className="h-4 w-4 mr-1" /> Nueva política
        </Button>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Catálogo</CardTitle>
          <CardDescription>
            {loading ? 'Cargando…' : `${items.length} política(s)`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {items.length === 0 && !loading ? (
            <p className="text-muted-foreground text-sm">
              No hay políticas registradas todavía.
            </p>
          ) : (
            <div className="space-y-3">
              {items.map((p) => (
                <div
                  key={p.id}
                  className="flex items-start justify-between gap-4 border rounded-lg p-4"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium truncate">{p.title}</h3>
                      <Badge variant={STATUS_VARIANT[p.status]}>
                        {p.status_display}
                      </Badge>
                      <Badge variant="outline">{p.kind_display}</Badge>
                    </div>
                    {p.description && (
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                        {p.description}
                      </p>
                    )}
                    <p className="text-xs text-muted-foreground mt-2">
                      Actualizada: {new Date(p.updated_at).toLocaleString('es-PE')}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    {p.status !== 'retired' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRetire(p.id)}
                        disabled={busyId === p.id}
                      >
                        <Archive className="h-4 w-4 mr-1" /> Retirar
                      </Button>
                    )}
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
