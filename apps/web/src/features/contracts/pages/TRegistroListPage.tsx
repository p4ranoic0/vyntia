import { useEffect, useState } from 'react'
import { Download, FileText, Send, ShieldAlert } from 'lucide-react'
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
  tRegistroService,
  type TRegistroDeclaration,
  type DeclarationStatus,
} from '../services/tRegistroService'

const STATUS_VARIANT: Record<
  DeclarationStatus,
  'secondary' | 'default' | 'outline' | 'destructive'
> = {
  draft: 'secondary',
  validated: 'outline',
  submitted: 'default',
  accepted: 'default',
  rejected: 'destructive',
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

export default function TRegistroListPage() {
  const [declarations, setDeclarations] = useState<TRegistroDeclaration[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  const reload = () => {
    setLoading(true)
    tRegistroService
      .list()
      .then(setDeclarations)
      .catch((e) =>
        toast.error(
          `Error cargando declaraciones: ${e instanceof Error ? e.message : 'desconocido'}`,
        ),
      )
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])

  const handleValidate = async (id: string) => {
    setBusyId(id)
    try {
      const out = await tRegistroService.validatePvs(id)
      if (out.pvs_errors.length) {
        toast.warning(`${out.pvs_errors.length} errores PVS`)
      } else {
        toast.success('Declaración validada PVS')
      }
      reload()
    } catch (e) {
      toast.error(`Error validando: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleSubmit = async (id: string) => {
    setBusyId(id)
    try {
      await tRegistroService.submit(id, '')
      toast.success('Declaración enviada')
      reload()
    } catch (e) {
      toast.error(`Error enviando: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setBusyId(null)
    }
  }

  const handleDownload = async (id: string, ruc: string, kind: string) => {
    setBusyId(id)
    try {
      const blob = await tRegistroService.downloadAnexo3Txt(id)
      downloadBlob(blob, `tregistro_${ruc}_${kind}.txt`)
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
          <ShieldAlert className="h-6 w-6 text-blue-600" />
          T-Registro SUNAT
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Vinculación Module 03.2 · declaraciones alta / baja / modificación
          de trabajadores con generación de Anexo 3 y validación PVS.
        </p>
      </header>

      {loading ? (
        <p className="text-muted-foreground">Cargando declaraciones…</p>
      ) : declarations.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No hay declaraciones T-Registro todavía.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {declarations.map((d) => (
            <Card key={d.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base leading-snug">
                    {d.worker_apellido_paterno} {d.worker_nombres}
                  </CardTitle>
                  <Badge variant={STATUS_VARIANT[d.status]}>
                    {d.status_display}
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  {d.declaration_type_display} · DNI {d.worker_doc_number} ·
                  Régimen {d.regimen_laboral_code}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-xs text-muted-foreground">
                  RUC {d.employer_ruc} — {d.employer_razon_social}
                </div>
                {d.pvs_errors.length > 0 && (
                  <div className="text-xs text-red-700 line-clamp-2">
                    {d.pvs_errors.length} error(es) PVS: {d.pvs_errors[0]}
                  </div>
                )}
                <div className="flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={busyId === d.id || d.status === 'submitted' || d.status === 'accepted'}
                    onClick={() => handleValidate(d.id)}
                  >
                    Validar PVS
                  </Button>
                  <Button
                    size="sm"
                    disabled={busyId === d.id || d.status === 'submitted' || d.status === 'accepted'}
                    onClick={() => handleSubmit(d.id)}
                  >
                    <Send className="h-3.5 w-3.5 mr-1" />
                    Enviar
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={busyId === d.id}
                    onClick={() => handleDownload(d.id, d.employer_ruc, d.declaration_type)}
                  >
                    <Download className="h-3.5 w-3.5 mr-1" />
                    Anexo 3
                  </Button>
                </div>
                {d.sunat_reference && (
                  <div className="text-xs text-muted-foreground flex items-center gap-1">
                    <FileText className="h-3 w-3" />
                    Constancia {d.sunat_reference}
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
