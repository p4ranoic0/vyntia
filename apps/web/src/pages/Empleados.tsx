import { Skeleton } from '@/components/common/LoadingSkeleton'
import { ProfileImage } from '@/components/common/ProfileImage'
import { TabAcademicos, TabFamiliares, TabLaborales, TabPersonales } from '@/components/empleados'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useEmpleados } from '@/hooks/useApi'
import { useDebounce } from '@/hooks/useDebounce'
import { contratosService } from '@/services/contratosService'
import { employeesService } from '@/services/employeesService'
import { OnboardingCreateData, onboardingService } from '@/services/onboardingService'
import {
    Award,
    ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight,
    Download,
    Edit,
    FileText,
    FolderOpen,
    GraduationCap,
    Mail,
    MoreHorizontal,
    Phone,
    Search,
    UserPlus,
    Users
} from 'lucide-react'
import { ChangeEvent, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

// Interfaz que refleja los campos reales del backend
interface Empleado {
  empleado_id: number
  nombres_empleado: string
  apellido_paterno: string
  apellido_materno: string
  numero_documento: string
  tipo_documento?: string
  genero_empleado: string
  estado_empleado: string
  nombre_completo: string
  edad: number | null
  telefono_celular?: string
  correo_personal?: string
  estado_civil?: string
  fecha_nacimiento?: string
  distrito_domicilio?: string
  provincia_domicilio?: string
  departamento_domicilio?: string
  ruta_fotografia?: string
  ubicacion_actual?: {
    area_id: number
    area_siglas: string
    area_nombre: string
  } | null
}

// ─── Dialog: Editar empleado (tabbed) ───────────────────────────────────────

interface EditarEmpleadoDialogProps {
  empleado: Empleado | null
  open: boolean
  onClose: () => void
  onSaved: () => void
}

// ── Main dialog ──────────────────────────────────────────────────────────────

function EditarEmpleadoDialog({ empleado, open, onClose, onSaved }: EditarEmpleadoDialogProps) {
  if (!empleado) return null

  const handleClose = () => {
    onSaved()
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={(v) => !v && handleClose()}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Editar Empleado</DialogTitle>
          <DialogDescription>
            {empleado.nombre_completo} — DNI {empleado.numero_documento}
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="personales" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="personales">Personales</TabsTrigger>
            <TabsTrigger value="laborales">Laborales</TabsTrigger>
            <TabsTrigger value="familiares">Familiares</TabsTrigger>
            <TabsTrigger value="academicos">
              <GraduationCap className="h-3.5 w-3.5 mr-1" />
              Academico
            </TabsTrigger>
          </TabsList>

          <TabsContent value="personales" className="mt-4">
            <TabPersonales empleadoId={empleado.empleado_id} initialData={empleado} />
          </TabsContent>

          <TabsContent value="laborales" className="mt-4">
            <TabLaborales empleadoId={empleado.empleado_id} />
          </TabsContent>

          <TabsContent value="familiares" className="mt-4">
            <TabFamiliares empleadoId={empleado.empleado_id} />
          </TabsContent>

          <TabsContent value="academicos" className="mt-4">
            <TabAcademicos empleadoId={empleado.empleado_id} />
          </TabsContent>
        </Tabs>

        <DialogFooter className="mt-2">
          <Button variant="outline" onClick={handleClose}>Cerrar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ─── Dialog: Nuevo empleado (vía onboarding) ────────────────────────────────

interface NuevoEmpleadoDialogProps {
  open: boolean
  onClose: () => void
  onCreated: () => void
}

const GENERO_OPTIONS = [
  { value: 'masculino', label: 'Masculino' },
  { value: 'femenino', label: 'Femenino' },
  { value: 'otro', label: 'Otro' },
]

function NuevoEmpleadoDialog({ open, onClose, onCreated }: NuevoEmpleadoDialogProps) {
  const emptyForm: OnboardingCreateData = {
    nombres_empleado: '',
    apellido_paterno: '',
    apellido_materno: '',
    numero_documento: '',
    correo_personal: '',
    genero_empleado: 'masculino',
  }
  const [form, setForm] = useState<OnboardingCreateData>(emptyForm)
  const [loading, setLoading] = useState(false)

  const handleCreate = async () => {
    if (!form.nombres_empleado || !form.apellido_paterno || !form.numero_documento || !form.correo_personal) {
      toast.error('Completa los campos obligatorios')
      return
    }
    setLoading(true)
    try {
      const result = await onboardingService.crear(form)
      toast.success(`Empleado creado. Usuario: ${result.username}`)
      setForm(emptyForm)
      onCreated()
      onClose()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al crear el empleado')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setForm(emptyForm)
    onClose()
  }

  const field = (key: keyof OnboardingCreateData) => ({
    value: (form[key] as string) || '',
    onChange: (e: ChangeEvent<HTMLInputElement>) =>
      setForm(f => ({ ...f, [key]: e.target.value })),
  })

  return (
    <Dialog open={open} onOpenChange={(v) => !v && handleClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Nuevo Empleado</DialogTitle>
          <DialogDescription>
            Se creara el empleado y se generaran sus credenciales de acceso al sistema.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-2">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor="n-nombres">Nombres <span className="text-destructive">*</span></Label>
              <Input id="n-nombres" placeholder="Juan Carlos" {...field('nombres_empleado')} />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="n-genero">Genero</Label>
              <Select value={form.genero_empleado || 'masculino'} onValueChange={(v) => setForm(f => ({ ...f, genero_empleado: v }))}>
                <SelectTrigger id="n-genero"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {GENERO_OPTIONS.map(o => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor="n-pat">Apellido Paterno <span className="text-destructive">*</span></Label>
              <Input id="n-pat" placeholder="Garcia" {...field('apellido_paterno')} />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="n-mat">Apellido Materno</Label>
              <Input id="n-mat" placeholder="Lopez" {...field('apellido_materno')} />
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor="n-dni">Numero de Documento <span className="text-destructive">*</span></Label>
            <Input id="n-dni" placeholder="12345678" maxLength={12} {...field('numero_documento')} />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor="n-email">Correo Personal <span className="text-destructive">*</span></Label>
            <Input id="n-email" type="email" placeholder="empleado@correo.com" {...field('correo_personal')} />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={loading}>Cancelar</Button>
          <Button onClick={handleCreate} disabled={loading}>
            {loading ? 'Creando...' : 'Crear Empleado'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ─── Componente principal ────────────────────────────────────────────────────

export function Empleados() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(15)
  const [searchTerm, setSearchTerm] = useState('')
  const [showInactive, setShowInactive] = useState(false)
  const [editTarget, setEditTarget] = useState<Empleado | null>(null)
  const [showNuevo, setShowNuevo] = useState(false)

  const debouncedSearchTerm = useDebounce(searchTerm, 500)

  const { data: empleadosData, isLoading, error, refetch } = useEmpleados({
    page,
    page_size: pageSize,
    search: debouncedSearchTerm || undefined,
    estado: showInactive ? undefined : 'true'
  })

  const empleados: Empleado[] = empleadosData?.results || []
  const totalCount = empleadosData?.count || 0
  const totalPages = Math.ceil(totalCount / pageSize)

  useEffect(() => {
    setPage(1)
  }, [debouncedSearchTerm, showInactive])

  const handleVerDetalle = (id: number) => {
    navigate(`/empleados/reporte/${id}`)
  }

  const handleDescargarPdf = async (id: number, nombre: string) => {
    try {
      await employeesService.reportes.descargarReporteIntegral(id)
      toast.success(`PDF descargado: ${nombre}`)
    } catch {
      toast.error('Error al descargar el PDF')
    }
  }

  const handleVerLegajo = (id: number) => {
    navigate(`/legajo/${id}`)
  }

  const handleGenerarDocumento = async (empleado: Empleado, tipo: 'constancia' | 'certificado') => {
    try {
      await contratosService.generarCertificado({
        empleado_id: empleado.empleado_id,
        tipo_certificado: tipo === 'certificado' ? 'trabajo' : 'constancia',
        guardar_documento: true,
      })
      toast.success(`${tipo === 'certificado' ? 'Certificado' : 'Constancia'} generado para ${empleado.nombre_completo}`)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al generar el documento')
    }
  }

  const getEstadoBadge = (estado: string) => {
    switch (estado) {
      case 'activo':
        return <Badge variant="default" className="bg-green-600">Activo</Badge>
      case 'inactivo':
        return <Badge variant="secondary">Inactivo</Badge>
      case 'suspendido':
        return <Badge variant="destructive">Suspendido</Badge>
      case 'cesado':
        return <Badge variant="outline">Cesado</Badge>
      default:
        return <Badge variant="secondary">{estado}</Badge>
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-4 w-72" />
          </div>
          <Skeleton className="h-10 w-36" />
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="flex items-center space-x-4">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <Skeleton className="h-4 flex-1" />
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-20" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4">
        <Users className="h-12 w-12 text-muted-foreground" />
        <h2 className="text-xl font-semibold">Error al cargar los empleados</h2>
        <p className="text-muted-foreground text-center max-w-md">
          No se pudo obtener la lista de empleados. Verifica tu conexion e intenta nuevamente.
        </p>
        <Button onClick={() => refetch()} variant="outline">
          Reintentar
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Dialogs */}
      <EditarEmpleadoDialog
        empleado={editTarget}
        open={!!editTarget}
        onClose={() => setEditTarget(null)}
        onSaved={() => refetch()}
      />
      <NuevoEmpleadoDialog
        open={showNuevo}
        onClose={() => setShowNuevo(false)}
        onCreated={() => refetch()}
      />

      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestion de Empleados</h1>
          <p className="text-muted-foreground">
            {totalCount} empleado{totalCount !== 1 ? 's' : ''} registrado{totalCount !== 1 ? 's' : ''}
          </p>
        </div>
        <Button onClick={() => setShowNuevo(true)}>
          <UserPlus className="mr-2 h-4 w-4" />
          Nuevo Empleado
        </Button>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-4 pb-4">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por nombre o DNI..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="show-inactive"
                checked={showInactive}
                onCheckedChange={(checked) => setShowInactive(checked as boolean)}
              />
              <Label htmlFor="show-inactive" className="text-sm">
                Incluir inactivos
              </Label>
            </div>
            <Select value={String(pageSize)} onValueChange={(v) => { setPageSize(Number(v)); setPage(1) }}>
              <SelectTrigger className="w-[130px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="10">10 por pag.</SelectItem>
                <SelectItem value="15">15 por pag.</SelectItem>
                <SelectItem value="25">25 por pag.</SelectItem>
                <SelectItem value="50">50 por pag.</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabla */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[60px]">ID</TableHead>
                  <TableHead className="w-[80px]">DNI</TableHead>
                  <TableHead>Empleado</TableHead>
                  <TableHead className="hidden md:table-cell">Area</TableHead>
                  <TableHead className="hidden lg:table-cell">Contacto</TableHead>
                  <TableHead className="hidden sm:table-cell w-[80px]">Edad</TableHead>
                  <TableHead className="w-[90px]">Estado</TableHead>
                  <TableHead className="w-[50px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {empleados.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-12">
                      <Users className="h-10 w-10 mx-auto mb-3 text-muted-foreground" />
                      <p className="text-muted-foreground">No se encontraron empleados</p>
                      {searchTerm && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Intenta con otro termino de busqueda
                        </p>
                      )}
                    </TableCell>
                  </TableRow>
                ) : (
                  empleados.map((emp) => (
                    <TableRow
                      key={emp.empleado_id}
                      className="cursor-pointer hover:bg-accent/50"
                      onClick={() => handleVerDetalle(emp.empleado_id)}
                    >
                      <TableCell className="text-xs text-muted-foreground">
                        {emp.empleado_id}
                      </TableCell>
                      <TableCell className="font-mono text-sm">
                        {emp.numero_documento}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-3 min-w-0">
                          <ProfileImage
                            src={emp.ruta_fotografia || ''}
                            alt={emp.nombre_completo}
                            size="md"
                            className="shrink-0"
                          />
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium truncate">
                              {emp.nombre_completo}
                            </p>
                            <p className="text-xs text-muted-foreground truncate">
                              {[emp.distrito_domicilio, emp.provincia_domicilio].filter(Boolean).join(', ')}
                            </p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="hidden md:table-cell">
                        {emp.ubicacion_actual ? (
                          <div>
                            <p className="text-sm font-medium">{emp.ubicacion_actual.area_siglas}</p>
                            <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                              {emp.ubicacion_actual.area_nombre}
                            </p>
                          </div>
                        ) : (
                          <span className="text-xs text-muted-foreground">Sin asignar</span>
                        )}
                      </TableCell>
                      <TableCell className="hidden lg:table-cell">
                        <div className="space-y-1">
                          {emp.correo_personal && (
                            <div className="flex items-center space-x-1 text-xs">
                              <Mail className="w-3 h-3 text-muted-foreground" />
                              <span className="truncate max-w-[180px]">{emp.correo_personal}</span>
                            </div>
                          )}
                          {emp.telefono_celular && (
                            <div className="flex items-center space-x-1 text-xs">
                              <Phone className="w-3 h-3 text-muted-foreground" />
                              <span>{emp.telefono_celular}</span>
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="hidden sm:table-cell text-center">
                        {emp.edad ?? '-'}
                      </TableCell>
                      <TableCell>
                        {getEstadoBadge(emp.estado_empleado)}
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
                            <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                            <DropdownMenuItem onClick={() => setEditTarget(emp)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Editar
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleDescargarPdf(emp.empleado_id, emp.nombre_completo)}>
                              <Download className="mr-2 h-4 w-4" />
                              Descargar PDF
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => handleVerLegajo(emp.empleado_id)}>
                              <FolderOpen className="mr-2 h-4 w-4" />
                              Legajo Digital
                            </DropdownMenuItem>
                            {/* Documentos condicionales por estado */}
                            {emp.estado_empleado === 'activo' && (
                              <>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={() => handleGenerarDocumento(emp, 'constancia')}>
                                  <FileText className="mr-2 h-4 w-4" />
                                  Constancia de Trabajo
                                </DropdownMenuItem>
                              </>
                            )}
                            {emp.estado_empleado === 'cesado' && (
                              <>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={() => handleGenerarDocumento(emp, 'certificado')}>
                                  <Award className="mr-2 h-4 w-4" />
                                  Certificado de Trabajo
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

          {/* Paginacion */}
          {totalCount > 0 && (
            <div className="flex items-center justify-between px-4 py-3 border-t">
              <p className="text-sm text-muted-foreground">
                Mostrando {((page - 1) * pageSize) + 1} - {Math.min(page * pageSize, totalCount)} de {totalCount}
              </p>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  disabled={page <= 1}
                  onClick={() => setPage(1)}
                >
                  <ChevronsLeft className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  disabled={page <= 1}
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-sm px-2">
                  Pagina {page} de {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  disabled={page >= totalPages}
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  className="h-8 w-8"
                  disabled={page >= totalPages}
                  onClick={() => setPage(totalPages)}
                >
                  <ChevronsRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
