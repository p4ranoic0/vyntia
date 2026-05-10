import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Users,
  Calendar,
  Shield,
  Building2,
  UserCheck,
  BarChart3,
  TrendingUp,
  AlertTriangle,
  Clock,
  Activity,
  Key,
  Lock,
  UserCog
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import { Progress } from '@/shared/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui/tabs'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'

// Interfaces para los datos del dashboard
interface DashboardStats {
  totalEmpleados: number
  empleadosActivos: number
  totalUsuarios: number
  usuariosActivos: number
  totalAreas: number
  solicitudesPendientes: number
  vacacionesPorVencer: number
  rolesActivos: number
  totalPermisos: number
  permisosActivos: number
  rolesConPermisos: number
}

interface QuickAction {
  title: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  href: string
  color: string
  count?: number
}

interface RecentActivity {
  id: string
  type: 'empleado' | 'usuario' | 'vacacion' | 'area'
  description: string
  timestamp: string
  user: string
}

export function AdminDashboard() {
  useAuth()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<DashboardStats>({
    totalEmpleados: 0,
    empleadosActivos: 0,
    totalUsuarios: 0,
    usuariosActivos: 0,
    totalAreas: 0,
    solicitudesPendientes: 0,
    vacacionesPorVencer: 0,
    rolesActivos: 0
  })

  // Datos de ejemplo - en producción vendrían del backend
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        // Simular carga de datos
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        setStats({
          totalEmpleados: 156,
          empleadosActivos: 142,
          totalUsuarios: 89,
          usuariosActivos: 76,
          totalAreas: 12,
          solicitudesPendientes: 8,
          vacacionesPorVencer: 23,
          rolesActivos: 6,
          totalPermisos: 45,
          permisosActivos: 42,
          rolesConPermisos: 5
        })
      } catch (error) {
        console.error('Error loading dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  // Acciones rápidas del dashboard
  const quickActions: QuickAction[] = [
    {
      title: 'Gestión de Empleados',
      description: 'Administrar información de empleados',
      icon: Users,
      href: '/empleados',
      color: 'bg-blue-500',
      count: stats.totalEmpleados
    },
    {
      title: 'Gestión de Usuarios',
      description: 'Administrar usuarios del sistema',
      icon: UserCheck,
      href: '/usuarios',
      color: 'bg-green-500',
      count: stats.totalUsuarios
    },
    {
      title: 'Gestión de Vacaciones',
      description: 'Administrar solicitudes y períodos',
      icon: Calendar,
      href: '/vacaciones',
      color: 'bg-purple-500',
      count: stats.solicitudesPendientes
    },
    {
      title: 'Gestión de Roles',
      description: 'Administrar roles y permisos',
      icon: Shield,
      href: '/seguridad/roles',
      color: 'bg-orange-500',
      count: stats.rolesActivos
    },
    {
      title: 'Gestión de Áreas',
      description: 'Administrar áreas organizacionales',
      icon: Building2,
      href: '/areas/listado',
      color: 'bg-teal-500',
      count: stats.totalAreas
    },
    {
      title: 'Gestión de Permisos',
      description: 'Administrar permisos del sistema',
      icon: Key,
      href: '/seguridad/permisos',
      color: 'bg-red-500',
      count: stats.totalPermisos
    },
    {
      title: 'Asignar Permisos a Roles',
      description: 'Configurar permisos por rol',
      icon: UserCog,
      href: '/seguridad/roles-permisos',
      color: 'bg-pink-500',
      count: stats.rolesConPermisos
    },
    {
      title: 'Reportes y Estadísticas',
      description: 'Ver reportes del sistema',
      icon: BarChart3,
      href: '/reportes',
      color: 'bg-indigo-500'
    }
  ]

  // Actividad reciente de ejemplo
  const recentActivity: RecentActivity[] = [
    {
      id: '1',
      type: 'empleado',
      description: 'Nuevo empleado registrado: Juan Pérez',
      timestamp: '2024-01-15 10:30',
      user: 'Admin RRHH'
    },
    {
      id: '2',
      type: 'vacacion',
      description: 'Solicitud de vacaciones aprobada para María García',
      timestamp: '2024-01-15 09:15',
      user: 'Jefe de Área'
    },
    {
      id: '3',
      type: 'usuario',
      description: 'Usuario Carlos López activado',
      timestamp: '2024-01-15 08:45',
      user: 'Admin Sistema'
    },
    {
      id: '4',
      type: 'area',
      description: 'Nueva área creada: Desarrollo de Software',
      timestamp: '2024-01-14 16:20',
      user: 'Admin RRHH'
    }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Panel de Administración</h1>
          <p className="text-muted-foreground">
            Gestión centralizada del sistema de recursos humanos
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-sm">
            <Activity className="w-3 h-3 mr-1" />
            Sistema Activo
          </Badge>
        </div>
      </div>

      {/* Estadísticas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Empleados</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalEmpleados}</div>
            <p className="text-xs text-muted-foreground">
              {stats.empleadosActivos} activos
            </p>
            <Progress 
              value={(stats.empleadosActivos / stats.totalEmpleados) * 100} 
              className="mt-2" 
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Usuarios Sistema</CardTitle>
            <UserCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalUsuarios}</div>
            <p className="text-xs text-muted-foreground">
              {stats.usuariosActivos} activos
            </p>
            <Progress 
              value={(stats.usuariosActivos / stats.totalUsuarios) * 100} 
              className="mt-2" 
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Solicitudes Pendientes</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.solicitudesPendientes}</div>
            <p className="text-xs text-muted-foreground">
              Requieren atención
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vacaciones por Vencer</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.vacacionesPorVencer}</div>
            <p className="text-xs text-muted-foreground">
              Próximas a vencer
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Estadísticas de seguridad y permisos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Permisos del Sistema</CardTitle>
            <Key className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalPermisos}</div>
            <p className="text-xs text-muted-foreground">
              {stats.permisosActivos} activos
            </p>
            <Progress 
              value={(stats.permisosActivos / stats.totalPermisos) * 100} 
              className="mt-2" 
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Roles con Permisos</CardTitle>
            <Lock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.rolesConPermisos}</div>
            <p className="text-xs text-muted-foreground">
              de {stats.rolesActivos} roles totales
            </p>
            <Progress 
              value={(stats.rolesConPermisos / stats.rolesActivos) * 100} 
              className="mt-2" 
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Configuración de Seguridad</CardTitle>
            <UserCog className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">Óptima</div>
            <p className="text-xs text-muted-foreground">
              Todos los roles configurados
            </p>
            <div className="mt-2 flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs text-green-600">Sistema seguro</span>
            </div>
            <div className="mt-3 pt-2 border-t">
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full"
                asChild
              >
                <Link to="/seguridad/roles-permisos">
                  <UserCog className="h-4 w-4 mr-2" />
                  Asignar Permisos
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Contenido principal con tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Vista General</TabsTrigger>
          <TabsTrigger value="actions">Acciones Rápidas</TabsTrigger>
          <TabsTrigger value="activity">Actividad Reciente</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Resumen por módulos */}
            <Card>
              <CardHeader>
                <CardTitle>Resumen por Módulos</CardTitle>
                <CardDescription>
                  Estado actual de cada módulo del sistema
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-blue-500" />
                    <span className="text-sm font-medium">Empleados</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">{stats.empleadosActivos}/{stats.totalEmpleados}</div>
                    <div className="text-xs text-muted-foreground">Activos</div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Building2 className="h-4 w-4 text-teal-500" />
                    <span className="text-sm font-medium">Áreas</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">{stats.totalAreas}</div>
                    <div className="text-xs text-muted-foreground">Registradas</div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4 text-orange-500" />
                    <span className="text-sm font-medium">Roles</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">{stats.rolesActivos}</div>
                    <div className="text-xs text-muted-foreground">Activos</div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-purple-500" />
                    <span className="text-sm font-medium">Vacaciones</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">{stats.solicitudesPendientes}</div>
                    <div className="text-xs text-muted-foreground">Pendientes</div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Key className="h-4 w-4 text-red-500" />
                    <span className="text-sm font-medium">Permisos</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">{stats.permisosActivos}/{stats.totalPermisos}</div>
                    <div className="text-xs text-muted-foreground">Activos</div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <UserCog className="h-4 w-4 text-pink-500" />
                    <span className="text-sm font-medium">Roles-Permisos</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">{stats.rolesConPermisos}</div>
                    <div className="text-xs text-muted-foreground">Configurados</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Alertas y notificaciones */}
            <Card>
              <CardHeader>
                <CardTitle>Alertas del Sistema</CardTitle>
                <CardDescription>
                  Elementos que requieren atención inmediata
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {stats.solicitudesPendientes > 0 && (
                  <div className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg border border-orange-200">
                    <Clock className="h-4 w-4 text-orange-600" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-orange-800">
                        {stats.solicitudesPendientes} solicitudes pendientes
                      </p>
                      <p className="text-xs text-orange-600">
                        Requieren revisión y aprobación
                      </p>
                    </div>
                    <Button size="sm" variant="outline" asChild>
                      <Link to="/vacaciones/solicitudes">Ver</Link>
                    </Button>
                  </div>
                )}

                {stats.vacacionesPorVencer > 0 && (
                  <div className="flex items-center gap-3 p-3 bg-red-50 rounded-lg border border-red-200">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-red-800">
                        {stats.vacacionesPorVencer} vacaciones por vencer
                      </p>
                      <p className="text-xs text-red-600">
                        Próximas a vencer en los próximos 90 días
                      </p>
                    </div>
                    <Button size="sm" variant="outline" asChild>
                      <Link to="/vacaciones/reportes">Ver</Link>
                    </Button>
                  </div>
                )}

                <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-green-800">
                      Sistema funcionando correctamente
                    </p>
                    <p className="text-xs text-green-600">
                      Todos los servicios están operativos
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="actions" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quickActions.map((action, index) => {
              const IconComponent = action.icon
              return (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${action.color} text-white`}>
                        <IconComponent className="h-5 w-5" />
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-base">{action.title}</CardTitle>
                        {action.count !== undefined && (
                          <Badge variant="secondary" className="text-xs">
                            {action.count}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <CardDescription className="mb-3">
                      {action.description}
                    </CardDescription>
                    <Button asChild className="w-full">
                      <Link to={action.href}>Acceder</Link>
                    </Button>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Actividad Reciente</CardTitle>
              <CardDescription>
                Últimas acciones realizadas en el sistema
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivity.map((activity) => {
                  const getActivityIcon = (type: string) => {
                    switch (type) {
                      case 'empleado': return <Users className="h-4 w-4 text-blue-500" />
                      case 'usuario': return <UserCheck className="h-4 w-4 text-green-500" />
                      case 'vacacion': return <Calendar className="h-4 w-4 text-purple-500" />
                      case 'area': return <Building2 className="h-4 w-4 text-teal-500" />
                      default: return <Activity className="h-4 w-4 text-gray-500" />
                    }
                  }

                  return (
                    <div key={activity.id} className="flex items-center gap-3 p-3 border rounded-lg">
                      {getActivityIcon(activity.type)}
                      <div className="flex-1">
                        <p className="text-sm font-medium">{activity.description}</p>
                        <p className="text-xs text-muted-foreground">
                          {activity.timestamp} • {activity.user}
                        </p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default AdminDashboard