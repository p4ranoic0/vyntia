import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog'
import { Loader2 } from 'lucide-react'
import { Area } from '@/features/organization/services/departmentsService'

const areaSchema = z.object({
  nombre_organo: z.string().min(1, 'El órgano es requerido'),
  nombre_unidad_organica: z.string().min(1, 'La unidad orgánica es requerida'),
  siglas_area: z.string().min(1, 'Las siglas son requeridas'),
  descripcion_area: z.string().optional(),
  nombre_completo: z.string().optional(),
  estado_area: z.enum(['activo', 'inactivo']).optional(),
})

type AreaFormData = z.infer<typeof areaSchema>

interface AreaFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  area?: Area | null
  onSubmit: (data: AreaFormData) => Promise<void>
  isLoading?: boolean
}

export function AreaForm({ open, onOpenChange, area, onSubmit, isLoading = false }: AreaFormProps) {
  const isEditing = !!area

  const form = useForm<AreaFormData>({
    resolver: zodResolver(areaSchema),
    defaultValues: {
      nombre_organo: area?.nombre_organo || '',
      nombre_unidad_organica: area?.nombre_unidad_organica || '',
      siglas_area: area?.siglas_area || '',
      descripcion_area: area?.descripcion_area || '',
      nombre_completo: area?.nombre_completo || '',
      estado_area: area?.estado_area || 'activo',
    },
  })

  React.useEffect(() => {
    if (area) {
      form.reset({
        nombre_organo: area.nombre_organo,
        nombre_unidad_organica: area.nombre_unidad_organica || '',
        siglas_area: area.siglas_area,
        descripcion_area: area.descripcion_area || '',
        nombre_completo: area.nombre_completo || '',
        estado_area: area.estado_area || 'activo',
      })
    } else {
      form.reset({
        nombre_organo: '',
        nombre_unidad_organica: '',
        siglas_area: '',
        descripcion_area: '',
        nombre_completo: '',
        estado_area: 'activo',
      })
    }
  }, [area, form])

  const handleSubmit = async (data: AreaFormData) => {
    try {
      await onSubmit(data)
      form.reset()
      onOpenChange(false)
    } catch {
      // Error handling is done in the parent component
    }
  }

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      form.reset()
    }
    onOpenChange(newOpen)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? 'Editar Área' : 'Nueva Área'}
          </DialogTitle>
          <DialogDescription>
            {isEditing 
              ? 'Modifica los datos del área seleccionada.'
              : 'Completa los datos para crear una nueva área.'}
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="nombre_organo">Órgano</Label>
            <Input
              id="nombre_organo"
              placeholder="Ingresa el órgano"
              {...form.register('nombre_organo')}
              disabled={isLoading}
            />
            {form.formState.errors.nombre_organo && (
              <p className="text-sm text-destructive">
                {form.formState.errors.nombre_organo.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="nombre_unidad_organica">Unidad Orgánica</Label>
            <Input
              id="nombre_unidad_organica"
              placeholder="Ingresa la unidad orgánica"
              {...form.register('nombre_unidad_organica')}
              disabled={isLoading}
            />
            {form.formState.errors.nombre_unidad_organica && (
              <p className="text-sm text-destructive">
                {form.formState.errors.nombre_unidad_organica.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="siglas_area">Siglas</Label>
            <Input
              id="siglas_area"
              placeholder="Ingresa las siglas"
              {...form.register('siglas_area')}
              disabled={isLoading}
            />
            {form.formState.errors.siglas_area && (
              <p className="text-sm text-destructive">
                {form.formState.errors.siglas_area.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="descripcion_area">Descripción</Label>
            <Input
              id="descripcion_area"
              placeholder="Describe las funciones del área"
              {...form.register('descripcion_area')}
              disabled={isLoading}
            />
            {form.formState.errors.descripcion_area && (
              <p className="text-sm text-destructive">
                {form.formState.errors.descripcion_area.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="nombre_completo">Jefe de Área</Label>
            <Input
              id="nombre_completo"
              placeholder="Nombre del jefe de área"
              {...form.register('nombre_completo')}
              disabled={isLoading}
            />
            {form.formState.errors.nombre_completo && (
              <p className="text-sm text-destructive">
                {form.formState.errors.nombre_completo.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="estado_area">Estado</Label>
            <select
              id="estado_area"
              {...form.register('estado_area')}
              disabled={isLoading}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <option value="activo">Activo</option>
              <option value="inactivo">Inactivo</option>
            </select>
            {form.formState.errors.estado_area && (
              <p className="text-sm text-destructive">
                {form.formState.errors.estado_area.message}
              </p>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={isLoading}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {isEditing ? 'Actualizar' : 'Crear'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}