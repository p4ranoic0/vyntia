import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/shared/ui/select'
import { useQuery } from '@tanstack/react-query'
import {
    Building2,
    Download,
    FileText,
    Filter,
    Search,
    TrendingUp,
    Users
} from 'lucide-react'
import { useState } from 'react'
// Progress component no disponible - usando alternativa con div
// Tabs component no disponible - usando navegación simple
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { AreasLayout } from '@/components/layout/AreasLayout'
import { useToast } from '@/shared/ui/use-toast'
import { Area, departmentsService, AreaStats } from '@/features/organization/services/departmentsService'

export function AreasManagementPage() {
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [filterEstado, setFilterEstado] = useState<string>('todos')
  const [filterOrgano, setFilterOrgano] = useState<string>('todos')

  const { data: areasData, isLoading } = useQuery({
    queryKey: ['areas'],
    queryFn: () => departmentsService.getAreas(),
  })

  const { data: statsData, isLoading: isLoadingStats } = useQuery({
    queryKey: ['areas-stats'],
    queryFn: () => departmentsService.getAreasStats(),
  })

  const areas = areasData?.data || []
  const stats: AreaStats = statsData || {
    total_areas: 0,
    areas_activas: 0,
    areas_inactivas: 0,
    total_empleados: 0,
    areas_sin_jefe: 0,
    promedio_empleados_por_area: 0
  }

  // Filtrar áreas
  const filteredAreas = areas.filter((area: Area) => {
    const matchesSearch = (area.nombre_unidad_organica || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                         area.nombre_organo.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         area.siglas_area.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (area.nombre_completo || '').toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesEstado = filterEstado === 'todos' || area.estado_area === filterEstado
    const matchesOrgano = filterOrgano === 'todos' || area.nombre_organo === filterOrgano
    
    return matchesSearch && matchesEstado && matchesOrgano
  })

  // Obtener órganos únicos para el filtro
  const organosUnicos = Array.from(new Set(areas.map((area: Area) => area.nombre_organo)))

  // Función para exportar datos
  const handleExport = (format: 'csv' | 'pdf') => {
    toast({
      title: 'Exportando datos',
      description: `Generando reporte en formato ${format.toUpperCase()}...`,
    })
    // Aquí iría la lógica de exportación
  }

  // Datos para gráficos
  const chartData = {
    areasPorOrgano: organosUnicos.map(organo => ({
      organo,
      cantidad: areas.filter((area: Area) => area.nombre_organo === organo).length
    })),
    empleadosPorArea: areas.map((area: Area) => ({
      area: area.siglas_area,
      empleados: area.empleados_activos_count || 0
    })).sort((a, b) => b.empleados - a.empleados).slice(0, 10)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <AreasLayout 
      title="Gestión de Áreas" 
      description="Panel de control y análisis de áreas organizacionales"
    >
      <div className="space-y-4 sm:space-y-6">
        {/* Header con botones de exportación */}
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-end">
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => handleExport('csv')} className="cursor-pointer flex-1 sm:flex-none text-xs sm:text-sm">
              <Download className="mr-2 h-4 w-4" />
              Exportar CSV
            </Button>
            <Button variant="outline" onClick={() => handleExport('pdf')} className="cursor-pointer flex-1 sm:flex-none text-xs sm:text-sm">
              <FileText className="mr-2 h-4 w-4" />
              Exportar PDF
            </Button>
          </div>
        </div>

      {/* Stats Cards */}
      <div className="grid gap-3 sm:gap-4 grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Áreas</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_areas}</div>
            <p className="text-xs text-muted-foreground">
              {stats.areas_activas} activas, {stats.areas_inactivas} inactivas
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Empleados</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_empleados}</div>
            <p className="text-xs text-muted-foreground">
              Promedio: {stats.promedio_empleados_por_area.toFixed(1)} por área
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Áreas sin Jefe</CardTitle>
            <Users className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.areas_sin_jefe}</div>
            <p className="text-xs text-muted-foreground">
              {((stats.areas_sin_jefe / stats.total_areas) * 100).toFixed(1)}% del total
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Eficiencia</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((stats.areas_activas / stats.total_areas) * 100).toFixed(0)}%
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className="bg-blue-600 h-2 rounded-full" 
                style={{ width: `${(stats.areas_activas / stats.total_areas) * 100}%` }}
              ></div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sección Principal */}
      <div className="space-y-4">
        {/* Sección de Resumen */}
        <div className="space-y-4">
          {/* Filtros */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="h-5 w-5" />
                Filtros y Búsqueda
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Buscar</label>
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Buscar área..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-8"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Estado</label>
                  <Select value={filterEstado} onValueChange={setFilterEstado}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="todos">Todos</SelectItem>
                      <SelectItem value="activo">Activas</SelectItem>
                      <SelectItem value="inactivo">Inactivas</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Órgano</label>
                  <Select value={filterOrgano} onValueChange={setFilterOrgano}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="todos">Todos</SelectItem>
                      {organosUnicos.map(organo => (
                        <SelectItem key={organo} value={organo}>{organo}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Resultados</label>
                  <div className="text-sm text-muted-foreground pt-2">
                    {filteredAreas.length} de {areas.length} áreas
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Lista de Áreas Filtradas */}
          <Card>
            <CardHeader>
              <CardTitle>Áreas Encontradas</CardTitle>
              <CardDescription>
                {filteredAreas.length} áreas coinciden con los filtros aplicados
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {filteredAreas.map((area: Area) => (
                  <div key={area.id} className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between p-3 sm:p-4 border rounded-lg">
                    <div className="flex items-center gap-3 sm:gap-4">
                      <div className="p-2 bg-blue-100 rounded-lg flex-shrink-0">
                        <Building2 className="h-4 w-4 sm:h-5 sm:w-5 text-blue-600" />
                      </div>
                      <div className="min-w-0">
                        <h3 className="font-semibold text-sm sm:text-base truncate">{area.nombre_unidad_organica || 'Sin unidad orgánica'}</h3>
                        <p className="text-xs sm:text-sm text-muted-foreground truncate">{area.nombre_organo}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 sm:gap-4 ml-11 sm:ml-0">
                      <Badge variant="outline">{area.siglas_area}</Badge>
                      <div className="text-xs sm:text-sm text-center">
                        <div className="font-medium">{area.empleados_activos_count || 0}</div>
                        <div className="text-muted-foreground">empleados</div>
                      </div>
                      <Badge variant={area.estado_area === 'activo' ? 'default' : 'secondary'}>
                        {area.estado_area === 'activo' ? 'Activa' : 'Inactiva'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      </div>
    </AreasLayout>
  )
}