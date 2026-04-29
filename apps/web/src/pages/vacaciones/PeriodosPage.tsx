import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useToast } from '@/hooks/use-toast'
import { useAuth } from '@/hooks/useAuth'
import timeOffService, {
    PeriodoVacacional,
    ResumenPeriodo
} from '@/services/timeOffService'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import {
    AlertTriangle,
    ArrowLeft,
    Calendar,
    CheckCircle,
    Clock,
    Download,
    Eye,
    Search
} from 'lucide-react'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

// Componente para mostrar el estado de un período
interface EstadoPeriodoBadgeProps {
  estado: string
}

const EstadoPeriodoBadge: React.FC<EstadoPeriodoBadgeProps> = ({ estado }) => {
  const variants: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline', className: string }> = {
    'activo': { variant: 'default', className: 'bg-green-100 text-green-800' },
    'vencido': { variant: 'destructive', className: 'bg-red-100 text-red-800' },
    'proximo_vencimiento': { variant: 'outline', className: 'bg-yellow-100 text-yellow-800' },
    'cerrado': { variant: 'secondary', className: 'bg-gray-100 text-gray-800' }
  }

  const config = variants[estado] || variants['activo']
  
  return (
    <Badge variant={config.variant} className={config.className}>
      {estado.replace('_', ' ').toUpperCase()}
    </Badge>
  )
}

// Componente para mostrar el resumen de un período
interface ResumenPeriodoCardProps {
  periodo: PeriodoVacacional
  resumen: ResumenPeriodo | null
  onVerDetalle: () => void
}

