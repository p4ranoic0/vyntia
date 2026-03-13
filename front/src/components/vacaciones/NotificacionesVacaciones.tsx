import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Bell, 
  AlertTriangle, 
  Clock, 
  CheckCircle, 
  XCircle,
  Calendar,
  Users,
  TrendingUp,
  X,
  Eye,
  Check
} from 'lucide-react'
import { format, parseISO, differenceInDays } from 'date-fns'
import { es } from 'date-fns/locale'
import vacacionesService, { EstadisticasVacaciones as EstadisticasVacacionesType, EmpleadoDiasVencidos } from '@/services/vacacionesService'

interface Notificacion {
  id: string
  tipo: 'vencimiento' | 'solicitud_pendiente' | 'solicitud_aprobada' | 'solicitud_rechazada' | 'configuracion' | 'estadistica'
  titulo: string
  mensaje: string
  fecha: string
  leida: boolean
  prioridad: 'alta' | 'media' | 'baja'
  accion?: {
    texto: string
    onClick: () => void
  }
  datos?: any
}

interface NotificacionesVacacionesProps {
  empleadoId?: number
  esPersonal?: boolean
  onNotificacionClick?: (notificacion: Notificacion) => void
  maxNotificaciones?: number
  showHeader?: boolean
  autoRefresh?: boolean
}

