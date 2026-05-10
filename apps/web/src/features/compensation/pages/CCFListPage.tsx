import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle2, FileText, Plus } from 'lucide-react'
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/shared/ui/dialog'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Textarea } from '@/shared/ui/textarea'

import { ccfService, type CCF } from '../services/ccfService'
import { useTenantSector } from '../hooks/useTenantSector'

const STATUS_VARIANT: Record<CCF['status'], 'secondary' | 'default' | 'outline'> = {
  draft: 'secondary',
  approved: 'default',
  superseded: 'outline',
  archived: 'outline',
}

export default function CCFListPage() {
  const sector = useTenantSector()
  const navigate = useNavigate()
  const [ccfs, setCcfs] = useState<CCF[]>([])
  const [loading, setLoading] = useState(true)
  const [createOpen, setCreateOpen] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    let cancelled = false
    ccfService
      .listCCFs()
      .then((rows) => {
        if (!cancelled) {
          setCcfs(rows)
          setLoading(false)
        }
      })
      .catch((e) => {
        if (cancelled) return
        toast.error(`Error cargando CCFs: ${e instanceof Error ? e.message : 'desconocido'}`)
        setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (sector === 'public') {
    return (
      <Card className="m-6">
        <CardHeader>
          <CardTitle>Cuadro de Categorías y Funciones (CCF)</CardTitle>
          <CardDescription>
            El CCF (Ley 30709) aplica únicamente al sector privado. Su tenant
            está clasificado como sector público — utilice MPP/CPE (módulo
            B.8) en su lugar.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  async function handleCreate() {
    if (!newTitle.trim()) {
      toast.error('El título es requerido')
      return
    }
    setSubmitting(true)
    try {
      const created = await ccfService.createCCF({
        title: newTitle.trim(),
        description: newDescription.trim(),
      })
      toast.success(`CCF "${created.title}" creado`)
      setCreateOpen(false)
      setNewTitle('')
      setNewDescription('')
      navigate(`/compensacion/ccf/${created.id}`)
    } catch (e) {
      toast.error(`Error creando CCF: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <FileText className="h-6 w-6 text-blue-600" />
            Cuadro de Categorías y Funciones (CCF)
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Cumplimiento <strong>Ley 30709</strong> · Categorías objetivas con
            metodología 4 factores (R.M. 243-2018-TR) y bandas salariales.
          </p>
        </div>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Nuevo CCF
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Crear CCF</DialogTitle>
              <DialogDescription>
                Cree un nuevo Cuadro de Categorías y Funciones. Quedará en estado
                "Borrador" hasta su aprobación.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-2">
              <div className="space-y-2">
                <Label htmlFor="title">Título *</Label>
                <Input
                  id="title"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="CCF 2026"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Descripción</Label>
                <Textarea
                  id="description"
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Cuadro vigente del ejercicio 2026"
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setCreateOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleCreate} disabled={submitting}>
                {submitting ? 'Creando...' : 'Crear'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </header>

      {loading ? (
        <p className="text-muted-foreground">Cargando CCFs…</p>
      ) : ccfs.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No hay CCFs creados todavía. Cree uno con el botón "Nuevo CCF" o
            importe desde Excel desde el editor.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {ccfs.map((ccf) => (
            <Card
              key={ccf.id}
              className="cursor-pointer hover:shadow-md transition"
              onClick={() => navigate(`/compensacion/ccf/${ccf.id}`)}
            >
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base leading-snug">
                    {ccf.title}
                  </CardTitle>
                  <Badge variant={STATUS_VARIANT[ccf.status]}>
                    {ccf.status_display}
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  v{ccf.version}
                  {ccf.effective_date && ` · efectivo desde ${ccf.effective_date}`}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                  {ccf.description || 'Sin descripción.'}
                </p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{ccf.category_count} categorías</span>
                  {ccf.status === 'approved' && (
                    <span className="flex items-center gap-1 text-green-700">
                      <CheckCircle2 className="h-3 w-3" />
                      Aprobado
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
