import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { 
  ArrowLeft, 
  User as UserIcon, 
  Mail, 
  Calendar, 
  Shield, 
  Building2, 
  Clock, 
  Edit, 
  Key,
  UserCheck,
  UserX,
  Activity,
  AlertTriangle
} from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'
import { Separator } from '@/shared/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui/tabs'
import { toast } from 'sonner'
import { usersService, type User } from '@/services/usersService'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { UsersLayout } from '@/components/layout/UsersLayout'

export function UsersManagement() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [statistics, setStatistics] = useState<any>(null)

  useEffect(() => {
    if (id) {
      loadUserData(parseInt(id))
      loadStatistics()
    }
  }, [id])

  const loadUserData = async (userId: number) => {
    try {
      setLoading(true)
      const userData = await usersService.getById(userId)
      setUser(userData)
    } catch (error) {
      console.error('Error loading user:', error)
      toast.error('Error al cargar los datos del usuario')
      navigate('/usuarios/listado')
    } finally {
      setLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      const stats = await usersService.getStatistics()
      setStatistics(stats)
    } catch (error) {
      console.error('Error loading statistics:', error)
    }
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusBadge = (user: User) => {
    if (user.is_active) {
      return <Badge variant="success">Activo</Badge>
    } else {
      return <Badge variant="destructive">Inactivo</Badge>
    }
  }

  const getTypeBadge = (type: string) => {
    const typeColors: Record<string, string> = {
      'administrador': 'bg-red-100 text-red-800',
      'supervisor': 'bg-blue-100 text-blue-800',
      'empleado': 'bg-green-100 text-green-800',
      'invitado': 'bg-gray-100 text-gray-800'
    }

    return (
      <Badge className={typeColors[type] || 'bg-gray-100 text-gray-800'}>
        {type?.charAt(0).toUpperCase() + type?.slice(1) || 'N/A'}
      </Badge>
    )
  }

  const getAccessLevelBadge = (level: string) => {
    const levelColors: Record<string, string> = {
      'alto': 'bg-red-100 text-red-800',
      'medio': 'bg-yellow-100 text-yellow-800',
      'basico': 'bg-green-100 text-green-800'
    }

    return (
      <Badge className={levelColors[level] || 'bg-gray-100 text-gray-800'}>
        {level?.charAt(0).toUpperCase() + level?.slice(1) || 'N/A'}
      </Badge>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!user) {
    return (
      <div className="text-center py-8">
        <h3 className="text-lg font-semibold mb-2">Usuario no encontrado</h3>
        <p className="text-muted-foreground mb-4">
          El usuario que buscas no existe o ha sido eliminado.
        </p>
        <Button onClick={() => navigate('/usuarios/listado')}>Volver al listado</Button>
      </div>
    )
  }

  return (
    <UsersLayout 
      title="Gestión de Usuario"
      description="Información detallada y administración del usuario seleccionado"
    >
      {/* Header Actions */}
      <div className="flex items-center justify-between mb-6">
        <Button variant="outline" onClick={() => navigate('/usuarios/listado')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver al Listado
        </Button>
        <div className="flex items-center space-x-2">
          <Button variant="outline" asChild>
            <Link to={`/usuarios/editar/${user.id}`}>
              <Edit className="w-4 h-4 mr-2" />
              Editar
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to={`/usuarios/cambiar-password/${user.id}`}>
              <Key className="w-4 h-4 mr-2" />
              Cambiar Contraseña
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to={`/usuarios/roles/${user.id}`}>
              <Shield className="w-4 h-4 mr-2" />
              Gestionar Roles
            </Link>
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Información General</TabsTrigger>
          <TabsTrigger value="roles">Roles y Permisos</TabsTrigger>
          <TabsTrigger value="activity">Actividad</TabsTrigger>
          <TabsTrigger value="statistics">Estadísticas</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Información básica */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <UserIcon className="w-5 h-5" />
                  Información Personal
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Nombres</p>
                    <p className="text-sm">{user.nombres_usuario || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Apellidos</p>
                    <p className="text-sm">{user.apellidos_usuario || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Usuario</p>
                    <p className="text-sm font-mono">@{user.username}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Email</p>
                    <p className="text-sm">{user.email || 'N/A'}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Configuración de Cuenta
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Tipo de Usuario</p>
                    <div className="mt-1">{getTypeBadge(user.tipo_usuario)}</div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Nivel de Acceso</p>
                    <div className="mt-1">{getAccessLevelBadge(user.nivel_acceso)}</div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Estado</p>
                    <div className="mt-1">{getStatusBadge(user)}</div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">ID Usuario</p>
                    <p className="text-sm font-mono">{user.id}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Información laboral */}
          {user.empleado && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="w-5 h-5" />
                  Información Laboral
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Empleado</p>
                    <p className="text-sm">
                      {user.empleado.nombres} {user.empleado.ape_paterno} {user.empleado.ape_materno}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">DNI</p>
                    <p className="text-sm font-mono">{user.empleado.dni}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Área</p>
                    <p className="text-sm">{user.empleado.area?.organo || 'N/A'}</p>
                    <p className="text-xs text-muted-foreground">{user.empleado.area?.siglas || ''}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Fechas importantes */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Fechas Importantes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Fecha de Registro</p>
                  <p className="text-sm">{formatDate(user.date_joined)}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Último Acceso</p>
                  <p className="text-sm">{formatDate(user.last_login || '')}</p>
                  {user.dias_sin_login !== undefined && (
                    <p className="text-xs text-muted-foreground">
                      Hace {user.dias_sin_login} días
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="roles" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Roles Asignados
              </CardTitle>
              <CardDescription>
                Roles y permisos activos del usuario
              </CardDescription>
            </CardHeader>
            <CardContent>
              {user.roles_activos && user.roles_activos.length > 0 ? (
                <div className="space-y-4">
                  {user.roles_activos.map((role) => (
                    <div key={role.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{role.nombre_rol}</h4>
                        <Badge variant="outline">Activo</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">
                        {role.descripcion_rol || 'Sin descripción'}
                      </p>
                      {role.permisos && role.permisos.length > 0 && (
                        <div>
                          <p className="text-sm font-medium mb-2">Permisos:</p>
                          <div className="flex flex-wrap gap-2">
                            {role.permisos.map((permiso) => (
                              <Badge key={permiso.id} variant="secondary" className="text-xs">
                                {permiso.nombre_permiso}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Shield className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Sin roles asignados</h3>
                  <p className="text-muted-foreground mb-4">
                    Este usuario no tiene roles asignados actualmente.
                  </p>
                  <Link to={`/usuarios/roles/${user.id}`}>
                    <Button>
                      <Shield className="w-4 h-4 mr-2" />
                      Asignar Roles
                    </Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Actividad del Usuario
              </CardTitle>
              <CardDescription>
                Historial de accesos y actividad reciente
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <Clock className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                    <p className="text-2xl font-bold">{user.dias_sin_login || 0}</p>
                    <p className="text-sm text-muted-foreground">Días sin acceso</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <UserCheck className="w-8 h-8 text-green-600 mx-auto mb-2" />
                    <p className="text-2xl font-bold">{user.is_active ? 'Sí' : 'No'}</p>
                    <p className="text-sm text-muted-foreground">Usuario activo</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <Calendar className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                    <p className="text-sm font-bold">{formatDate(user.last_login || '')}</p>
                    <p className="text-sm text-muted-foreground">Último acceso</p>
                  </div>
                </div>

                {user.dias_sin_login && user.dias_sin_login > 30 && (
                  <div className="flex items-center gap-2 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <AlertTriangle className="w-5 h-5 text-yellow-600" />
                    <div>
                      <p className="text-sm font-medium text-yellow-800">
                        Usuario inactivo por más de 30 días
                      </p>
                      <p className="text-sm text-yellow-700">
                        Considera revisar si el usuario sigue siendo necesario en el sistema.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="statistics" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Estadísticas del Sistema
              </CardTitle>
              <CardDescription>
                Métricas generales del sistema de usuarios
              </CardDescription>
            </CardHeader>
            <CardContent>
              {statistics ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <Users className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                    <p className="text-2xl font-bold">{statistics.total_usuarios || 0}</p>
                    <p className="text-sm text-muted-foreground">Total usuarios</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <UserCheck className="w-8 h-8 text-green-600 mx-auto mb-2" />
                    <p className="text-2xl font-bold">{statistics.usuarios_activos || 0}</p>
                    <p className="text-sm text-muted-foreground">Usuarios activos</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <UserX className="w-8 h-8 text-red-600 mx-auto mb-2" />
                    <p className="text-2xl font-bold">{statistics.usuarios_inactivos || 0}</p>
                    <p className="text-sm text-muted-foreground">Usuarios inactivos</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <Clock className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
                    <p className="text-2xl font-bold">{statistics.sin_login_reciente || 0}</p>
                    <p className="text-sm text-muted-foreground">Sin acceso reciente</p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <LoadingSpinner size="lg" />
                  <p className="text-muted-foreground mt-4">Cargando estadísticas...</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </UsersLayout>
  )
}

export default UsersManagement