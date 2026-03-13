import { Skeleton } from '@/components/common/LoadingSkeleton'
import { ProfileImage } from '@/components/common/ProfileImage'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { apiClient } from '@/lib/api'
import { employeesService } from '@/services/employeesService'
import {
    ArrowLeft,
    Briefcase,
    Building2,
    Calendar,
    CreditCard,
    Download,
    FileText,
    GraduationCap,
    Mail,
    MapPin,
    Phone,
    Printer,
    User,
    Users
} from 'lucide-react'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'

// Interfaz alineada con los campos reales del backend (EmpleadoSerializer)
interface EmpleadoDetalle {
  empleado_id: number
  nombres_empleado: string
  apellido_paterno: string
  apellido_materno: string
  numero_documento: string
  fecha_nacimiento: string
  genero_empleado: string
  genero_texto: string
  estado_civil: string
  direccion_domicilio: string
  distrito_domicilio: string
  telefono_celular: string
  correo_personal: string
  es_padre_familia: boolean
  entidad_bancaria: string
  numero_cuenta_bancaria: string
  estado_empleado: string
  nombre_completo: string
  edad: number | null
  es_activo: boolean
  ruta_fotografia?: string
  datos_laborales_actuales?: {
    dato_laboral_id: number
    cargo_empleado: string
    tipo_contrato: string
    regimen_laboral: string
    modalidad_trabajo: string
    jornada_laboral: string
    fecha_ingreso: string
    fecha_cese?: string
    sueldo_basico?: number
    area?: number
    area_nombre?: string
    es_activo?: boolean
    tiempo_servicio?: string
    [key: string]: any
  } | null
  familiares?: Array<{
    familiar_id: number
    nombres_familiar: string
    apellido_paterno: string
    apellido_materno: string
    parentesco: string
    fecha_nacimiento: string
    numero_documento: string
    genero_familiar: string
    es_dependiente: boolean
    es_beneficiario: boolean
    es_contacto_emergencia?: boolean
    estado_familiar: string
    nombres_completos?: string
    edad?: number
    es_menor_edad?: boolean
    telefono_familiar?: string
    [key: string]: any
  }>
  formacion?: Array<{
    academico_id: number
    tipo_formacion: string
    nombre_institucion: string
    carrera_especialidad: string
    titulo_obtenido?: string
    fecha_inicio_estudios?: string
    fecha_termino_estudios?: string
    estado_estudios: string
    nivel_educativo: string
    [key: string]: any
  }>
}

type ReportSection = 'todos' | 'personales' | 'laborales' | 'academicos' | 'familiares'

