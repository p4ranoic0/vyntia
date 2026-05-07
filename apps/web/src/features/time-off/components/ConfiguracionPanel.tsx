import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Switch } from '@/shared/ui/switch'
import { Textarea } from '@/shared/ui/textarea'
import { Badge } from '@/shared/ui/badge'
import { Alert, AlertDescription } from '@/shared/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui/tabs'
import { Separator } from '@/shared/ui/separator'
import { Settings, Save, RefreshCw, AlertTriangle, CheckCircle, Calendar, Users, Clock } from 'lucide-react'
import { useToast } from '@/shared/hooks/use-toast'
import timeOffService, { ConfiguracionVacaciones } from '@/features/time-off/services/timeOffService'

interface ConfiguracionPanelProps {
  onConfiguracionUpdated?: () => void
}

const ConfiguracionPanel: React.FC<ConfiguracionPanelProps> = ({ onConfiguracionUpdated }) => {
  const { toast } = useToast()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [configuracion, setConfiguracion] = useState<ConfiguracionVacaciones | null>(null)
  
  // Formulario de configuración
  const [formData, setFormData] = useState({
    dias_vacaciones_anuales: 15,
    dias_maximos_acumulables: 30,
    dias_minimos_solicitud: 1,
    dias_maximos_solicitud: 15,
    dias_anticipacion_minima: 7,
    permite_fraccionamiento: true,
    dias_minimos_fraccionamiento: 1,
    requiere_aprobacion_jefe: true,
    requiere_aprobacion_rrhh: true,
    notificar_vencimiento_dias: 30,
    auto_aprobar_solicitudes: false,
    permitir_solicitudes_retroactivas: false,
    dias_retroactivos_permitidos: 0,
    mensaje_politicas: '',
    activo: true
  })

  // Cargar configuración actual
  useEffect(() => {
    cargarConfiguracion()
  }, [])

  const cargarConfiguracion = async () => {
    try {
      setLoading(true)
      const configuraciones = await timeOffService.getConfiguraciones()
      
      // Buscar configuración general activa
      const config = configuraciones?.find(c =>
        c.tipo_configuracion === 'general' &&
        c.is_active
      )
      
      if (config) {
        setConfiguracion(config)
        setFormData({
          dias_vacaciones_anuales: config.dias_por_ano || 15,
          dias_maximos_acumulables: config.max_dias_acumulables || 30,
          dias_minimos_solicitud: config.dias_minimos_solicitud || 1,
          dias_maximos_solicitud: config.dias_maximos_solicitud || 15,
          dias_anticipacion_minima: config.dias_anticipacion_minima || 7,
          permite_fraccionamiento: config.permite_fraccionamiento ?? true,
          dias_minimos_fraccionamiento: config.min_dias_por_fraccion || 1,
          requiere_aprobacion_jefe: config.requiere_aprobacion_jefe ?? true,
          requiere_aprobacion_rrhh: config.requiere_aprobacion_rrhh ?? true,
          notificar_vencimiento_dias: 30, // Campo no existe en el modelo
          auto_aprobar_solicitudes: false, // Campo no existe en el modelo
          permitir_solicitudes_retroactivas: false, // Campo no existe en el modelo
          dias_retroactivos_permitidos: 0, // Campo no existe en el modelo
          mensaje_politicas: config.observaciones || '',
          activo: config.is_active ?? true
        })
      }
    } catch (error) {
      console.error('Error al cargar configuración:', error)
      toast({
        title: 'Error',
        description: 'No se pudo cargar la configuración',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setSaving(true)
      
      // Mapear los datos del formulario a los nombres de campos del modelo
      const configData = {
        tipo_configuracion: 'general',
        dias_por_ano: formData.dias_vacaciones_anuales,
        max_dias_acumulables: formData.dias_maximos_acumulables,
        dias_minimos_solicitud: formData.dias_minimos_solicitud,
        dias_maximos_solicitud: formData.dias_maximos_solicitud,
        dias_anticipacion_minima: formData.dias_anticipacion_minima,
        permite_fraccionamiento: formData.permite_fraccionamiento,
        min_dias_por_fraccion: formData.dias_minimos_fraccionamiento,
        requiere_aprobacion_jefe: formData.requiere_aprobacion_jefe,
        requiere_aprobacion_rrhh: formData.requiere_aprobacion_rrhh,
        observaciones: formData.mensaje_politicas,
        is_active: formData.activo
      }
      
      if (configuracion) {
        await timeOffService.updateConfiguracion(configuracion.id, configData)
        toast({
          title: 'Éxito',
          description: 'Configuración actualizada correctamente'
        })
      } else {
        await timeOffService.createConfiguracion(configData)
        toast({
          title: 'Éxito',
          description: 'Configuración creada correctamente'
        })
      }
      
      cargarConfiguracion()
      onConfiguracionUpdated?.()
    } catch (error) {
      console.error('Error al guardar configuración:', error)
      toast({
        title: 'Error',
        description: 'No se pudo guardar la configuración',
        variant: 'destructive'
      })
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    if (configuracion) {
      setFormData({
        dias_vacaciones_anuales: configuracion.dias_por_ano || 15,
        dias_maximos_acumulables: configuracion.max_dias_acumulables || 30,
        dias_minimos_solicitud: configuracion.dias_minimos_solicitud || 1,
        dias_maximos_solicitud: configuracion.dias_maximos_solicitud || 15,
        dias_anticipacion_minima: configuracion.dias_anticipacion_minima || 7,
        permite_fraccionamiento: configuracion.permite_fraccionamiento ?? true,
        dias_minimos_fraccionamiento: configuracion.min_dias_por_fraccion || 1,
        requiere_aprobacion_jefe: configuracion.requiere_aprobacion_jefe ?? true,
        requiere_aprobacion_rrhh: configuracion.requiere_aprobacion_rrhh ?? true,
        notificar_vencimiento_dias: 30, // Campo no existe en el modelo
        auto_aprobar_solicitudes: false, // Campo no existe en el modelo
        permitir_solicitudes_retroactivas: false, // Campo no existe en el modelo
        dias_retroactivos_permitidos: 0, // Campo no existe en el modelo
        mensaje_politicas: configuracion.observaciones || '',
        activo: configuracion.is_active ?? true
      })
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando configuración...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Estado de la configuración */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Settings className="h-5 w-5" />
              <CardTitle>Estado de la Configuración</CardTitle>
            </div>
            {configuracion ? (
              <Badge variant={configuracion.is_active ? 'default' : 'secondary'}>
                <CheckCircle className="mr-1 h-3 w-3" />
                {configuracion.is_active ? 'Activa' : 'Inactiva'}
              </Badge>
            ) : (
              <Badge variant="destructive">
                <AlertTriangle className="mr-1 h-3 w-3" />
                Sin Configurar
              </Badge>
            )}
          </div>
        </CardHeader>
        
        {!configuracion && (
          <CardContent>
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                No hay una configuración activa. Configure las políticas de vacaciones para habilitar el módulo.
              </AlertDescription>
            </Alert>
          </CardContent>
        )}
      </Card>

      {/* Formulario de configuración */}
      <form onSubmit={handleSubmit}>
        <Tabs defaultValue="general" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="solicitudes">Solicitudes</TabsTrigger>
            <TabsTrigger value="aprobaciones">Aprobaciones</TabsTrigger>
            <TabsTrigger value="notificaciones">Notificaciones</TabsTrigger>
          </TabsList>

          {/* Configuración General */}
          <TabsContent value="general">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5" />
                  <span>Configuración General</span>
                </CardTitle>
                <CardDescription>
                  Configure los parámetros básicos del sistema de vacaciones
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="dias_vacaciones_anuales">Días de Vacaciones Anuales</Label>
                    <Input
                      id="dias_vacaciones_anuales"
                      type="number"
                      value={formData.dias_vacaciones_anuales}
                      onChange={(e) => setFormData({ ...formData, dias_vacaciones_anuales: parseInt(e.target.value) })}
                      min={1}
                      max={30}
                      required
                    />
                    <p className="text-sm text-muted-foreground mt-1">
                      Días de vacaciones asignados por año
                    </p>
                  </div>
                  
                  <div>
                    <Label htmlFor="dias_maximos_acumulables">Días Máximos Acumulables</Label>
                    <Input
                      id="dias_maximos_acumulables"
                      type="number"
                      value={formData.dias_maximos_acumulables}
                      onChange={(e) => setFormData({ ...formData, dias_maximos_acumulables: parseInt(e.target.value) })}
                      min={formData.dias_vacaciones_anuales}
                      max={60}
                      required
                    />
                    <p className="text-sm text-muted-foreground mt-1">
                      Máximo de días que se pueden acumular
                    </p>
                  </div>
                </div>
                
                <Separator />
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Estado de la Configuración</Label>
                    <p className="text-sm text-muted-foreground">
                      Activar o desactivar el sistema de vacaciones
                    </p>
                  </div>
                  <Switch
                    checked={formData.activo}
                    onCheckedChange={(checked) => setFormData({ ...formData, activo: checked })}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Configuración de Solicitudes */}
          <TabsContent value="solicitudes">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="h-5 w-5" />
                  <span>Configuración de Solicitudes</span>
                </CardTitle>
                <CardDescription>
                  Configure las reglas para las solicitudes de vacaciones
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="dias_minimos_solicitud">Días Mínimos por Solicitud</Label>
                    <Input
                      id="dias_minimos_solicitud"
                      type="number"
                      value={formData.dias_minimos_solicitud}
                      onChange={(e) => setFormData({ ...formData, dias_minimos_solicitud: parseInt(e.target.value) })}
                      min={1}
                      max={formData.dias_maximos_solicitud}
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="dias_maximos_solicitud">Días Máximos por Solicitud</Label>
                    <Input
                      id="dias_maximos_solicitud"
                      type="number"
                      value={formData.dias_maximos_solicitud}
                      onChange={(e) => setFormData({ ...formData, dias_maximos_solicitud: parseInt(e.target.value) })}
                      min={formData.dias_minimos_solicitud}
                      max={30}
                      required
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="dias_anticipacion_minima">Días de Anticipación Mínima</Label>
                  <Input
                    id="dias_anticipacion_minima"
                    type="number"
                    value={formData.dias_anticipacion_minima}
                    onChange={(e) => setFormData({ ...formData, dias_anticipacion_minima: parseInt(e.target.value) })}
                    min={1}
                    max={30}
                    required
                  />
                  <p className="text-sm text-muted-foreground mt-1">
                    Días mínimos de anticipación para solicitar vacaciones
                  </p>
                </div>
                
                <Separator />
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Permitir Fraccionamiento</Label>
                      <p className="text-sm text-muted-foreground">
                        Permitir solicitar vacaciones en períodos separados
                      </p>
                    </div>
                    <Switch
                      checked={formData.permite_fraccionamiento}
                      onCheckedChange={(checked) => setFormData({ ...formData, permite_fraccionamiento: checked })}
                    />
                  </div>
                  
                  {formData.permite_fraccionamiento && (
                    <div>
                      <Label htmlFor="dias_minimos_fraccionamiento">Días Mínimos por Fracción</Label>
                      <Input
                        id="dias_minimos_fraccionamiento"
                        type="number"
                        value={formData.dias_minimos_fraccionamiento}
                        onChange={(e) => setFormData({ ...formData, dias_minimos_fraccionamiento: parseInt(e.target.value) })}
                        min={1}
                        max={formData.dias_minimos_solicitud}
                        required
                      />
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Permitir Solicitudes Retroactivas</Label>
                      <p className="text-sm text-muted-foreground">
                        Permitir solicitar vacaciones para fechas pasadas
                      </p>
                    </div>
                    <Switch
                      checked={formData.permitir_solicitudes_retroactivas}
                      onCheckedChange={(checked) => setFormData({ ...formData, permitir_solicitudes_retroactivas: checked })}
                    />
                  </div>
                  
                  {formData.permitir_solicitudes_retroactivas && (
                    <div>
                      <Label htmlFor="dias_retroactivos_permitidos">Días Retroactivos Permitidos</Label>
                      <Input
                        id="dias_retroactivos_permitidos"
                        type="number"
                        value={formData.dias_retroactivos_permitidos}
                        onChange={(e) => setFormData({ ...formData, dias_retroactivos_permitidos: parseInt(e.target.value) })}
                        min={1}
                        max={30}
                        required
                      />
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Configuración de Aprobaciones */}
          <TabsContent value="aprobaciones">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5" />
                  <span>Configuración de Aprobaciones</span>
                </CardTitle>
                <CardDescription>
                  Configure el flujo de aprobación de solicitudes
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Requiere Aprobación del Jefe</Label>
                      <p className="text-sm text-muted-foreground">
                        Las solicitudes deben ser aprobadas por el jefe directo
                      </p>
                    </div>
                    <Switch
                      checked={formData.requiere_aprobacion_jefe}
                      onCheckedChange={(checked) => setFormData({ ...formData, requiere_aprobacion_jefe: checked })}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Requiere Aprobación de RRHH</Label>
                      <p className="text-sm text-muted-foreground">
                        Las solicitudes deben ser aprobadas por Recursos Humanos
                      </p>
                    </div>
                    <Switch
                      checked={formData.requiere_aprobacion_rrhh}
                      onCheckedChange={(checked) => setFormData({ ...formData, requiere_aprobacion_rrhh: checked })}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Auto-aprobar Solicitudes</Label>
                      <p className="text-sm text-muted-foreground">
                        Aprobar automáticamente las solicitudes que cumplan los criterios
                      </p>
                    </div>
                    <Switch
                      checked={formData.auto_aprobar_solicitudes}
                      onCheckedChange={(checked) => setFormData({ ...formData, auto_aprobar_solicitudes: checked })}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Configuración de Notificaciones */}
          <TabsContent value="notificaciones">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="h-5 w-5" />
                  <span>Configuración de Notificaciones</span>
                </CardTitle>
                <CardDescription>
                  Configure las notificaciones y alertas del sistema
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="notificar_vencimiento_dias">Notificar Vencimiento (días)</Label>
                  <Input
                    id="notificar_vencimiento_dias"
                    type="number"
                    value={formData.notificar_vencimiento_dias}
                    onChange={(e) => setFormData({ ...formData, notificar_vencimiento_dias: parseInt(e.target.value) })}
                    min={1}
                    max={90}
                    required
                  />
                  <p className="text-sm text-muted-foreground mt-1">
                    Días antes del vencimiento para enviar notificaciones
                  </p>
                </div>
                
                <Separator />
                
                <div>
                  <Label htmlFor="mensaje_politicas">Mensaje de Políticas</Label>
                  <Textarea
                    id="mensaje_politicas"
                    value={formData.mensaje_politicas}
                    onChange={(e) => setFormData({ ...formData, mensaje_politicas: e.target.value })}
                    placeholder="Mensaje informativo sobre las políticas de vacaciones..."
                    rows={4}
                  />
                  <p className="text-sm text-muted-foreground mt-1">
                    Mensaje que se mostrará a los empleados sobre las políticas de vacaciones
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Botones de acción */}
        <div className="flex items-center justify-end space-x-2">
          <Button type="button" variant="outline" onClick={handleReset}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Restablecer
          </Button>
          <Button type="submit" disabled={saving}>
            {saving ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            ) : (
              <Save className="mr-2 h-4 w-4" />
            )}
            {saving ? 'Guardando...' : 'Guardar Configuración'}
          </Button>
        </div>
      </form>
    </div>
  )
}

export default ConfiguracionPanel