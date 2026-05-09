import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { z } from 'zod'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'

import { createTenant, type CreateTenantPayload } from '../services/tenantsAdminService'

const Schema = z.object({
  slug: z.string().min(2).max(63).regex(/^[a-z0-9][a-z0-9-]*[a-z0-9]$/, 'Solo a-z, 0-9, guiones'),
  name: z.string().min(2).max(200),
  ruc: z.string().regex(/^\d{11}$/, 'RUC de 11 dígitos'),
  plan: z.enum(['starter', 'pro', 'enterprise', 'govtech']),
  trial_days: z.coerce.number().int().min(0).max(90),
  admin_email: z.string().email(),
  admin_name: z.string().min(2),
})

type FormValues = z.infer<typeof Schema>

export function CreateTenantPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const form = useForm<FormValues>({
    resolver: zodResolver(Schema),
    defaultValues: { plan: 'starter', trial_days: 30 } as FormValues,
  })

  const mutation = useMutation({
    mutationFn: (values: FormValues) => createTenant(values as CreateTenantPayload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['admin-tenants'] })
      toast.success(
        `Tenant "${data.tenant.slug}" creado. URL de activación: ${data.invitation.activation_url}`,
        { duration: 15000 },
      )
      navigate(`/admin/tenants/${data.tenant.id}`)
    },
    onError: (err: any) => {
      const detail = err?.response?.data?.message || 'Error al crear tenant'
      toast.error(detail)
    },
  })

  const fields: Array<[keyof FormValues, string, string?]> = [
    ['slug', 'Slug (subdomain)', 'acme'],
    ['name', 'Nombre legal', 'Acme Corp S.A.C.'],
    ['ruc', 'RUC (11 dígitos)', '20123456789'],
    ['admin_name', 'Nombre del admin', 'María Pérez'],
    ['admin_email', 'Email del admin', 'ceo@acme.com'],
  ]

  return (
    <div className="mx-auto max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Nuevo tenant</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={form.handleSubmit((v) => mutation.mutate(v))}
            className="space-y-4"
          >
            {fields.map(([name, label, placeholder]) => (
              <div className="space-y-2" key={name}>
                <Label htmlFor={name}>{label}</Label>
                <Input id={name} placeholder={placeholder} {...form.register(name)} />
                {form.formState.errors[name] && (
                  <p className="text-xs text-destructive">
                    {form.formState.errors[name]?.message as string}
                  </p>
                )}
              </div>
            ))}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="plan">Plan</Label>
                <select
                  id="plan"
                  {...form.register('plan')}
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                >
                  <option value="starter">Starter</option>
                  <option value="pro">Pro</option>
                  <option value="enterprise">Enterprise</option>
                  <option value="govtech">GovTech</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="trial_days">Trial (días)</Label>
                <Input
                  id="trial_days"
                  type="number"
                  {...form.register('trial_days', { valueAsNumber: true })}
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button type="button" variant="ghost" onClick={() => navigate('/admin/tenants')}>
                Cancelar
              </Button>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? 'Creando…' : 'Crear tenant'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
