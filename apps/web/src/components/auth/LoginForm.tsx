'use client'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/components/ui/use-toast'
import { useAuth } from '@/hooks/useAuth'
import { zodResolver } from '@hookform/resolvers/zod'
import { Eye, EyeOff, Landmark, Loader2, Lock, ShieldCheck, User } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import * as z from 'zod'

const loginSchema = z.object({
  username: z.string().min(1, 'El nombre de usuario es requerido'),
  password: z.string().min(1, 'La contraseña es requerida'),
})

const forgotPasswordSchema = z.object({
  email: z.string().email('Ingrese un email válido').min(1, 'El email es requerido'),
})

type LoginFormData = z.infer<typeof loginSchema>

export default function LoginForm() {
  const { login, forgotPassword } = useAuth()
  const navigate = useNavigate()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [isForgotPasswordLoading, setIsForgotPasswordLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showForgotPassword, setShowForgotPassword] = useState(false)
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
  })

  const {
    register: registerForgot,
    handleSubmit: handleSubmitForgot,
    formState: { errors: errorsForgot },
    reset: resetForgot,
  } = useForm<z.infer<typeof forgotPasswordSchema>>({
    resolver: zodResolver(forgotPasswordSchema),
  })

  const onSubmit = async (values: z.infer<typeof loginSchema>) => {
    setIsLoading(true)
    try {
      const user = await login(values.username, values.password)
      toast({
        title: 'Éxito',
        description: 'Inicio de sesión exitoso'
      })
      
      // Verificar si el usuario necesita cambiar su contraseña
      if (user.requiere_cambio_password) {
        toast({
          title: 'Cambio de contraseña requerido',
          description: 'Por seguridad, debe cambiar su contraseña'
        })
        navigate('/cambiar-password')
      } else if (user.username === 'admin') {
        // Mantener la lógica existente para el usuario admin como respaldo
        toast({
          title: 'Recomendación de seguridad',
          description: 'Se recomienda cambiar la contraseña por seguridad'
        })
        navigate('/cambiar-password')
      } else {
        navigate('/dashboard')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error al iniciar sesión. Verifique sus credenciales.'
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const onForgotPasswordSubmit = async (values: z.infer<typeof forgotPasswordSchema>) => {
    setIsForgotPasswordLoading(true)
    try {
      const response = await forgotPassword(values.email)
      toast({
        title: 'Éxito',
        description: response.message || 'Se ha enviado un enlace de recuperación a su email'
      })
      setShowForgotPassword(false)
      resetForgot()
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error al enviar el enlace de recuperación'
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive'
      })
    } finally {
      setIsForgotPasswordLoading(false)
    }
  }

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }

  const handleBackToLogin = () => {
    setShowForgotPassword(false)
    resetForgot()
  }

  if (showForgotPassword) {
    return (
      <div className="relative min-h-screen overflow-hidden bg-slate-950 p-4 sm:p-6">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(34,211,238,0.25),transparent_40%),radial-gradient(circle_at_80%_0%,rgba(250,204,21,0.2),transparent_35%),radial-gradient(circle_at_50%_100%,rgba(14,165,233,0.15),transparent_40%)]" />
        <div className="relative mx-auto flex min-h-[92vh] max-w-6xl items-center justify-center">
          <Card className="w-full max-w-md border-slate-700/60 bg-slate-900/70 text-slate-100 shadow-2xl backdrop-blur-md">
            <CardHeader className="space-y-4 text-center pb-6">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-400/20 ring-1 ring-cyan-300/30">
                <Lock className="h-6 w-6 text-cyan-300" />
              </div>
              <CardTitle className="text-2xl font-bold text-slate-50">Recuperar Contraseña</CardTitle>
              <CardDescription className="text-slate-300">
                Enviaremos un enlace seguro a tu correo institucional.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <form onSubmit={handleSubmitForgot(onForgotPasswordSubmit)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-medium text-slate-200">
                    Email
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="ejemplo@empresa.com"
                    {...registerForgot('email')}
                    disabled={isForgotPasswordLoading}
                    className="h-12 border-slate-700 bg-slate-950/70 text-slate-50 placeholder:text-slate-400 focus-visible:ring-cyan-300"
                  />
                  {errorsForgot.email && (
                    <p className="text-sm text-red-300">
                      {errorsForgot.email.message}
                    </p>
                  )}
                </div>
                <div className="space-y-3">
                  <Button
                    type="submit"
                    className="h-12 w-full bg-cyan-300 text-slate-950 hover:bg-cyan-200"
                    disabled={isForgotPasswordLoading}
                  >
                    {isForgotPasswordLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Enviar Enlace de Recuperación
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    className="h-12 w-full border-slate-600 bg-slate-900 text-slate-100 hover:bg-slate-800"
                    onClick={handleBackToLogin}
                    disabled={isForgotPasswordLoading}
                  >
                    Volver al Login
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 p-4 sm:p-6">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(34,211,238,0.25),transparent_40%),radial-gradient(circle_at_85%_10%,rgba(250,204,21,0.22),transparent_35%),radial-gradient(circle_at_50%_100%,rgba(14,165,233,0.16),transparent_40%)]" />

      {import.meta.env.VITE_MOCK_MODE === 'true' && (
        <div className="absolute left-4 top-4 z-20 rounded-lg border border-amber-400/60 bg-amber-300/20 px-4 py-2 text-sm text-amber-100">
          <strong>Modo Demo:</strong> Usuario: admin, Contraseña: admin
        </div>
      )}

      <div className="relative mx-auto grid min-h-[92vh] max-w-6xl items-center gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="hidden rounded-3xl border border-slate-700/60 bg-slate-900/65 p-10 text-slate-100 shadow-2xl backdrop-blur-md lg:block">
          <div className="inline-flex items-center gap-2 rounded-full bg-[#6C63FF]/20 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-[#A5A0FF]">
            <ShieldCheck className="h-3.5 w-3.5" />
            VYNTIA · Acceso seguro
          </div>
          <h1 className="mt-5 text-4xl font-black leading-tight text-white">
            Donde el talento se convierte en valor.
          </h1>
          <p className="mt-4 max-w-xl text-sm leading-relaxed text-slate-300">
            VYNTIA conecta a tu equipo con datos, decisiones y procesos de RRHH en una sola plataforma.
          </p>

          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-cyan-300/20 bg-cyan-400/10 p-4">
              <p className="text-xs uppercase tracking-wide text-cyan-200">Módulos</p>
              <p className="mt-2 text-2xl font-bold text-white">13+</p>
            </div>
            <div className="rounded-2xl border border-emerald-300/20 bg-emerald-400/10 p-4">
              <p className="text-xs uppercase tracking-wide text-emerald-200">Procesos</p>
              <p className="mt-2 text-2xl font-bold text-white">Nómina</p>
            </div>
            <div className="rounded-2xl border border-amber-300/20 bg-amber-400/10 p-4">
              <p className="text-xs uppercase tracking-wide text-amber-200">Seguridad</p>
              <p className="mt-2 text-2xl font-bold text-white">RBAC</p>
            </div>
          </div>
        </section>

        <Card className="w-full border-slate-700/60 bg-slate-900/70 text-slate-100 shadow-2xl backdrop-blur-md">
          <CardHeader className="space-y-4 pb-6 text-center">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-400/20 ring-1 ring-cyan-300/30">
              <Landmark className="h-6 w-6 text-cyan-300" />
            </div>
            <CardTitle className="text-2xl font-bold text-slate-50">Iniciar Sesión</CardTitle>
            <CardDescription className="text-slate-300">
              Sistema Integral de Recursos Humanos
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username" className="text-sm font-medium text-slate-200">
                  Usuario
                </Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <Input
                    id="username"
                    type="text"
                    placeholder="Ingrese su usuario"
                    {...register('username')}
                    disabled={isLoading}
                    className="h-12 border-slate-700 bg-slate-950/70 pl-10 text-base text-slate-50 placeholder:text-slate-400 focus-visible:ring-cyan-300"
                  />
                </div>
                {errors.username && (
                  <p className="text-sm text-red-300">
                    {errors.username.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium text-slate-200">
                  Contraseña
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Ingrese su contraseña"
                    {...register('password')}
                    disabled={isLoading}
                    className="h-12 border-slate-700 bg-slate-950/70 pl-10 pr-10 text-base text-slate-50 placeholder:text-slate-400 focus-visible:ring-cyan-300"
                  />
                  <button
                    type="button"
                    onClick={togglePasswordVisibility}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 transition-colors hover:text-slate-100"
                    disabled={isLoading}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-sm text-red-300">
                    {errors.password.message}
                  </p>
                )}
              </div>

              <div className="flex items-center justify-end">
                <button
                  type="button"
                  onClick={() => setShowForgotPassword(true)}
                  className="text-sm font-medium text-cyan-300 transition-colors hover:text-cyan-200"
                  disabled={isLoading}
                >
                  ¿Olvidó su contraseña?
                </button>
              </div>

              <Button
                type="submit"
                className="h-12 w-full bg-cyan-300 text-slate-950 hover:bg-cyan-200"
                disabled={isLoading}
              >
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Iniciar Sesión
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}