import { useQuery } from '@tanstack/react-query'

import { Badge } from '@/shared/ui/badge'

import { fetchSupportSessions } from '../services/supportSessionsService'

export function SupportSessionsListPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-support-sessions'],
    queryFn: () => fetchSupportSessions(1, 50),
  })

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Support Sessions</h1>
        <p className="text-sm text-muted-foreground">
          Historial de impersonaciones realizadas por staff de Vyntia.
        </p>
      </div>

      {isLoading && <div className="text-center py-8">Cargando…</div>}

      {data && data.results.length === 0 && (
        <div className="rounded-lg border border-dashed p-12 text-center text-sm text-muted-foreground">
          Sin sesiones de soporte registradas.
        </div>
      )}

      {data && data.results.length > 0 && (
        <div className="rounded-lg border bg-card">
          <table className="w-full text-sm">
            <thead className="border-b text-left text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3">Staff</th>
                <th className="px-4 py-3">Usuario</th>
                <th className="px-4 py-3">Tenant</th>
                <th className="px-4 py-3">Motivo</th>
                <th className="px-4 py-3">Inicio</th>
                <th className="px-4 py-3">Estado</th>
                <th className="px-4 py-3 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((s) => {
                const ended = !!s.ended_at
                const expired = !ended && new Date(s.expires_at) < new Date()
                return (
                  <tr key={s.id} className="border-b last:border-0 hover:bg-accent/50">
                    <td className="px-4 py-3 font-medium">{s.staff_user}</td>
                    <td className="px-4 py-3">{s.target_user}</td>
                    <td className="px-4 py-3 font-mono text-xs">{s.tenant_slug}</td>
                    <td className="px-4 py-3 max-w-xs truncate" title={s.reason}>{s.reason}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">
                      {new Date(s.started_at).toLocaleString('es-PE')}
                    </td>
                    <td className="px-4 py-3">
                      {ended ? <Badge variant="outline">Finalizada</Badge>
                        : expired ? <Badge variant="secondary">Expirada</Badge>
                        : <Badge>Activa</Badge>}
                    </td>
                    <td className="px-4 py-3 text-right">{s.actions_count}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
