import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'
import { useAuth } from '@/hooks/useAuth'
import { cn } from '@/lib/utils'
import vacacionesService, {
    PeriodoVacacional,
    ResumenPeriodo,
    SolicitudVacacionesForm
} from '@/services/vacacionesService'
import { zodResolver } from '@hookform/resolvers/zod'
import { addDays, differenceInDays, format, isWeekend } from 'date-fns'
import { es } from 'date-fns/locale'
import { AlertTriangle, ArrowLeft, CalendarIcon, CheckCircle, Clock } from 'lucide-react'
import React, { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import * as z from 'zod'

// Schema de validación
const solicitudSchema = z.object({
  periodo_vacacional_id: z.string().min(1, 'Debe seleccionar un período vacacional'),
  fecha_inicio_solicitud: z.date({
    required_error: 'La fecha de inicio es requerida'
  }),
  fecha_fin_solicitud: z.date({
    required_error: 'La fecha de fin es requerida'
  }),
  observaciones_solicitud: z.string().optional(),
  fraccionamiento: z.boolean().default(false),
  medio_dia: z.boolean().default(false)
}).refine((data) => {
  return data.fecha_fin_solicitud >= data.fecha_inicio_solicitud
}, {
  message: 'La fecha de fin debe ser posterior a la fecha de inicio',
  path: ['fecha_fin_solicitud']
}).refine((data) => {
  if (!data.medio_dia) return true
  return data.fecha_inicio_solicitud && data.fecha_fin_solicitud
    ? data.fecha_inicio_solicitud.toDateString() === data.fecha_fin_solicitud.toDateString()
    : true
}, {
  message: 'El medio día solo aplica cuando la fecha de inicio y fin son iguales',
  path: ['medio_dia']
})

type SolicitudFormData = z.infer<typeof solicitudSchema>

// Componente para mostrar información del período seleccionado
interface InfoPeriodoProps {
  periodo: PeriodoVacacional | null
  resumen: ResumenPeriodo | null
}

const InfoPeriodo: React.FC<InfoPeriodoProps> = ({ periodo, resumen }) => {
  if (!periodo || !resumen) return null

  const porcentajeUso = (resumen?.dias_correspondientes || 0) > 0 
    ? (((resumen?.dias_correspondientes || 0) - (resumen?.dias_pendientes || 0)) / (resumen?.dias_correspondientes || 1)) * 100 
    : 0

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="text-lg">Información del Período</CardTitle>
        <CardDescription>
          Período vacacional {periodo.ano_periodo}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-2">
            <Label className="text-sm font-medium">Días Correspondientes</Label>
            <div className="text-2xl font-bold text-blue-600">
              {resumen?.dias_correspondientes || 0}
            </div>
          </div>
          
          <div className="space-y-2">
            <Label className="text-sm font-medium">Días Pendientes</Label>
            <div className="text-2xl font-bold text-green-600">
              {resumen?.dias_pendientes || 0}
            </div>
          </div>
          
          <div className="space-y-2">
            <Label className="text-sm font-medium">Días Utilizados</Label>
            <div className="text-2xl font-bold text-orange-600">
              {(resumen?.dias_correspondientes || 0) - (resumen?.dias_pendientes || 0)}
            </div>
          </div>
        </div>
        
        {/* Barra de progreso */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-muted-foreground mb-2">
            <span>Uso del período</span>
            <span>{porcentajeUso.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
              style={{ width: `${porcentajeUso}%` }}
            ></div>
          </div>
        </div>
        
        {/* Alertas */}
        {(resumen?.dias_pendientes || 0) === 0 && (
          <Alert className="mt-4">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              No tienes días pendientes en este período.
            </AlertDescription>
          </Alert>
        )}
        
        {resumen?.vencimiento_proximo && (
          <Alert className="mt-4">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Tienes días próximos a vencer en este período.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}

// Componente para mostrar el cálculo de días
interface CalculoDiasProps {
  fechaInicio: Date | null
  fechaFin: Date | null
  fraccionamiento: boolean
  medioDia: boolean
}

const CalculoDias: React.FC<CalculoDiasProps> = ({ fechaInicio, fechaFin, fraccionamiento, medioDia }) => {
  const [calculo, setCalculo] = useState<{
    dias_calendario: number
    dias_habiles: number
    incluye_fines_semana: boolean
  } | null>(null)

  useEffect(() => {
    if (fechaInicio && fechaFin) {
      if (medioDia) {
        setCalculo({
          dias_calendario: 1,
          dias_habiles: 0.5,
          incluye_fines_semana: isWeekend(fechaInicio)
        })
        return
      }
      const diasCalendario = differenceInDays(fechaFin, fechaInicio) + 1
      let diasHabiles = 0
      let incluyeFinesSemana = false
      
      // Calcular días hábiles
      for (let i = 0; i < diasCalendario; i++) {
        const fecha = addDays(fechaInicio, i)
        if (isWeekend(fecha)) {
          incluyeFinesSemana = true
        } else {
          diasHabiles++
        }
      }
      
      setCalculo({
        dias_calendario: diasCalendario,
        dias_habiles: diasHabiles,
        incluye_fines_semana: incluyeFinesSemana
      })
    } else {
      setCalculo(null)
    }
  }, [fechaInicio, fechaFin, medioDia])

  if (!calculo) return null

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="text-lg">Cálculo de Días</CardTitle>
        <CardDescription>
          Resumen de los días solicitados
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label className="text-sm font-medium">Días Calendario</Label>
            <div className="text-xl font-bold">{calculo.dias_calendario}</div>
            <p className="text-xs text-muted-foreground">
              Total de días incluyendo fines de semana
            </p>
          </div>
          
          <div className="space-y-2">
            <Label className="text-sm font-medium">Días Hábiles</Label>
            <div className="text-xl font-bold text-blue-600">{calculo.dias_habiles}</div>
            <p className="text-xs text-muted-foreground">
              Días que se descontarán del período
            </p>
          </div>
        </div>
        
        {calculo.incluye_fines_semana && (
          <Alert className="mt-4">
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>
              El período incluye fines de semana que no se descontarán de tu saldo.
            </AlertDescription>
          </Alert>
        )}
        
        {fraccionamiento && (
          <Alert className="mt-4">
            <Clock className="h-4 w-4" />
            <AlertDescription>
              Esta solicitud será marcada como fraccionamiento de vacaciones.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}

// Componente principal
const NuevaSolicitudPage: React.FC = () => {
  const { user } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [periodos, setPeriodos] = useState<PeriodoVacacional[]>([])
  const [resumenPeriodo, setResumenPeriodo] = useState<ResumenPeriodo | null>(null)
  const [periodoSeleccionado, setPeriodoSeleccionado] = useState<PeriodoVacacional | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors }
  } = useForm<SolicitudFormData>({
    resolver: zodResolver(solicitudSchema)
  })

  const watchedValues = watch()
  const { fecha_inicio_solicitud, fecha_fin_solicitud, periodo_vacacional_id, fraccionamiento, medio_dia } = watchedValues

  // Cargar períodos disponibles
  useEffect(() => {
    const cargarPeriodos = async () => {
      if (!user?.empleado_id) return
      
      try {
        setLoading(true)
        const periodosRes = await vacacionesService.getPeriodosByEmpleado(user.empleado_id)
        // Filtrar solo períodos activos con días pendientes
        const periodosDisponibles = periodosRes.filter(
          periodo => periodo.estado_periodo === 'activo' && periodo.dias_pendientes > 0
        )
        setPeriodos(periodosDisponibles)
      } catch (error) {
        console.error('Error al cargar períodos:', error)
        toast({
          title: 'Error',
          description: 'No se pudieron cargar los períodos vacacionales',
          variant: 'destructive'
        })
      } finally {
        setLoading(false)
      }
    }

    cargarPeriodos()
  }, [user?.empleado_id, toast])

  // Cargar resumen del período seleccionado
  useEffect(() => {
    const cargarResumenPeriodo = async () => {
      if (!periodo_vacacional_id || !user?.empleado_id || periodos.length === 0) {
        setResumenPeriodo(null)
        setPeriodoSeleccionado(null)
        return
      }
      
      try {
        const periodo = periodos.find(p => p.id.toString() === periodo_vacacional_id)
        if (periodo) {
          setPeriodoSeleccionado(periodo)
          const resumen = await vacacionesService.getResumenPeriodo(user.empleado_id, periodo.id)
          setResumenPeriodo(resumen)
        }
      } catch (error) {
        console.error('Error al cargar resumen del período:', error)
      }
    }

    cargarResumenPeriodo()
  }, [periodo_vacacional_id, user?.empleado_id, periodos])

  const onSubmit = async (data: SolicitudFormData) => {
    if (!user?.empleado_id) return
    
    try {
      setSubmitting(true)
      
      const solicitudData: SolicitudVacacionesForm = {
        empleado_id: user?.empleado_id || 0,
        periodo_vacacional_id: parseInt(data.periodo_vacacional_id),
        fecha_inicio_solicitud: format(data.fecha_inicio_solicitud, 'yyyy-MM-dd'),
        fecha_fin_solicitud: format(data.fecha_fin_solicitud, 'yyyy-MM-dd'),
        observaciones_solicitud: data.observaciones_solicitud || '',
        fraccionamiento: data.fraccionamiento,
        medio_dia: data.medio_dia
      }
      
      await vacacionesService.createSolicitud(solicitudData)
      
      toast({
        title: 'Solicitud creada',
        description: 'Tu solicitud de vacaciones ha sido enviada correctamente'
      })
      
      navigate('/vacaciones')
      
    } catch (error: any) {
      console.error('Error al crear solicitud:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.message || 'No se pudo crear la solicitud',
        variant: 'destructive'
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleVolver = () => {
    navigate('/vacaciones')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  if ((periodos?.length || 0) === 0) {
    return (
      <div className="container mx-auto p-4 sm:p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4 mb-4 sm:mb-6">
          <Button variant="outline" onClick={handleVolver}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver
          </Button>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Nueva Solicitud de Vacaciones</h1>
          </div>
        </div>
        
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            No tienes períodos vacacionales activos con días disponibles para solicitar.
            Contacta con Recursos Humanos para más información.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-4 sm:p-6 max-w-4xl">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4 mb-4 sm:mb-6">
        <Button variant="outline" onClick={handleVolver}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Volver
        </Button>
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Nueva Solicitud de Vacaciones</h1>
          <p className="text-muted-foreground">
            Completa el formulario para solicitar tus días de vacaciones
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Selección de período */}
        <Card>
          <CardHeader>
            <CardTitle>Período Vacacional</CardTitle>
            <CardDescription>
              Selecciona el período del cual deseas tomar vacaciones
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="periodo">Período *</Label>
              <Select 
                value={periodo_vacacional_id || ''} 
                onValueChange={(value) => setValue('periodo_vacacional_id', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un período vacacional" />
                </SelectTrigger>
                <SelectContent>
                  {(periodos || [])
                    .filter(periodo => periodo?.id && periodo?.ano_periodo)
                    .map((periodo) => (
                    <SelectItem key={periodo.id} value={periodo.id.toString()}>
                      <div className="flex items-center justify-between w-full">
                        <span>Período {periodo.ano_periodo}</span>
                        <Badge variant="outline" className="ml-2">
                          {periodo?.dias_pendientes || 0} días disponibles
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.periodo_vacacional_id && (
                <p className="text-sm text-red-500">{errors.periodo_vacacional_id.message}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Información del período seleccionado */}
        <InfoPeriodo periodo={periodoSeleccionado} resumen={resumenPeriodo} />

        {/* Fechas de solicitud */}
        <Card>
          <CardHeader>
            <CardTitle>Fechas de Vacaciones</CardTitle>
            <CardDescription>
              Selecciona las fechas de inicio y fin de tus vacaciones
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              {/* Fecha de inicio */}
              <div className="space-y-2">
                <Label>Fecha de Inicio *</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        'w-full justify-start text-left font-normal',
                        !fecha_inicio_solicitud && 'text-muted-foreground'
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {fecha_inicio_solicitud ? (
                        format(fecha_inicio_solicitud, 'PPP', { locale: es })
                      ) : (
                        'Selecciona fecha de inicio'
                      )}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                      mode="single"
                      selected={fecha_inicio_solicitud}
                      onSelect={(date) => setValue('fecha_inicio_solicitud', date!)}
                      disabled={(date) => date < new Date()}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
                {errors.fecha_inicio_solicitud && (
                  <p className="text-sm text-red-500">{errors.fecha_inicio_solicitud.message}</p>
                )}
              </div>

              {/* Fecha de fin */}
              <div className="space-y-2">
                <Label>Fecha de Fin *</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        'w-full justify-start text-left font-normal',
                        !fecha_fin_solicitud && 'text-muted-foreground'
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {fecha_fin_solicitud ? (
                        format(fecha_fin_solicitud, 'PPP', { locale: es })
                      ) : (
                        'Selecciona fecha de fin'
                      )}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                      mode="single"
                      selected={fecha_fin_solicitud}
                      onSelect={(date) => setValue('fecha_fin_solicitud', date!)}
                      disabled={(date) => 
                        date < new Date() || 
                        (fecha_inicio_solicitud && date < fecha_inicio_solicitud)
                      }
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
                {errors.fecha_fin_solicitud && (
                  <p className="text-sm text-red-500">{errors.fecha_fin_solicitud.message}</p>
                )}
              </div>
            </div>

            {/* Fraccionamiento y medio día */}
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-6">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="fraccionamiento"
                  {...register('fraccionamiento')}
                  className="rounded border-gray-300"
                />
                <Label htmlFor="fraccionamiento" className="text-sm">
                  Marcar como fraccionamiento de vacaciones
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="medio_dia"
                  {...register('medio_dia')}
                  className="rounded border-gray-300"
                />
                <Label htmlFor="medio_dia" className="text-sm">
                  Solicitar medio día
                </Label>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Cálculo de días */}
        <CalculoDias 
          fechaInicio={fecha_inicio_solicitud}
          fechaFin={fecha_fin_solicitud}
          fraccionamiento={fraccionamiento || false}
          medioDia={medio_dia || false}
        />

        {/* Observaciones */}
        <Card>
          <CardHeader>
            <CardTitle>Observaciones</CardTitle>
            <CardDescription>
              Agrega cualquier comentario o información adicional (opcional)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Textarea
              {...register('observaciones_solicitud')}
              placeholder="Escribe aquí cualquier observación sobre tu solicitud..."
              rows={4}
            />
          </CardContent>
        </Card>

        {/* Botones de acción */}
        <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end sm:gap-4">
          <Button type="button" variant="outline" onClick={handleVolver}>
            Cancelar
          </Button>
          <Button type="submit" disabled={submitting}>
            {submitting ? (
              <>
                <LoadingSpinner className="mr-2 h-4 w-4" />
                Enviando...
              </>
            ) : (
              'Enviar Solicitud'
            )}
          </Button>
        </div>
      </form>
    </div>
  )
}

export default NuevaSolicitudPage
