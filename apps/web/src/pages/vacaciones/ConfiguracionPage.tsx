import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'
import { useAuth } from '@/hooks/useAuth'
import timeOffService, {
    ConfiguracionVacaciones,
    PeriodoVacacional
} from '@/services/timeOffService'
import { zodResolver } from '@hookform/resolvers/zod'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import {
    AlertTriangle,
    ArrowLeft,
    Calendar,
    CheckCircle,
    Edit,
    Eye,
    Plus,
    RefreshCw,
    Save,
    Settings,
    Trash2,
    X
} from 'lucide-react'
import React, { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { z } from 'zod'

// Esquemas de validación
const configuracionSchema = z.object({
  dias_por_ano: z.number().min(1, 'Debe ser mayor a 0').max(365, 'No puede exceder 365 días'),
  dias_minimos_solicitud: z.number().min(1, 'Debe ser mayor a 0'),
  dias_maximos_solicitud: z.number().min(1, 'Debe ser mayor a 0'),
  permite_fraccionamiento: z.boolean(),
  dias_minimos_fraccionamiento: z.number().min(1, 'Debe ser mayor a 0').optional(),
  dias_anticipacion_solicitud: z.number().min(0, 'No puede ser negativo'),
  fecha_inicio_vigencia: z.string().min(1, 'Fecha requerida'),
  fecha_fin_vigencia: z.string().optional(),
  observaciones: z.string().optional()
}).refine((data) => {
  return data.dias_maximos_solicitud >= data.dias_minimos_solicitud
}, {
  message: "Los días máximos deben ser mayor o igual a los días mínimos",
  path: ["dias_maximos_solicitud"]
}).refine((data) => {
  if (data.permite_fraccionamiento && !data.dias_minimos_fraccionamiento) {
    return false
  }
  return true
}, {
  message: "Debe especificar los días mínimos para fraccionamiento",
  path: ["dias_minimos_fraccionamiento"]
})

const periodoSchema = z.object({
  empleado_id: z.number().min(1, 'Empleado requerido'),
  ano_periodo: z.number().min(2020, 'Año inválido').max(2030, 'Año inválido'),
  fecha_inicio: z.string().min(1, 'Fecha requerida'),
  fecha_fin: z.string().min(1, 'Fecha requerida'),
  dias_correspondientes: z.number().min(1, 'Debe ser mayor a 0'),
  fecha_vencimiento: z.string().optional(),
  observaciones: z.string().optional()
}).refine((data) => {
  return new Date(data.fecha_fin) > new Date(data.fecha_inicio)
}, {
  message: "La fecha de fin debe ser posterior a la fecha de inicio",
  path: ["fecha_fin"]
})

type ConfiguracionFormData = z.infer<typeof configuracionSchema>
type PeriodoFormData = z.infer<typeof periodoSchema>

// Componente para mostrar el estado de configuración
interface EstadoConfiguracionBadgeProps {
  activa: boolean
}

const EstadoConfiguracionBadge: React.FC<EstadoConfiguracionBadgeProps> = ({ activa }) => {
  return (
    <Badge variant={activa ? 'default' : 'secondary'} className={activa ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
      {activa ? 'ACTIVA' : 'INACTIVA'}
    </Badge>
  )
}

// Componente para formulario de configuración
interface FormularioConfiguracionProps {
  configuracion?: ConfiguracionVacaciones
  onSubmit: (data: ConfiguracionFormData) => Promise<void>
  onCancel: () => void
  loading?: boolean
}

const FormularioConfiguracion: React.FC<FormularioConfiguracionProps> = ({ 
  configuracion, 
  onSubmit, 
  onCancel, 
  loading = false 
}) => {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors }
  } = useForm<ConfiguracionFormData>({
    resolver: zodResolver(configuracionSchema),
    defaultValues: configuracion ? {
      dias_por_ano: configuracion.dias_por_ano,
      dias_minimos_solicitud: configuracion.dias_minimos_solicitud,
      dias_maximos_solicitud: configuracion.dias_maximos_solicitud,
      permite_fraccionamiento: configuracion.permite_fraccionamiento,
      dias_minimos_fraccionamiento: configuracion.dias_minimos_fraccionamiento || undefined,
      dias_anticipacion_solicitud: configuracion.dias_anticipacion_solicitud,
      fecha_inicio_vigencia: configuracion.fecha_inicio_vigencia,
      fecha_fin_vigencia: configuracion.fecha_fin_vigencia || '',
      observaciones: configuracion.observaciones || ''
    } : {
      dias_por_ano: 15,
      dias_minimos_solicitud: 1,
      dias_maximos_solicitud: 15,
      permite_fraccionamiento: true,
      dias_minimos_fraccionamiento: 1,
      dias_anticipacion_solicitud: 15,
      fecha_inicio_vigencia: format(new Date(), 'yyyy-MM-dd'),
      fecha_fin_vigencia: '',
      observaciones: ''
    }
  })

  const permiteFraccionamiento = watch('permite_fraccionamiento')

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Configuración básica */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="dias_por_ano">Días por Año *</Label>
          <Input
            id="dias_por_ano"
            type="number"
            {...register('dias_por_ano', { valueAsNumber: true })}
            className={errors.dias_por_ano ? 'border-red-500' : ''}
          />
          {errors.dias_por_ano && (
            <p className="text-sm text-red-500">{errors.dias_por_ano.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="dias_anticipacion_solicitud">Días de Anticipación *</Label>
          <Input
            id="dias_anticipacion_solicitud"
            type="number"
            {...register('dias_anticipacion_solicitud', { valueAsNumber: true })}
            className={errors.dias_anticipacion_solicitud ? 'border-red-500' : ''}
          />
          {errors.dias_anticipacion_solicitud && (
            <p className="text-sm text-red-500">{errors.dias_anticipacion_solicitud.message}</p>
          )}
        </div>
      </div>

      {/* Límites de solicitud */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="dias_minimos_solicitud">Días Mínimos por Solicitud *</Label>
          <Input
            id="dias_minimos_solicitud"
            type="number"
            {...register('dias_minimos_solicitud', { valueAsNumber: true })}
            className={errors.dias_minimos_solicitud ? 'border-red-500' : ''}
          />
          {errors.dias_minimos_solicitud && (
            <p className="text-sm text-red-500">{errors.dias_minimos_solicitud.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="dias_maximos_solicitud">Días Máximos por Solicitud *</Label>
          <Input
            id="dias_maximos_solicitud"
            type="number"
            {...register('dias_maximos_solicitud', { valueAsNumber: true })}
            className={errors.dias_maximos_solicitud ? 'border-red-500' : ''}
          />
          {errors.dias_maximos_solicitud && (
            <p className="text-sm text-red-500">{errors.dias_maximos_solicitud.message}</p>
          )}
        </div>
      </div>

      {/* Fraccionamiento */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <Switch
            id="permite_fraccionamiento"
            checked={permiteFraccionamiento}
            onCheckedChange={(checked) => setValue('permite_fraccionamiento', checked)}
          />
          <Label htmlFor="permite_fraccionamiento">Permitir Fraccionamiento</Label>
        </div>

        {permiteFraccionamiento && (
          <div className="space-y-2">
            <Label htmlFor="dias_minimos_fraccionamiento">Días Mínimos para Fraccionamiento *</Label>
            <Input
              id="dias_minimos_fraccionamiento"
              type="number"
              {...register('dias_minimos_fraccionamiento', { valueAsNumber: true })}
              className={errors.dias_minimos_fraccionamiento ? 'border-red-500' : ''}
            />
            {errors.dias_minimos_fraccionamiento && (
              <p className="text-sm text-red-500">{errors.dias_minimos_fraccionamiento.message}</p>
            )}
          </div>
        )}
      </div>

      {/* Fechas de vigencia */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="fecha_inicio_vigencia">Fecha Inicio Vigencia *</Label>
          <Input
            id="fecha_inicio_vigencia"
            type="date"
            {...register('fecha_inicio_vigencia')}
            className={errors.fecha_inicio_vigencia ? 'border-red-500' : ''}
          />
          {errors.fecha_inicio_vigencia && (
            <p className="text-sm text-red-500">{errors.fecha_inicio_vigencia.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="fecha_fin_vigencia">Fecha Fin Vigencia</Label>
          <Input
            id="fecha_fin_vigencia"
            type="date"
            {...register('fecha_fin_vigencia')}
          />
          <p className="text-sm text-muted-foreground">Opcional - Dejar vacío para vigencia indefinida</p>
        </div>
      </div>

      {/* Observaciones */}
      <div className="space-y-2">
        <Label htmlFor="observaciones">Observaciones</Label>
        <Textarea
          id="observaciones"
          {...register('observaciones')}
          rows={3}
          placeholder="Observaciones adicionales sobre la configuración..."
        />
      </div>

      {/* Botones */}
      <div className="flex gap-2 justify-end">
        <Button type="button" variant="outline" onClick={onCancel}>
          <X className="mr-2 h-4 w-4" />
          Cancelar
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? (
            <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Save className="mr-2 h-4 w-4" />
          )}
          {configuracion ? 'Actualizar' : 'Crear'}
        </Button>
      </div>
    </form>
  )
}

// Componente principal
const ConfiguracionPage: React.FC = () => {
  const { user } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  
  // Estados para datos
  const [configuraciones, setConfiguraciones] = useState<ConfiguracionVacaciones[]>([])
  const [periodos, setPeriodos] = useState<PeriodoVacacional[]>([])
  const [selectedConfiguracion, setSelectedConfiguracion] = useState<ConfiguracionVacaciones | null>(null)
  
  // Estados para modales
  const [showConfiguracionForm, setShowConfiguracionForm] = useState(false)
  const [showPeriodoForm, setShowPeriodoForm] = useState(false)
  const [showConfiguracionDetail, setShowConfiguracionDetail] = useState(false)

  // Verificar permisos
  useEffect(() => {
    if (!user?.is_staff) {
      navigate('/vacaciones')
      return
    }
  }, [user, navigate])

  // Cargar datos
  const cargarDatos = async () => {
    try {
      setLoading(true)
      
      // Cargar configuraciones
      const configuracionesRes = await timeOffService.getConfiguraciones()
      setConfiguraciones(configuracionesRes)
      
      // Cargar períodos recientes (últimos 50)
      const periodosRes = await timeOffService.getPeriodos({ limit: 50 })
      setPeriodos(periodosRes.results || [])
      
    } catch (error) {
      console.error('Error al cargar datos de configuración:', error)
      toast({
        title: 'Error',
        description: 'No se pudieron cargar los datos de configuración',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user?.is_staff) {
      cargarDatos()
    }
  }, [user])

  const handleVolver = () => {
    navigate('/vacaciones')
  }

  const handleCrearConfiguracion = async (data: ConfiguracionFormData) => {
    try {
      setSaving(true)
      await timeOffService.createConfiguracion(data)
      toast({
        title: 'Éxito',
        description: 'Configuración creada correctamente'
      })
      setShowConfiguracionForm(false)
      await cargarDatos()
    } catch (error) {
      console.error('Error al crear configuración:', error)
      toast({
        title: 'Error',
        description: 'Error al crear la configuración',
        variant: 'destructive'
      })
    } finally {
      setSaving(false)
    }
  }

  const handleActualizarConfiguracion = async (data: ConfiguracionFormData) => {
    if (!selectedConfiguracion) return
    
    try {
      setSaving(true)
      await timeOffService.updateConfiguracion(selectedConfiguracion.id, data)
      toast({
        title: 'Éxito',
        description: 'Configuración actualizada correctamente'
      })
      setShowConfiguracionForm(false)
      setSelectedConfiguracion(null)
      await cargarDatos()
    } catch (error) {
      console.error('Error al actualizar configuración:', error)
      toast({
        title: 'Error',
        description: 'Error al actualizar la configuración',
        variant: 'destructive'
      })
    } finally {
      setSaving(false)
    }
  }

  const handleEliminarConfiguracion = async (id: number) => {
    if (!confirm('¿Está seguro de eliminar esta configuración?')) return
    
    try {
      await timeOffService.deleteConfiguracion(id)
      toast({
        title: 'Éxito',
        description: 'Configuración eliminada correctamente'
      })
      await cargarDatos()
    } catch (error) {
      console.error('Error al eliminar configuración:', error)
      toast({
        title: 'Error',
        description: 'Error al eliminar la configuración',
        variant: 'destructive'
      })
    }
  }

  const handleVerDetalle = (configuracion: ConfiguracionVacaciones) => {
    setSelectedConfiguracion(configuracion)
    setShowConfiguracionDetail(true)
  }

  const handleEditarConfiguracion = (configuracion: ConfiguracionVacaciones) => {
    setSelectedConfiguracion(configuracion)
    setShowConfiguracionForm(true)
  }

  // Estadísticas rápidas
  const configuracionActiva = configuraciones.find(c => {
    if (!c.fecha_inicio_vigencia) return false
    const ahora = new Date()
    const inicio = new Date(c.fecha_inicio_vigencia)
    const fin = c.fecha_fin_vigencia ? new Date(c.fecha_fin_vigencia) : null
    return inicio <= ahora && (!fin || fin >= ahora)
  })
  
  const totalConfiguraciones = configuraciones?.length || 0
  const totalPeriodos = periodos?.length || 0
  const periodosActivos = periodos?.filter(p => p.estado_periodo === 'activo')?.length || 0

  if (!user?.is_staff) {
    return null
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="container mx-auto p-4 sm:p-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4 mb-4 sm:mb-6">
        <Button variant="outline" onClick={handleVolver}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Volver
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Configuración de Vacaciones</h1>
          <p className="text-muted-foreground">
            Administra las configuraciones y períodos vacacionales
          </p>
        </div>
        <Button onClick={() => setShowConfiguracionForm(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Nueva Configuración
        </Button>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid gap-4 md:grid-cols-4 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Configuración Activa</CardTitle>
            <Settings className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {configuracionActiva ? (
                <Badge variant="default" className="bg-green-100 text-green-800">
                  Activa
                </Badge>
              ) : (
                <Badge variant="destructive">
                  Sin configurar
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Configuraciones</CardTitle>
            <Settings className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalConfiguraciones}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Períodos</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalPeriodos}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Períodos Activos</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{periodosActivos}</div>
          </CardContent>
        </Card>
      </div>

      {/* Alerta si no hay configuración activa */}
      {!configuracionActiva && (
        <Alert className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            No hay una configuración de vacaciones activa. Es necesario crear y activar una configuración para que el sistema funcione correctamente.
          </AlertDescription>
        </Alert>
      )}

      {/* Contenido principal con tabs */}
      <Tabs defaultValue="configuraciones" className="space-y-4">
        <TabsList>
          <TabsTrigger value="configuraciones">
            <Settings className="mr-2 h-4 w-4" />
            Configuraciones
          </TabsTrigger>
          <TabsTrigger value="periodos">
            <Calendar className="mr-2 h-4 w-4" />
            Períodos Recientes
          </TabsTrigger>
        </TabsList>

        {/* Tab de configuraciones */}
        <TabsContent value="configuraciones">
          <Card>
            <CardHeader>
              <CardTitle>Configuraciones de Vacaciones</CardTitle>
              <CardDescription>
                Gestiona las configuraciones que definen las reglas de vacaciones
              </CardDescription>
            </CardHeader>
            <CardContent>
              {configuraciones.length === 0 ? (
                <div className="text-center py-8">
                  <Settings className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-lg font-medium">No hay configuraciones</p>
                  <p className="text-muted-foreground mb-4">
                    Crea la primera configuración para comenzar
                  </p>
                  <Button onClick={() => setShowConfiguracionForm(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    Crear Configuración
                  </Button>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Vigencia</TableHead>
                        <TableHead>Días por Año</TableHead>
                        <TableHead>Límites Solicitud</TableHead>
                        <TableHead>Fraccionamiento</TableHead>
                        <TableHead>Estado</TableHead>
                        <TableHead>Acciones</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {configuraciones.map((configuracion) => {
                        const ahora = new Date()
                        const inicio = new Date(configuracion.fecha_inicio_vigencia)
                        const fin = configuracion.fecha_fin_vigencia ? new Date(configuracion.fecha_fin_vigencia) : null
                        const activa = inicio <= ahora && (!fin || fin >= ahora)
                        
                        return (
                          <TableRow key={configuracion.id}>
                            <TableCell>
                              <div className="text-sm">
                                <p>{format(new Date(configuracion.fecha_inicio_vigencia), 'dd/MM/yyyy')}</p>
                                {configuracion.fecha_fin_vigencia && (
                                  <p className="text-muted-foreground">
                                    {format(new Date(configuracion.fecha_fin_vigencia), 'dd/MM/yyyy')}
                                  </p>
                                )}
                              </div>
                            </TableCell>
                            <TableCell>
                              <span className="font-medium">{configuracion.dias_por_ano}</span>
                            </TableCell>
                            <TableCell>
                              <div className="text-sm">
                                <p>Min: {configuracion.dias_minimos_solicitud}</p>
                                <p>Max: {configuracion.dias_maximos_solicitud}</p>
                              </div>
                            </TableCell>
                            <TableCell>
                              {configuracion.permite_fraccionamiento ? (
                                <div className="text-sm">
                                  <Badge variant="outline" className="bg-green-100 text-green-800">
                                    Sí
                                  </Badge>
                                  {configuracion.dias_minimos_fraccionamiento && (
                                    <p className="text-muted-foreground mt-1">
                                      Min: {configuracion.dias_minimos_fraccionamiento}
                                    </p>
                                  )}
                                </div>
                              ) : (
                                <Badge variant="outline" className="bg-red-100 text-red-800">
                                  No
                                </Badge>
                              )}
                            </TableCell>
                            <TableCell>
                              <EstadoConfiguracionBadge activa={activa} />
                            </TableCell>
                            <TableCell>
                              <div className="flex gap-1">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleVerDetalle(configuracion)}
                                >
                                  <Eye className="h-3 w-3" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleEditarConfiguracion(configuracion)}
                                >
                                  <Edit className="h-3 w-3" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleEliminarConfiguracion(configuracion.id)}
                                  className="text-red-600 hover:text-red-700"
                                >
                                  <Trash2 className="h-3 w-3" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        )
                      })}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab de períodos recientes */}
        <TabsContent value="periodos">
          <Card>
            <CardHeader>
              <CardTitle>Períodos Vacacionales Recientes</CardTitle>
              <CardDescription>
                Últimos períodos creados en el sistema
              </CardDescription>
            </CardHeader>
            <CardContent>
              {periodos.length === 0 ? (
                <div className="text-center py-8">
                  <Calendar className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-lg font-medium">No hay períodos registrados</p>
                  <p className="text-muted-foreground">
                    Los períodos aparecerán aquí cuando se creen
                  </p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Empleado</TableHead>
                        <TableHead>Período</TableHead>
                        <TableHead>Fechas</TableHead>
                        <TableHead>Días</TableHead>
                        <TableHead>Estado</TableHead>
                        <TableHead>Creado</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {periodos.map((periodo) => (
                        <TableRow key={periodo.id}>
                          <TableCell>
                            <div>
                              <p className="font-medium">{periodo.empleado_nombre_completo || 'N/A'}</p>
                              <p className="text-sm text-muted-foreground">{periodo.empleado_numero_empleado || 'N/A'}</p>
                            </div>
                          </TableCell>
                          <TableCell className="font-medium">{periodo.ano_periodo || 'N/A'}</TableCell>
                          <TableCell>
                            <div className="text-sm">
                              {periodo.fecha_inicio ? (
                                <p>{format(new Date(periodo.fecha_inicio), 'dd/MM/yyyy')}</p>
                              ) : (
                                <p>N/A</p>
                              )}
                              {periodo.fecha_fin ? (
                                <p className="text-muted-foreground">
                                  {format(new Date(periodo.fecha_fin), 'dd/MM/yyyy')}
                                </p>
                              ) : (
                                <p className="text-muted-foreground">N/A</p>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="text-sm">
                              <p>Corresp: <span className="font-medium text-blue-600">{periodo.dias_correspondientes ?? 0}</span></p>
                              <p>Pend: <span className="font-medium text-green-600">{periodo.dias_pendientes ?? 0}</span></p>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge 
                              variant={periodo.estado_periodo === 'activo' ? 'default' : 'secondary'}
                              className={periodo.estado_periodo === 'activo' ? 'bg-green-100 text-green-800' : ''}
                            >
                              {periodo.estado_periodo?.toUpperCase() || 'DESCONOCIDO'}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {periodo.created_at ? format(new Date(periodo.created_at), 'dd/MM/yyyy') : 'N/A'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Dialog para formulario de configuración */}
      <Dialog open={showConfiguracionForm} onOpenChange={setShowConfiguracionForm}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {selectedConfiguracion ? 'Editar Configuración' : 'Nueva Configuración'}
            </DialogTitle>
            <DialogDescription>
              {selectedConfiguracion 
                ? 'Modifica los parámetros de la configuración de vacaciones'
                : 'Define los parámetros para la gestión de vacaciones'
              }
            </DialogDescription>
          </DialogHeader>
          
          <FormularioConfiguracion
            configuracion={selectedConfiguracion || undefined}
            onSubmit={selectedConfiguracion ? handleActualizarConfiguracion : handleCrearConfiguracion}
            onCancel={() => {
              setShowConfiguracionForm(false)
              setSelectedConfiguracion(null)
            }}
            loading={saving}
          />
        </DialogContent>
      </Dialog>

      {/* Dialog para detalle de configuración */}
      <Dialog open={showConfiguracionDetail} onOpenChange={setShowConfiguracionDetail}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Detalle de Configuración</DialogTitle>
            <DialogDescription>
              Información completa de la configuración de vacaciones
            </DialogDescription>
          </DialogHeader>
          
          {selectedConfiguracion && (
            <div className="space-y-4">
              {/* Información básica */}
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Días por Año</Label>
                  <p className="text-lg font-semibold">{selectedConfiguracion.dias_por_ano}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Días de Anticipación</Label>
                  <p className="text-lg font-semibold">{selectedConfiguracion.dias_anticipacion_solicitud}</p>
                </div>
              </div>

              {/* Límites */}
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Días Mínimos por Solicitud</Label>
                  <p className="text-lg font-semibold">{selectedConfiguracion.dias_minimos_solicitud}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Días Máximos por Solicitud</Label>
                  <p className="text-lg font-semibold">{selectedConfiguracion.dias_maximos_solicitud}</p>
                </div>
              </div>

              {/* Fraccionamiento */}
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Fraccionamiento</Label>
                <div className="mt-1">
                  {selectedConfiguracion.permite_fraccionamiento ? (
                    <div>
                      <Badge variant="outline" className="bg-green-100 text-green-800 mb-2">
                        Permitido
                      </Badge>
                      <p className="text-sm text-muted-foreground">
                        Días mínimos: {selectedConfiguracion.dias_minimos_fraccionamiento}
                      </p>
                    </div>
                  ) : (
                    <Badge variant="outline" className="bg-red-100 text-red-800">
                      No Permitido
                    </Badge>
                  )}
                </div>
              </div>

              {/* Vigencia */}
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Fecha Inicio Vigencia</Label>
                  <p className="text-lg">
                    {format(new Date(selectedConfiguracion.fecha_inicio_vigencia), 'PPP', { locale: es })}
                  </p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Fecha Fin Vigencia</Label>
                  <p className="text-lg">
                    {selectedConfiguracion.fecha_fin_vigencia 
                      ? format(new Date(selectedConfiguracion.fecha_fin_vigencia), 'PPP', { locale: es })
                      : 'Sin fecha de fin'
                    }
                  </p>
                </div>
              </div>

              {/* Observaciones */}
              {selectedConfiguracion.observaciones && (
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Observaciones</Label>
                  <p className="text-sm mt-1">{selectedConfiguracion.observaciones}</p>
                </div>
              )}

              {/* Fechas de auditoría */}
              <div className="border-t pt-4">
                <h4 className="font-medium mb-3">Información de Auditoría</h4>
                
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Fecha de Creación</Label>
                    <p className="text-sm">
                      {format(new Date(selectedConfiguracion.created_at), 'PPP', { locale: es })}
                    </p>
                  </div>
                  
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Última Actualización</Label>
                    <p className="text-sm">
                      {format(new Date(selectedConfiguracion.updated_at), 'PPP', { locale: es })}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default ConfiguracionPage