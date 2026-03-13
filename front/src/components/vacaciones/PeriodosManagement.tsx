import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Calendar, Users, Clock, AlertTriangle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import vacacionesService, { PeriodoVacacional } from '@/services/vacacionesService'

interface PeriodosManagementProps {
  onPeriodoCreated?: () => void
}

const PeriodosManagement: React.FC<PeriodosManagementProps> = ({ onPeriodoCreated }) => {
  const { toast } = useToast()
  const [loading, setLoading] = useState(true)
  const [periodos, setPeriodos] = useState<PeriodoVacacional[]>([])
  const [selectedPeriodo, setSelectedPeriodo] = useState<PeriodoVacacional | null>(null)
  const [showAjusteDialog, setShowAjusteDialog] = useState(false)
  const [ajusteData, setAjusteData] = useState({ nuevos_dias: 30, motivo: '' })

  // Cargar datos iniciales
  useEffect(() => {
    cargarDatos()
  }, [])

  const cargarDatos = async () => {
    try {
      setLoading(true)
      const periodosRes = await vacacionesService.getPeriodos()
      setPeriodos(periodosRes)
    } catch (error) {
      console.error('Error al cargar períodos:', error)
      toast({
        title: 'Error',
        description: 'No se pudieron cargar los períodos',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleAjusteSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedPeriodo) return
    try {
      await vacacionesService.ajustarDiasPeriodo(selectedPeriodo.periodo_id, ajusteData.nuevos_dias, ajusteData.motivo)
      toast({
        title: 'Éxito',
        description: 'Período ajustado correctamente'
      })
      setShowAjusteDialog(false)
      setSelectedPeriodo(null)
      setAjusteData({ nuevos_dias: 30, motivo: '' })
      cargarDatos()
      onPeriodoCreated?.()
    } catch (error) {
      console.error('Error al ajustar período:', error)
      toast({
        title: 'Error',
        description: 'No se pudo ajustar el período',
        variant: 'destructive'
      })
    }
  }

  const getEstadoBadge = (estado: string) => {
    const variants = {
      'activo': 'default',
      'cerrado': 'secondary',
      'vencido': 'destructive',
      'cancelado': 'outline'
    } as const
    
    return (
      <Badge variant={variants[estado as keyof typeof variants] || 'secondary'}>
        {estado.charAt(0).toUpperCase() + estado.slice(1)}
      </Badge>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando períodos...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header con estadísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Calendar className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm font-medium">Períodos Activos</p>
                <p className="text-2xl font-bold">
                  {periodos.filter(p => p.estado_periodo === 'activo').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm font-medium">Empleados con Períodos</p>
                <p className="text-2xl font-bold">{new Set(periodos.map(p => p.empleado)).size}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-orange-500" />
              <div>
                <p className="text-sm font-medium">Próximos a Vencer</p>
                <p className="text-2xl font-bold">
                  {periodos.filter(p => (p.dias_vencidos || 0) > 0).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gestión de períodos */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Gestión de Períodos Vacacionales</CardTitle>
              <CardDescription>
                Administre los períodos vacacionales de la organización
              </CardDescription>
            </div>
            <Dialog open={showAjusteDialog} onOpenChange={setShowAjusteDialog}>
              <DialogTrigger asChild>
                <Button variant="outline" onClick={() => setShowAjusteDialog(true)}>
                  Ajustar Días
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Ajustar días de período</DialogTitle>
                  <DialogDescription>
                    Selecciona el período y registra el motivo del ajuste.
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleAjusteSubmit} className="space-y-4">
                  <div>
                    <Label>Período</Label>
                    <Select
                      value={selectedPeriodo ? String(selectedPeriodo.periodo_id) : ''}
                      onValueChange={(value) => {
                        const periodo = periodos.find((p) => String(p.periodo_id) === value) || null
                        setSelectedPeriodo(periodo)
                        if (periodo) {
                          setAjusteData({ ...ajusteData, nuevos_dias: periodo.dias_correspondientes })
                        }
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecciona un período" />
                      </SelectTrigger>
                      <SelectContent>
                        {periodos.map((p) => (
                          <SelectItem key={p.periodo_id} value={String(p.periodo_id)}>
                            {p.empleado_nombre} - {p.periodo_label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="nuevos_dias">Nuevos días</Label>
                      <Input
                        id="nuevos_dias"
                        type="number"
                        value={ajusteData.nuevos_dias}
                        onChange={(e) => setAjusteData({ ...ajusteData, nuevos_dias: parseInt(e.target.value) })}
                        min={0}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="motivo">Motivo</Label>
                      <Input
                        id="motivo"
                        value={ajusteData.motivo}
                        onChange={(e) => setAjusteData({ ...ajusteData, motivo: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setShowAjusteDialog(false)}>
                      Cancelar
                    </Button>
                    <Button type="submit" disabled={!selectedPeriodo}>
                      Ajustar
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        
        <CardContent>
          {periodos.length === 0 ? (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                No hay períodos vacacionales configurados. Cree el primer período para comenzar.
              </AlertDescription>
            </Alert>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Año</TableHead>
                  <TableHead>Período</TableHead>
                  <TableHead>Días Asignados</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Empleados</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {periodos.map((periodo) => {
                  return (
                    <TableRow key={periodo.periodo_id}>
                      <TableCell className="font-medium">{periodo.ano_periodo}</TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div>{new Date(periodo.fecha_inicio_periodo).toLocaleDateString()} - {new Date(periodo.fecha_fin_periodo).toLocaleDateString()}</div>
                          <div className="text-muted-foreground">{periodo.empleado_nombre}</div>
                          {periodo.contrato_numero && (
                            <div className="text-muted-foreground">Contrato: {periodo.contrato_numero}</div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{periodo.dias_correspondientes} días</TableCell>
                      <TableCell>{getEstadoBadge(periodo.estado_periodo)}</TableCell>
                      <TableCell>1 empleado</TableCell>
                      <TableCell>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedPeriodo(periodo)
                            setAjusteData({ nuevos_dias: periodo.dias_correspondientes, motivo: '' })
                            setShowAjusteDialog(true)
                          }}
                        >
                          Ajustar
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default PeriodosManagement
