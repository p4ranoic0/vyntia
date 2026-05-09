import { useQuery } from '@tanstack/react-query'
import { Building2, ChevronRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card'
import {
  exchangeWorkspace,
  fetchWorkspaces,
  type Workspace,
} from '../services/workspaceService'

/**
 * Workspace switcher page — the entry point at app.vyntia.pe.
 *
 * After login at app.vyntia.pe, lists the user's active workspaces.
 * Selecting one calls /workspaces/<slug>/exchange/ and redirects the browser
 * to <slug>.vyntia.pe/auth/exchange?token=<exchange_token>.
 */
export function WorkspacesPage() {
  const navigate = useNavigate()
  const { data, isLoading, isError } = useQuery({
    queryKey: ['workspaces'],
    queryFn: fetchWorkspaces,
  })

  async function handleSelect(workspace: Workspace) {
    try {
      const { redirect_url } = await exchangeWorkspace(workspace.slug)
      if (redirect_url) {
        window.location.href = redirect_url
      } else {
        toast.error('No se pudo abrir el workspace.')
      }
    } catch {
      toast.error(`Error al abrir ${workspace.name}.`)
    }
  }

  if (isLoading) {
    return <div className="p-8 text-center">Cargando workspaces…</div>
  }

  if (isError) {
    return (
      <div className="p-8 text-center text-destructive">
        Error al cargar workspaces. Intenta nuevamente.
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="mx-auto max-w-md p-8">
        <Card>
          <CardHeader>
            <CardTitle>Sin workspaces</CardTitle>
            <CardDescription>
              No tienes acceso activo a ningún workspace de VYNTIA. Si crees que
              esto es un error, contacta a tu administrador.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" onClick={() => navigate('/login')}>
              Volver al login
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      <h1 className="mb-2 text-2xl font-semibold">Selecciona un workspace</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        Tienes acceso a {data.length} workspace{data.length !== 1 ? 's' : ''} en VYNTIA.
      </p>
      <div className="space-y-3">
        {data.map((workspace) => (
          <button
            key={workspace.tenant_id}
            type="button"
            onClick={() => handleSelect(workspace)}
            className="flex w-full items-center gap-4 rounded-lg border bg-card p-4 text-left transition-colors hover:bg-accent"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-primary">
              <Building2 size={20} aria-hidden />
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-medium">{workspace.name}</div>
              <div className="text-xs text-muted-foreground">
                {workspace.slug}.vyntia.pe · {workspace.role} · plan {workspace.plan}
              </div>
            </div>
            <ChevronRight size={18} className="text-muted-foreground" aria-hidden />
          </button>
        ))}
      </div>
    </div>
  )
}
