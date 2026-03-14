import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { useQueryClient } from '@tanstack/react-query'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import apiClient from '@/lib/api'
import { DocumentInfo } from '../types/onboarding'
import { DocumentUploadZone } from './DocumentUploadZone'

const schema = z.object({
  telefono_celular: z.string().min(9, 'Mínimo 9 dígitos').max(15).optional().or(z.literal('')),
  direccion_domicilio: z.string().max(200).optional().or(z.literal('')),
  fecha_nacimiento: z.string().optional().or(z.literal('')),
})

type FormValues = z.infer<typeof schema>

interface OnboardingTabPersonalProps {
  empleadoId: number
  docs: DocumentInfo[]
  initialValues?: {
    telefono_celular?: string
    direccion_domicilio?: string
    fecha_nacimiento?: string
  }
}

export function OnboardingTabPersonal({ empleadoId, docs, initialValues }: OnboardingTabPersonalProps) {
  const queryClient = useQueryClient()
  const fotoDoc = docs.find(d => d.tipo_documento === 'foto') ?? null

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      telefono_celular: initialValues?.telefono_celular ?? '',
      direccion_domicilio: initialValues?.direccion_domicilio ?? '',
      fecha_nacimiento: initialValues?.fecha_nacimiento ?? '',
    },
  })

  const onSubmit = async (data: FormValues) => {
    try {
      await apiClient.patch(`/api/v1/rrhh/empleados/${empleadoId}/`, {
        telefono_celular: data.telefono_celular || undefined,
        direccion_domicilio: data.direccion_domicilio || undefined,
        fecha_nacimiento: data.fecha_nacimiento || undefined,
      })
      toast.success('Datos personales guardados')
      queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg ?? 'Error al guardar los datos')
    }
  }

  return (
    <div className="space-y-6">
      {/* Section 1: Avatar + photo upload */}
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

      {/* Section 2: Editable personal fields */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-2">
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

        <div className="space-y-2">
          <Label htmlFor="direccion_domicilio">Dirección domicilio</Label>
          <Input
            id="direccion_domicilio"
            type="text"
            placeholder="Ej: Av. Lima 123, Miraflores"
            {...register('direccion_domicilio')}
          />
          {errors.direccion_domicilio && (
            <p className="text-sm text-destructive">{errors.direccion_domicilio.message}</p>
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

        <Button type="submit" disabled={isSubmitting} className="min-h-[44px]">
          {isSubmitting ? 'Guardando...' : 'Guardar datos personales'}
        </Button>
      </form>

      {/* Section 3: Document upload zones */}
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
  )
}
