import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'

import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'

import {
  cancelTenant,
  fetchTenant,
  reinviteTenant,
  suspendTenant,
} from '../services/tenantsAdminService'

export function TenantDetailPage() {
  const { id = '' } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [reinviteEmail, setReinviteEmail] = useState('')

  const { data: tenant, isLoading, isError } = useQuery({
    queryKey: ['admin-tenant', id],
    queryFn: () => fetchTenant(id),
    enabled: !!id,
  })

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['admin-tenant', id] })
    qc.invalidateQueries({ queryKey: ['admin-tenants'] })
  }

  const suspend = useMutation({
    mutationFn: () => suspendTenant(id),
    onSuccess: () => { toast.success('Tenant suspendido'); invalidate() },
    onError: () => toast.error('No se pudo suspender'),
  })

  const cancel = useMutation({
    mutationFn: () => cancelTenant(id),
    onSuccess: () => { toast.success('Tenant cancelado'); invalidate() },
    onError: () => toast.error('No se pudo cancelar'),
  })

  const reinvite = useMutation({
    mutationFn: () => reinviteTenant(id, reinviteEmail),
    onSuccess: (data) => {
      toast.success(`Invitación enviada. URL: ${data.activation_url}`, { duration: 15000 })
      setReinviteEmail('')
    },
    onError: () => toast.error('No se pudo crear la invitación'),
  })

  if (isLoading) return <div>Cargando…</div>
  if (isError || !tenant) return <div className="text-destructive">No encontrado</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">{tenant.name}</h1>
          <div className="text-sm text-muted-foreground font-mono">
            {tenant.slug}.vyntia.pe · RUC {tenant.ruc}
          </div>
        </div>
        <Button variant="outline" onClick={() => navigate('/admin/tenants')}>
          ← Volver
        </Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Estado</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 text-sm">
          <div>Plan: <Badge>{tenant.plan}</Badge></div>
          <div>Estado: <Badge>{tenant.status}</Badge></div>
          <div>Miembros activos: <strong>{tenant.member_count}</strong></div>
          <div>Max usuarios: {tenant.max_users}</div>
          <div>Trial expira: {tenant.trial_ends_at?.split('T')[0] ?? '—'}</div>
          <div>Creado: {tenant.created_at.split('T')[0]}</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Acciones</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => suspend.mutate()}
              disabled={tenant.status === 'cancelled' || suspend.isPending}
            >
              Suspender
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                if (confirm(`¿Cancelar tenant ${tenant.name}? Esta acción es irreversible.`)) {
                  cancel.mutate()
                }
              }}
              disabled={tenant.status === 'cancelled' || cancel.isPending}
            >
              Cancelar tenant
            </Button>
          </div>
          <div className="flex gap-2 items-end pt-2 border-t">
            <div className="flex-1">
              <label className="text-xs text-muted-foreground">Re-invitar admin</label>
              <Input
                type="email"
                placeholder="email@ejemplo.com"
                value={reinviteEmail}
                onChange={(e) => setReinviteEmail(e.target.value)}
              />
            </div>
            <Button
              onClick={() => reinvite.mutate()}
              disabled={!reinviteEmail || reinvite.isPending}
            >
              Re-invitar
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