export default function EmpleadoReportPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const printRef = useRef<HTMLDivElement>(null)
  const [empleado, setEmpleado] = useState<EmpleadoDetalle | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<ReportSection>('todos')
  const [isDownloading, setIsDownloading] = useState(false)

  useEffect(() => {
    const fetchEmpleado = async () => {
      if (!id) return
      try {
        setIsLoading(true)
        setError(null)
        const data = await apiClient.getEmpleadoDetail(Number(id))
        setEmpleado(data)
      } catch {
        setError('No se pudo cargar la informacion del empleado')
      } finally {
        setIsLoading(false)
      }
    }
    fetchEmpleado()
  }, [id])

  const handlePrint = useCallback(() => {
    const previousTab = activeTab
    setActiveTab('todos')
    // Wait for React to re-render all sections before printing
    setTimeout(() => {
      window.print()
      setActiveTab(previousTab)
    }, 100)
  }, [activeTab])

  const handleDownloadPdf = async () => {
    if (!id) return
    setIsDownloading(true)
    try {
      const seccionMap: Record<string, 'personal' | 'laboral' | 'academico' | 'familiar'> = {
        personales: 'personal',
        laborales: 'laboral',
        academicos: 'academico',
        familiares: 'familiar',
      }
      if (activeTab === 'todos') {
        await employeesService.reportes.descargarReporteIntegral(Number(id))
      } else {
        const seccion = seccionMap[activeTab]
        if (seccion) {
          await employeesService.reportes.descargarReporteSeccion(Number(id), seccion)
        }
      }
      toast.success('Reporte PDF descargado')
    } catch {
      toast.error('Error al descargar el reporte PDF')
    } finally {
      setIsDownloading(false)
    }
  }

  const formatDate = (date?: string | null) => {
    if (!date) return '-'
    try {
      return new Date(date).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
    } catch { return date }
  }

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10 rounded-full" />
          <Skeleton className="h-8 w-64" />
        </div>
        <Skeleton className="h-48" />
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-40" />
          <Skeleton className="h-40" />
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (error || !empleado) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4">
        <User className="h-12 w-12 text-muted-foreground" />
        <h2 className="text-xl font-semibold">{error || 'Empleado no encontrado'}</h2>
        <Button onClick={() => navigate('/empleados')} variant="outline" className="cursor-pointer">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Volver a la lista
        </Button>
      </div>
    )
  }

  const lab = empleado.datos_laborales_actuales

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header de acciones */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between print:hidden">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => navigate('/empleados')} className="cursor-pointer">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold">Reporte del Empleado</h1>
            <p className="text-sm text-muted-foreground">{empleado.nombre_completo}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleDownloadPdf} disabled={isDownloading} className="cursor-pointer">
            <Download className="mr-2 h-4 w-4" />
            <span className="hidden sm:inline">{isDownloading ? 'Descargando...' : 'Descargar PDF'}</span>
            <span className="sm:hidden">PDF</span>
          </Button>
          <Button variant="outline" size="sm" onClick={handlePrint} className="cursor-pointer">
            <Printer className="mr-2 h-4 w-4" />
            <span className="hidden sm:inline">Imprimir</span>
          </Button>
        </div>
      </div>

      {/* Tabs de secciones */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as ReportSection)} className="print:hidden">
        <TabsList className="w-full overflow-x-auto flex">
          <TabsTrigger value="todos" className="flex-1 cursor-pointer text-xs sm:text-sm">Todos</TabsTrigger>
          <TabsTrigger value="personales" className="flex-1 cursor-pointer text-xs sm:text-sm">Personales</TabsTrigger>
          <TabsTrigger value="laborales" className="flex-1 cursor-pointer text-xs sm:text-sm">Laborales</TabsTrigger>
          <TabsTrigger value="academicos" className="flex-1 cursor-pointer text-xs sm:text-sm">Academicos</TabsTrigger>
          <TabsTrigger value="familiares" className="flex-1 cursor-pointer text-xs sm:text-sm">Familiares</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Contenido del reporte */}
      <div ref={printRef} className="space-y-6 print:space-y-4">

        {/* Encabezado para impresion */}
        <div className="hidden print:block text-center border-b-2 border-primary pb-4 mb-6">
          <h1 className="text-2xl font-bold tracking-tight">REPORTE DEL EMPLEADO</h1>
          <p className="text-sm text-muted-foreground mt-1">Generado el {new Date().toLocaleDateString('es-PE')}</p>
        </div>

        {/* Ficha resumen del empleado - siempre visible */}
        <Card className="overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-blue-800 px-4 sm:px-6 py-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
              <ProfileImage
                src={empleado.ruta_fotografia || ''}
                alt={empleado.nombre_completo}
                size="lg"
                className="shrink-0 ring-2 ring-white/30"
              />
              <div className="text-white min-w-0">
                <h2 className="text-lg sm:text-xl font-bold truncate">{empleado.nombre_completo}</h2>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1 text-blue-100 text-xs sm:text-sm">
                  <span className="font-mono">{empleado.numero_documento}</span>
                  {lab?.cargo_empleado && (
                    <>
                      <span className="hidden sm:inline">|</span>
                      <span>{lab.cargo_empleado}</span>
                    </>
                  )}
                  {lab?.area_nombre && (
                    <>
                      <span className="hidden sm:inline">|</span>
                      <span>{lab.area_nombre}</span>
                    </>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant={empleado.es_activo ? 'default' : 'secondary'} className={empleado.es_activo ? 'bg-green-500 text-white hover:bg-green-600' : ''}>
                    {empleado.estado_empleado}
                  </Badge>
                  {empleado.edad && (
                    <span className="text-blue-200 text-xs">{empleado.edad} anos</span>
                  )}
                </div>
              </div>
            </div>
          </div>
          {/* Stats rapidos */}
          <div className="grid grid-cols-2 sm:grid-cols-4 divide-x divide-border">
            <StatBox label="Ingreso" value={lab ? formatDate(lab.fecha_ingreso) : '-'} />
            <StatBox label="Contrato" value={lab?.tipo_contrato || '-'} />
            <StatBox label="Familiares" value={String(empleado.familiares?.length || 0)} />
            <StatBox label="Formacion" value={String(empleado.formacion?.length || 0)} />
          </div>
        </Card>

        {/* DATOS PERSONALES */}
        {(activeTab === 'todos' || activeTab === 'personales') && (
          <SectionCard icon={<User className="h-5 w-5" />} title="Datos Personales">
            <div className="grid gap-x-8 gap-y-3 sm:grid-cols-2 lg:grid-cols-3">
              <FieldRow label="Nombres" value={empleado.nombres_empleado} />
              <FieldRow label="Apellido Paterno" value={empleado.apellido_paterno} />
              <FieldRow label="Apellido Materno" value={empleado.apellido_materno} />
              <FieldRow label="DNI" value={empleado.numero_documento} mono />
              <FieldRow label="Fecha de Nacimiento" value={formatDate(empleado.fecha_nacimiento)} />
              <FieldRow label="Genero" value={empleado.genero_texto} />
              <FieldRow label="Estado Civil" value={empleado.estado_civil} />
              <FieldRow label="Telefono" value={empleado.telefono_celular} icon={<Phone className="h-3.5 w-3.5" />} />
              <FieldRow label="Correo Personal" value={empleado.correo_personal} icon={<Mail className="h-3.5 w-3.5" />} />
              <FieldRow label="Direccion" value={empleado.direccion_domicilio} icon={<MapPin className="h-3.5 w-3.5" />} />
              <FieldRow label="Distrito" value={empleado.distrito_domicilio} />
              <FieldRow label="Padre de Familia" value={empleado.es_padre_familia ? 'Si' : 'No'} />
              <FieldRow label="Entidad Bancaria" value={empleado.entidad_bancaria} icon={<CreditCard className="h-3.5 w-3.5" />} />
              <FieldRow label="Cuenta Bancaria" value={empleado.numero_cuenta_bancaria} mono />
            </div>
          </SectionCard>
        )}

        {/* DATOS LABORALES */}
        {(activeTab === 'todos' || activeTab === 'laborales') && (
          <SectionCard icon={<Briefcase className="h-5 w-5" />} title="Datos Laborales">
            {lab ? (
              <div className="grid gap-x-8 gap-y-3 sm:grid-cols-2 lg:grid-cols-3">
                <FieldRow label="Cargo" value={lab.cargo_empleado} />
                <FieldRow label="Area" value={lab.area_nombre} icon={<Building2 className="h-3.5 w-3.5" />} />
                <FieldRow label="Tipo de Contrato" value={lab.tipo_contrato} />
                <FieldRow label="Regimen Laboral" value={lab.regimen_laboral} />
                <FieldRow label="Modalidad" value={lab.modalidad_trabajo} />
                <FieldRow label="Jornada" value={lab.jornada_laboral} />
                <FieldRow label="Fecha de Ingreso" value={formatDate(lab.fecha_ingreso)} icon={<Calendar className="h-3.5 w-3.5" />} />
                {lab.fecha_cese && (
                  <FieldRow label="Fecha de Cese" value={formatDate(lab.fecha_cese)} />
                )}
                {lab.tiempo_servicio && (
                  <FieldRow label="Tiempo de Servicio" value={lab.tiempo_servicio} />
                )}
              </div>
            ) : (
              <EmptyState text="No hay datos laborales registrados" />
            )}
          </SectionCard>
        )}

        {/* FORMACION ACADEMICA */}
        {(activeTab === 'todos' || activeTab === 'academicos') && (
          <SectionCard
            icon={<GraduationCap className="h-5 w-5" />}
            title="Formacion Academica"
            count={empleado.formacion?.length}
          >
            {empleado.formacion && empleado.formacion.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left py-2.5 px-3 font-semibold text-xs uppercase tracking-wider text-muted-foreground">Nivel</th>
                      <th className="text-left py-2.5 px-3 font-semibold text-xs uppercase tracking-wider text-muted-foreground">Institucion</th>
                      <th className="text-left py-2.5 px-3 font-semibold text-xs uppercase tracking-wider text-muted-foreground hidden sm:table-cell">Carrera / Titulo</th>
                      <th className="text-left py-2.5 px-3 font-semibold text-xs uppercase tracking-wider text-muted-foreground hidden md:table-cell">Periodo</th>
                      <th className="text-left py-2.5 px-3 font-semibold text-xs uppercase tracking-wider text-muted-foreground">Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {empleado.formacion.map((f, idx) => (
                      <tr key={f.academico_id || idx} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                        <td className="py-2.5 px-3">
                          <span className="font-medium">{f.nivel_educativo || f.tipo_formacion}</span>
                        </td>
                        <td className="py-2.5 px-3">{f.nombre_institucion}</td>
                        <td className="py-2.5 px-3 hidden sm:table-cell">
                          {f.titulo_obtenido || f.carrera_especialidad || '-'}
                        </td>
                        <td className="py-2.5 px-3 hidden md:table-cell text-muted-foreground text-xs">
                          {f.fecha_inicio_estudios ? formatDate(f.fecha_inicio_estudios) : '-'}
                          {f.fecha_termino_estudios ? ` - ${formatDate(f.fecha_termino_estudios)}` : ''}
                        </td>
                        <td className="py-2.5 px-3">
                          <Badge variant={f.estado_estudios === 'completado' ? 'default' : 'secondary'} className="text-xs">
                            {f.estado_estudios}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <EmptyState text="No hay datos academicos registrados" />
            )}
          </SectionCard>
        )}

        {/* DATOS FAMILIARES / DEPENDIENTES */}
        {(activeTab === 'todos' || activeTab === 'familiares') && (
          <SectionCard
            icon={<Users className="h-5 w-5" />}
            title="Datos Familiares"
            count={empleado.familiares?.length}
          >
            {empleado.familiares && empleado.familiares.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left py-2.5 px-3 font-semibold text-xs uppercase tracking-wider text-muted-foreground">Nombre Completo</th>
                      <th className="text-left py-2.5 px-3 font-semibold text-xs uppercase tracking-wider text-muted-foreground">Parentesco</th>
                      <th className="text-left py-2.5 px-3 font-semibold text-xs uppercase tracking-wider text-muted-foreground hidden sm:table-cell">DNI</th>
                      <th className="text-left py-2.5 px-3 font-semibold text-xs uppercase tracking-wider text-muted-foreground hidden md:table-cell">F. Nacimiento</th>
                      <th className="text-left py-2.5 px-3 font-semibold text-xs uppercase tracking-wider text-muted-foreground hidden lg:table-cell">Edad</th>
                      <th className="text-left py-2.5 px-3 font-semibold text-xs uppercase tracking-wider text-muted-foreground">Tipo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {empleado.familiares.map((f, idx) => (
                      <tr key={f.familiar_id || idx} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                        <td className="py-2.5 px-3">
                          <span className="font-medium">
                            {f.nombres_completos || `${f.nombres_familiar} ${f.apellido_paterno} ${f.apellido_materno}`}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 capitalize">{f.parentesco}</td>
                        <td className="py-2.5 px-3 font-mono hidden sm:table-cell">{f.numero_documento || '-'}</td>
                        <td className="py-2.5 px-3 hidden md:table-cell">{formatDate(f.fecha_nacimiento)}</td>
                        <td className="py-2.5 px-3 hidden lg:table-cell">
                          {f.edad != null ? `${f.edad} anos` : '-'}
                          {f.es_menor_edad && <span className="ml-1 text-amber-600 text-xs">(menor)</span>}
                        </td>
                        <td className="py-2.5 px-3">
                          <div className="flex flex-wrap gap-1">
                            {f.es_dependiente && <Badge variant="outline" className="text-[10px]">Dependiente</Badge>}
                            {f.es_beneficiario && <Badge variant="outline" className="text-[10px]">Beneficiario</Badge>}
                            {f.es_contacto_emergencia && <Badge variant="outline" className="text-[10px] border-red-300 text-red-600">Emergencia</Badge>}
                            {!f.es_dependiente && !f.es_beneficiario && !f.es_contacto_emergencia && (
                              <span className="text-muted-foreground text-xs">-</span>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <EmptyState text="No hay datos familiares registrados" />
            )}
          </SectionCard>
        )}

        {/* Footer para impresion */}
        <div className="hidden print:block text-center border-t pt-4 mt-8">
          <p className="text-xs text-muted-foreground">
            Reporte generado automaticamente por el Sistema de Intranet RRHH | {new Date().toLocaleDateString('es-PE')}
          </p>
          <p className="text-xs text-muted-foreground">Este documento es de uso interno y confidencial.</p>
        </div>
      </div>
    </div>
  )
}

// ---- Componentes auxiliares ----

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="py-3 px-4 text-center">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="font-semibold text-sm mt-0.5 truncate">{value}</p>
    </div>
  )
}

function SectionCard({ icon, title, count, children }: {
  icon: React.ReactNode
  title: string
  count?: number
  children: React.ReactNode
}) {
  return (
    <Card className="print:shadow-none print:border">
      <div className="px-4 sm:px-6 pt-4 sm:pt-5 pb-3">
        <div className="flex items-center gap-2">
          <div className="text-primary">{icon}</div>
          <h3 className="font-semibold text-base sm:text-lg">{title}</h3>
          {count != null && (
            <Badge variant="secondary" className="ml-auto text-xs">{count}</Badge>
          )}
        </div>
        <Separator className="mt-3" />
      </div>
      <CardContent className="px-4 sm:px-6 pb-5">
        {children}
      </CardContent>
    </Card>
  )
}

function FieldRow({ label, value, icon, mono }: {
  label: string
  value?: string | null
  icon?: React.ReactNode
  mono?: boolean
}) {
  return (
    <div className="flex items-start gap-2 py-1.5 border-b border-dashed border-border/50 last:border-0">
      {icon && <div className="text-muted-foreground mt-0.5 shrink-0">{icon}</div>}
      <div className="min-w-0 flex-1">
        <p className="text-[11px] text-muted-foreground uppercase tracking-wider">{label}</p>
        <p className={`text-sm font-medium truncate ${mono ? 'font-mono' : ''}`}>{value || '-'}</p>
      </div>
    </div>
  )
}

function EmptyState({ text }: { text: string }) {
  return (
    <div className="text-center py-8 text-muted-foreground">
      <FileText className="h-8 w-8 mx-auto mb-2 opacity-40" />
      <p className="text-sm">{text}</p>
    </div>
  )
}
