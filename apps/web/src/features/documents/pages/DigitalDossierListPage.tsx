import { useEffect, useState } from 'react'
import { Archive, Download, FolderTree } from 'lucide-react'
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
  dossierService,
  type DigitalDossier,
} from '../services/dossierService'

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

export default function DigitalDossierListPage() {
  const [dossiers, setDossiers] = useState<DigitalDossier[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    dossierService
      .list()
      .then((rows) => {
        if (cancelled) return
        setDossiers(rows)
        setLoading(false)
      })
      .catch((e) => {
        if (cancelled) return
        toast.error(
          `Error cargando legajos: ${e instanceof Error ? e.message : 'desconocido'}`,
        )
        setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const handleDownload = async (id: string) => {
    setBusyId(id)
    try {
      const blob = await dossierService.downloadConsolidatedPdf(id)
      downloadBlob(blob, `legajo_${id}.pdf`)
    } catch (e) {
      toast.error(
        `Error descargando: ${e instanceof Error ? e.message : 'desconocido'}`,
      )
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <header>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <FolderTree className="h-6 w-6 text-blue-600" />
          Legajos digitales
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Module 03.5 · expediente digital permanente del trabajador con 15
          secciones (incluye médicos y accidentes con permission level 9).
          Retención mínima 5 años post-cese (Ley 29733).
        </p>
      </header>

      {loading ? (
        <p className="text-muted-foreground">Cargando legajos…</p>
      ) : dossiers.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No hay legajos digitales todavía.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {dossiers.map((d) => (
            <Card key={d.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base leading-snug flex items-center gap-2">
                    <Archive className="h-4 w-4 text-muted-foreground" />
                    {d.id.slice(0, 8)}…
                  </CardTitle>
                  <Badge variant={d.is_closed ? 'outline' : 'default'}>
                    {d.is_closed ? 'Cerrado' : 'Activo'}
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  {d.sections.length} secciones · creado {new Date(d.created_at).toLocaleDateString()}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {d.retention_until && (
                  <div className="text-xs text-muted-foreground">
                    Retención hasta {new Date(d.retention_until).toLocaleDateString()}
                  </div>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  disabled={busyId === d.id}
                  onClick={() => handleDownload(d.id)}
                >
                  <Download className="h-3.5 w-3.5 mr-1" />
                  PDF consolidado
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
