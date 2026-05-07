import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/shared/ui/dropdown-menu'
import { useAuth } from '@/features/auth/hooks/useAuth'
import timeOffService, { SolicitudVacaciones } from '@/services/timeOffService'
import { Bell } from 'lucide-react'
import React, { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

interface NotificacionItem {
  id: string
  titulo: string
  descripcion: string
}

function buildItems(solicitudes: SolicitudVacaciones[]): NotificacionItem[] {
  return solicitudes.map((s) => ({
    id: s.id,
    titulo: s.empleado_nombre || s.empleado_nombre_completo || 'Solicitud',
    descripcion: `${s.fecha_inicio} - ${s.fecha_fin} (${s.dias_solicitados} días)`,
  }))
}

const NotificationsBell: React.FC = () => {
  const { isAdminOrRRHH, isJefe } = useAuth()
  const [items, setItems] = useState<NotificacionItem[]>([])
  const [loading, setLoading] = useState(false)

  const isGestor = isAdminOrRRHH()
  const esJefe = isJefe()

  const load = async () => {
    if (!esJefe && !isGestor) {
      setItems([])
      return
    }
    try {
      setLoading(true)
      const data = isGestor
        ? await timeOffService.getSolicitudesPendientes()
        : await timeOffService.getSolicitudesPendientesJefe()
      setItems(buildItems(data).slice(0, 5))
    } catch {
      setItems([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    const interval = setInterval(load, 2 * 60 * 1000)
    return () => clearInterval(interval)
  }, [esJefe, isGestor])

  const count = useMemo(() => items.length, [items])

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-10 w-10 relative cursor-pointer">
          <Bell className="w-5 h-5" />
          {count > 0 && (
            <Badge className="absolute -top-1 -right-1 h-5 min-w-[20px] px-1 text-[10px] flex items-center justify-center">
              {count}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel>Notificaciones</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {loading && (
          <DropdownMenuItem className="text-muted-foreground">Cargando...</DropdownMenuItem>
        )}
        {!loading && items.length === 0 && (
          <DropdownMenuItem className="text-muted-foreground">Sin notificaciones</DropdownMenuItem>
        )}
        {!loading &&
          items.map((item) => (
            <DropdownMenuItem key={item.id} className="flex flex-col items-start gap-1">
              <span className="text-sm font-medium">{item.titulo}</span>
              <span className="text-xs text-muted-foreground">{item.descripcion}</span>
            </DropdownMenuItem>
          ))}
        {(esJefe || isGestor) && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild>
              <Link to="/vacaciones/solicitudes">Ver solicitudes</Link>
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default NotificationsBell
