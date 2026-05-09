import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'
import { z } from 'zod'

import { Button } from '@/shared/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'

import { activateInvitation } from '../services/activationService'

const ActivationSchema = z.object({
  name: z.string().min(2, 'Nombre requerido'),
  password: z.string().min(8, 'Mínimo 8 caracteres'),
})

type FormValues = z.infer<typeof ActivationSchema>

export function ActivationPage() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const token = params.get('token') ?? ''

  const form = useForm<FormValues>({
    resolver: zodResolver(ActivationSchema),
    defaultValues: { name: '', password: '' },
  })

  const mutation = useMutation({
    mutationFn: (values: FormValues) =>
      activateInvitation({ token, name: values.name, password: values.password }),
    onSuccess: (data) => {
      // Persist tokens and redirect to dashboard
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      toast.success(`Cuenta activada — bienvenido a ${data.tenant.name}`)
      navigate('/dashboard')
    },
    onError: () => {
      toast.error(
        'No se pudo activar la cuenta. El enlace puede haber expirado o ya se utilizó.',
      )
    },
  })

  if (!token) {
    return (
      <div className="mx-auto max-w-md p-8">
        <Card>
          <CardHeader>
            <CardTitle>Enlace inválido</CardTitle>
            <CardDescription>
              Este enlace de activación no es válido. Solicita uno nuevo a tu
              administrador de VYNTIA.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-md p-8">
      <Card>
        <CardHeader>
          <CardTitle>Activa tu cuenta VYNTIA</CardTitle>
          <CardDescription>
            Configura tu nombre y contraseña para acceder a tu workspace.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={form.handleSubmit((values) => mutation.mutate(values))}
            className="space-y-4"
          >
            <div className="space-y-2">
              <Label htmlFor="name">Nombre completo</Label>
              <Input id="name" autoComplete="name" {...form.register('name')} />
              {form.formState.errors.name && (
                <p className="text-xs text-destructive">
                  {form.formState.errors.name.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Contraseña</Label>
              <Input
                id="password"
                type="password"
                autoComplete="new-password"
                {...form.register('password')}
              />
              {form.formState.errors.password && (
                <p className="text-xs text-destructive">
                  {form.formState.errors.password.message}
                </p>
              )}
            </div>
            <Button type="submit" className="w-full" disabled={mutation.isPending}>
              {mutation.isPending ? 'Activando…' : 'Activar mi cuenta'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
