import { useAuth } from '@/features/auth/hooks/useAuth'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { Button } from '@/shared/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card'
import LoginForm from '@/features/auth/components/LoginForm'

interface AdminLoginGateProps {
  children: React.ReactNode
}

export function AdminLoginGate({ children }: AdminLoginGateProps) {
  const { isAuthenticated, isLoading, user, logout } = useAuth()

  if (isLoading) return <LoadingSpinner />
  if (!isAuthenticated) return <LoginForm />

  if (!user?.is_vyntia_staff) {
    return (
      <div className="mx-auto max-w-md p-8">
        <Card>
          <CardHeader>
            <CardTitle>Acceso restringido</CardTitle>
            <CardDescription>
              Esta sección está reservada para personal de Vyntia. Si crees que
              deberías tener acceso, contacta al equipo de operaciones.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" onClick={() => logout()}>
              Cerrar sesión
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return <>{children}</>
}
