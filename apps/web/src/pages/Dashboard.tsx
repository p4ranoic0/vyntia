import { LoadingSpinner, Skeleton, useLoading, useLoadingWithDelay } from '@/shared/components'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { Building2, Calendar, CalendarDays, FileText, FolderOpen, Landmark, Shield, User, Users } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

// =============================================
// Dashboard para USUARIO NORMAL (personal)
// =============================================
function UserDashboard() {
  const { user } = useAuth()
  const { isLoading } = useLoadingWithDelay(800)

  const employeeName = user?.empleado
    ? `${user.empleado.nombres || ''} ${user.empleado.apellido_paterno || ''}`.trim()
    : user?.username || 'Usuario'

  const quickLinks = [
    {
      title: 'Mis Datos Personales',
      description: 'Ver y actualizar tu informacion personal',
      icon: User,
      href: '/empleados/datos-personales',
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20',
    },
    {
      title: 'Mi Legajo',
      description: 'Consulta tu legajo digital',
      icon: FolderOpen,
      href: '/legajo',
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
    },
    {
      title: 'Solicitar Vacaciones',
      description: 'Crear una nueva solicitud de vacaciones',
      icon: CalendarDays,
      href: '/vacaciones/nueva-solicitud',
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900/20',
    },
    {
      title: 'Mis Solicitudes',
      description: 'Ver el estado de tus solicitudes',
      icon: Calendar,
      href: '/vacaciones/solicitudes',
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/20',
    },
  ]

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-5 w-96" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {['datos', 'legajo', 'vacaciones', 'solicitudes'].map((key) => (
            <Card key={key}>
              <CardHeader><Skeleton className="h-4 w-32" /></CardHeader>
              <CardContent><Skeleton className="h-8 w-20" /></CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
          Bienvenido, {employeeName}
        </h1>
        <p className="text-muted-foreground">
          Portal del empleado - Accede a tu informacion y servicios
        </p>
      </div>

      {/* Accesos rapidos */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {quickLinks.map((link) => {
          const Icon = link.icon
          return (
            <Card key={link.title} className="hover:shadow-md transition-shadow animate-fade-in-up">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{link.title}</CardTitle>
                <div className={`p-2 rounded-lg ${link.bgColor}`}>
                  <Icon className={`h-4 w-4 ${link.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground mb-3">{link.description}</p>
                <Button asChild variant="outline" size="sm" className="w-full">
                  <Link to={link.href}>Acceder</Link>
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Informacion adicional */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Mis Datos</CardTitle>
            <CardDescription>Acceso rapido a tu informacion</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {[
              { label: 'Datos Personales', href: '/empleados/datos-personales' },
              { label: 'Datos Laborales', href: '/empleados/datos-laborales' },
              { label: 'Formacion Academica', href: '/empleados/datos-academicos' },
              { label: 'Datos Familiares', href: '/empleados/datos-familiares' },
            ].map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className="flex items-center p-2 rounded-lg hover:bg-accent transition-colors duration-200 text-sm cursor-pointer"
              >
                <FileText className="w-4 h-4 mr-2 text-muted-foreground" />
                {item.label}
              </Link>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Vacaciones</CardTitle>
            <CardDescription>Gestion de tus vacaciones</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link
              to="/vacaciones/nueva-solicitud"
              className="flex items-center p-2 rounded-lg hover:bg-accent transition-colors duration-200 text-sm cursor-pointer"
            >
              <CalendarDays className="w-4 h-4 mr-2 text-muted-foreground" />
              Nueva Solicitud
            </Link>
            <Link
              to="/vacaciones/solicitudes"
              className="flex items-center p-2 rounded-lg hover:bg-accent transition-colors duration-200 text-sm cursor-pointer"
            >
              <Calendar className="w-4 h-4 mr-2 text-muted-foreground" />
              Mis Solicitudes
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// =============================================
// Dashboard para ADMINISTRADOR / RRHH
// =============================================
function AdminDashboardView() {
  const { isLoading: isLoadingStats, stopLoading: stopStatsLoading } = useLoading(true)
  const { isLoading: isLoadingActivity } = useLoadingWithDelay(2000)
  const [isLoadingQuickActions, setIsLoadingQuickActions] = useState(true)

  const stats = [
    {
      title: 'Total Empleados',
      value: '245',
      description: '+12% respecto al mes anterior',
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/20',
      accentBorder: 'border-t-blue-500',
    },
    {
      title: 'Areas Activas',
      value: '18',
      description: '3 nuevas areas este mes',
      icon: Building2,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/20',
      accentBorder: 'border-t-green-500',
    },
    {
      title: 'Boletas Procesadas',
      value: '1,234',
      description: 'Este mes',
      icon: FileText,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900/20',
      accentBorder: 'border-t-orange-500',
    },
    {
      title: 'Usuarios Activos',
      value: '89',
      description: 'Con diferentes roles',
      icon: Shield,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/20',
      accentBorder: 'border-t-purple-500',
    },
    {
      title: 'Conceptos Remuneración',
      value: '32',
      description: 'AFP, ingresos y descuentos',
      icon: Landmark,
      color: 'text-cyan-700',
      bgColor: 'bg-cyan-100 dark:bg-cyan-900/20',
      accentBorder: 'border-t-cyan-600',
    },
  ]

  useEffect(() => {
    const timer = setTimeout(() => { stopStatsLoading() }, 1500)
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => { setIsLoadingQuickActions(false) }, 3000)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Resumen general del sistema de recursos humanos
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
        {isLoadingStats ? (
          ['s1', 's2', 's3', 's4', 's5'].map((skeletonKey) => (
            <Card key={skeletonKey}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-8 w-8 rounded-lg" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-16 mb-2" />
                <Skeleton className="h-3 w-32" />
              </CardContent>
            </Card>
          ))
        ) : (
          stats.map((stat) => {
            const Icon = stat.icon
            return (
              <Card key={stat.title} className={`animate-fade-in-up border-t-2 ${stat.accentBorder} hover:shadow-md transition-shadow duration-200`}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                  <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                    <Icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <p className="text-xs text-muted-foreground">{stat.description}</p>
                </CardContent>
              </Card>
            )
          })
        )}
      </div>

      {/* Recent Activity + Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="md:col-span-4">
          <CardHeader>
            <CardTitle>Actividad Reciente</CardTitle>
            <CardDescription>Ultimas acciones realizadas en el sistema</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingActivity ? (
              <div className="space-y-4">
                <div className="flex items-center justify-center py-8">
                  <LoadingSpinner size="md" variant="pulse" color="primary" text="Cargando actividad reciente..." />
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {[
                  { action: 'Nuevo empleado registrado', details: 'Juan Perez - Area de Desarrollo', time: 'Hace 2 horas' },
                  { action: 'Boleta procesada', details: 'Nomina de Octubre 2024', time: 'Hace 4 horas' },
                  { action: 'Usuario actualizado', details: 'Maria Gonzalez - Permisos modificados', time: 'Hace 1 dia' },
                  { action: 'Nueva area creada', details: 'Area de Marketing Digital', time: 'Hace 2 dias' },
                ].map((activity, index) => (
                  <div key={activity.action} className="flex items-start space-x-4 animate-fade-in-up" style={{ animationDelay: `${index * 100}ms` }}>
                    <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{activity.action}</p>
                      <p className="text-xs text-muted-foreground">{activity.details}</p>
                      <p className="text-xs text-muted-foreground mt-1">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-3">
          <CardHeader>
            <CardTitle>Accesos Rapidos</CardTitle>
            <CardDescription>Modulos de administracion</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingQuickActions ? (
              <div className="space-y-3">
                {['q1', 'q2', 'q3', 'q4'].map((skeletonKey) => (
                  <div key={skeletonKey} className="flex items-center p-3 rounded-lg border">
                    <Skeleton className="w-5 h-5 mr-3 rounded" />
                    <Skeleton className="h-4 flex-1" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid gap-2">
                {[
                  { title: 'Gestion de Empleados', icon: Users, href: '/empleados' },
                  { title: 'Módulo de Remuneraciones', icon: Landmark, href: '/remuneraciones' },
                  { title: 'Gestion de Usuarios', icon: Shield, href: '/usuarios/listado' },
                  { title: 'Gestion de Areas', icon: Building2, href: '/areas/listado' },
                  { title: 'Panel de Administracion', icon: FileText, href: '/admin' },
                ].map((item, index) => {
                  const Icon = item.icon
                  return (
                    <Link
                      key={item.href}
                      to={item.href}
                      className="flex items-center p-3 rounded-lg border hover:bg-accent hover:border-primary/20 cursor-pointer transition-colors duration-200 animate-fade-in-up"
                      style={{ animationDelay: `${index * 150}ms` }}
                    >
                      <Icon className="w-5 h-5 mr-3 text-primary" />
                      <span className="text-sm font-medium">{item.title}</span>
                    </Link>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// =============================================
// Dashboard Principal (detecta el rol)
// =============================================
export function Dashboard() {
  const { isAdminOrRRHH } = useAuth()

  if (isAdminOrRRHH()) {
    return <AdminDashboardView />
  }

  return <UserDashboard />
}