const ResumenPeriodoCard: React.FC<ResumenPeriodoCardProps> = ({ periodo, resumen, onVerDetalle }) => {
  if (!resumen) return null

  const porcentajeUso = resumen.dias_correspondientes > 0 
    ? ((resumen.dias_correspondientes - resumen.dias_pendientes) / resumen.dias_correspondientes) * 100 
    : 0

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Período {periodo.ano_periodo}</CardTitle>
          <EstadoPeriodoBadge estado={periodo.estado_periodo} />
        </div>
        <CardDescription>
          {format(new Date(periodo.fecha_inicio), 'dd/MM/yyyy')} - {format(new Date(periodo.fecha_fin), 'dd/MM/yyyy')}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Estadísticas */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-blue-600">{resumen.dias_correspondientes}</p>
              <p className="text-xs text-muted-foreground">Correspondientes</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{resumen.dias_pendientes}</p>
              <p className="text-xs text-muted-foreground">Pendientes</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-orange-600">
                {resumen.dias_correspondientes - resumen.dias_pendientes}
              </p>
              <p className="text-xs text-muted-foreground">Utilizados</p>
            </div>
          </div>

          {/* Barra de progreso */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Uso del período</span>
              <span>{porcentajeUso.toFixed(1)}%</span>
            </div>
            <Progress value={porcentajeUso} className="h-2" />
          </div>

          {/* Alertas */}
          {resumen.vencimiento_proximo && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="text-sm">
                Días próximos a vencer
              </AlertDescription>
            </Alert>
          )}

          {/* Solicitudes */}
          {resumen.solicitudes_activas > 0 && (
            <div className="text-sm text-muted-foreground">
              <Clock className="inline h-3 w-3 mr-1" />
              {resumen.solicitudes_activas} solicitud(es) activa(s)
            </div>
          )}

          {/* Botón de acción */}
          <Button variant="outline" className="w-full" onClick={onVerDetalle}>
            <Eye className="mr-2 h-4 w-4" />
            Ver Detalle
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

// Componente para el detalle de un período
interface DetallePeriodoProps {
  periodo: PeriodoVacacional
  resumen: ResumenPeriodo | null
  onClose: () => void
}

const DetallePeriodo: React.FC<DetallePeriodoProps> = ({ periodo, resumen, onClose }) => {
  return (
    <div className="space-y-6">
      {/* Información básica */}
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Período</Label>
          <p className="text-lg font-semibold">{periodo.ano_periodo}</p>
        </div>
        
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Estado</Label>
          <div className="mt-1">
            <EstadoPeriodoBadge estado={periodo.estado_periodo} />
          </div>
        </div>
      </div>

      {/* Fechas */}
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Fecha de Inicio</Label>
          <p className="text-lg">
            {format(new Date(periodo.fecha_inicio), 'PPP', { locale: es })}
          </p>
        </div>
        
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Fecha de Fin</Label>
          <p className="text-lg">
            {format(new Date(periodo.fecha_fin), 'PPP', { locale: es })}
          </p>
        </div>
      </div>

      {/* Días */}
      <div className="grid gap-4 md:grid-cols-3">
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Días Correspondientes</Label>
          <p className="text-2xl font-bold text-blue-600">{periodo.dias_correspondientes}</p>
        </div>
        
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Días Pendientes</Label>
          <p className="text-2xl font-bold text-green-600">{periodo.dias_pendientes}</p>
        </div>
        
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Días Utilizados</Label>
          <p className="text-2xl font-bold text-orange-600">
            {periodo.dias_correspondientes - periodo.dias_pendientes}
          </p>
        </div>
      </div>

      {/* Fechas de vencimiento */}
      {periodo.fecha_vencimiento && (
        <div>
          <Label className="text-sm font-medium text-muted-foreground">Fecha de Vencimiento</Label>
          <p className="text-lg">
            {format(new Date(periodo.fecha_vencimiento), 'PPP', { locale: es })}
          </p>
        </div>
      )}

      {/* Información adicional del resumen */}
      {resumen && (
        <div className="border-t pt-4">
          <h4 className="font-medium mb-3">Información Adicional</h4>
          
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label className="text-sm font-medium text-muted-foreground">Solicitudes Activas</Label>
              <p className="text-lg">{resumen.solicitudes_activas}</p>
            </div>
            
            <div>
              <Label className="text-sm font-medium text-muted-foreground">Vencimiento Próximo</Label>
              <p className="text-lg">
                {resumen.vencimiento_proximo ? (
                  <Badge variant="outline" className="bg-yellow-100 text-yellow-800">
                    Sí
                  </Badge>
                ) : (
                  <Badge variant="outline" className="bg-green-100 text-green-800">
                    No
                  </Badge>
                )}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Fechas de auditoría */}
      <div className="border-t pt-4">
        <h4 className="font-medium mb-3">Información de Auditoría</h4>
        
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <Label className="text-sm font-medium text-muted-foreground">Fecha de Creación</Label>
            <p className="text-sm">
              {format(new Date(periodo.created_at), 'PPP', { locale: es })}
            </p>
          </div>
          
          <div>
            <Label className="text-sm font-medium text-muted-foreground">Última Actualización</Label>
            <p className="text-sm">
              {format(new Date(periodo.updated_at), 'PPP', { locale: es })}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

// Componente principal
const PeriodosPage: React.FC = () => {
  const { user } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [periodos, setPeriodos] = useState<PeriodoVacacional[]>([])
  const [resumenes, setResumenes] = useState<Record<number, ResumenPeriodo>>({})
  const [selectedPeriodo, setSelectedPeriodo] = useState<PeriodoVacacional | null>(null)
  const [showDetail, setShowDetail] = useState(false)
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards')
  
  // Filtros
  const [searchTerm, setSearchTerm] = useState('')
  const [estadoFilter, setEstadoFilter] = useState<string>('todos')
  const [anoFilter, setAnoFilter] = useState<string>('todos')

  // Cargar períodos
  useEffect(() => {
    const cargarPeriodos = async () => {
      if (!user?.empleado_id) return
      
      try {
        setLoading(true)
        
        // Cargar períodos del empleado
        const periodosRes = await timeOffService.getPeriodosByEmpleado(user.empleado_id)
        setPeriodos(periodosRes)
        
        // Cargar resúmenes de cada período
        const resumenesData: Record<number, ResumenPeriodo> = {}
        for (const periodo of periodosRes) {
          try {
            const resumen = await timeOffService.getResumenPeriodo(user.empleado_id, periodo.id)
            resumenesData[periodo.id] = resumen
          } catch (error) {
            console.error(`Error al cargar resumen del período ${periodo.id}:`, error)
          }
        }
        setResumenes(resumenesData)
        
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

  const handleVerDetalle = (periodo: PeriodoVacacional) => {
    setSelectedPeriodo(periodo)
    setShowDetail(true)
  }

  const handleVolver = () => {
    navigate('/vacaciones')
  }

  // Filtrar períodos
  const filteredPeriodos = periodos.filter(periodo => {
    if (estadoFilter !== 'todos' && periodo.estado_periodo !== estadoFilter) return false
    if (anoFilter !== 'todos' && periodo.ano_periodo.toString() !== anoFilter) return false
    if (searchTerm && !periodo.ano_periodo.toString().includes(searchTerm)) return false
    return true
  })

  const estadosDisponibles = ['activo', 'vencido', 'proximo_vencimiento', 'cerrado']
  const anosDisponibles = Array.from(new Set(periodos.map(p => p.ano_periodo))).sort((a, b) => b - a)

  // Estadísticas rápidas
  const totalPeriodos = periodos.length
  const periodosActivos = periodos.filter(p => p.estado_periodo === 'activo').length
  const diasTotales = periodos.reduce((sum, p) => sum + p.dias_correspondientes, 0)
  const diasPendientes = periodos.reduce((sum, p) => sum + p.dias_pendientes, 0)

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
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Mis Períodos Vacacionales</h1>
          <p className="text-muted-foreground">
            Gestiona y consulta tus períodos de vacaciones
          </p>
        </div>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid gap-4 md:grid-cols-4 mb-6">
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

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Días Totales</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{diasTotales}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Días Pendientes</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{diasPendientes}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Filtros</CardTitle>
            <div className="flex gap-2">
              <Button
                variant={viewMode === 'cards' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('cards')}
              >
                Tarjetas
              </Button>
              <Button
                variant={viewMode === 'table' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('table')}
              >
                Tabla
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="space-y-2">
              <Label htmlFor="search">Buscar</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Año del período..."
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
              <Button variant="outline" className="w-full">
                <Download className="mr-2 h-4 w-4" />
                Exportar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Contenido principal */}
      {filteredPeriodos.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <Calendar className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-lg font-medium">No hay períodos vacacionales</p>
            <p className="text-muted-foreground">
              {searchTerm || estadoFilter || anoFilter 
                ? 'No se encontraron períodos con los filtros aplicados'
                : 'No tienes períodos vacacionales asignados'
              }
            </p>
          </CardContent>
        </Card>
      ) : viewMode === 'cards' ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredPeriodos.map((periodo) => (
            <ResumenPeriodoCard
              key={periodo.id}
              periodo={periodo}
              resumen={resumenes[periodo.id] || null}
              onVerDetalle={() => handleVerDetalle(periodo)}
            />
          ))}
        </div>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Períodos ({filteredPeriodos.length})</CardTitle>
            <CardDescription>
              Lista de períodos vacacionales
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Período</TableHead>
                    <TableHead>Fechas</TableHead>
                    <TableHead>Días Correspondientes</TableHead>
                    <TableHead>Días Pendientes</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead>Uso</TableHead>
                    <TableHead>Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPeriodos.map((periodo) => {
                    const resumen = resumenes[periodo.id]
                    const porcentajeUso = resumen && resumen.dias_correspondientes > 0 
                      ? ((resumen.dias_correspondientes - resumen.dias_pendientes) / resumen.dias_correspondientes) * 100 
                      : 0
                    
                    return (
                      <TableRow key={periodo.id}>
                        <TableCell className="font-medium">{periodo.ano_periodo}</TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <p>{format(new Date(periodo.fecha_inicio), 'dd/MM/yyyy')}</p>
                            <p className="text-muted-foreground">
                              {format(new Date(periodo.fecha_fin), 'dd/MM/yyyy')}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <span className="font-medium text-blue-600">
                            {periodo.dias_correspondientes}
                          </span>
                        </TableCell>
                        <TableCell>
                          <span className="font-medium text-green-600">
                            {periodo.dias_pendientes}
                          </span>
                        </TableCell>
                        <TableCell>
                          <EstadoPeriodoBadge estado={periodo.estado_periodo} />
                        </TableCell>
                        <TableCell>
                          <div className="w-20">
                            <Progress value={porcentajeUso} className="h-2" />
                            <p className="text-xs text-muted-foreground mt-1">
                              {porcentajeUso.toFixed(1)}%
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleVerDetalle(periodo)}
                          >
                            <Eye className="mr-1 h-3 w-3" />
                            Ver
                          </Button>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Dialog de detalle */}
      <Dialog open={showDetail} onOpenChange={setShowDetail}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Detalle del Período Vacacional</DialogTitle>
            <DialogDescription>
              Información completa del período vacacional
            </DialogDescription>
          </DialogHeader>
          
          {selectedPeriodo && (
            <DetallePeriodo
              periodo={selectedPeriodo}
              resumen={resumenes[selectedPeriodo.id] || null}
              onClose={() => setShowDetail(false)}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default PeriodosPage
