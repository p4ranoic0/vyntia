import { useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { useQueryClient } from '@tanstack/react-query'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { apiClient } from '@/lib/api'
import { DocumentInfo } from '../types/onboarding'
import { DocumentUploadZone } from './DocumentUploadZone'

const schema = z.object({
  telefono_celular: z.string().min(9, 'Mínimo 9 dígitos').max(15).optional().or(z.literal('')),
  direccion_domicilio: z.string().max(200).optional().or(z.literal('')),
  fecha_nacimiento: z.string().optional().or(z.literal('')),
  genero_empleado: z.enum(['masculino', 'femenino', 'otro', 'no_especifica']).optional().or(z.literal('')),
  estado_civil: z.enum(['soltero', 'casado', 'divorciado', 'viudo', 'conviviente']).optional().or(z.literal('')),
  numero_ruc: z.string().max(20).optional().or(z.literal('')),
  distrito_domicilio: z.string().max(100).optional().or(z.literal('')),
  provincia_domicilio: z.string().max(100).optional().or(z.literal('')),
  departamento_domicilio: z.string().max(100).optional().or(z.literal('')),
  entidad_bancaria: z.string().max(100).optional().or(z.literal('')),
  numero_cuenta_bancaria: z.string().max(30).optional().or(z.literal('')),
  numero_cci: z.string().max(30).optional().or(z.literal('')),
  sistema_pensiones: z.string().optional().or(z.literal('')),
  tipo_comision: z.enum(['FLUJO', 'MIXTA']).optional().or(z.literal('')),
  codigo_cuspp: z.string().max(20).optional().or(z.literal('')),
})

type FormValues = z.infer<typeof schema>

const AFP_OPTIONS = ['AFP PRIMA', 'AFP INTEGRA', 'AFP PROFUTURO', 'AFP HABITAT']

const SISTEMA_PENSIONES_OPTIONS = [
  'ONP',
  'AFP PRIMA',
  'AFP INTEGRA',
  'AFP PROFUTURO',
  'AFP HABITAT',
  'PENSIONISTA-SPP',
  'PENSIONISTA-CMP',
  'PENSIONISTA-OTRO',
  'SIN PENSION',
]

interface OnboardingTabPersonalProps {
  empleadoId: number
  docs: DocumentInfo[]
  initialValues?: Record<string, unknown>
}

export function OnboardingTabPersonal({ empleadoId, docs, initialValues }: OnboardingTabPersonalProps) {
  const queryClient = useQueryClient()
  const fotoDoc = docs.find(d => d.tipo_documento === 'foto') ?? null

  const { register, handleSubmit, formState: { errors, isSubmitting }, reset, watch, control } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      telefono_celular: '',
      direccion_domicilio: '',
      fecha_nacimiento: '',
      genero_empleado: '',
      estado_civil: '',
      numero_ruc: '',
      distrito_domicilio: '',
      provincia_domicilio: '',
      departamento_domicilio: '',
      entidad_bancaria: '',
      numero_cuenta_bancaria: '',
      numero_cci: '',
      sistema_pensiones: '',
      tipo_comision: '',
      codigo_cuspp: '',
    },
  })

  useEffect(() => {
    if (initialValues) {
      reset({
        telefono_celular: (initialValues.telefono_celular as string) ?? '',
        fecha_nacimiento: (initialValues.fecha_nacimiento as string) ?? '',
        direccion_domicilio: (initialValues.direccion_domicilio as string) ?? '',
        genero_empleado: (initialValues.genero_empleado as string) ?? '',
        estado_civil: (initialValues.estado_civil as string) ?? '',
        numero_ruc: (initialValues.numero_ruc as string) ?? '',
        distrito_domicilio: (initialValues.distrito_domicilio as string) ?? '',
        provincia_domicilio: (initialValues.provincia_domicilio as string) ?? '',
        departamento_domicilio: (initialValues.departamento_domicilio as string) ?? '',
        entidad_bancaria: (initialValues.entidad_bancaria as string) ?? '',
        numero_cuenta_bancaria: (initialValues.numero_cuenta_bancaria as string) ?? '',
        numero_cci: (initialValues.numero_cci as string) ?? '',
        sistema_pensiones: (initialValues.sistema_pensiones as string) ?? '',
        tipo_comision: (initialValues.tipo_comision as string) ?? '',
        codigo_cuspp: (initialValues.codigo_cuspp as string) ?? '',
      })
    }
  }, [initialValues, reset])

  const sistemaPensiones = watch('sistema_pensiones')
  const isAFP = AFP_OPTIONS.includes(sistemaPensiones ?? '')

  const onSubmit = async (data: FormValues) => {
    try {
      await apiClient.patch(`/api/v1/rrhh/empleados/${empleadoId}/`, {
        telefono_celular: data.telefono_celular || undefined,
        direccion_domicilio: data.direccion_domicilio || undefined,
        fecha_nacimiento: data.fecha_nacimiento || undefined,
        genero_empleado: data.genero_empleado || undefined,
        estado_civil: data.estado_civil || undefined,
        numero_ruc: data.numero_ruc || undefined,
        distrito_domicilio: data.distrito_domicilio || undefined,
        provincia_domicilio: data.provincia_domicilio || undefined,
        departamento_domicilio: data.departamento_domicilio || undefined,
        entidad_bancaria: data.entidad_bancaria || undefined,
        numero_cuenta_bancaria: data.numero_cuenta_bancaria || undefined,
        numero_cci: data.numero_cci || undefined,
        sistema_pensiones: data.sistema_pensiones || undefined,
        tipo_comision: (isAFP && data.tipo_comision) ? data.tipo_comision : undefined,
        codigo_cuspp: (isAFP && data.codigo_cuspp) ? data.codigo_cuspp : undefined,
      })
      toast.success('Datos personales guardados')
      queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
      queryClient.invalidateQueries({ queryKey: ['empleado-data', empleadoId] })
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg ?? 'Error al guardar los datos')
    }
  }

  return (
    <div className="space-y-6">
      {/* Avatar + photo upload */}
      <div className="flex flex-col items-center gap-4">
        <Avatar className="h-24 w-24">
          <AvatarImage src={fotoDoc?.archivo_url ?? undefined} alt="Foto de perfil" />
          <AvatarFallback className="text-lg">FT</AvatarFallback>
        </Avatar>
        <div className="w-full">
          <DocumentUploadZone
            tipoDocumento="foto"
            label="Foto de perfil"
            acceptImages={true}
            existingDoc={fotoDoc}
            empleadoId={empleadoId}
          />
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">

        {/* Sub-section: Datos personales */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground border-b pb-1">
            Datos personales
          </h3>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="genero_empleado">Género</Label>
              <Controller
                name="genero_empleado"
                control={control}
                render={({ field }) => (
                  <Select onValueChange={field.onChange} value={field.value ?? ''}>
                    <SelectTrigger id="genero_empleado">
                      <SelectValue placeholder="Seleccionar..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="masculino">Masculino</SelectItem>
                      <SelectItem value="femenino">Femenino</SelectItem>
                      <SelectItem value="otro">Otro</SelectItem>
                      <SelectItem value="no_especifica">Prefiero no indicar</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="estado_civil">Estado civil</Label>
              <Controller
                name="estado_civil"
                control={control}
                render={({ field }) => (
                  <Select onValueChange={field.onChange} value={field.value ?? ''}>
                    <SelectTrigger id="estado_civil">
                      <SelectValue placeholder="Seleccionar..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="soltero">Soltero/a</SelectItem>
                      <SelectItem value="casado">Casado/a</SelectItem>
                      <SelectItem value="divorciado">Divorciado/a</SelectItem>
                      <SelectItem value="viudo">Viudo/a</SelectItem>
                      <SelectItem value="conviviente">Conviviente</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="numero_ruc">RUC</Label>
              <Input
                id="numero_ruc"
                type="text"
                placeholder="Ej: 10123456789"
                {...register('numero_ruc')}
              />
              {errors.numero_ruc && (
                <p className="text-sm text-destructive">{errors.numero_ruc.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="fecha_nacimiento">Fecha de nacimiento</Label>
              <Input
                id="fecha_nacimiento"
                type="date"
                {...register('fecha_nacimiento')}
              />
              {errors.fecha_nacimiento && (
                <p className="text-sm text-destructive">{errors.fecha_nacimiento.message}</p>
              )}
            </div>

            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="telefono_celular">Teléfono celular</Label>
              <Input
                id="telefono_celular"
                type="tel"
                placeholder="Ej: 987654321"
                {...register('telefono_celular')}
              />
              {errors.telefono_celular && (
                <p className="text-sm text-destructive">{errors.telefono_celular.message}</p>
              )}
            </div>
          </div>
        </div>

        {/* Sub-section: Domicilio */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground border-b pb-1">
            Domicilio
          </h3>

          <div className="space-y-2">
            <Label htmlFor="direccion_domicilio">Dirección</Label>
            <Input
              id="direccion_domicilio"
              type="text"
              placeholder="Ej: Av. Lima 123"
              {...register('direccion_domicilio')}
            />
            {errors.direccion_domicilio && (
              <p className="text-sm text-destructive">{errors.direccion_domicilio.message}</p>
            )}
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="distrito_domicilio">Distrito</Label>
              <Input
                id="distrito_domicilio"
                type="text"
                placeholder="Ej: Miraflores"
                {...register('distrito_domicilio')}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="provincia_domicilio">Provincia</Label>
              <Input
                id="provincia_domicilio"
                type="text"
                placeholder="Ej: Lima"
                {...register('provincia_domicilio')}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="departamento_domicilio">Departamento</Label>
              <Input
                id="departamento_domicilio"
                type="text"
                placeholder="Ej: Lima"
                {...register('departamento_domicilio')}
              />
            </div>
          </div>
        </div>

        {/* Sub-section: Sistema de pensiones */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground border-b pb-1">
            Sistema de pensiones
          </h3>

          <div className="space-y-2">
            <Label htmlFor="sistema_pensiones">Sistema de pensiones</Label>
            <Controller
              name="sistema_pensiones"
              control={control}
              render={({ field }) => (
                <Select onValueChange={field.onChange} value={field.value ?? ''}>
                  <SelectTrigger id="sistema_pensiones">
                    <SelectValue placeholder="Seleccionar..." />
                  </SelectTrigger>
                  <SelectContent>
                    {SISTEMA_PENSIONES_OPTIONS.map(opt => (
                      <SelectItem key={opt} value={opt}>{opt}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
          </div>

          {isAFP && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="codigo_cuspp">Código CUSPP</Label>
                <Input
                  id="codigo_cuspp"
                  type="text"
                  placeholder="Ej: GALA20000101"
                  {...register('codigo_cuspp')}
                />
                {errors.codigo_cuspp && (
                  <p className="text-sm text-destructive">{errors.codigo_cuspp.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="tipo_comision">Tipo de comisión</Label>
                <Controller
                  name="tipo_comision"
                  control={control}
                  render={({ field }) => (
                    <Select onValueChange={field.onChange} value={field.value ?? ''}>
                      <SelectTrigger id="tipo_comision">
                        <SelectValue placeholder="Seleccionar..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="FLUJO">Flujo</SelectItem>
                        <SelectItem value="MIXTA">Mixta</SelectItem>
                      </SelectContent>
                    </Select>
                  )}
                />
              </div>
            </div>
          )}
        </div>

        {/* Sub-section: Datos bancarios */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground border-b pb-1">
            Datos bancarios
          </h3>

          <div className="space-y-2">
            <Label htmlFor="entidad_bancaria">Entidad bancaria</Label>
            <Input
              id="entidad_bancaria"
              type="text"
              placeholder="Ej: BCP, Interbank"
              {...register('entidad_bancaria')}
            />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="numero_cuenta_bancaria">Número de cuenta</Label>
              <Input
                id="numero_cuenta_bancaria"
                type="text"
                placeholder="Ej: 19412345678901"
                {...register('numero_cuenta_bancaria')}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="numero_cci">Número CCI</Label>
              <Input
                id="numero_cci"
                type="text"
                placeholder="Ej: 00219412345678901234"
                {...register('numero_cci')}
              />
            </div>
          </div>
        </div>

        <Button type="submit" disabled={isSubmitting} className="min-h-[44px] w-full sm:w-auto">
          {isSubmitting ? 'Guardando...' : 'Guardar datos personales'}
        </Button>
      </form>

      {/* Document upload zones */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground border-b pb-1">
          Documentos de identidad
        </h3>
        <DocumentUploadZone
          tipoDocumento="dni"
          label="DNI"
          existingDoc={docs.find(d => d.tipo_documento === 'dni') ?? null}
          empleadoId={empleadoId}
        />
        <DocumentUploadZone
          tipoDocumento="carnet_extranjeria"
          label="Carné de extranjería"
          existingDoc={docs.find(d => d.tipo_documento === 'carnet_extranjeria') ?? null}
          empleadoId={empleadoId}
        />
      </div>
    </div>
  )
}
