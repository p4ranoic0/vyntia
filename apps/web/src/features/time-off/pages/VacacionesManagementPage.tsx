import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { Alert, AlertDescription } from '@/shared/ui/alert'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui/tabs'
import CalendarioVacaciones from '@/features/time-off/components/CalendarioVacaciones'
import ConfiguracionPanel from '@/features/time-off/components/ConfiguracionPanel'
import EstadisticasVacaciones from '@/features/time-off/components/EstadisticasVacaciones'
import HistorialSolicitudes from '@/features/time-off/components/HistorialSolicitudes'
import NotificacionesVacaciones from '@/features/time-off/components/NotificacionesVacaciones'
import PeriodosManagement from '@/features/time-off/components/PeriodosManagement'
import ResumenDiasVacaciones from '@/features/time-off/components/ResumenDiasVacaciones'
import { useToast } from '@/shared/hooks/use-toast'
import { useAuth } from '@/features/auth/hooks/useAuth'
import timeOffService, {
    EmpleadoDiasVencidos,
    EstadisticasVacaciones as EstadisticasVacacionesType,
    PeriodoVacacional,
    SolicitudVacaciones
} from '@/features/time-off/services/timeOffService'
import { AlertTriangle, Calendar, Clock, FileText, Plus } from 'lucide-react'
import React, { useEffect, useState } from 'react'

// Componente para mostrar estadísticas rápidas
interface EstadisticasRapidasProps {
  estadisticas: EstadisticasVacacionesType[]
  empleadosVencidos: EmpleadoDiasVencidos[]
  solicitudesPendientes: SolicitudVacaciones[]
}

const EstadisticasRapidas: React.FC<EstadisticasRapidasProps> = ({
  estadisticas,
  empleadosVencidos,
  solicitudesPendientes
}) => {
  const totalDiasAsignados = estadisticas?.reduce((sum, est) => sum + (est?.total_dias_asignados || 0), 0) || 0
  const totalDiasGozados = estadisticas?.reduce((sum, est) => sum + (est?.total_dias_gozados || 0), 0) || 0
  const totalSolicitudes = estadisticas?.reduce((sum, est) => sum + (est?.total_solicitudes || 0), 0) || 0
  const porcentajeUsoPromedio = estadisticas?.length > 0 
    ? estadisticas.reduce((sum, est) => sum + (est?.porcentaje_uso || 0), 0) / estadisticas.length 
    : 0

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Días Asignados</CardTitle>
          <Calendar className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalDiasAsignados}</div>
          <p className="text-xs text-muted-foreground">
            Total de días de vacaciones asignados
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Días Gozados</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalDiasGozados}</div>
          <p className="text-xs text-muted-foreground">
            {porcentajeUsoPromedio.toFixed(1)}% de uso promedio
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Solicitudes Pendientes</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{solicitudesPendientes?.length || 0}</div>
          <p className="text-xs text-muted-foreground">
            Requieren aprobación
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Días por Vencer</CardTitle>
          <AlertTriangle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-orange-600">{empleadosVencidos?.length || 0}</div>
          <p className="text-xs text-muted-foreground">
            Empleados con días próximos a vencer
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

// Componente para mostrar solicitudes recientes
interface SolicitudesRecientesProps {
  solicitudes: SolicitudVacaciones[]
  onVerDetalle: (solicitud: SolicitudVacaciones) => void
}