const NotificacionesVacaciones: React.FC<NotificacionesVacacionesProps> = ({ 
  empleadoId,
  esPersonal = false,
  onNotificacionClick,
  maxNotificaciones = 10,
  showHeader = true,
  autoRefresh = true
}) => {
  const [notificaciones, setNotificaciones] = useState<Notificacion[]>([])
  const [loading, setLoading] = useState(true)
  const [estadisticas, setEstadisticas] = useState<EstadisticasVacacionesType | null>(null)
  const [empleadosVencidos, setEmpleadosVencidos] = useState<EmpleadoDiasVencidos[]>([])

  // Cargar datos iniciales
  useEffect(() => {
    cargarNotificaciones()
    
    if (autoRefresh) {
      const interval = setInterval(cargarNotificaciones, 5 * 60 * 1000) // Cada 5 minutos
      return () => clearInterval(interval)
    }
  }, [empleadoId, esPersonal, autoRefresh])

  const cargarNotificaciones = async () => {
    try {
      setLoading(true)
      
      // Cargar estadísticas
      const statsData = await vacacionesService.getEstadisticas()
      setEstadisticas(statsData[0] || null) // Tomar el primer elemento del array
      
      // Cargar empleados con días vencidos si es personal
      let empleadosVencidosData: EmpleadoDiasVencidos[] = []
      if (esPersonal) {
        empleadosVencidosData = await vacacionesService.getEmpleadosDiasVencidos()
        setEmpleadosVencidos(empleadosVencidosData)
      }
      
      // Generar notificaciones basadas en los datos
      const nuevasNotificaciones = await generarNotificaciones(statsData, empleadosVencidosData)
      setNotificaciones(nuevasNotificaciones.slice(0, maxNotificaciones))
      
    } catch (error) {
      console.error('Error al cargar notificaciones:', error)
    } finally {
      setLoading(false)
    }
  }

  const generarNotificaciones = async (stats: EstadisticasVacacionesType, empleadosVencidos: EmpleadoDiasVencidos[]): Promise<Notificacion[]> => {
    const notificaciones: Notificacion[] = []
    const ahora = new Date()

    // Notificaciones para empleados con días vencidos (solo para personal)
    if (esPersonal && empleadosVencidos.length > 0) {
      empleadosVencidos.forEach(empleado => {
        if (empleado.dias_vencidos > 0) {
          notificaciones.push({
            id: `vencido-${empleado.empleado.id}`,
            tipo: 'vencimiento',
            titulo: 'Días de vacaciones vencidos',
            mensaje: `${empleado.empleado.nombres} ${empleado.empleado.apellidos} tiene ${empleado.dias_vencidos} días vencidos desde ${format(parseISO(empleado.fecha_vencimiento), 'dd/MM/yyyy')}`,
            fecha: empleado.fecha_vencimiento,
            leida: false,
            prioridad: empleado.dias_vencidos > 30 ? 'alta' : 'media',
            datos: empleado
          })
        }
        
        // Verificar días próximos a vencer
        const diasRestantes = differenceInDays(parseISO(empleado.fecha_vencimiento), ahora)
        if (diasRestantes <= 30 && diasRestantes > 0) {
          const diasPorVencer = empleado.dias_totales - empleado.dias_vencidos
          if (diasPorVencer > 0) {
            notificaciones.push({
              id: `por-vencer-${empleado.empleado.id}`,
              tipo: 'vencimiento',
              titulo: 'Días próximos a vencer',
              mensaje: `${empleado.empleado.nombres} ${empleado.empleado.apellidos} tiene ${diasPorVencer} días que vencen en ${diasRestantes} días`,
              fecha: empleado.fecha_vencimiento,
              leida: false,
              prioridad: diasRestantes <= 7 ? 'alta' : 'media',
              datos: empleado
            })
          }
        }
      })
    }

    // Notificaciones de solicitudes pendientes (solo para personal)
    if (esPersonal && stats.solicitudes_pendientes > 0) {
      notificaciones.push({
        id: 'solicitudes-pendientes',
        tipo: 'solicitud_pendiente',
        titulo: 'Solicitudes pendientes de aprobación',
        mensaje: `Hay ${stats.solicitudes_pendientes} solicitudes esperando tu aprobación`,
        fecha: ahora.toISOString(),
        leida: false,
        prioridad: stats.solicitudes_pendientes > 5 ? 'alta' : 'media',
        accion: {
          texto: 'Revisar solicitudes',
          onClick: () => {
            // Navegar a la página de solicitudes
            window.location.hash = '#solicitudes'
          }
        }
      })
    }

    // Notificaciones de estadísticas importantes
    if (empleadosVencidos.length > 0) {
      const empleadosConDiasVencidos = empleadosVencidos.filter(emp => emp.dias_vencidos > 0).length
      if (empleadosConDiasVencidos > 0) {
        notificaciones.push({
          id: 'empleados-vencidos',
          tipo: 'estadistica',
          titulo: 'Empleados con días vencidos',
          mensaje: `${empleadosConDiasVencidos} empleados tienen días de vacaciones vencidos`,
          fecha: ahora.toISOString(),
          leida: false,
          prioridad: 'media',
          datos: { empleados_vencidos: empleadosConDiasVencidos }
        })
      }
    }

    // Notificación si no hay configuración activa (solo para personal)
    if (esPersonal) {
      try {
        const configuraciones = await vacacionesService.getConfiguraciones()
        const configuracionActiva = configuraciones.find(c => c.activo)
        
        if (!configuracionActiva) {
          notificaciones.push({
            id: 'sin-configuracion',
            tipo: 'configuracion',
            titulo: 'Sin configuración activa',
            mensaje: 'No hay una configuración de vacaciones activa. Los empleados no podrán solicitar vacaciones.',
            fecha: ahora.toISOString(),
            leida: false,
            prioridad: 'alta',
            accion: {
              texto: 'Configurar',
              onClick: () => {
                window.location.hash = '#configuracion'
              }
            }
          })
        }
      } catch (error) {
        console.error('Error al verificar configuración:', error)
      }
    }

    // Ordenar por prioridad y fecha
    return notificaciones.sort((a, b) => {
      const prioridadOrder = { alta: 3, media: 2, baja: 1 }
      const prioridadDiff = prioridadOrder[b.prioridad] - prioridadOrder[a.prioridad]
      if (prioridadDiff !== 0) return prioridadDiff
      
      return new Date(b.fecha).getTime() - new Date(a.fecha).getTime()
    })
  }

  const marcarComoLeida = (notificacionId: string) => {
    setNotificaciones(prev => 
      prev.map(n => n.id === notificacionId ? { ...n, leida: true } : n)
    )
  }

  const eliminarNotificacion = (notificacionId: string) => {
    setNotificaciones(prev => prev.filter(n => n.id !== notificacionId))
  }

  const getIconoTipo = (tipo: Notificacion['tipo']) => {
    switch (tipo) {
      case 'vencimiento':
        return <AlertTriangle className="h-4 w-4" />
      case 'solicitud_pendiente':
        return <Clock className="h-4 w-4" />
      case 'solicitud_aprobada':
        return <CheckCircle className="h-4 w-4" />
      case 'solicitud_rechazada':
        return <XCircle className="h-4 w-4" />
      case 'configuracion':
        return <Calendar className="h-4 w-4" />
      case 'estadistica':
        return <TrendingUp className="h-4 w-4" />
      default:
        return <Bell className="h-4 w-4" />
    }
  }

  const getColorPrioridad = (prioridad: Notificacion['prioridad']) => {
    switch (prioridad) {
      case 'alta':
        return 'border-red-200 bg-red-50'
      case 'media':
        return 'border-orange-200 bg-orange-50'
      case 'baja':
        return 'border-blue-200 bg-blue-50'
      default:
        return 'border-gray-200 bg-gray-50'
    }
  }

  const notificacionesNoLeidas = notificaciones.filter(n => !n.leida).length

  if (loading) {
    return (
      <Card>
        {showHeader && (
          <CardHeader>
            <div className="h-6 bg-gray-200 rounded w-48 mb-2 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-32 animate-pulse"></div>
          </CardHeader>
        )}
        <CardContent>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="p-3 border rounded-lg animate-pulse">
                <div className="flex items-start gap-3">
                  <div className="h-4 w-4 bg-gray-200 rounded"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 rounded w-48 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-64"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      {showHeader && (
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notificaciones
                {notificacionesNoLeidas > 0 && (
                  <Badge variant="destructive" className="ml-2">
                    {notificacionesNoLeidas}
                  </Badge>
                )}
              </CardTitle>
              <CardDescription>
                {notificaciones.length === 0 
                  ? 'No hay notificaciones'
                  : `${notificaciones.length} notificaciones`
                }
              </CardDescription>
            </div>
            
            <Button variant="outline" size="sm" onClick={cargarNotificaciones}>
              <Bell className="mr-2 h-4 w-4" />
              Actualizar
            </Button>
          </div>
        </CardHeader>
      )}
      
      <CardContent>
        {notificaciones.length === 0 ? (
          <div className="text-center py-6">
            <Bell className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Sin notificaciones</h3>
            <p className="text-gray-500">No hay notificaciones pendientes en este momento.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {notificaciones.map((notificacion) => (
              <Alert 
                key={notificacion.id} 
                className={`cursor-pointer transition-all hover:shadow-sm ${
                  !notificacion.leida ? getColorPrioridad(notificacion.prioridad) : 'border-gray-200'
                } ${!notificacion.leida ? 'border-l-4' : ''}`}
                onClick={() => {
                  if (!notificacion.leida) {
                    marcarComoLeida(notificacion.id)
                  }
                  onNotificacionClick?.(notificacion)
                }}
              >
                <div className="flex items-start gap-3">
                  <div className={`mt-0.5 ${
                    notificacion.prioridad === 'alta' ? 'text-red-600' :
                    notificacion.prioridad === 'media' ? 'text-orange-600' :
                    'text-blue-600'
                  }`}>
                    {getIconoTipo(notificacion.tipo)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className={`text-sm font-medium ${
                          !notificacion.leida ? 'text-gray-900' : 'text-gray-600'
                        }`}>
                          {notificacion.titulo}
                        </h4>
                        <AlertDescription className="mt-1">
                          {notificacion.mensaje}
                        </AlertDescription>
                        <p className="text-xs text-muted-foreground mt-2">
                          {format(parseISO(notificacion.fecha), 'PPp', { locale: es })}
                        </p>
                      </div>
                      
                      <div className="flex items-center gap-1 ml-2">
                        {!notificacion.leida && (
                          <Badge variant="secondary" className="text-xs">
                            Nuevo
                          </Badge>
                        )}
                        
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            eliminarNotificacion(notificacion.id)
                          }}
                          className="h-6 w-6 p-0"
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    {notificacion.accion && (
                      <div className="mt-3">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            notificacion.accion!.onClick()
                          }}
                        >
                          {notificacion.accion.texto}
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </Alert>
            ))}
          </div>
        )}
        
        {notificacionesNoLeidas > 0 && (
          <div className="mt-4 pt-4 border-t">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setNotificaciones(prev => prev.map(n => ({ ...n, leida: true })))
              }}
              className="w-full"
            >
              <Check className="mr-2 h-4 w-4" />
              Marcar todas como leídas
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default NotificacionesVacaciones