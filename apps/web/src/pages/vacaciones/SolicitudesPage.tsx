import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'
import { useAuth } from '@/hooks/useAuth'
import vacacionesService, {
    AprobacionSolicitudForm,
    SolicitudesFilter,
    SolicitudVacaciones
} from '@/services/vacacionesService'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import {
    ArrowLeft,
    CheckCircle,
    Clock,
    Download,
    Eye,
    FileText,
    Search,
    XCircle
} from 'lucide-react'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

// Componente para mostrar el estado de una solicitud
interface EstadoBadgeProps {
  estado: string
}

const EstadoBadge: React.FC<EstadoBadgeProps> = ({ estado }) => {
  const variants: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline', className: string }> = {
    'borrador': { variant: 'outline', className: 'bg-gray-100 text-gray-800' },
    'enviada': { variant: 'secondary', className: 'bg-blue-100 text-blue-800' },
    'en_revision': { variant: 'default', className: 'bg-yellow-100 text-yellow-800' },
    'aprobada': { variant: 'default', className: 'bg-green-100 text-green-800' },
    'rechazada': { variant: 'destructive', className: 'bg-red-100 text-red-800' },
    'cancelada': { variant: 'secondary', className: 'bg-gray-100 text-gray-800' }
  }

  const config = variants[estado] || variants['borrador']
  
  return (
    <Badge variant={config.variant} className={config.className}>
      {estado.replace('_', ' ').toUpperCase()}
    </Badge>
  )
}

// Componente para el detalle de una solicitud
interface DetalleSolicitudProps {
  solicitud: SolicitudVacaciones
  onClose: () => void
  onApprove?: (solicitudId: number, data: AprobacionSolicitudForm) => void
  onReject?: (solicitudId: number, data: AprobacionSolicitudForm) => void
  canApprove: boolean
}

