import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select'
import { 
  Calendar, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Search,
  Filter,
  Eye,
  Download,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { format, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'
import { HistorialSolicitudVacaciones } from '@/services/timeOffService'

interface HistorialSolicitudesProps {
  solicitudes: HistorialSolicitudVacaciones[]
  loading?: boolean
  onVerDetalle?: (solicitudId: number) => void
  onExportar?: () => void
  showFilters?: boolean
  showPagination?: boolean
  currentPage?: number
  totalPages?: number
  onPageChange?: (page: number) => void
}

const HistorialSolicitudes: React.FC<HistorialSolicitudesProps> = ({ 
  solicitudes, 
  loading = false,
  onVerDetalle,
  onExportar,
  showFilters = true,
  showPagination = false,
  currentPage = 1,
  totalPages = 1,
  onPageChange
}) => {
  const [filtros, setFiltros] = useState({
    busqueda: '',
    estado: 'todos',
    ano: 'todos',
    mes: 'todos'
  })

  // Función para obtener el color del badge según el estado
  const getEstadoBadge = (estado: string) => {
    switch (estado.toLowerCase()) {
      case 'pendiente':
        return (
          <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
            <Clock className="mr-1 h-3 w-3" />
            Pendiente
          </Badge>
        )
      case 'aprobada':
        return (
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
            <CheckCircle className="mr-1 h-3 w-3" />
            Aprobada
          </Badge>
        )
      case 'rechazada':
        return (
          <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
            <XCircle className="mr-1 h-3 w-3" />
            Rechazada
          </Badge>
        )
      case 'cancelada':
        return (
          <Badge variant="outline" className="bg-gray-50 text-gray-700 border-gray-200">
            <XCircle className="mr-1 h-3 w-3" />
            Cancelada
          </Badge>
        )
      default:
        return (
          <Badge variant="outline">
            <AlertCircle className="mr-1 h-3 w-3" />
            {estado}
          </Badge>
        )
    }
  }

  // Función para obtener el color del badge según el tipo
  const getTipoBadge = (tipo: string) => {
    switch (tipo.toLowerCase()) {
      case 'normal':
        return <Badge variant="secondary">Normal</Badge>
      case 'fraccionamiento':
        return <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">Fraccionamiento</Badge>
      case 'compensatorio':
        return <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">Compensatorio</Badge>
      default:
        return <Badge variant="secondary">{tipo}</Badge>
    }
  }

  // Filtrar solicitudes
  const solicitudesFiltradas = (solicitudes || []).filter(solicitud => {
    const cumpleBusqueda = !filtros.busqueda || 
      solicitud.observaciones?.toLowerCase().includes(filtros.busqueda.toLowerCase()) ||
      solicitud.estado.toLowerCase().includes(filtros.busqueda.toLowerCase())
    
    const cumpleEstado = filtros.estado === 'todos' || solicitud.estado === filtros.estado
    
    const fechaInicio = parseISO(solicitud.fecha_inicio)
    const cumpleAno = filtros.ano === 'todos' || fechaInicio.getFullYear().toString() === filtros.ano
    const cumpleMes = filtros.mes === 'todos' || (fechaInicio.getMonth() + 1).toString() === filtros.mes
    
    return cumpleBusqueda && cumpleEstado && cumpleAno && cumpleMes
  })

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="h-6 bg-gray-200 rounded w-48 mb-2 animate-pulse"></div>
          <div className="h-4 bg-gray-200 rounded w-64 animate-pulse"></div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="p-4 border rounded-lg animate-pulse">
                <div className="flex justify-between items-start mb-2">
                  <div className="h-4 bg-gray-200 rounded w-32"></div>
                  <div className="h-6 bg-gray-200 rounded w-20"></div>
                </div>
                <div className="h-3 bg-gray-200 rounded w-48 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-24"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Historial de Solicitudes
            </CardTitle>
            <CardDescription>
              {solicitudesFiltradas.length} de {(solicitudes || []).length} solicitudes
            </CardDescription>
          </div>
          
          {onExportar && (
            <Button variant="outline" onClick={onExportar}>
              <Download className="mr-2 h-4 w-4" />
              Exportar
            </Button>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Filtros */}
        {showFilters && (
          <div className="grid gap-4 md:grid-cols-4 p-4 bg-gray-50 rounded-lg">
            <div className="space-y-2">
              <label className="text-sm font-medium">Buscar</label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar en observaciones..."
                  value={filtros.busqueda}
                  onChange={(e) => setFiltros(prev => ({ ...prev, busqueda: e.target.value }))}
                  className="pl-8"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Estado</label>
              <Select value={filtros.estado} onValueChange={(value) => setFiltros(prev => ({ ...prev, estado: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos los estados" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos los estados</SelectItem>
                  <SelectItem value="pendiente">Pendiente</SelectItem>
                  <SelectItem value="aprobada">Aprobada</SelectItem>
                  <SelectItem value="rechazada">Rechazada</SelectItem>
                  <SelectItem value="cancelada">Cancelada</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Año</label>
              <Select value={filtros.ano} onValueChange={(value) => setFiltros(prev => ({ ...prev, ano: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos los años" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos los años</SelectItem>
                  <SelectItem value="2024">2024</SelectItem>
                  <SelectItem value="2023">2023</SelectItem>
                  <SelectItem value="2022">2022</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Mes</label>
              <Select value={filtros.mes} onValueChange={(value) => setFiltros(prev => ({ ...prev, mes: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos los meses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos los meses</SelectItem>
                  <SelectItem value="1">Enero</SelectItem>
                  <SelectItem value="2">Febrero</SelectItem>
                  <SelectItem value="3">Marzo</SelectItem>
                  <SelectItem value="4">Abril</SelectItem>
                  <SelectItem value="5">Mayo</SelectItem>
                  <SelectItem value="6">Junio</SelectItem>
                  <SelectItem value="7">Julio</SelectItem>
                  <SelectItem value="8">Agosto</SelectItem>
                  <SelectItem value="9">Septiembre</SelectItem>
                  <SelectItem value="10">Octubre</SelectItem>
                  <SelectItem value="11">Noviembre</SelectItem>
                  <SelectItem value="12">Diciembre</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        )}
        
        {/* Lista de solicitudes */}
        {solicitudesFiltradas.length === 0 ? (
          <div className="text-center py-8">
            <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No hay solicitudes</h3>
            <p className="text-gray-500">
              {(solicitudes || []).length === 0 
                ? 'No se encontraron solicitudes de vacaciones.'
                : 'No hay solicitudes que coincidan con los filtros aplicados.'
              }
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {solicitudesFiltradas.map((solicitud) => (
              <div key={solicitud.id} className="p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div>
                      <h4 className="font-medium">
                        {format(parseISO(solicitud.fecha_inicio), 'dd/MM/yyyy')} - {format(parseISO(solicitud.fecha_fin), 'dd/MM/yyyy')}
                      </h4>
                      <p className="text-sm text-muted-foreground">
                        {solicitud.dias_calendario} días calendario • {solicitud.dias_habiles} días hábiles
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {getEstadoBadge(solicitud.estado)}
                    {solicitud.es_fraccionamiento && getTipoBadge('fraccionamiento')}
                  </div>
                </div>
                
                {/* Información adicional */}
                <div className="grid gap-2 md:grid-cols-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Período:</span>
                    <span className="ml-2 font-medium">{solicitud.periodo_ano}</span>
                  </div>
                  
                  <div>
                    <span className="text-muted-foreground">Solicitado:</span>
                    <span className="ml-2 font-medium">
                      {format(parseISO(solicitud.fecha_solicitud), 'dd/MM/yyyy HH:mm')}
                    </span>
                  </div>
                  
                  {solicitud.fecha_aprobacion && (
                    <div>
                      <span className="text-muted-foreground">Procesado:</span>
                      <span className="ml-2 font-medium">
                        {format(parseISO(solicitud.fecha_aprobacion), 'dd/MM/yyyy HH:mm')}
                      </span>
                    </div>
                  )}
                  
                  {solicitud.aprobado_por_nombre && (
                    <div>
                      <span className="text-muted-foreground">Procesado por:</span>
                      <span className="ml-2 font-medium">{solicitud.aprobado_por_nombre}</span>
                    </div>
                  )}
                </div>
                
                {/* Observaciones */}
                {solicitud.observaciones && (
                  <div className="mt-3 p-2 bg-gray-50 rounded text-sm">
                    <span className="text-muted-foreground">Observaciones:</span>
                    <p className="mt-1">{solicitud.observaciones}</p>
                  </div>
                )}
                
                {/* Comentarios de aprobación/rechazo */}
                {solicitud.comentarios_aprobacion && (
                  <div className={`mt-3 p-2 rounded text-sm ${
                    solicitud.estado === 'aprobada' 
                      ? 'bg-green-50 border border-green-200' 
                      : 'bg-red-50 border border-red-200'
                  }`}>
                    <span className="text-muted-foreground">
                      {solicitud.estado === 'aprobada' ? 'Comentarios de aprobación:' : 'Motivo de rechazo:'}
                    </span>
                    <p className="mt-1">{solicitud.comentarios_aprobacion}</p>
                  </div>
                )}
                
                {/* Acciones */}
                {onVerDetalle && (
                  <div className="mt-3 pt-3 border-t">
                    <Button variant="outline" size="sm" onClick={() => onVerDetalle(solicitud.id)}>
                      <Eye className="mr-2 h-4 w-4" />
                      Ver Detalle
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
        
        {/* Paginación */}
        {showPagination && totalPages > 1 && (
          <div className="flex items-center justify-between pt-4 border-t">
            <p className="text-sm text-muted-foreground">
              Página {currentPage} de {totalPages}
            </p>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange?.(currentPage - 1)}
                disabled={currentPage <= 1}
              >
                <ChevronLeft className="h-4 w-4" />
                Anterior
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange?.(currentPage + 1)}
                disabled={currentPage >= totalPages}
              >
                Siguiente
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default HistorialSolicitudes