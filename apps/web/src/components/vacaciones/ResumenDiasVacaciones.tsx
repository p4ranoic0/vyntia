import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { 
  Calendar, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  TrendingUp,
  Eye,
  Plus,
  RefreshCw
} from 'lucide-react'
import { format, differenceInDays, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'
import { ResumenPeriodo } from '@/services/timeOffService'

interface ResumenDiasVacacionesProps {
  resumen: ResumenPeriodo
  loading?: boolean
  onNuevaSolicitud?: () => void
  onVerDetalle?: () => void
  onActualizar?: () => void
  showActions?: boolean
}

const ResumenDiasVacaciones: React.FC<ResumenDiasVacacionesProps> = ({ 
  resumen, 
  loading = false,
  onNuevaSolicitud,
  onVerDetalle,
  onActualizar,
  showActions = true
}) => {
  if (loading) {
    return (
      <Card className="animate-pulse">
        <CardHeader>
          <div className="h-6 bg-gray-200 rounded w-48 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-64"></div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 bg-gray-200 rounded w-24"></div>
                <div className="h-8 bg-gray-200 rounded w-16"></div>
                <div className="h-2 bg-gray-200 rounded w-full"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  // Cálculos
  const porcentajeUtilizado = resumen.dias_correspondientes > 0 
    ? (resumen.dias_utilizados / resumen.dias_correspondientes) * 100 
    : 0

  const porcentajePendiente = resumen.dias_correspondientes > 0 
    ? (resumen.dias_pendientes / resumen.dias_correspondientes) * 100 
    : 0

  const diasVencenProximamente = resumen.fecha_vencimiento 
    ? differenceInDays(parseISO(resumen.fecha_vencimiento), new Date())
    : null

  const estaVenciendo = diasVencenProximamente !== null && diasVencenProximamente <= 30 && diasVencenProximamente > 0
  const yaVencio = diasVencenProximamente !== null && diasVencenProximamente <= 0

  return (
    <Card className={`${yaVencio ? 'border-red-200 bg-red-50' : estaVenciendo ? 'border-orange-200 bg-orange-50' : ''}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Resumen de Vacaciones {resumen.ano_periodo}
            </CardTitle>
            <CardDescription>
              Período: {format(parseISO(resumen.fecha_inicio), 'dd/MM/yyyy')} - {format(parseISO(resumen.fecha_fin), 'dd/MM/yyyy')}
            </CardDescription>
          </div>
          
          <div className="flex items-center gap-2">
            <Badge 
              variant={resumen.estado_periodo === 'activo' ? 'default' : 'secondary'}
              className={resumen.estado_periodo === 'activo' ? 'bg-green-100 text-green-800' : ''}
            >
              {resumen.estado_periodo.toUpperCase()}
            </Badge>
            
            {yaVencio && (
              <Badge variant="destructive">
                <AlertTriangle className="mr-1 h-3 w-3" />
                Vencido
              </Badge>
            )}
            
            {estaVenciendo && (
              <Badge variant="outline" className="bg-orange-100 text-orange-800">
                <Clock className="mr-1 h-3 w-3" />
                Vence pronto
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Alerta de vencimiento */}
        {(estaVenciendo || yaVencio) && (
          <div className={`p-4 rounded-lg border ${
            yaVencio 
              ? 'bg-red-50 border-red-200 text-red-800' 
              : 'bg-orange-50 border-orange-200 text-orange-800'
          }`}>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              <span className="font-medium">
                {yaVencio 
                  ? `Días vencidos hace ${Math.abs(diasVencenProximamente!)} días`
                  : `Días vencen en ${diasVencenProximamente} días`
                }
              </span>
            </div>
            {resumen.fecha_vencimiento && (
              <p className="text-sm mt-1">
                Fecha de vencimiento: {format(parseISO(resumen.fecha_vencimiento), 'PPP', { locale: es })}
              </p>
            )}
          </div>
        )}
        
        {/* Estadísticas principales */}
        <div className="grid gap-4 md:grid-cols-3">
          {/* Días Correspondientes */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-muted-foreground">Días Asignados</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {resumen.dias_correspondientes}
            </div>
            <p className="text-xs text-muted-foreground">
              Total de días para este período
            </p>
          </div>
          
          {/* Días Utilizados */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-muted-foreground">Días Utilizados</span>
            </div>
            <div className="text-2xl font-bold text-green-600">
              {resumen.dias_utilizados}
            </div>
            <div className="space-y-1">
              <Progress value={porcentajeUtilizado} className="h-2" />
              <p className="text-xs text-muted-foreground">
                {porcentajeUtilizado.toFixed(1)}% del total
              </p>
            </div>
          </div>
          
          {/* Días Pendientes */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-orange-600" />
              <span className="text-sm font-medium text-muted-foreground">Días Disponibles</span>
            </div>
            <div className="text-2xl font-bold text-orange-600">
              {resumen.dias_pendientes}
            </div>
            <div className="space-y-1">
              <Progress value={porcentajePendiente} className="h-2" />
              <p className="text-xs text-muted-foreground">
                {porcentajePendiente.toFixed(1)}% disponible
              </p>
            </div>
          </div>
        </div>
        
        {/* Información adicional */}
        <div className="grid gap-4 md:grid-cols-2">
          {/* Solicitudes */}
          <div className="p-3 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Actividad de Solicitudes
            </h4>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Total solicitudes:</span>
                <span className="font-medium">{resumen.total_solicitudes}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Aprobadas:</span>
                <span className="font-medium text-green-600">{resumen.solicitudes_aprobadas}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Pendientes:</span>
                <span className="font-medium text-orange-600">{resumen.solicitudes_pendientes}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Rechazadas:</span>
                <span className="font-medium text-red-600">{resumen.solicitudes_rechazadas}</span>
              </div>
            </div>
          </div>
          
          {/* Fechas importantes */}
          <div className="p-3 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2 flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Fechas Importantes
            </h4>
            <div className="space-y-1 text-sm">
              <div>
                <span className="text-muted-foreground">Inicio período:</span>
                <p className="font-medium">
                  {format(parseISO(resumen.fecha_inicio), 'PPP', { locale: es })}
                </p>
              </div>
              <div>
                <span className="text-muted-foreground">Fin período:</span>
                <p className="font-medium">
                  {format(parseISO(resumen.fecha_fin), 'PPP', { locale: es })}
                </p>
              </div>
              {resumen.fecha_vencimiento && (
                <div>
                  <span className="text-muted-foreground">Vencimiento:</span>
                  <p className={`font-medium ${
                    yaVencio ? 'text-red-600' : estaVenciendo ? 'text-orange-600' : 'text-gray-900'
                  }`}>
                    {format(parseISO(resumen.fecha_vencimiento), 'PPP', { locale: es })}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Acciones */}
        {showActions && (
          <div className="flex gap-2 pt-4 border-t">
            {onNuevaSolicitud && resumen.dias_pendientes > 0 && resumen.estado_periodo === 'activo' && (
              <Button onClick={onNuevaSolicitud} className="flex-1">
                <Plus className="mr-2 h-4 w-4" />
                Nueva Solicitud
              </Button>
            )}
            
            {onVerDetalle && (
              <Button variant="outline" onClick={onVerDetalle}>
                <Eye className="mr-2 h-4 w-4" />
                Ver Detalle
              </Button>
            )}
            
            {onActualizar && (
              <Button variant="outline" onClick={onActualizar}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Actualizar
              </Button>
            )}
          </div>
        )}
        
        {/* Mensaje si no hay días disponibles */}
        {resumen.dias_pendientes === 0 && resumen.estado_periodo === 'activo' && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <CheckCircle className="inline mr-1 h-4 w-4" />
              Has utilizado todos los días de vacaciones de este período.
            </p>
          </div>
        )}
        
        {/* Mensaje si el período está inactivo */}
        {resumen.estado_periodo !== 'activo' && (
          <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
            <p className="text-sm text-gray-600">
              <Clock className="inline mr-1 h-4 w-4" />
              Este período está {resumen.estado_periodo}. No se pueden crear nuevas solicitudes.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default ResumenDiasVacaciones