const DetalleSolicitud: React.FC<DetalleSolicitudProps> = ({ 
  solicitud, 
  onClose, 
  onApprove, 
  onReject, 
  canApprove 
}) => {
  const [accion, setAccion] = useState<'aprobar' | 'rechazar' | null>(null)
  const [motivo, setMotivo] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmitAprobacion = async () => {
    if (!accion || !onApprove || !onReject) return
    
    try {
      setSubmitting(true)
      const data: AprobacionSolicitudForm = {
        accion_aprobacion: accion === 'aprobar' ? 'aprobar' : 'rechazar',
        motivo_aprobacion: motivo
      }
      
      if (accion === 'aprobar') {
        await onApprove(solicitud.id, data)
      } else {
        await onReject(solicitud.id, data)
      }
      
      onClose()
    } catch (error) {
      console.error('Error al procesar aprobación:', error)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Información del empleado */}
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Empleado</Label>
          <p className="text-lg font-semibold">
            {solicitud?.empleado?.nombres || ''} {solicitud?.empleado?.apellidos || ''}
          </p>
          <p className="text-sm text-muted-foreground">
            {solicitud?.empleado?.numero_identificacion || ''}
          </p>
        </div>
        
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Área</Label>
          <p className="text-lg">{solicitud?.area?.nombre_area || ''}</p>
        </div>
      </div>

      {/* Información de la solicitud */}
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Período</Label>
          <p className="text-lg">{solicitud?.periodo_vacacional?.ano_periodo || ''}</p>
        </div>
        
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Estado</Label>
          <div className="mt-1">
            <EstadoBadge estado={solicitud?.estado_solicitud || 'borrador'} />
          </div>
        </div>
      </div>

      {/* Fechas y días */}
      <div className="grid gap-4 md:grid-cols-3">
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Fecha de Inicio</Label>
          <p className="text-lg">
            {solicitud?.fecha_inicio_solicitud ? format(new Date(solicitud.fecha_inicio_solicitud), 'PPP', { locale: es }) : 'No definida'}
          </p>
        </div>
        
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Fecha de Fin</Label>
          <p className="text-lg">
            {solicitud?.fecha_fin_solicitud ? format(new Date(solicitud.fecha_fin_solicitud), 'PPP', { locale: es }) : 'No definida'}
          </p>
        </div>
        
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Días Solicitados</Label>
          <p className="text-lg font-semibold text-blue-600">
            {solicitud?.dias_solicitados || 0} días
          </p>
        </div>
      </div>

      {/* Cálculo de días */}
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Días Calendario</Label>
          <p className="text-lg">{solicitud?.dias_calendario || 0}</p>
        </div>
        
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Días Hábiles</Label>
          <p className="text-lg">{solicitud?.dias_habiles || 0}</p>
        </div>
      </div>

      {/* Fraccionamiento */}
      {solicitud.fraccionamiento && (
        <Alert>
          <Clock className="h-4 w-4" />
          <AlertDescription>
            Esta solicitud está marcada como fraccionamiento de vacaciones.
          </AlertDescription>
        </Alert>
      )}

      {/* Observaciones */}
      {solicitud.observaciones_solicitud && (
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Observaciones</Label>
          <p className="mt-1 p-3 bg-gray-50 rounded-md">
            {solicitud.observaciones_solicitud}
          </p>
        </div>
      )}

      {/* Información de aprobación */}
      {solicitud.aprobador && (
        <div className="border-t pt-4">
          <h4 className="font-medium mb-3">Información de Aprobación</h4>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label className="text-sm font-medium text-muted-foreground">Aprobador</Label>
              <p>{solicitud?.aprobador?.nombres || ''} {solicitud?.aprobador?.apellidos || ''}</p>
            </div>
            
            {solicitud.fecha_aprobacion && (
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Fecha de Aprobación</Label>
                <p>{format(new Date(solicitud.fecha_aprobacion), 'PPP', { locale: es })}</p>
              </div>
            )}
          </div>
          
          {solicitud.motivo_aprobacion && (
            <div className="mt-3">
              <Label className="text-sm font-medium text-muted-foreground">Motivo</Label>
              <p className="mt-1 p-3 bg-gray-50 rounded-md">
                {solicitud.motivo_aprobacion}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Acciones de aprobación */}
      {canApprove && solicitud.estado_solicitud === 'en_revision' && (
        <div className="border-t pt-4">
          <h4 className="font-medium mb-3">Acciones de Aprobación</h4>
          
          {!accion ? (
            <div className="flex gap-2">
              <Button 
                onClick={() => setAccion('aprobar')}
                className="bg-green-600 hover:bg-green-700"
              >
                <CheckCircle className="mr-2 h-4 w-4" />
                Aprobar
              </Button>
              <Button 
                onClick={() => setAccion('rechazar')}
                variant="destructive"
              >
                <XCircle className="mr-2 h-4 w-4" />
                Rechazar
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <Label htmlFor="motivo">Motivo de {accion === 'aprobar' ? 'aprobación' : 'rechazo'}</Label>
                <Textarea
                  id="motivo"
                  value={motivo}
                  onChange={(e) => setMotivo(e.target.value)}
                  placeholder={`Escribe el motivo de ${accion === 'aprobar' ? 'aprobación' : 'rechazo'}...`}
                  rows={3}
                />
              </div>
              
              <div className="flex gap-2">
                <Button 
                  onClick={handleSubmitAprobacion}
                  disabled={submitting || !motivo.trim()}
                  className={accion === 'aprobar' ? 'bg-green-600 hover:bg-green-700' : ''}
                  variant={accion === 'rechazar' ? 'destructive' : 'default'}
                >
                  {submitting ? (
                    <LoadingSpinner className="mr-2 h-4 w-4" />
                  ) : accion === 'aprobar' ? (
                    <CheckCircle className="mr-2 h-4 w-4" />
                  ) : (
                    <XCircle className="mr-2 h-4 w-4" />
                  )}
                  Confirmar {accion === 'aprobar' ? 'Aprobación' : 'Rechazo'}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setAccion(null)
                    setMotivo('')
                  }}
                >
                  Cancelar
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Componente principal
const SolicitudesPage: React.FC = () => {
  const { user, isAdminOrRRHH, isJefe } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [solicitudes, setSolicitudes] = useState<SolicitudVacaciones[]>([])
  const [filteredSolicitudes, setFilteredSolicitudes] = useState<SolicitudVacaciones[]>([])
  const [selectedSolicitud, setSelectedSolicitud] = useState<SolicitudVacaciones | null>(null)
  const [showDetail, setShowDetail] = useState(false)
  
  // Filtros
  const [searchTerm, setSearchTerm] = useState('')
  const [estadoFilter, setEstadoFilter] = useState<string>('todos')
  const [anoFilter, setAnoFilter] = useState<string>('todos')
  const esGestor = isAdminOrRRHH()
  const esJefe = isJefe()

  // Cargar solicitudes
  useEffect(() => {
    const cargarSolicitudes = async () => {
      try {
        setLoading(true)
        
        const filters: SolicitudesFilter = {}
        if (estadoFilter !== 'todos') filters.estado = estadoFilter
        if (anoFilter !== 'todos') filters.ano = parseInt(anoFilter)
        
        let solicitudesRes: SolicitudVacaciones[] | any
        if (user?.empleado_id && !esGestor && !esJefe) {
          solicitudesRes = await vacacionesService.getMisSolicitudes()
        } else {
          solicitudesRes = await vacacionesService.getSolicitudes(filters)
        }
        setSolicitudes(solicitudesRes)
        setFilteredSolicitudes(solicitudesRes)
        
      } catch (error) {
        console.error('Error al cargar solicitudes:', error)
        toast({
          title: 'Error',
          description: 'No se pudieron cargar las solicitudes',
          variant: 'destructive'
        })
      } finally {
        setLoading(false)
      }
    }

    cargarSolicitudes()
  }, [user, estadoFilter, anoFilter, toast])

  // Aplicar filtros de búsqueda
  useEffect(() => {
    let filtered = solicitudes
    
    if (searchTerm) {
      filtered = filtered.filter(solicitud => 
        `${solicitud.empleado.nombres} ${solicitud.empleado.apellidos}`
          .toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        (solicitud.empleado.numero_identificacion || '')
          .toLowerCase()
          .includes(searchTerm.toLowerCase())
      )
    }
    
    setFilteredSolicitudes(filtered)
  }, [searchTerm, solicitudes])

  const handleVerDetalle = (solicitud: SolicitudVacaciones) => {
    setSelectedSolicitud(solicitud)
    setShowDetail(true)
  }

  const handleApprove = async (solicitudId: number, data: AprobacionSolicitudForm) => {
    try {
      await vacacionesService.aprobarSolicitud(solicitudId, data)
      toast({
        title: 'Solicitud aprobada',
        description: 'La solicitud ha sido aprobada correctamente'
      })
      
      // Recargar solicitudes
      const solicitudesRes = esGestor || esJefe
        ? await vacacionesService.getSolicitudes()
        : await vacacionesService.getMisSolicitudes()
      setSolicitudes(solicitudesRes)
      setFilteredSolicitudes(solicitudesRes)
      
    } catch (error: any) {
      console.error('Error al aprobar solicitud:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.message || 'No se pudo aprobar la solicitud',
        variant: 'destructive'
      })
    }
  }

  const handleReject = async (solicitudId: number, data: AprobacionSolicitudForm) => {
    try {
      await vacacionesService.rechazarSolicitud(solicitudId, data)
      toast({
        title: 'Solicitud rechazada',
        description: 'La solicitud ha sido rechazada'
      })
      
      // Recargar solicitudes
      const solicitudesRes = esGestor || esJefe
        ? await vacacionesService.getSolicitudes()
        : await vacacionesService.getMisSolicitudes()
      setSolicitudes(solicitudesRes)
      setFilteredSolicitudes(solicitudesRes)
      
    } catch (error: any) {
      console.error('Error al rechazar solicitud:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.message || 'No se pudo rechazar la solicitud',
        variant: 'destructive'
      })
    }
  }

  const handleVolver = () => {
    navigate('/vacaciones')
  }

  const handleExportar = () => {
    if (!filteredSolicitudes.length) {
      toast({
        title: 'Sin datos',
        description: 'No hay solicitudes para exportar',
        variant: 'destructive'
      })
      return
    }

    const headers = [
      'ID',
      'Empleado',
      'Documento',
      'Area',
      'Periodo',
      'Fecha Inicio',
      'Fecha Fin',
      'Dias Solicitados',
      'Estado',
      'Fecha Creacion'
    ]

    const rows = filteredSolicitudes.map((s) => [
      s.solicitud_id ?? s.id,
      `${s.empleado?.nombres || ''} ${s.empleado?.apellidos || ''}`.trim(),
      s.empleado?.numero_identificacion || '',
      s.area_nombre || '',
      s.periodo_vacacional?.ano_periodo || '',
      s.fecha_inicio_solicitud || s.fecha_inicio,
      s.fecha_fin_solicitud || s.fecha_fin,
      s.dias_solicitados ?? '',
      s.estado_solicitud || '',
      s.created_at || ''
    ])

    const escape = (value: any) => `"${String(value ?? '').replace(/"/g, '""')}"`
    const csv = [headers, ...rows].map((row) => row.map(escape).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `solicitudes_vacaciones_${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const canApprove = (solicitud: SolicitudVacaciones): boolean => {
    // Solo gestores o jefes pueden aprobar
    if (!esGestor && !esJefe) return false
    
    // No puede aprobar sus propias solicitudes
    if (solicitud?.empleado?.id === user?.empleado_id) return false
    
    return true
  }

  const estadosDisponibles = ['borrador', 'enviada', 'en_revision', 'aprobada', 'rechazada', 'cancelada']
  const anosDisponibles = Array.from(new Set(
    (solicitudes || [])
      .filter(s => s?.created_at)
      .map(s => new Date(s.created_at).getFullYear())
      .filter(ano => !isNaN(ano) && ano > 1900) // Filtrar años inválidos
  )).sort((a, b) => b - a)

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
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Gestión de Solicitudes</h1>
          <p className="text-muted-foreground">
            {esGestor || esJefe ? 'Administra las solicitudes de vacaciones' : 'Mis solicitudes de vacaciones'}
          </p>
        </div>
        <Button onClick={() => navigate('/vacaciones/nueva-solicitud')}>
          <FileText className="mr-2 h-4 w-4" />
          Nueva Solicitud
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
              <Label htmlFor="search">Buscar</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Nombre o identificación..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="estado">Estado</Label>
              <Select value={estadoFilter} onValueChange={setEstadoFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos los estados" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos los estados</SelectItem>
                  {estadosDisponibles.map(estado => (
                    <SelectItem key={estado} value={estado}>
                      {estado.replace('_', ' ').toUpperCase()}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="ano">Año</Label>
              <Select value={anoFilter} onValueChange={setAnoFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos los años" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos los años</SelectItem>
                  {anosDisponibles.map(ano => (
                    <SelectItem key={ano} value={ano.toString()}>
                      {ano}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label>Acciones</Label>
              <Button variant="outline" className="w-full" onClick={handleExportar}>
                <Download className="mr-2 h-4 w-4" />
                Exportar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabla de solicitudes */}
      <Card>
        <CardHeader>
          <CardTitle>Solicitudes ({filteredSolicitudes?.length || 0})</CardTitle>
          <CardDescription>
            Lista de solicitudes de vacaciones
          </CardDescription>
        </CardHeader>
        <CardContent>
          {(filteredSolicitudes?.length || 0) === 0 ? (
            <div className="text-center py-8">
              <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium">No hay solicitudes</p>
              <p className="text-muted-foreground">
                {searchTerm || estadoFilter || anoFilter 
                  ? 'No se encontraron solicitudes con los filtros aplicados'
                  : 'No hay solicitudes de vacaciones registradas'
                }
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
                    <TableHead>Fecha Solicitud</TableHead>
                    <TableHead>Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(filteredSolicitudes || []).map((solicitud) => (
                    <TableRow key={solicitud.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">
                            {solicitud?.empleado?.nombres || ''} {solicitud?.empleado?.apellidos || ''}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {solicitud?.empleado?.numero_identificacion || ''}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>{solicitud?.periodo_vacacional?.ano_periodo || ''}</TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <p>{solicitud?.fecha_inicio_solicitud ? format(new Date(solicitud.fecha_inicio_solicitud), 'dd/MM/yyyy') : 'No definida'}</p>
                          <p className="text-muted-foreground">
                            {solicitud?.fecha_fin_solicitud ? format(new Date(solicitud.fecha_fin_solicitud), 'dd/MM/yyyy') : 'No definida'}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="font-medium">{solicitud?.dias_solicitados || 0}</span>
                        {solicitud?.fraccionamiento && (
                          <Badge variant="outline" className="ml-1 text-xs">
                            Fracc.
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <EstadoBadge estado={solicitud?.estado_solicitud || 'borrador'} />
                      </TableCell>
                      <TableCell>
                        {solicitud?.created_at ? format(new Date(solicitud.created_at), 'dd/MM/yyyy') : 'No definida'}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleVerDetalle(solicitud)}
                        >
                          <Eye className="mr-1 h-3 w-3" />
                          Ver
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

      {/* Dialog de detalle */}
      <Dialog open={showDetail} onOpenChange={setShowDetail}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Detalle de Solicitud</DialogTitle>
            <DialogDescription>
              Información completa de la solicitud de vacaciones
            </DialogDescription>
          </DialogHeader>
          
          {selectedSolicitud && (
            <DetalleSolicitud
              solicitud={selectedSolicitud}
              onClose={() => setShowDetail(false)}
              onApprove={handleApprove}
              onReject={handleReject}
              canApprove={canApprove(selectedSolicitud)}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default SolicitudesPage
