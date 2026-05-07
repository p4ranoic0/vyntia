import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Label } from '@/shared/ui/label'
import { Progress } from '@/shared/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shared/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui/tabs'
import { useToast } from '@/shared/hooks/use-toast'
import { useAuth } from '@/features/auth/hooks/useAuth'
import timeOffService, {
    EmpleadoDiasVencidos,
    EstadisticasVacaciones as EstadisticasVacacionesType,
    SolicitudVacaciones
} from '@/features/time-off/services/timeOffService'
import { format } from 'date-fns'
import {
    AlertTriangle,
    ArrowLeft,
    BarChart3,
    Calendar,
    Clock,
    Download,
    FileText,
    RefreshCw,
    TrendingUp,
    Users
} from 'lucide-react'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

// Componente para estadísticas por área
interface EstadisticasAreaCardProps {
  estadisticas: EstadisticasVacacionesType
}

const EstadisticasAreaCard: React.FC<EstadisticasAreaCardProps> = ({ estadisticas }) => {
  const porcentajeUso = (estadisticas?.total_dias_correspondientes || 0) > 0 
    ? (((estadisticas?.total_dias_correspondientes || 0) - (estadisticas?.total_dias_pendientes || 0)) / (estadisticas?.total_dias_correspondientes || 1)) * 100 
    : 0

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{estadisticas.area_nombre}</CardTitle>
        <CardDescription>Año {estadisticas.ano}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Estadísticas principales */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{estadisticas.total_empleados}</p>
              <p className="text-xs text-muted-foreground">Empleados</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{estadisticas.total_solicitudes}</p>
              <p className="text-xs text-muted-foreground">Solicitudes</p>
            </div>
          </div>

          {/* Días */}
          <div className="grid grid-cols-3 gap-2">
            <div className="text-center">
              <p className="text-lg font-semibold">{estadisticas.total_dias_correspondientes}</p>
              <p className="text-xs text-muted-foreground">Correspondientes</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-semibold text-orange-600">
                {estadisticas.total_dias_correspondientes - estadisticas.total_dias_pendientes}
              </p>
              <p className="text-xs text-muted-foreground">Utilizados</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-semibold text-green-600">{estadisticas.total_dias_pendientes}</p>
              <p className="text-xs text-muted-foreground">Pendientes</p>
            </div>
          </div>

          {/* Barra de progreso */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Uso de vacaciones</span>
              <span>{porcentajeUso.toFixed(1)}%</span>
            </div>
            <Progress value={porcentajeUso} className="h-2" />
          </div>

          {/* Goces */}
          <div className="text-sm text-muted-foreground">
            <Calendar className="inline h-3 w-3 mr-1" />
            {estadisticas.total_goces} goce(s) registrado(s)
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Componente para empleados con días vencidos
interface EmpleadoVencidoRowProps {
  empleado: EmpleadoDiasVencidos
}

const EmpleadoVencidoRow: React.FC<EmpleadoVencidoRowProps> = ({ empleado }) => {
  const getSeverityColor = (porcentaje: number) => {
    if (porcentaje >= 80) return 'text-red-600'
    if (porcentaje >= 60) return 'text-orange-600'
    if (porcentaje >= 40) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getSeverityBadge = (porcentaje: number) => {
    if (porcentaje >= 80) return { variant: 'destructive' as const, text: 'Crítico' }
    if (porcentaje >= 60) return { variant: 'outline' as const, text: 'Alto', className: 'bg-orange-100 text-orange-800' }
    if (porcentaje >= 40) return { variant: 'outline' as const, text: 'Medio', className: 'bg-yellow-100 text-yellow-800' }
    return { variant: 'outline' as const, text: 'Bajo', className: 'bg-green-100 text-green-800' }
  }

  const badge = getSeverityBadge(empleado.porcentaje_uso)

  return (
    <TableRow>
      <TableCell>
        <div>
          <p className="font-medium">{empleado.empleado_nombre_completo}</p>
          <p className="text-sm text-muted-foreground">{empleado.empleado_numero_empleado}</p>
        </div>
      </TableCell>
      <TableCell>{empleado.area_nombre}</TableCell>
      <TableCell className="text-center">{empleado.ano}</TableCell>
      <TableCell className="text-center">
        <span className="font-medium text-blue-600">{empleado.dias_correspondientes}</span>
      </TableCell>
      <TableCell className="text-center">
        <span className="font-medium text-red-600">{empleado.dias_vencidos}</span>
      </TableCell>
      <TableCell className="text-center">
        <span className={`font-medium ${getSeverityColor(empleado?.porcentaje_uso || 0)}`}>
          {(empleado?.porcentaje_uso || 0).toFixed(1)}%
        </span>
      </TableCell>
      <TableCell>
        <Badge variant={badge.variant} className={badge.className}>
          {badge.text}
        </Badge>
      </TableCell>
    </TableRow>
  )
}

// Componente principal
const ReportesPage: React.FC = () => {
  const { user, isAdminOrRRHH } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  
  // Estados para datos
  const [estadisticas, setEstadisticas] = useState<EstadisticasVacacionesType[]>([])
  const [empleadosVencidos, setEmpleadosVencidos] = useState<EmpleadoDiasVencidos[]>([])
  const [solicitudesPendientes, setSolicitudesPendientes] = useState<SolicitudVacaciones[]>([])
  
  // Filtros
  const [anoFilter, setAnoFilter] = useState<string>(new Date().getFullYear().toString())
  const [areaFilter, setAreaFilter] = useState<string>('todos')
  const [severidadFilter, setSeveridadFilter] = useState<string>('todos')

  const esGestor = isAdminOrRRHH()

  // Cargar datos
  const cargarDatos = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true)
      else setRefreshing(true)
      
      const ano = parseInt(anoFilter) || new Date().getFullYear()
      
      if (esGestor) {
        // Cargar estadísticas por área
        const estadisticasRes = await timeOffService.getEstadisticasPorArea(ano)
        setEstadisticas(estadisticasRes)
        
        // Cargar empleados con días vencidos
        const empleadosVencidosRes = await timeOffService.getEmpleadosDiasVencidos(ano)
        setEmpleadosVencidos(empleadosVencidosRes)
        
        // Cargar solicitudes pendientes (RRHH)
        const solicitudesPendientesRes = await timeOffService.getSolicitudes({ estado: 'aprobada_jefe' })
        setSolicitudesPendientes(solicitudesPendientesRes.results || solicitudesPendientesRes || [])
      } else {
        setEstadisticas([])
        setEmpleadosVencidos([])
        setSolicitudesPendientes([])
      }
      
    } catch (error) {
      console.error('Error al cargar datos de reportes:', error)
      toast({
        title: 'Error',
        description: 'No se pudieron cargar los datos de reportes',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    cargarDatos()
  }, [anoFilter, user, esGestor])

  const handleVolver = () => {
    navigate('/vacaciones')
  }

  const handleRefresh = () => {
    cargarDatos(false)
  }

  const handleExportarEstadisticas = async () => {
    try {
      if (!estadisticas.length && !empleadosVencidos.length) {
        toast({
          title: 'Sin datos',
          description: 'No hay datos para exportar',
          variant: 'destructive'
        })
        return
      }

      const escape = (value: any) => `"${String(value ?? '').replace(/"/g, '""')}"`

      const estadisticasHeaders = [
        'Area',
        'Ano',
        'Total Empleados',
        'Total Solicitudes',
        'Dias Correspondientes',
        'Dias Pendientes',
        'Total Goces'
      ]
      const estadisticasRows = estadisticas.map((e) => [
        e.area_nombre,
        e.ano,
        e.total_empleados,
        e.total_solicitudes,
        e.total_dias_correspondientes,
        e.total_dias_pendientes,
        e.total_goces
      ])

      const vencidosHeaders = [
        'Empleado',
        'Documento',
        'Area',
        'Ano',
        'Dias Correspondientes',
        'Dias Vencidos',
        'Porcentaje Uso',
        'Fecha Vencimiento'
      ]
      const vencidosRows = empleadosVencidos.map((e) => [
        e.empleado_nombre_completo,
        e.empleado_numero_empleado,
        e.area_nombre,
        e.ano,
        e.dias_correspondientes,
        e.dias_vencidos,
        `${(e.porcentaje_uso || 0).toFixed(1)}%`,
        e.fecha_vencimiento
      ])

      const lines: string[] = []
      if (estadisticas.length) {
        lines.push('ESTADISTICAS')
        lines.push(estadisticasHeaders.map(escape).join(','))
        lines.push(...estadisticasRows.map((row) => row.map(escape).join(',')))
        lines.push('')
      }
      if (empleadosVencidos.length) {
        lines.push('EMPLEADOS_VENCIDOS')
        lines.push(vencidosHeaders.map(escape).join(','))
        lines.push(...vencidosRows.map((row) => row.map(escape).join(',')))
      }

      const csv = lines.join('\n')
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `reportes_vacaciones_${anoFilter}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error al exportar estadísticas',
        variant: 'destructive'
      })
    }
  }

  // Filtrar datos
  const estadisticasFiltradas = estadisticas.filter(est => {
    if (areaFilter !== 'todos' && est.area_nombre !== areaFilter) return false
    return true
  })

  const empleadosVencidosFiltrados = empleadosVencidos.filter(emp => {
    if (areaFilter !== 'todos' && emp?.area_nombre !== areaFilter) return false
    if (severidadFilter !== 'todos') {
      const porcentaje = emp?.porcentaje_uso || 0
      switch (severidadFilter) {
        case 'critico': return porcentaje >= 80
        case 'alto': return porcentaje >= 60 && porcentaje < 80
        case 'medio': return porcentaje >= 40 && porcentaje < 60
        case 'bajo': return porcentaje < 40
        default: return true
      }
    }
    return true
  })

  // Obtener áreas disponibles
  const areasDisponibles = Array.from(new Set(
    (estadisticas || [])
      .filter(est => est?.area_nombre && est.area_nombre.trim() !== '') // Filtrar valores vacíos o undefined
      .map(est => est.area_nombre)
  )).sort()
  const anosDisponibles = [2023, 2024, 2025] // Puedes hacer esto dinámico

  // Calcular totales
  const totalEmpleados = estadisticas.reduce((sum, est) => sum + (est?.total_empleados || 0), 0)
  const totalSolicitudes = estadisticas.reduce((sum, est) => sum + (est?.total_solicitudes || 0), 0)
  const totalDiasCorrespondientes = estadisticas.reduce((sum, est) => sum + (est?.total_dias_correspondientes || 0), 0)
  const totalDiasPendientes = estadisticas.reduce((sum, est) => sum + (est?.total_dias_pendientes || 0), 0)
  const totalDiasUtilizados = totalDiasCorrespondientes - totalDiasPendientes
  const porcentajeUsoGeneral = totalDiasCorrespondientes > 0 
    ? (totalDiasUtilizados / totalDiasCorrespondientes) * 100 
    : 0

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
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Reportes de Vacaciones</h1>
          <p className="text-muted-foreground">
            Estadísticas y análisis del uso de vacaciones
          </p>
        </div>
        <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          Actualizar
        </Button>
      </div>

      {/* Filtros */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-lg">Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="space-y-2">
              <Label htmlFor="ano">Año</Label>
              <Select value={anoFilter} onValueChange={setAnoFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar año" />
                </SelectTrigger>
                <SelectContent>
                  {anosDisponibles.map(ano => (
                    <SelectItem key={ano} value={ano.toString()}>
                      {ano}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="area">Área</Label>
              <Select value={areaFilter} onValueChange={setAreaFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Todas las áreas" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todas las áreas</SelectItem>
                  {areasDisponibles.map(area => (
                    <SelectItem key={area} value={area}>
                      {area}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="severidad">Severidad</Label>
              <Select value={severidadFilter} onValueChange={setSeveridadFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Todas las severidades" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todas las severidades</SelectItem>
                  <SelectItem value="critico">Crítico (≥80%)</SelectItem>
                  <SelectItem value="alto">Alto (60-79%)</SelectItem>
                  <SelectItem value="medio">Medio (40-59%)</SelectItem>
                  <SelectItem value="bajo">Bajo (menos de 40%)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label>Acciones</Label>
              <Button variant="outline" className="w-full" onClick={handleExportarEstadisticas}>
                <Download className="mr-2 h-4 w-4" />
                Exportar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Resumen general */}
      <div className="grid gap-4 grid-cols-2 md:grid-cols-3 lg:grid-cols-5 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Empleados</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalEmpleados}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Solicitudes</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalSolicitudes}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Días Correspondientes</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{totalDiasCorrespondientes}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Días Utilizados</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{totalDiasUtilizados}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">% Uso General</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{porcentajeUsoGeneral.toFixed(1)}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Contenido principal con tabs */}
      <Tabs defaultValue="estadisticas" className="space-y-4">
        <TabsList>
          <TabsTrigger value="estadisticas">
            <BarChart3 className="mr-2 h-4 w-4" />
            Estadísticas por Área
          </TabsTrigger>
          <TabsTrigger value="vencidos">
            <AlertTriangle className="mr-2 h-4 w-4" />
            Días Vencidos
          </TabsTrigger>
          {esGestor && (
            <TabsTrigger value="pendientes">
              <Clock className="mr-2 h-4 w-4" />
              Solicitudes Pendientes
            </TabsTrigger>
          )}
        </TabsList>

        {/* Tab de estadísticas por área */}
        <TabsContent value="estadisticas">
          <Card>
            <CardHeader>
              <CardTitle>Estadísticas por Área - Año {anoFilter}</CardTitle>
              <CardDescription>
                Resumen del uso de vacaciones por área organizacional
              </CardDescription>
            </CardHeader>
            <CardContent>
              {estadisticasFiltradas.length === 0 ? (
                <div className="text-center py-8">
                  <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-lg font-medium">No hay estadísticas disponibles</p>
                  <p className="text-muted-foreground">
                    No se encontraron datos para los filtros seleccionados
                  </p>
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {estadisticasFiltradas.map((estadistica) => (
                    <EstadisticasAreaCard
                      key={`${estadistica.area_nombre}-${estadistica.ano}`}
                      estadisticas={estadistica}
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab de empleados con días vencidos */}
        <TabsContent value="vencidos">
          <Card>
            <CardHeader>
              <CardTitle>Empleados con Días Vencidos - Año {anoFilter}</CardTitle>
              <CardDescription>
                Lista de empleados con días de vacaciones próximos a vencer o vencidos
              </CardDescription>
            </CardHeader>
            <CardContent>
              {empleadosVencidosFiltrados.length === 0 ? (
                <div className="text-center py-8">
                  <AlertTriangle className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-lg font-medium">No hay empleados con días vencidos</p>
                  <p className="text-muted-foreground">
                    {empleadosVencidos.length === 0 
                      ? 'Todos los empleados están al día con sus vacaciones'
                      : 'No se encontraron empleados con los filtros aplicados'
                    }
                  </p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Empleado</TableHead>
                        <TableHead>Área</TableHead>
                        <TableHead className="text-center">Año</TableHead>
                        <TableHead className="text-center">Días Correspondientes</TableHead>
                        <TableHead className="text-center">Días Vencidos</TableHead>
                        <TableHead className="text-center">% Uso</TableHead>
                        <TableHead>Severidad</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {empleadosVencidosFiltrados.map((empleado) => (
                        <EmpleadoVencidoRow
                          key={`${empleado.empleado_id}-${empleado.ano}`}
                          empleado={empleado}
                        />
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab de solicitudes pendientes (solo para personal) */}
        {esGestor && (
          <TabsContent value="pendientes">
            <Card>
              <CardHeader>
                <CardTitle>Solicitudes Pendientes de Aprobación</CardTitle>
                <CardDescription>
                  Lista de solicitudes que requieren revisión
                </CardDescription>
              </CardHeader>
              <CardContent>
                {solicitudesPendientes.length === 0 ? (
                  <div className="text-center py-8">
                    <Clock className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                    <p className="text-lg font-medium">No hay solicitudes pendientes</p>
                    <p className="text-muted-foreground">
                      Todas las solicitudes han sido procesadas
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
                          <TableHead className="text-center">Días</TableHead>
                          <TableHead>Fecha Solicitud</TableHead>
                          <TableHead>Estado</TableHead>
                          <TableHead>Acciones</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {solicitudesPendientes.map((solicitud) => (
                          <TableRow key={solicitud.id}>
                            <TableCell>
                              <div>
                                <p className="font-medium">{solicitud.empleado_nombre_completo || solicitud.empleado_nombre}</p>
                                <p className="text-sm text-muted-foreground">{solicitud.empleado?.numero_identificacion || solicitud.empleado_rut || ''}</p>
                              </div>
                            </TableCell>
                            <TableCell>{solicitud.periodo_ano}</TableCell>
                            <TableCell>
                              <div className="text-sm">
                                <p>{format(new Date(solicitud.fecha_inicio), 'dd/MM/yyyy')}</p>
                                <p className="text-muted-foreground">
                                  {format(new Date(solicitud.fecha_fin), 'dd/MM/yyyy')}
                                </p>
                              </div>
                            </TableCell>
                            <TableCell className="text-center">
                              <span className="font-medium">{solicitud.dias_calendario}</span>
                            </TableCell>
                            <TableCell>
                              {solicitud.created_at ? format(new Date(solicitud.created_at), 'dd/MM/yyyy') : '-'}
                            </TableCell>
                            <TableCell>
                              <Badge variant="outline" className="bg-yellow-100 text-yellow-800">
                                {(solicitud.estado_solicitud || '').replace('_', ' ').toUpperCase()}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => navigate(`/vacaciones/solicitudes?id=${solicitud.id}`)}
                              >
                                Revisar
                              </Button>
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
        )}
      </Tabs>
    </div>
  )
}

export default ReportesPage
