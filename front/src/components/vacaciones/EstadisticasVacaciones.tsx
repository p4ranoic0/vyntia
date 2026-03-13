import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  Calendar, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  Users,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react'
import { EstadisticasVacaciones as EstadisticasType } from '@/services/vacacionesService'

interface EstadisticasVacacionesProps {
  estadisticas: EstadisticasType
  loading?: boolean
}

const EstadisticasVacaciones: React.FC<EstadisticasVacacionesProps> = ({ 
  estadisticas, 
  loading = false 
}) => {
  if (loading || !estadisticas) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="h-4 bg-gray-200 rounded w-24"></div>
              <div className="h-4 w-4 bg-gray-200 rounded"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded w-16 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-32"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  const porcentajeUtilizacion = estadisticas.total_dias_asignados > 0 
    ? (estadisticas.total_dias_utilizados / estadisticas.total_dias_asignados) * 100 
    : 0

  const porcentajePendientes = estadisticas.total_dias_asignados > 0 
    ? (estadisticas.total_dias_pendientes / estadisticas.total_dias_asignados) * 100 
    : 0

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {/* Total Días Asignados */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Días Asignados</CardTitle>
          <Calendar className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-blue-600">
            {estadisticas.total_dias_asignados.toLocaleString()}
          </div>
          <p className="text-xs text-muted-foreground">
            Total de días de vacaciones asignados
          </p>
        </CardContent>
      </Card>

      {/* Días Utilizados */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Días Utilizados</CardTitle>
          <CheckCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-600">
            {estadisticas.total_dias_utilizados.toLocaleString()}
          </div>
          <div className="flex items-center space-x-2 mt-2">
            <Progress value={porcentajeUtilizacion} className="flex-1" />
            <span className="text-xs text-muted-foreground">
              {porcentajeUtilizacion.toFixed(1)}%
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Días ya disfrutados
          </p>
        </CardContent>
      </Card>

      {/* Días Pendientes */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Días Pendientes</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-orange-600">
            {estadisticas.total_dias_pendientes.toLocaleString()}
          </div>
          <div className="flex items-center space-x-2 mt-2">
            <Progress value={porcentajePendientes} className="flex-1" />
            <span className="text-xs text-muted-foreground">
              {porcentajePendientes.toFixed(1)}%
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Días disponibles para usar
          </p>
        </CardContent>
      </Card>

      {/* Días Vencidos */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Días Vencidos</CardTitle>
          <AlertTriangle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-red-600">
            {estadisticas.total_dias_vencidos.toLocaleString()}
          </div>
          <p className="text-xs text-muted-foreground">
            Días que han expirado
          </p>
          {estadisticas.total_dias_vencidos > 0 && (
            <Badge variant="destructive" className="mt-2">
              Requiere atención
            </Badge>
          )}
        </CardContent>
      </Card>

      {/* Solicitudes Pendientes */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Solicitudes Pendientes</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-purple-600">
            {estadisticas.solicitudes_pendientes.toLocaleString()}
          </div>
          <p className="text-xs text-muted-foreground">
            Solicitudes esperando aprobación
          </p>
          {estadisticas.solicitudes_pendientes > 0 && (
            <Badge variant="outline" className="mt-2 bg-purple-100 text-purple-800">
              Revisar
            </Badge>
          )}
        </CardContent>
      </Card>

      {/* Solicitudes Aprobadas */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Solicitudes Aprobadas</CardTitle>
          <CheckCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-600">
            {estadisticas.solicitudes_aprobadas.toLocaleString()}
          </div>
          <p className="text-xs text-muted-foreground">
            Solicitudes aprobadas este período
          </p>
        </CardContent>
      </Card>

      {/* Empleados con Días Vencidos */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Empleados Afectados</CardTitle>
          <AlertTriangle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-red-600">
            {estadisticas.empleados_con_dias_vencidos.toLocaleString()}
          </div>
          <p className="text-xs text-muted-foreground">
            Empleados con días vencidos
          </p>
          {estadisticas.empleados_con_dias_vencidos > 0 && (
            <Badge variant="destructive" className="mt-2">
              Acción requerida
            </Badge>
          )}
        </CardContent>
      </Card>

      {/* Promedio Días por Empleado */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Promedio por Empleado</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-indigo-600">
            {estadisticas.promedio_dias_por_empleado.toFixed(1)}
          </div>
          <p className="text-xs text-muted-foreground">
            Días promedio asignados
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default EstadisticasVacaciones