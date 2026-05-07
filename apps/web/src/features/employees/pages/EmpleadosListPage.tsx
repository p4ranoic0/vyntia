'use client'

import DatosAcademicosModal from '@/components/modals/DatosAcademicosModal'
import DatosFamiliaresModal from '@/components/modals/DatosFamiliaresModal'
import DatosLaboralesModal from '@/components/modals/DatosLaboralesModal'
import DatosPersonalesModal from '@/components/modals/DatosPersonalesModal'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/shared/ui/dropdown-menu'
import { Input } from '@/shared/ui/input'
import { LoadingSpinner } from '@/shared/ui/loading-spinner'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/shared/ui/select'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/shared/ui/table'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useEmployeePermissions } from '@/hooks/useEmployeePermissions'
import { employeesService, type Employee } from '@/services/employeesService'
import {
    AlertCircle,
    Briefcase,
    Building,
    Calendar,
    Edit,
    Filter,
    GraduationCap,
    Heart,
    MoreHorizontal,
    Plus,
    Search,
    Trash2,
    User,
    Users
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

// Componente principal de lista de empleados
export default function EmpleadosListPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth()
  const { 
    permissions, 
    canViewEmployeeList, 
    getEmployeeFilter, 
    canAccessEmployeeData,
    currentEmployeeId,
    isEmployee
  } = useEmployeePermissions()
  
  // Debug inicial
  console.log('🔍 DEBUG: EmpleadosListPage montado')
  console.log('🔍 DEBUG: isAuthenticated:', isAuthenticated)
  console.log('🔍 DEBUG: authLoading:', authLoading)
  console.log('🔍 DEBUG: user:', user)
  
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedArea, setSelectedArea] = useState<string>('todos')
  const [selectedEstado, setSelectedEstado] = useState<string>('todos')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [accessDenied, setAccessDenied] = useState(false)
  const itemsPerPage = 10
  
  // Estados para los modales
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<number | null>(null)
  const [modalType, setModalType] = useState<'personal' | 'laboral' | 'familiar' | 'academico' | null>(null)

  // Verificar si el usuario es administrador
  const isAdmin = user?.tipo_usuario === 'administrador' || user?.nivel_acceso === 'admin'

  // Cargar empleados
  const loadEmployees = async () => {
    try {
      setLoading(true)
      console.log('🔍 DEBUG: Iniciando carga de empleados')
      console.log('🔍 DEBUG: Usuario actual:', user)
      console.log('🔍 DEBUG: Roles del usuario:', user?.roles || 'No hay roles')
      console.log('🔍 DEBUG: Permisos del usuario:', user?.permissions || 'No hay permisos')
      console.log('🔍 DEBUG: Permisos calculados:', { isAdmin, isRRHH, isSupervisor, isEmployee })
      console.log('🔍 DEBUG: canViewEmployeeList():', canViewEmployeeList())
      console.log('🔍 DEBUG: permissions.canViewAllEmployees:', permissions.canViewAllEmployees)
      
      // Verificar si el usuario puede ver la lista de empleados
      if (!canViewEmployeeList()) {
        console.log('❌ DEBUG: Usuario no tiene permisos para ver la lista de empleados')
        // Si es empleado normal, redirigir a su perfil
        if (isEmployee && currentEmployeeId) {
          // En lugar de mostrar la lista, mostrar solo sus datos
          setAccessDenied(true)
          return
        } else {
          setAccessDenied(true)
          return
        }
      }
      
      const params: Record<string, any> = {
        page: currentPage,
        page_size: itemsPerPage
      }

      if (searchTerm) {
        params.search = searchTerm
      }
      if (selectedArea !== 'todos') {
        params.area = selectedArea
      }
      if (selectedEstado !== 'todos') {
        params.estado = selectedEstado
      }

      console.log('🔍 DEBUG: Parámetros de consulta:', params)
      const data = await employeesService.getAll(params)
      console.log('🔍 DEBUG: Datos recibidos del backend:', data)
      
      // Filtrar empleados según permisos
      const filteredData = filterEmployeesByPermissions(data)
      console.log('🔍 DEBUG: Datos después del filtro:', filteredData)
      
      setEmployees(filteredData)
      console.log('🔍 DEBUG: Estado de empleados actualizado con:', filteredData.length, 'empleados')
      
      // Calcular páginas (esto debería venir del backend)
      setTotalPages(Math.ceil(filteredData.length / itemsPerPage))
    } catch (error) {
      console.error('❌ DEBUG: Error loading employees:', error)
      toast.error('Error al cargar la lista de empleados')
    } finally {
      setLoading(false)
    }
  }

  const filterEmployeesByPermissions = (employeeList: Employee[]): Employee[] => {
    const filter = getEmployeeFilter()
    console.log('🔍 DEBUG: Filtro aplicado:', filter)
    console.log('🔍 DEBUG: Lista original de empleados:', employeeList.length, 'empleados')
    console.log('🔍 DEBUG: currentEmployeeId:', currentEmployeeId)
    
    switch (filter) {
      case 'all':
        console.log('✅ DEBUG: Aplicando filtro "all" - devolviendo todos los empleados')
        return employeeList
      case 'team':
        // TODO: Implementar filtro por equipo cuando tengamos la relación supervisor-empleado
        console.log('✅ DEBUG: Aplicando filtro "team" - devolviendo todos los empleados (temporal)')
        return employeeList
      case 'own':
        const ownEmployees = employeeList.filter(emp => emp.id === currentEmployeeId)
        console.log('✅ DEBUG: Aplicando filtro "own" - devolviendo', ownEmployees.length, 'empleados')
        return ownEmployees
      default:
        console.log('❌ DEBUG: Filtro desconocido - devolviendo array vacío')
        return []
    }
  }

  // Debug de autenticación
  useEffect(() => {
    console.log('=== EMPLEADOS LIST PAGE DEBUG ===');
    console.log('isAuthenticated:', isAuthenticated);
    console.log('authLoading:', authLoading);
    console.log('user:', user);
    console.log('localStorage auth_token:', localStorage.getItem('auth_token'));
    console.log('localStorage user_data:', localStorage.getItem('user_data'));
  }, [isAuthenticated, authLoading, user]);

  // Efectos
  useEffect(() => {
    loadEmployees()
  }, [currentPage, searchTerm, selectedArea, selectedEstado, permissions])

  // Manejar búsqueda
  const handleSearch = (value: string) => {
    setSearchTerm(value)
    setCurrentPage(1)
  }

  // Manejar filtros
  const handleAreaFilter = (value: string) => {
    setSelectedArea(value)
    setCurrentPage(1)
  }

  const handleEstadoFilter = (value: string) => {
    setSelectedEstado(value)
    setCurrentPage(1)
  }

  // Limpiar filtros
  const clearFilters = () => {
    setSearchTerm('')
    setSelectedArea('todos')
    setSelectedEstado('todos')
    setCurrentPage(1)
  }
  
  // Funciones para manejar los modales
  const handleViewEmployee = (employeeId: number, type: 'personal' | 'laboral' | 'familiar' | 'academico') => {
    if (canAccessEmployeeData(employeeId)) {
      setSelectedEmployeeId(employeeId)
      setModalType(type)
    }
  }

  const handleEditEmployee = (employeeId: number, type: 'personal' | 'laboral' | 'familiar' | 'academico') => {
    if (canAccessEmployeeData(employeeId)) {
      setSelectedEmployeeId(employeeId)
      setModalType(type)
    }
  }
  
  const closeModal = () => {
    setSelectedEmployeeId(null)
    setModalType(null)
  }

  // Obtener áreas únicas para el filtro
  const uniqueAreas = Array.from(
    new Set(employees.map(emp => emp.area?.organo).filter(Boolean))
  )

  // Formatear fecha
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('es-ES')
  }

  // Obtener badge de estado
  const getEstadoBadge = (estado?: string) => {
    switch (estado?.toLowerCase()) {
      case 'activo':
        return <Badge variant="default" className="bg-green-100 text-green-800">Activo</Badge>
      case 'inactivo':
        return <Badge variant="secondary">Inactivo</Badge>
      case 'cesado':
        return <Badge variant="destructive">Cesado</Badge>
      default:
        return <Badge variant="outline">Sin estado</Badge>
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  // Mostrar mensaje de acceso denegado para empleados normales
  if (accessDenied) {
    return (
      <div className="container mx-auto p-6">
        <Card className="max-w-md mx-auto">
          <CardHeader className="text-center">
            <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
            <CardTitle>Acceso Restringido</CardTitle>
            <p className="text-muted-foreground">
              {isEmployee 
                ? 'Como empleado, solo puedes acceder a tus datos personales. Contacta a Recursos Humanos si necesitas ver información adicional.'
                : 'No tienes permisos para acceder a la lista de empleados.'}
            </p>
          </CardHeader>
          <CardContent className="text-center">
            <Button 
              onClick={() => window.history.back()}
              variant="outline"
            >
              Volver
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Empleados</h1>
          <p className="text-muted-foreground text-xs sm:text-sm">
            Gestión de empleados y su información
          </p>
        </div>
        {permissions.canCreateEmployee && (
          <Button size="sm" className="w-fit cursor-pointer">
            <Plus className="mr-2 h-4 w-4" />
            Nuevo Empleado
          </Button>
        )}
      </div>

      {/* Estadísticas rápidas - Solo para usuarios con permisos de visualización completa */}
      {permissions.canViewAllEmployees && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Users className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Empleados</p>
                  <p className="text-2xl font-bold">{employees.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Building className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Áreas</p>
                  <p className="text-2xl font-bold">{uniqueAreas.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Activos</p>
                  <p className="text-2xl font-bold">
                    {employees.filter(emp => emp.estado === 'activo').length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filtros y búsqueda */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filtros y Búsqueda
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            {/* Búsqueda */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder={permissions.canViewAllEmployees ? "Buscar por nombre, DNI o email..." : "Buscar en mis datos..."}
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            
            {/* Filtros - Solo para usuarios con permisos completos */}
            {permissions.canViewAllEmployees && (
              <>
                {/* Filtro por área */}
                <Select value={selectedArea} onValueChange={handleAreaFilter}>
                  <SelectTrigger className="w-full md:w-[200px]">
                    <SelectValue placeholder="Filtrar por área" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todos">Todas las áreas</SelectItem>
                    {uniqueAreas.map((area) => (
                      <SelectItem key={area} value={area}>
                        {area}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {/* Filtro por estado */}
                <Select value={selectedEstado} onValueChange={handleEstadoFilter}>
                  <SelectTrigger className="w-full md:w-[200px]">
                    <SelectValue placeholder="Filtrar por estado" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todos">Todos los estados</SelectItem>
                    <SelectItem value="activo">Activo</SelectItem>
                    <SelectItem value="inactivo">Inactivo</SelectItem>
                    <SelectItem value="cesado">Cesado</SelectItem>
                  </SelectContent>
                </Select>
              </>
            )}

            {/* Limpiar filtros */}
            <Button variant="outline" onClick={clearFilters}>
              Limpiar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Tabla de empleados */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Empleados</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Empleado</TableHead>
                  <TableHead>DNI</TableHead>
                  {permissions.canViewAllEmployees && <TableHead>Área</TableHead>}
                  <TableHead>Cargo</TableHead>
                  <TableHead>Estado</TableHead>
                  {permissions.canViewContractData && <TableHead>Fecha Ingreso</TableHead>}
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {employees.length === 0 ? (
                  <TableRow>
                    <TableCell 
                      colSpan={permissions.canViewAllEmployees ? (permissions.canViewContractData ? 7 : 6) : (permissions.canViewContractData ? 6 : 5)} 
                      className="text-center py-8"
                    >
                      <div className="flex flex-col items-center gap-2">
                        <Users className="h-8 w-8 text-muted-foreground" />
                        <p className="text-muted-foreground">
                          {isEmployee ? 'No se encontraron datos' : 'No se encontraron empleados'}
                        </p>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  employees.map((employee) => (
                    <TableRow key={employee.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">
                            {employee.nombres} {employee.ape_paterno} {employee.ape_materno}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {employee.email || 'Sin email'}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell className="font-mono">{employee.dni}</TableCell>
                      {permissions.canViewAllEmployees && (
                        <TableCell>
                          <div>
                            <p className="font-medium">{employee.area?.organo || 'Sin área'}</p>
                            <p className="text-sm text-muted-foreground">
                              {employee.area?.siglas || ''}
                            </p>
                          </div>
                        </TableCell>
                      )}
                      <TableCell>{employee.cargo?.nombre || 'Sin cargo'}</TableCell>
                      <TableCell>{getEstadoBadge(employee.estado)}</TableCell>
                      {permissions.canViewContractData && (
                        <TableCell>{formatDate(employee.fecha_ingreso)}</TableCell>
                      )}
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <span className="sr-only">Abrir menú</span>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Ver datos</DropdownMenuLabel>
                            <DropdownMenuItem onClick={() => handleViewEmployee(employee.id, 'personal')}>
                              <User className="mr-2 h-4 w-4" />
                              Datos personales
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleViewEmployee(employee.id, 'laboral')}>
                              <Briefcase className="mr-2 h-4 w-4" />
                              Datos laborales
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleViewEmployee(employee.id, 'familiar')}>
                              <Heart className="mr-2 h-4 w-4" />
                              Datos familiares
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleViewEmployee(employee.id, 'academico')}>
                              <GraduationCap className="mr-2 h-4 w-4" />
                              Datos académicos
                            </DropdownMenuItem>
                            
                            {permissions.canEditEmployee && (
                              <>
                                <DropdownMenuSeparator />
                                <DropdownMenuLabel>Editar datos</DropdownMenuLabel>
                                <DropdownMenuItem onClick={() => handleEditEmployee(employee.id, 'personal')}>
                                  <Edit className="mr-2 h-4 w-4" />
                                  Editar personales
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleEditEmployee(employee.id, 'laboral')}>
                                  <Edit className="mr-2 h-4 w-4" />
                                  Editar laborales
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleEditEmployee(employee.id, 'familiar')}>
                                  <Edit className="mr-2 h-4 w-4" />
                                  Editar familiares
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleEditEmployee(employee.id, 'academico')}>
                                  <Edit className="mr-2 h-4 w-4" />
                                  Editar académicos
                                </DropdownMenuItem>
                              </>
                            )}
                            
                            {permissions.canDeleteEmployee && (
                              <>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem className="text-destructive">
                                  <Trash2 className="mr-2 h-4 w-4" />
                                  Eliminar empleado
                                </DropdownMenuItem>
                              </>
                            )}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          {/* Paginación */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <p className="text-sm text-muted-foreground">
                Página {currentPage} de {totalPages}
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                >
                  Anterior
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                >
                  Siguiente
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* Modales */}
      {selectedEmployeeId && modalType === 'personal' && (
        <DatosPersonalesModal
          isOpen={true}
          onClose={closeModal}
          employeeId={selectedEmployeeId}
          title="Datos Personales"
        />
      )}
      
      {selectedEmployeeId && modalType === 'laboral' && (
        <DatosLaboralesModal
          isOpen={true}
          onClose={closeModal}
          employeeId={selectedEmployeeId}
          title="Datos Laborales"
        />
      )}
      
      {selectedEmployeeId && modalType === 'familiar' && (
        <DatosFamiliaresModal
          isOpen={true}
          onClose={closeModal}
          employeeId={selectedEmployeeId}
          title="Datos Familiares"
        />
      )}
      
      {selectedEmployeeId && modalType === 'academico' && (
        <DatosAcademicosModal
          isOpen={true}
          onClose={closeModal}
          employeeId={selectedEmployeeId}
          title="Datos Académicos"
        />
      )}
    </div>
  )
}
