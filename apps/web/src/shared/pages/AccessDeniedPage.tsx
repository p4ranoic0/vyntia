import { Button } from '@/shared/ui/button'
import { ShieldAlert } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function AccessDeniedPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-center">
      <ShieldAlert className="h-16 w-16 text-destructive" />
      <h1 className="text-2xl font-bold text-foreground">Acceso Denegado</h1>
      <p className="text-muted-foreground max-w-md">
        No tienes permisos suficientes para acceder a esta seccion.
        Contacta al administrador del sistema si crees que esto es un error.
      </p>
      <Button asChild variant="outline">
        <Link to="/dashboard">Volver al inicio</Link>
      </Button>
    </div>
  )
}
