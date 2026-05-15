import { useEffect, useState } from 'react'
import { Send, ClipboardCheck, Folder } from 'lucide-react'
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
  hiringBundleService,
  type HiringDocumentBundle,
  type BundleStatus,
} from '../services/hiringBundleService'

const STATUS_VARIANT: Record<
  BundleStatus,
  'secondary' | 'default' | 'outline'
> = {
  draft: 'secondary',
  sent: 'outline',
  acknowledged: 'default',
}

export default function HiringBundleListPage() {
  const [bundles, setBundles] = useState<HiringDocumentBundle[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  const reload = () => {
    setLoading(true)
    hiringBundleService
      .listBundles()
      .then(setBundles)
      .catch((e) =>
        toast.error(
          `Error cargando bundles: ${e instanceof Error ? e.message : 'desconocido'}`,
        ),
      )
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])

  const handleSend = async (id: string) => {
    setBusyId(id)
    try {
      await hiringBundleService.send(id)
      toast.success('Bundle enviado al colaborador')
      reload()
    } catch (e) {
      toast.error(`Error enviando: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleAcknowledge = async (id: string) => {
    setBusyId(id)
    try {
      await hiringBundleService.acknowledge(id)
      toast.success('Bundle acusado')
      reload()
    } catch (e) {
      toast.warning(
        `Aún faltan firmas: ${e instanceof Error ? e.message : 'incompleto'}`,
      )
    } finally {
      setBusyId(null)
    }
  }

  const countSigned = (b: HiringDocumentBundle) =>
    b.items.filter((it) => it.signature).length

  return (
    <div className="p-6 space-y-6">
      <header>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Folder className="h-6 w-6 text-blue-600" />
          Bundles de vinculación
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Vinculación Module 03.2 · paquete obligatorio (Contrato + RIT +
          Reglamento SST + Código de Ética + Política de Datos + Manual de
          Funciones) con acuse del colaborador.
        </p>
      </header>

      {loading ? (
        <p className="text-muted-foreground">Cargando bundles…</p>
      ) : bundles.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No hay bundles de vinculación todavía.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {bundles.map((b) => (
            <Card key={b.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base leading-snug">
                    {b.title}
                  </CardTitle>
                  <Badge variant={STATUS_VARIANT[b.status]}>
                    {b.status_display}
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  {b.items.length} ítems · {countSigned(b)} firmados
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <ul className="text-xs text-muted-foreground space-y-1">
                  {b.items.slice(0, 6).map((it) => (
                    <li key={it.id} className="flex justify-between">
                      <span>{it.kind_display}</span>
                      <span>
                        {it.document ? '📎' : '—'}{' '}
                        {it.signature ? '✓' : ''}
                      </span>
                    </li>
                  ))}
                </ul>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    disabled={busyId === b.id || b.status !== 'draft'}
                    onClick={() => handleSend(b.id)}
                  >
                    <Send className="h-3.5 w-3.5 mr-1" />
                    Enviar
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={busyId === b.id || b.status !== 'sent'}
                    onClick={() => handleAcknowledge(b.id)}
                  >
                    <ClipboardCheck className="h-3.5 w-3.5 mr-1" />
                    Acusar
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
