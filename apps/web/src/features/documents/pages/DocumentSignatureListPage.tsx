import { useEffect, useState } from 'react'
import { PenLine } from 'lucide-react'
import { toast } from 'sonner'

import { Badge } from '@/shared/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card'

import {
  documentSignatureService,
  type DocumentSignature,
  type SignatureStatus,
} from '../services/documentSignatureService'

const STATUS_VARIANT: Record<
  SignatureStatus,
  'secondary' | 'default' | 'outline' | 'destructive'
> = {
  requested: 'secondary',
  signed: 'default',
  rejected: 'destructive',
  expired: 'outline',
}

export default function DocumentSignatureListPage() {
  const [signatures, setSignatures] = useState<DocumentSignature[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    documentSignatureService
      .list()
      .then((rows) => {
        if (cancelled) return
        setSignatures(rows)
        setLoading(false)
      })
      .catch((e) => {
        if (cancelled) return
        toast.error(
          `Error cargando firmas: ${e instanceof Error ? e.message : 'desconocido'}`,
        )
        setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="p-6 space-y-6">
      <header>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <PenLine className="h-6 w-6 text-blue-600" />
          Firmas electrónicas
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Vinculación Module 03.2 · captura de firma manuscrita (canvas),
          tipeada o acuse simple para cualquier DigitalDocument del bundle.
        </p>
      </header>

      {loading ? (
        <p className="text-muted-foreground">Cargando firmas…</p>
      ) : signatures.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No hay solicitudes de firma todavía.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {signatures.map((sig) => (
            <Card key={sig.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base leading-snug">
                    {sig.signer_name}
                  </CardTitle>
                  <Badge variant={STATUS_VARIANT[sig.status]}>
                    {sig.status_display}
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  {sig.kind_display} · Doc {sig.signer_doc_number}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2 text-xs text-muted-foreground">
                <div>Solicitada {new Date(sig.requested_at).toLocaleString()}</div>
                {sig.signed_at && (
                  <div>Firmada {new Date(sig.signed_at).toLocaleString()}</div>
                )}
                {sig.expires_at && sig.status === 'requested' && (
                  <div>
                    Vence {new Date(sig.expires_at).toLocaleDateString()}
                  </div>
                )}
                {sig.rejection_reason && (
                  <div className="text-red-700 line-clamp-2">
                    {sig.rejection_reason}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
