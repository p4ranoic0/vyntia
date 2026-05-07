import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { ArrowLeft, Save, Building2 } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import { Textarea } from '@/shared/ui/textarea'
import { Label } from '@/shared/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui/select'
// Form components no disponibles - usando formularios HTML nativos
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { useToast } from '@/shared/ui/use-toast'
import { departmentsService, Area, CreateAreaData } from '@/features/organization/services/departmentsService'
import { AreasLayout } from '@/shared/layout/AreasLayout'
import { getErrorMessage } from '@/shared/api/errorUtils'

// Schema de validación
const areaSchema = z.object({
  nombre_organo: z.string().min(1, 'El órgano es requerido'),
  nombre_unidad_organica: z.string().optional(),
  siglas_area: z.string().min(1, 'Las siglas son requeridas').max(10, 'Las siglas no pueden exceder 10 caracteres'),
  nombre_completo: z.string().optional(),
  descripcion_area: z.string().optional(),
  estado_area: z.enum(['activo', 'inactivo']).default('activo'),
})

type AreaFormData = z.infer<typeof areaSchema>

export function AreaFormPage() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const isEditing = Boolean(id)

  const form = useForm<AreaFormData>({
    resolver: zodResolver(areaSchema),
    defaultValues: {
      nombre_organo: '',
      nombre_unidad_organica: '',
      siglas_area: '',
      nombre_completo: '',
      descripcion_area: '',
      estado_area: 'activo',
    },
  })

  // Cargar datos del área si estamos editando
  const { data: areaData, isLoading: isLoadingArea } = useQuery({
    queryKey: ['area', id],
    queryFn: () => departmentsService.getArea(Number(id)),
    enabled: isEditing,
  })

  // Nota: La asignación de jefe se maneja desde la gestión de empleados

  // Llenar el formulario cuando se cargan los datos del área
  useEffect(() => {
    if (areaData && isEditing) {
      form.reset({
        nombre_organo: areaData.nombre_organo || '',
        nombre_unidad_organica: areaData.nombre_unidad_organica || '',
        siglas_area: areaData.siglas_area || '',
        nombre_completo: areaData.nombre_completo || '',
        descripcion_area: areaData.descripcion_area || '',
        estado_area: areaData.estado_area || 'activo',
      })
    }
  }, [areaData, isEditing, form])

  // Mutación para crear área
  const createAreaMutation = useMutation({
    mutationFn: (data: AreaFormData) => departmentsService.createArea(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['areas'] })
      toast({
        title: 'Área creada',
        description: 'El área se ha creado exitosamente.',
      })
      navigate('/areas')
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: getErrorMessage(error, 'No se pudo crear el área.'),
        variant: 'destructive',
      })
    },
  })

  // Mutación para actualizar área
  const updateAreaMutation = useMutation({
    mutationFn: (data: AreaFormData) => departmentsService.updateArea(Number(id), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['areas'] })
      queryClient.invalidateQueries({ queryKey: ['area', id] })
      toast({
        title: 'Área actualizada',
        description: 'El área se ha actualizado exitosamente.',
      })
      navigate('/areas')
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: getErrorMessage(error, 'No se pudo actualizar el área.'),
        variant: 'destructive',
      })
    },
  })

  const onSubmit = (data: AreaFormData) => {
    if (isEditing) {
      updateAreaMutation.mutate(data)
    } else {
      createAreaMutation.mutate(data)
    }
  }

  const isLoading = createAreaMutation.isPending || updateAreaMutation.isPending

  if (isEditing && isLoadingArea) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <AreasLayout 
      title={isEditing ? 'Editar Área' : 'Nueva Área'}
      description={isEditing ? 'Modifica los datos del área' : 'Crea una nueva área organizacional'}
    >
      <div className="space-y-6">
        {/* Navigation */}
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => navigate('/areas')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver al listado
          </Button>
        </div>

      {/* Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Información del Área
          </CardTitle>
          <CardDescription>
            Completa los datos básicos del área organizacional
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Órgano */}
              <div className="space-y-2">
                <Label htmlFor="nombre_organo">Órgano *</Label>
                <Input 
                  id="nombre_organo"
                  placeholder="Ej: Gerencia General" 
                  {...form.register('nombre_organo')}
                />
                <p className="text-sm text-muted-foreground">
                  Nombre del órgano al que pertenece el área
                </p>
                {form.formState.errors.nombre_organo && (
                  <p className="text-sm text-red-600">
                    {form.formState.errors.nombre_organo.message}
                  </p>
                )}
              </div>

              {/* Unidad Orgánica */}
              <div className="space-y-2">
                <Label htmlFor="nombre_unidad_organica">Unidad Orgánica</Label>
                <Input 
                  id="nombre_unidad_organica"
                  placeholder="Ej: Recursos Humanos" 
                  {...form.register('nombre_unidad_organica')}
                />
                <p className="text-sm text-muted-foreground">
                  Nombre específico de la unidad orgánica
                </p>
                {form.formState.errors.nombre_unidad_organica && (
                  <p className="text-sm text-red-600">
                    {form.formState.errors.nombre_unidad_organica.message}
                  </p>
                )}
              </div>

              {/* Siglas */}
              <div className="space-y-2">
                <Label htmlFor="siglas_area">Siglas *</Label>
                <Input 
                  id="siglas_area"
                  placeholder="Ej: RRHH" 
                  maxLength={10}
                  {...form.register('siglas_area')}
                />
                <p className="text-sm text-muted-foreground">
                  Siglas o abreviatura del área (máx. 10 caracteres)
                </p>
                {form.formState.errors.siglas_area && (
                  <p className="text-sm text-red-600">
                    {form.formState.errors.siglas_area.message}
                  </p>
                )}
              </div>

              {/* Nombre Completo */}
              <div className="space-y-2">
                <Label htmlFor="nombre_completo">Nombre Completo</Label>
                <Input 
                  id="nombre_completo"
                  placeholder="Ej: Gerencia de Recursos Humanos" 
                  {...form.register('nombre_completo')}
                />
                <p className="text-sm text-muted-foreground">
                  Nombre completo y descriptivo del área
                </p>
                {form.formState.errors.nombre_completo && (
                  <p className="text-sm text-red-600">
                    {form.formState.errors.nombre_completo.message}
                  </p>
                )}
              </div>

              {/* Estado */}
              <div className="space-y-2">
                <Label htmlFor="estado_area">Estado</Label>
                <Select onValueChange={(value) => form.setValue('estado_area', value)} defaultValue={form.watch('estado_area')}>
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar estado" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="activo">Activo</SelectItem>
                    <SelectItem value="inactivo">Inactivo</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground">
                  Estado actual del área
                </p>
                {form.formState.errors.estado_area && (
                  <p className="text-sm text-red-600">
                    {form.formState.errors.estado_area.message}
                  </p>
                )}
              </div>
            </div>

            {/* Descripción */}
            <div className="space-y-2">
              <Label htmlFor="descripcion_area">Descripción</Label>
              <Textarea 
                id="descripcion_area"
                placeholder="Describe las funciones y responsabilidades del área..."
                className="min-h-[100px]"
                {...form.register('descripcion_area')}
              />
              <p className="text-sm text-muted-foreground">
                Descripción detallada de las funciones del área
              </p>
              {form.formState.errors.descripcion_area && (
                <p className="text-sm text-red-600">
                  {form.formState.errors.descripcion_area.message}
                </p>
              )}
            </div>

            {/* Botones */}
            <div className="flex justify-end gap-4">
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => navigate('/areas')}
                disabled={isLoading}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? (
                  <LoadingSpinner className="mr-2 h-4 w-4" />
                ) : (
                  <Save className="mr-2 h-4 w-4" />
                )}
                {isEditing ? 'Actualizar' : 'Crear'} Área
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
      </div>
    </AreasLayout>
  )
}