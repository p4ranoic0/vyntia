import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
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

import {
  publicPositionService,
  type PositionRegister,
  type RegisterType,
} from '../services/publicPositionService'
import { useTenantSector } from '../hooks/useTenantSector'

const STATUS_VARIANT: Record<
  PositionRegister['status'],
  'secondary' | 'default' | 'outline'
> = {
  draft: 'secondary',
  approved: 'default',
  registered_servir: 'default',
  superseded: 'outline',
  archived: 'outline',
}

const TYPE_TITLES: Record<RegisterType, { title: string; subtitle: string; basis: string }> = {
  cpe: {
    title: 'Cuadro de Puestos de la Entidad (CPE)',
    subtitle: 'Ley 30057 SERVIR · Servicio Civil',
    basis:
      'El CPE inventaría todos los puestos del régimen Ley 30057 y se registra en SERVIR tras su aprobación. El MPP se genera a partir de él.',
  },
  cap: {
    title: 'Cuadro de Asignación de Personal (CAP)',
    subtitle: 'DL 276 / DL 728 — régimen transitorio',
    basis:
      'El CAP es el instrumento del régimen transitorio (276 / 728). Clasifica los cargos en FP, EC, SP-DS, SP-EJ, SP-ES, SP-AP y RE.',
  },
}

interface Props {
  defaultType?: RegisterType
}

export default function PositionRegisterListPage({ defaultType }: Readonly<Props>) {
  const sector = useTenantSector()
  const navigate = useNavigate()
  const params = useParams<{ type?: string }>()

  const type: RegisterType = useMemo(() => {
    if (defaultType) return defaultType
    if (params.type === 'cap') return 'cap'
    return 'cpe'
  }, [defaultType, params.type])

  const [registers, setRegisters] = useState<PositionRegister[]>([])
  const [loading, setLoading] = useState(true)
  const [createOpen, setCreateOpen] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    publicPositionService
      .listRegisters(type)
      .then((rows) => {
        if (cancelled) return
        setRegisters(rows)
        setLoading(false)
      })
      .catch((e) => {
        if (cancelled) return
        toast.error(
          `Error cargando registros: ${e instanceof Error ? e.message : 'desconocido'}`,
        )
        setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [type])

  if (sector !== 'public') {
    return (
      <Card className="m-6">
        <CardHeader>
          <CardTitle>Cuadros de Puestos del Sector Público</CardTitle>
          <CardDescription>
            Estos instrumentos (CPE — Ley 30057 SERVIR · CAP — DL 276/728)
            aplican únicamente a tenants del sector público. Su tenant está
            clasificado como sector privado — utilice el módulo CCF (B.7) en
            su lugar.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const meta = TYPE_TITLES[type]

  async function handleCreate() {
    if (!newTitle.trim()) {
      toast.error('El título es requerido')
      return
    }
    setSubmitting(true)
    try {
      const created = await publicPositionService.createRegister({
        register_type: type,
        title: newTitle.trim(),
        description: newDescription.trim(),
      })
      toast.success(`Registro "${created.title}" creado`)
      setCreateOpen(false)
      setNewTitle('')
      setNewDescription('')
      navigate(`/organizacion/registros/${type}/${created.id}`)
    } catch (e) {
      toast.error(
        `Error creando registro: ${e instanceof Error ? e.message : 'desconocido'}`,
      )
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
            {meta.title}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">{meta.subtitle}</p>
          <p className="text-sm text-muted-foreground mt-2 max-w-3xl">{meta.basis}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={type === 'cpe' ? 'default' : 'outline'}
            onClick={() => navigate('/organizacion/registros/cpe')}
            size="sm"
          >
            CPE
          </Button>
          <Button
            variant={type === 'cap' ? 'default' : 'outline'}
            onClick={() => navigate('/organizacion/registros/cap')}
            size="sm"
          >
            CAP
          </Button>
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Nuevo {type.toUpperCase()}
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Crear {type.toUpperCase()}</DialogTitle>
                <DialogDescription>
                  El registro quedará en estado "Borrador" hasta su aprobación.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-2">
                <div className="space-y-2">
                  <Label htmlFor="title">Título *</Label>
                  <Input
                    id="title"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder={`${type.toUpperCase()} 2026`}
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
        </div>
      </header>

      {loading ? (
        <p className="text-muted-foreground">Cargando registros…</p>
      ) : registers.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            No hay registros {type.toUpperCase()} todavía. Cree uno con el
            botón "Nuevo {type.toUpperCase()}".
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {registers.map((reg) => (
            <Card
              key={reg.id}
              className="cursor-pointer hover:shadow-md transition"
              onClick={() => navigate(`/organizacion/registros/${type}/${reg.id}`)}
            >
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base leading-snug">{reg.title}</CardTitle>
                  <Badge variant={STATUS_VARIANT[reg.status]}>{reg.status_display}</Badge>
                </div>
                <CardDescription className="text-xs">
                  v{reg.version}
                  {reg.effective_date && ` · efectivo desde ${reg.effective_date}`}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                  {reg.description || 'Sin descripción.'}
                </p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{reg.entry_count} puestos</span>
                  {reg.status === 'registered_servir' && (
                    <span className="flex items-center gap-1 text-green-700">
                      <CheckCircle2 className="h-3 w-3" />
                      Registrado SERVIR
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
