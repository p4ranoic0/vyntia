import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Badge } from '@/shared/ui/badge'
import { Avatar, AvatarFallback } from '@/shared/ui/avatar'
import { getInitials } from '@/shared/utils/cn'
import {
  Building,
  Calendar,
  Clock,
  Eye,
  Mail,
  MapPin,
  Settings,
  Shield,
  User,
  Users,
  X
} from 'lucide-react'
import { Separator } from '@/shared/ui/separator'
// import { ScrollArea } from '@/shared/ui/scroll-area' // Componente no disponible
import { toast } from 'sonner'
import { 
  usersService, 
  type User as UserType 
} from '@/features/identity/services/usersService'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'

interface UserDetailsModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  userId: number
}

export function UserDetailsModal({ open, onOpenChange, userId }: UserDetailsModalProps) {
  const [user, setUser] = useState<UserType | null>(null)
  const [loading, setLoading] = useState(false)

  // Cargar datos cuando se abre el modal
  useEffect(() => {
    if (open && userId) {
      loadUserData(userId)
    }
  }, [open, userId])

  const loadUserData = async (userId: number) => {
    try {
      setLoading(true)
      const userData = await usersService.getById(userId)
      setUser(userData.data)
    } catch (error) {
      console.error('Error loading user data:', error)
      toast.error('Error al cargar los datos del usuario')
      onOpenChange(false)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'activo':
        return <Badge className="bg-green-100 text-green-800">Activo</Badge>
      case 'inactivo':
        return <Badge variant="destructive">Inactivo</Badge>
      case 'suspendido':
        return <Badge className="bg-yellow-100 text-yellow-800">Suspendido</Badge>
      default:
        return <Badge variant="outline">{status || 'Sin estado'}</Badge>
    }
  }

  const getTypeBadge = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'administrador':
        return <Badge className="bg-purple-100 text-purple-800">Administrador</Badge>
      case 'empleado':
        return <Badge className="bg-blue-100 text-blue-800">Empleado</Badge>
      case 'supervisor':
        return <Badge className="bg-orange-100 text-orange-800">Supervisor</Badge>
      default:
        return <Badge variant="outline">{type || 'Sin tipo'}</Badge>
    }
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'No disponible'
    try {
      return new Date(dateString).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return 'Fecha inválida'
    }
  }



  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5" />
            Detalles del Usuario
          </DialogTitle>
          <DialogDescription>
            Información completa del usuario y sus datos asociados
          </DialogDescription>
        </DialogHeader>

        {loading ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner />
          </div>
        ) : user ? (
          <div className="max-h-[70vh] overflow-y-auto pr-4">
            <div className="space-y-6">
              {/* Información Principal */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    Información Personal
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-start gap-6">
                    <Avatar className="h-20 w-20">
                      <AvatarFallback className="text-2xl">
                        {getInitials(user.nombres_usuario, user.apellidos_usuario)}
                      </AvatarFallback>
                    </Avatar>
                    
                    <div className="flex-1 space-y-4">
                      <div>
                        <h3 className="text-xl font-semibold">
                          {user.nombres_usuario} {user.apellidos_usuario}
                        </h3>
                        <p className="text-muted-foreground">@{user.username}</p>
                      </div>
                      
                      <div className="flex flex-wrap gap-2">
                        {getStatusBadge(user.estado_usuario)}
                        {getTypeBadge(user.tipo_usuario)}
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="flex items-center gap-2">
                          <Mail className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{user.email || 'No disponible'}</span>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">
                            Creado: {formatDate(user.created_at)}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">
                            Último acceso: {user.ultimo_login_texto || 'Nunca'}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">
                            Días sin login: {user.dias_sin_login || 0}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Información Laboral */}
              {user.empleado_detalle && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Building className="h-5 w-5" />
                      Información Laboral
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Código Empleado</label>
                        <p className="text-sm">{user.empleado_detalle.codigo_empleado || 'No asignado'}</p>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Área</label>
                        <p className="text-sm">{user.empleado_detalle.area_nombre || 'No asignada'}</p>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Cargo</label>
                        <p className="text-sm">{user.empleado_detalle.cargo || 'No asignado'}</p>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Fecha Ingreso</label>
                        <p className="text-sm">{formatDate(user.empleado_detalle.fecha_ingreso)}</p>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Estado Laboral</label>
                        <p className="text-sm">{user.empleado_detalle.estado_laboral || 'No definido'}</p>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Salario</label>
                        <p className="text-sm">
                          {user.empleado_detalle.salario ? 
                            `$${Number(user.empleado_detalle.salario).toLocaleString()}` : 
                            'No definido'
                          }
                        </p>
                      </div>
                    </div>
                    
                    {user.empleado_detalle.observaciones && (
                      <div className="mt-4">
                        <label className="text-sm font-medium text-muted-foreground">Observaciones</label>
                        <p className="text-sm mt-1 p-3 bg-muted/50 rounded-md">
                          {user.empleado_detalle.observaciones}
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Roles Asignados */}
              {user.roles_activos && user.roles_activos.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="h-5 w-5" />
                      Roles Asignados ({user.roles_activos.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {user.roles_activos.map((role) => (
                        <div key={role.id} className="p-3 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium">{role.nombre_rol}</h4>
                            <Badge variant="outline">Nivel {role.nivel_rol}</Badge>
                          </div>
                          {role.descripcion_rol && (
                            <p className="text-sm text-muted-foreground">
                              {role.descripcion_rol}
                            </p>
                          )}
                          <div className="flex items-center gap-2 mt-2">
                            <Shield className="h-3 w-3 text-muted-foreground" />
                            <span className="text-xs text-muted-foreground">
                              Estado: {role.estado_rol}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Información Familiar */}
              {user.familiares && user.familiares.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="h-5 w-5" />
                      Información Familiar ({user.familiares.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {user.familiares.map((familiar, index) => (
                        <div key={index} className="p-3 border rounded-lg">
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                              <label className="text-sm font-medium text-muted-foreground">Nombre</label>
                              <p className="text-sm">{familiar.nombre_familiar || 'No disponible'}</p>
                            </div>
                            
                            <div>
                              <label className="text-sm font-medium text-muted-foreground">Parentesco</label>
                              <p className="text-sm">{familiar.parentesco || 'No definido'}</p>
                            </div>
                            
                            <div>
                              <label className="text-sm font-medium text-muted-foreground">Teléfono</label>
                              <p className="text-sm">{familiar.telefono_familiar || 'No disponible'}</p>
                            </div>
                          </div>
                          
                          {familiar.direccion_familiar && (
                            <div className="mt-2">
                              <label className="text-sm font-medium text-muted-foreground">Dirección</label>
                              <p className="text-sm flex items-center gap-1">
                                <MapPin className="h-3 w-3" />
                                {familiar.direccion_familiar}
                              </p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Información del Sistema */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    Información del Sistema
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">ID Usuario</label>
                      <p className="text-sm font-mono">{user.id}</p>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Fecha Creación</label>
                      <p className="text-sm">{formatDate(user.created_at)}</p>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Última Modificación</label>
                      <p className="text-sm">{formatDate(user.updated_at)}</p>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Último Login</label>
                      <p className="text-sm">{formatDate(user.ultimo_login)}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No se pudieron cargar los datos del usuario
          </div>
        )}

        <div className="flex justify-end pt-4 border-t">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            <X className="mr-2 h-4 w-4" />
            Cerrar
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}