const SolicitudesRecientes: React.FC<SolicitudesRecientesProps> = ({ solicitudes, onVerDetalle }) => {
  const getEstadoBadge = (estado: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      'borrador': 'outline',
      'enviada': 'secondary',
      'en_revision': 'default',
      'aprobada': 'default',
      'rechazada': 'destructive',
      'cancelada': 'secondary'
    }
    
    const colors: Record<string, string> = {
      'borrador': 'bg-gray-100 text-gray-800',
      'enviada': 'bg-blue-100 text-blue-800',
      'en_revision': 'bg-yellow-100 text-yellow-800',
      'aprobada': 'bg-green-100 text-green-800',
      'rechazada': 'bg-red-100 text-red-800',
      'cancelada': 'bg-gray-100 text-gray-800'
    }

    return (
      <Badge variant={variants[estado] || 'outline'} className={colors[estado]}>
        {estado.replace('_', ' ').toUpperCase()}
      </Badge>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Solicitudes Recientes</CardTitle>
        <CardDescription>
          Últimas solicitudes de vacaciones en el sistema
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {solicitudes.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No hay solicitudes recientes
            </p>
          ) : (
            solicitudes.slice(0, 5).map((solicitud) => (
              <div key={solicitud.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">
                      {solicitud.empleado.nombres} {solicitud.empleado.apellidos}
                    </span>
                    {getEstadoBadge(solicitud.estado_solicitud)}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">
                    {solicitud.fecha_inicio_solicitud} - {solicitud.fecha_fin_solicitud}
                    <span className="ml-2">({solicitud.dias_solicitados} días)</span>
                  </div>
                </div>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => onVerDetalle(solicitud)}
                >
                  Ver
                </Button>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// Componente principal
const VacacionesManagementPage: React.FC = () => {
  const { user, isAdminOrRRHH, isJefe } = useAuth()
  const { toast } = useToast()
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('dashboard')
  
  // Estados para datos
  const [estadisticas, setEstadisticas] = useState<EstadisticasVacacionesType[]>([])
  const [empleadosVencidos, setEmpleadosVencidos] = useState<EmpleadoDiasVencidos[]>([])
  const [solicitudesPendientes, setSolicitudesPendientes] = useState<SolicitudVacaciones[]>([])
  const [solicitudesRecientes, setSolicitudesRecientes] = useState<SolicitudVacaciones[]>([])
  const [misPeriodos, setMisPeriodos] = useState<PeriodoVacacional[]>([])
  const [periodosEmpleado, setPeriodosEmpleado] = useState<PeriodoVacacional[]>([])

  const esGestor = isAdminOrRRHH()
  const esJefe = isJefe()

  // Función para recargar datos
  const cargarDatos = async () => {
    try {
      setLoading(true)
      
      // Datos de gestión solo para RRHH/Admin
      if (esGestor) {
        const estadisticasRes = await timeOffService.getEstadisticas({ ano: new Date().getFullYear() })
        setEstadisticas(Array.isArray(estadisticasRes) ? estadisticasRes : [])
        
        const empleadosVencidosRes = await timeOffService.getEmpleadosDiasVencidos(new Date().getFullYear())
        setEmpleadosVencidos(Array.isArray(empleadosVencidosRes) ? empleadosVencidosRes : [])
      } else {
        setEstadisticas([])
        setEmpleadosVencidos([])
      }
      
      // Cargar solicitudes pendientes (RRHH o Jefe)
      if (esGestor || esJefe) {
        try {
          const solicitudesPendientesRes = esGestor
            ? await timeOffService.getSolicitudesPendientes()
            : await timeOffService.getSolicitudesPendientesJefe()
          setSolicitudesPendientes(Array.isArray(solicitudesPendientesRes) ? solicitudesPendientesRes : [])
        } catch (error) {
          console.warn('Error al cargar solicitudes pendientes:', error)
          setSolicitudesPendientes([])
        }
      } else {
        setSolicitudesPendientes([])
      }
      
      // Cargar solicitudes recientes
      try {
        if (esGestor || esJefe) {
          const solicitudesRes = await timeOffService.getSolicitudes({
            fecha_inicio: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0]
          })
          setSolicitudesRecientes(Array.isArray(solicitudesRes) ? solicitudesRes.slice(0, 10) : [])
        } else {
          const solicitudesRes = await timeOffService.getMisSolicitudes()
          setSolicitudesRecientes(Array.isArray(solicitudesRes) ? solicitudesRes.slice(0, 10) : [])
        }
      } catch (error) {
        console.warn('Error al cargar solicitudes recientes:', error)
        setSolicitudesRecientes([])
      }
      
      // Si es empleado, cargar sus períodos
      if (user?.empleado_id) {
        try {
          const periodosRes = await timeOffService.getPeriodosByEmpleado(user.empleado_id)
          setMisPeriodos(Array.isArray(periodosRes) ? periodosRes : [])
          setPeriodosEmpleado(Array.isArray(periodosRes) ? periodosRes : [])
        } catch (error) {
          console.warn('Error al cargar períodos del empleado:', error)
          setMisPeriodos([])
          setPeriodosEmpleado([])
        }
      }
      
    } catch (error) {
      console.error('Error al cargar datos:', error)
      toast({
        title: 'Error',
        description: 'No se pudieron cargar algunos datos de vacaciones',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  // Cargar datos iniciales
  useEffect(() => {
    cargarDatos()
  }, [user, toast, esGestor, esJefe])

  const handleVerDetalleSolicitud = () => {
    // TODO: Implementar navegación a detalle de solicitud
  }

  const handleNuevaSolicitud = () => {
    window.location.href = '/vacaciones/nueva-solicitud'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="container mx-auto p-4 sm:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Gestión de Vacaciones</h1>
          <p className="text-muted-foreground">
            Administra solicitudes, períodos y configuraciones de vacaciones
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleNuevaSolicitud}>
            <FileText className="mr-2 h-4 w-4" />
            Nueva Solicitud
          </Button>
        </div>
      </div>

      {/* Alertas importantes */}
      {esGestor && empleadosVencidos.length > 0 && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Hay {empleadosVencidos.length} empleados con días de vacaciones próximos a vencer.
            <Button variant="link" className="p-0 h-auto ml-2">
              Ver detalles
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Estadísticas rápidas */}
      {esGestor && (
        <EstadisticasRapidas 
          estadisticas={estadisticas}
          empleadosVencidos={empleadosVencidos}
          solicitudesPendientes={solicitudesPendientes}
        />
      )}

      {/* Contenido principal con tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <div className="overflow-x-auto">
          <TabsList>
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="solicitudes">Solicitudes</TabsTrigger>
            <TabsTrigger value="periodos">Períodos</TabsTrigger>
            {esGestor && <TabsTrigger value="reportes">Reportes</TabsTrigger>}
            {esGestor && (
              <TabsTrigger value="configuracion">Configuración</TabsTrigger>
            )}
          </TabsList>
        </div>

        <TabsContent value="dashboard" className="space-y-4">
          <div className="grid gap-6">
            {/* Componente de estadísticas */}
            {esGestor && (
              <EstadisticasVacaciones 
                estadisticas={estadisticas[0]}
                loading={loading}
              />
            )}

            {/* Notificaciones y alertas */}
            <NotificacionesVacaciones />

            {/* Resumen de días de vacaciones para empleados */}
            {!esGestor && periodosEmpleado.length > 0 && (
              <ResumenDiasVacaciones 
                periodo={periodosEmpleado[0]}
                loading={loading}
                onNuevaSolicitud={handleNuevaSolicitud}
                onVerDetalles={() => setActiveTab('periodos')}
                onActualizar={cargarDatos}
              />
            )}

            {/* Calendario de vacaciones */}
            <CalendarioVacaciones 
              empleadoId={esGestor ? undefined : user?.empleado_id}
              areaId={esGestor ? undefined : user?.area_id}
            />

            {/* Historial de solicitudes recientes */}
            <Card>
              <CardHeader>
                <CardTitle>Solicitudes Recientes</CardTitle>
                <CardDescription>
                  Últimas 5 solicitudes de vacaciones
                </CardDescription>
              </CardHeader>
              <CardContent>
                <HistorialSolicitudes 
                  empleadoId={esGestor || esJefe ? undefined : user?.empleado_id}
                  limite={5}
                  mostrarFiltros={false}
                />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="solicitudes">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold tracking-tight">Solicitudes de Vacaciones</h2>
              <p className="text-muted-foreground">
                {esGestor || esJefe ? 'Gestiona y revisa las solicitudes de vacaciones' : 'Revisa el estado de tus solicitudes'}
              </p>
            </div>
              <Button onClick={handleNuevaSolicitud}>
                <Plus className="mr-2 h-4 w-4" />
                Nueva Solicitud
              </Button>
            </div>
            
            <HistorialSolicitudes 
              empleadoId={esGestor || esJefe ? undefined : user?.empleado_id}
              mostrarFiltros={true}
              mostrarAcciones={esGestor || esJefe}
            />
          </div>
        </TabsContent>

        <TabsContent value="periodos">
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold tracking-tight">Períodos Vacacionales</h2>
              <p className="text-muted-foreground">
                Consulta y gestiona los períodos de vacaciones
              </p>
            </div>
            
            {/* Resumen de períodos para empleados */}
            {!esGestor && periodosEmpleado.map((periodo) => (
              <ResumenDiasVacaciones 
                key={periodo.id}
                periodo={periodo}
                loading={loading}
                onNuevaSolicitud={() => window.location.href = '/vacaciones/nueva-solicitud'}
                onVerDetalles={() => window.location.href = '/vacaciones/periodos'}
                onActualizar={cargarDatos}
              />
            ))}
            
            {/* Para personal: vista completa de períodos */}
            {esGestor && (
              <PeriodosManagement onPeriodoCreated={cargarDatos} />
            )}
          </div>
        </TabsContent>

        {esGestor && (
          <TabsContent value="reportes">
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight">Reportes y Estadísticas</h2>
                <p className="text-muted-foreground">
                  Visualiza estadísticas detalladas y genera reportes
                </p>
              </div>
              
              {/* Estadísticas detalladas */}
              <EstadisticasVacaciones 
                estadisticas={estadisticas}
                loading={loading}
              />
              
              {/* Calendario con vista de reportes */}
              <CalendarioVacaciones 
                empleadoId={esGestor ? undefined : user?.empleado_id}
                areaId={esGestor ? undefined : user?.area_id}
                vistaReporte={true}
              />
            </div>
          </TabsContent>
        )}

        {esGestor && (
          <TabsContent value="configuracion">
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight">Configuración del Sistema</h2>
                <p className="text-muted-foreground">
                  Configura parámetros y reglas del módulo de vacaciones
                </p>
              </div>
              
              <ConfiguracionPanel onConfiguracionUpdated={cargarDatos} />
            </div>
          </TabsContent>
        )}
      </Tabs>
    </div>
  )
}

export default VacacionesManagementPage
