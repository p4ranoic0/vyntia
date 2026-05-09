import { useQuery } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { fetchTenants } from '../services/tenantsAdminService'

const statusBadgeVariant = {
  trial: 'secondary',
  active: 'default',
  suspended: 'destructive',
  cancelled: 'outline',
} as const

export function TenantsListPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin-tenants'],
    queryFn: () => fetchTenants(1, 50),
  })

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Tenants</h1>
          <p className="text-sm text-muted-foreground">
            Listado completo de workspaces VYNTIA.
          </p>
        </div>
        <Button asChild>
          <Link to="/admin/tenants/new">
            <Plus size={16} className="mr-2" /> Nuevo tenant
          </Link>
        </Button>
      </div>

      {isLoading && <div className="text-center py-8">Cargando…</div>}
      {isError && <div className="text-destructive text-center py-8">Error al cargar tenants.</div>}
      {data && data.results.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          No hay tenants. Crea el primero con el botón "Nuevo tenant".
        </div>
      )}

      {data && data.results.length > 0 && (
        <div className="rounded-lg border bg-card">
          <table className="w-full text-sm">
            <thead className="border-b text-left text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3">Slug</th>
                <th className="px-4 py-3">Nombre</th>
                <th className="px-4 py-3">Plan</th>
                <th className="px-4 py-3">Estado</th>
                <th className="px-4 py-3 text-right">Miembros</th>
                <th className="px-4 py-3">Creado</th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((t) => (
                <tr key={t.id} className="border-b last:border-0 hover:bg-accent/50">
                  <td className="px-4 py-3 font-mono">
                    <Link to={`/admin/tenants/${t.id}`} className="text-primary hover:underline">
                      {t.slug}
                    </Link>
                  </td>
                  <td className="px-4 py-3">{t.name}</td>
                  <td className="px-4 py-3">{t.plan}</td>
                  <td className="px-4 py-3">
                    <Badge variant={statusBadgeVariant[t.status]}>{t.status}</Badge>
                  </td>
                  <td className="px-4 py-3 text-right">{t.member_count}</td>
                  <td className="px-4 py-3 text-xs text-muted-foreground">
                    {new Date(t.created_at).toLocaleDateString('es-PE')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
