import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/shared/ui/dialog'
import { 
  ChevronLeft, 
  ChevronRight, 
  Calendar as CalendarIcon,
  Users,
  Clock,
  MapPin,
  Eye
} from 'lucide-react'
import { format, 
  startOfMonth, 
  endOfMonth, 
  startOfWeek, 
  endOfWeek, 
  addDays, 
  addMonths, 
  subMonths, 
  isSameMonth, 
  isSameDay, 
  isToday,
  parseISO
} from 'date-fns'
import { es } from 'date-fns/locale'
import { SolicitudVacaciones } from '@/features/time-off/services/timeOffService'
import timeOffService from '@/features/time-off/services/timeOffService'
import { useToast } from '@/shared/hooks/use-toast'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'

interface CalendarioVacacionesProps {
  empleadoId?: number
  areaId?: number
  className?: string
}

interface EventoCalendario {
  id: number
  titulo: string
  fechaInicio: Date
  fechaFin: Date
  tipo: 'vacaciones' | 'feriado' | 'evento'
  estado?: string
  empleado?: {
    id: number
    nombre: string
    area: string
  }
  solicitud?: SolicitudVacaciones
}

const CalendarioVacaciones: React.FC<CalendarioVacacionesProps> = ({ 
  empleadoId, 
  areaId, 
  className = '' 
}) => {
  const { toast } = useToast()
  const [currentDate, setCurrentDate] = useState(new Date())
  const [loading, setLoading] = useState(false)
  const [eventos, setEventos] = useState<EventoCalendario[]>([])
  const [selectedEvent, setSelectedEvent] = useState<EventoCalendario | null>(null)
  const [showEventDetail, setShowEventDetail] = useState(false)
  const [vistaActual, setVistaActual] = useState<'mes' | 'semana'>('mes')

  // Cargar eventos del calendario
  const cargarEventos = async (fecha: Date) => {
    try {
      setLoading(true)
      
      const inicioMes = startOfMonth(fecha)
      const finMes = endOfMonth(fecha)
      
      // Cargar solicitudes aprobadas para el mes
      const solicitudes = await timeOffService.getSolicitudes({
        fecha_inicio_desde: format(inicioMes, 'yyyy-MM-dd'),
        fecha_inicio_hasta: format(finMes, 'yyyy-MM-dd'),
        estado: 'aprobada',
        empleado_id: empleadoId,
        area_id: areaId
      })
      
      // Convertir solicitudes a eventos
      const eventosVacaciones: EventoCalendario[] = (solicitudes.results || solicitudes || []).map(solicitud => {
        // Manejar diferentes estructuras de datos del backend
        const empleadoNombre = solicitud.empleado_nombre_completo || 
                              `${solicitud.empleado?.nombres || ''} ${solicitud.empleado?.apellidos || ''}`.trim() ||
                              'Empleado'
        const fechaInicio = solicitud.fecha_inicio || solicitud.fecha_inicio_solicitud
        const fechaFin = solicitud.fecha_fin || solicitud.fecha_fin_solicitud
        const estado = solicitud.estado || solicitud.estado_solicitud
        const empleadoId = solicitud.empleado_id || solicitud.empleado?.id
        const empleadoArea = solicitud.empleado_area || solicitud.empleado?.area?.nombre || 'Sin área'
        
        // Validar fechas antes de parsear
        if (!fechaInicio || !fechaFin) {
          return null
        }
        
        try {
          return {
            id: solicitud.id,
            titulo: `${empleadoNombre} - Vacaciones`,
            fechaInicio: parseISO(fechaInicio),
            fechaFin: parseISO(fechaFin),
            tipo: 'vacaciones',
            estado: estado,
            empleado: {
              id: empleadoId,
              nombre: empleadoNombre,
              area: empleadoArea
            },
            solicitud
          }
        } catch (error) {
          console.warn('Error al parsear fechas para solicitud:', solicitud.id, error)
          return null
        }
      }).filter(evento => evento !== null) // Filtrar eventos nulos
      
      setEventos(eventosVacaciones)
      
    } catch (error) {
      console.error('Error al cargar eventos del calendario:', error)
      toast({
        title: 'Error',
        description: 'No se pudieron cargar los eventos del calendario',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    cargarEventos(currentDate)
  }, [currentDate, empleadoId, areaId])

  // Navegación del calendario
  const irMesAnterior = () => {
    setCurrentDate(subMonths(currentDate, 1))
  }

  const irMesSiguiente = () => {
    setCurrentDate(addMonths(currentDate, 1))
  }

  const irHoy = () => {
    setCurrentDate(new Date())
  }

  // Obtener eventos para una fecha específica
  const getEventosParaFecha = (fecha: Date): EventoCalendario[] => {
    return eventos.filter(evento => {
      const fechaEvento = evento.fechaInicio
      const fechaFinEvento = evento.fechaFin
      
      return fecha >= fechaEvento && fecha <= fechaFinEvento
    })
  }

  // Generar días del calendario
  const generarDiasCalendario = () => {
    const inicioMes = startOfMonth(currentDate)
    const finMes = endOfMonth(currentDate)
    const inicioCalendario = startOfWeek(inicioMes, { weekStartsOn: 1 }) // Lunes
    const finCalendario = endOfWeek(finMes, { weekStartsOn: 1 })
    
    const dias = []
    let dia = inicioCalendario
    
    while (dia <= finCalendario) {
      dias.push(dia)
      dia = addDays(dia, 1)
    }
    
    return dias
  }

  const handleVerDetalle = (evento: EventoCalendario) => {
    setSelectedEvent(evento)
    setShowEventDetail(true)
  }

  const dias = generarDiasCalendario()
  const diasSemana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <CalendarIcon className="h-5 w-5" />
              Calendario de Vacaciones
            </CardTitle>
            <CardDescription>
              {empleadoId ? 'Vacaciones del empleado' : 'Vacaciones de todos los empleados'}
            </CardDescription>
          </div>
          
          <div className="flex items-center gap-2">
            <Select value={vistaActual} onValueChange={(value: 'mes' | 'semana') => setVistaActual(value)}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="mes">Vista Mes</SelectItem>
                <SelectItem value="semana">Vista Semana</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        
        {/* Navegación del calendario */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={irMesAnterior}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={irMesSiguiente}>
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={irHoy}>
              Hoy
            </Button>
          </div>
          
          <h3 className="text-lg font-semibold">
            {format(currentDate, 'MMMM yyyy', { locale: es })}
          </h3>
          
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="bg-blue-100 text-blue-800">
              <Users className="mr-1 h-3 w-3" />
              {eventos.length} eventos
            </Badge>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <LoadingSpinner />
          </div>
        ) : (
          <div className="space-y-4">
            {/* Encabezados de días */}
            <div className="grid grid-cols-7 gap-1">
              {diasSemana.map(dia => (
                <div key={dia} className="p-2 text-center text-sm font-medium text-muted-foreground">
                  {dia}
                </div>
              ))}
            </div>
            
            {/* Días del calendario */}
            <div className="grid grid-cols-7 gap-1">
              {dias.map(dia => {
                const eventosDelDia = getEventosParaFecha(dia)
                const esHoy = isToday(dia)
                const esMesActual = isSameMonth(dia, currentDate)
                
                return (
                  <div
                    key={dia.toISOString()}
                    className={`
                      min-h-[80px] p-1 border rounded-lg transition-colors
                      ${esMesActual ? 'bg-white' : 'bg-gray-50'}
                      ${esHoy ? 'ring-2 ring-blue-500 bg-blue-50' : ''}
                      hover:bg-gray-50
                    `}
                  >
                    {/* Número del día */}
                    <div className={`
                      text-sm font-medium mb-1
                      ${esMesActual ? 'text-gray-900' : 'text-gray-400'}
                      ${esHoy ? 'text-blue-600 font-bold' : ''}
                    `}>
                      {format(dia, 'd')}
                    </div>
                    
                    {/* Eventos del día */}
                    <div className="space-y-1">
                      {eventosDelDia.slice(0, 2).map(evento => (
                        <div
                          key={evento.id}
                          className="text-xs p-1 rounded cursor-pointer transition-colors bg-blue-100 text-blue-800 hover:bg-blue-200"
                          onClick={() => handleVerDetalle(evento)}
                          title={evento.titulo}
                        >
                          <div className="truncate font-medium">
                            {evento.empleado?.nombre.split(' ')[0]}
                          </div>
                          {evento.tipo === 'vacaciones' && (
                            <div className="flex items-center gap-1">
                              <Clock className="h-2 w-2" />
                              <span>Vacaciones</span>
                            </div>
                          )}
                        </div>
                      ))}
                      
                      {/* Indicador de más eventos */}
                      {eventosDelDia.length > 2 && (
                        <div className="text-xs text-muted-foreground text-center">
                          +{eventosDelDia.length - 2} más
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
            
            {/* Leyenda */}
            <div className="flex items-center gap-4 pt-4 border-t">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-blue-100 border border-blue-300"></div>
                <span className="text-sm text-muted-foreground">Vacaciones Aprobadas</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-green-100 border border-green-300"></div>
                <span className="text-sm text-muted-foreground">Vacaciones en Curso</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded bg-orange-100 border border-orange-300"></div>
                <span className="text-sm text-muted-foreground">Vacaciones Futuras</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
      
      {/* Dialog para detalle del evento */}
      <Dialog open={showEventDetail} onOpenChange={setShowEventDetail}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Detalle de Vacaciones</DialogTitle>
            <DialogDescription>
              Información completa del período de vacaciones
            </DialogDescription>
          </DialogHeader>
          
          {selectedEvent && selectedEvent.solicitud && (
            <div className="space-y-4">
              {/* Información del empleado */}
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <Users className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="font-medium">{selectedEvent.empleado?.nombre}</p>
                  <p className="text-sm text-muted-foreground">
                    {selectedEvent.empleado?.area}
                  </p>
                </div>
              </div>
              
              {/* Fechas */}
              <div className="grid gap-3">
                <div className="flex items-center gap-2">
                  <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Período de Vacaciones</p>
                    <p className="text-sm text-muted-foreground">
                      {format(selectedEvent.fechaInicio, 'PPP', { locale: es })} - {format(selectedEvent.fechaFin, 'PPP', { locale: es })}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Duración</p>
                    <p className="text-sm text-muted-foreground">
                      {selectedEvent.solicitud.dias_calendario} días calendario, {selectedEvent.solicitud.dias_habiles} días hábiles
                    </p>
                  </div>
                </div>
              </div>
              
              {/* Estado */}
              <div className="flex items-center gap-2">
                <Badge 
                  variant={selectedEvent.estado === 'aprobada' ? 'default' : 'secondary'}
                  className={selectedEvent.estado === 'aprobada' ? 'bg-green-100 text-green-800' : ''}
                >
                  {selectedEvent.estado?.toUpperCase()}
                </Badge>
                
                {selectedEvent.solicitud.es_fraccionamiento && (
                  <Badge variant="outline" className="bg-blue-100 text-blue-800">
                    Fraccionamiento
                  </Badge>
                )}
              </div>
              
              {/* Observaciones */}
              {selectedEvent.solicitud.observaciones && (
                <div>
                  <p className="text-sm font-medium mb-1">Observaciones</p>
                  <p className="text-sm text-muted-foreground bg-gray-50 p-2 rounded">
                    {selectedEvent.solicitud.observaciones}
                  </p>
                </div>
              )}
              
              {/* Información del período */}
              <div className="border-t pt-3">
                <p className="text-sm font-medium mb-2">Información del Período</p>
                <div className="text-sm text-muted-foreground space-y-1">
                  <p>Período: {selectedEvent.solicitud.periodo_ano}</p>
                  <p>Solicitud creada: {format(new Date(selectedEvent.solicitud.created_at), 'PPP', { locale: es })}</p>
                  {selectedEvent.solicitud.fecha_aprobacion && (
                    <p>Aprobada: {format(new Date(selectedEvent.solicitud.fecha_aprobacion), 'PPP', { locale: es })}</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </Card>
  )
}

export default CalendarioVacaciones