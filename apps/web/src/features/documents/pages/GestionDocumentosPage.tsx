import React, { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Building2, Upload, Search, FileUp, X, FileText } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/shared/ui/select'
import { Textarea } from '@/shared/ui/textarea'
import {
  Dialog, DialogContent, DialogDescription, DialogFooter,
  DialogHeader, DialogTitle,
} from '@/shared/ui/dialog'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { toast } from 'sonner'
import {
  legajoService,
  TIPO_DOCUMENTO_LABELS,
  CATEGORIA_LABELS,
} from '@/features/documents/services/legajoService'
import { employeesService } from '@/features/employees/services/employeesService'

/* --------------------------------------------------------
   Institutional document types allowed for upload
   -------------------------------------------------------- */

const TIPOS_INSTITUCIONALES_UPLOAD: Record<string, string> = {
  boleta_pago: 'Boleta de Pago',
  constancia_trabajo: 'Constancia de Trabajo',
  constancia_participacion: 'Constancia de Participacion',
  constancia_haberes: 'Constancia de Haberes',
  resolucion_encargatura: 'Resolucion de Encargatura',
  resolucion_licencia: 'Resolucion de Licencia',
  resolucion_sancion: 'Resolucion de Sancion',
  contrato_trabajo: 'Contrato de Trabajo',
  adenda_contrato: 'Adenda de Contrato',
  memorandum: 'Memorandum',
  carta_amonestacion: 'Carta de Amonestacion',
  carta_cese: 'Carta de Cese',
  evaluacion_desempeno: 'Evaluacion de Desempeno',
}

/* --------------------------------------------------------
   Auto-suggest document name based on selected type
   -------------------------------------------------------- */

function sugerirNombre(tipo: string): string {
  const hoy = new Date()
  const fecha = hoy.toLocaleDateString('es-PE', { year: 'numeric', month: '2-digit', day: '2-digit' })
  const label = TIPOS_INSTITUCIONALES_UPLOAD[tipo]
  if (!label) return ''
  return `${label} - ${fecha}`
}

/* --------------------------------------------------------
   Employee interface (raw shape from getAll)
   -------------------------------------------------------- */

interface EmpleadoOption {
  id: string
  nombres_empleado: string
  apellido_paterno: string
  apellido_materno: string
}

/* --------------------------------------------------------
   Form state
   -------------------------------------------------------- */

interface FormState {
  tipo_documento: string
  nombre_documento: string
  descripcion: string
  fecha_emision: string
  periodo: string
  archivos: File[]
}

const INITIAL_FORM: FormState = {
  tipo_documento: '',
  nombre_documento: '',
  descripcion: '',
  fecha_emision: '',
  periodo: '',
  archivos: [],
}

/* --------------------------------------------------------
   ConfirmDialog
   -------------------------------------------------------- */

function ConfirmDialog({
  open,
  empleadoNombre,
  tipoLabel,
  cantidadArchivos,
  onConfirm,
  onCancel,
  submitting,
}: {
  open: boolean
  empleadoNombre: string
  tipoLabel: string
  cantidadArchivos: number
  onConfirm: () => void
  onCancel: () => void
  submitting: boolean
}) {
  return (
    <Dialog open={open} onOpenChange={onCancel}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Confirmar subida</DialogTitle>
          <DialogDescription>
            Se subira {cantidadArchivos} archivo{cantidadArchivos > 1 ? 's' : ''} de tipo{' '}
            <strong>{tipoLabel}</strong> al legajo de <strong>{empleadoNombre}</strong>.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={onCancel} disabled={submitting}>
            Cancelar
          </Button>
          <Button onClick={onConfirm} disabled={submitting}>
            {submitting ? (
              <LoadingSpinner size="sm" />
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Confirmar
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

/* --------------------------------------------------------
   GestionDocumentosPage (main)
   -------------------------------------------------------- */

export default function GestionDocumentosPage() {
  const queryClient = useQueryClient()

  // Employee selection
  const [selectedEmpleado, setSelectedEmpleado] = useState<string | null>(null)
  const [empleadoSearch, setEmpleadoSearch] = useState('')
  const [empleadoDropdownOpen, setEmpleadoDropdownOpen] = useState(false)

  // Form state
  const [form, setForm] = useState<FormState>(INITIAL_FORM)

  // Confirm dialog
  const [confirmOpen, setConfirmOpen] = useState(false)

  // Fetch employees
  const { data: empleados = [], isLoading: loadingEmpleados } = useQuery({
    queryKey: ['empleados-all'],
    queryFn: () => employeesService.getAll(),
  })

  // Filter employees by search text
  const empleadosFiltrados = useMemo(() => {
    if (!empleadoSearch.trim()) return empleados as EmpleadoOption[]
    const term = empleadoSearch.toLowerCase()
    return (empleados as EmpleadoOption[]).filter((emp) => {
      const fullName = `${emp.nombres_empleado} ${emp.apellido_paterno} ${emp.apellido_materno}`.toLowerCase()
      return fullName.includes(term)
    })
  }, [empleados, empleadoSearch])

  // Find selected employee object
  const empleadoSeleccionado = useMemo(() => {
    if (!selectedEmpleado) return null
    return (empleados as EmpleadoOption[]).find(
      (e) => e.id === selectedEmpleado,
    ) ?? null
  }, [empleados, selectedEmpleado])

  const empleadoNombreCompleto = empleadoSeleccionado
    ? `${empleadoSeleccionado.nombres_empleado} ${empleadoSeleccionado.apellido_paterno} ${empleadoSeleccionado.apellido_materno}`
    : ''

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: legajoService.subirInstitucional,
    onSuccess: (result) => {
      const count = Array.isArray(result) ? result.length : 1
      toast.success(
        `${count} documento${count > 1 ? 's' : ''} subido${count > 1 ? 's' : ''} exitosamente`,
      )
      // Reset form after success
      setForm(INITIAL_FORM)
      setConfirmOpen(false)
      // Invalidate legajo queries for this employee
      queryClient.invalidateQueries({ queryKey: ['documentos', selectedEmpleado] })
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Error al subir documento(s)')
      setConfirmOpen(false)
    },
  })

  // Handlers
  const updateForm = (field: keyof FormState, value: string | File[]) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleTipoChange = (tipo: string) => {
    setForm((prev) => ({
      ...prev,
      tipo_documento: tipo,
      nombre_documento: prev.nombre_documento || sugerirNombre(tipo),
    }))
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files) {
      updateForm('archivos', Array.from(files))
    }
  }

  const removeFile = (index: number) => {
    setForm((prev) => ({
      ...prev,
      archivos: prev.archivos.filter((_, i) => i !== index),
    }))
  }

  const handleSelectEmpleado = (emp: EmpleadoOption) => {
    setSelectedEmpleado(emp.id)
    setEmpleadoSearch('')
    setEmpleadoDropdownOpen(false)
  }

  const clearEmpleado = () => {
    setSelectedEmpleado(null)
    setEmpleadoSearch('')
  }

  const canSubmit =
    selectedEmpleado !== null &&
    form.tipo_documento !== '' &&
    form.archivos.length > 0

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!canSubmit) {
      toast.error('Seleccione un empleado, tipo de documento y al menos un archivo')
      return
    }
    setConfirmOpen(true)
  }

  const handleConfirmUpload = () => {
    if (!selectedEmpleado) return
    uploadMutation.mutate({
      empleado: selectedEmpleado,
      tipo_documento: form.tipo_documento,
      nombre_documento: form.nombre_documento || undefined,
      descripcion: form.descripcion || undefined,
      fecha_emision: form.fecha_emision || undefined,
      periodo: form.periodo || undefined,
      archivos: form.archivos,
    })
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Building2 className="h-6 w-6 text-purple-600" />
          Gestion de Documentos Institucionales
        </h1>
        <p className="text-muted-foreground text-sm mt-1">
          Suba documentos institucionales al legajo digital de los empleados
        </p>
      </div>

      {/* Employee selector */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Seleccionar Empleado</CardTitle>
          <CardDescription>
            Busque y seleccione al empleado destino del documento
          </CardDescription>
        </CardHeader>
        <CardContent>
          {empleadoSeleccionado ? (
            <div className="flex items-center justify-between p-3 border rounded-lg bg-muted/30">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-50 rounded-lg">
                  <Building2 className="h-4 w-4 text-purple-600" />
                </div>
                <div>
                  <p className="font-medium text-sm">{empleadoNombreCompleto}</p>
                  <p className="text-xs text-muted-foreground">
                    ID: {empleadoSeleccionado.id}
                  </p>
                </div>
              </div>
              <Button variant="ghost" size="sm" onClick={clearEmpleado}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div className="relative">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar empleado por nombre..."
                  value={empleadoSearch}
                  onChange={(e) => {
                    setEmpleadoSearch(e.target.value)
                    setEmpleadoDropdownOpen(true)
                  }}
                  onFocus={() => setEmpleadoDropdownOpen(true)}
                  className="pl-10"
                />
              </div>
              {empleadoDropdownOpen && (
                <div className="absolute z-50 w-full mt-1 bg-background border rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {loadingEmpleados ? (
                    <div className="flex justify-center py-4">
                      <LoadingSpinner size="sm" />
                    </div>
                  ) : empleadosFiltrados.length === 0 ? (
                    <p className="text-center text-muted-foreground py-4 text-sm">
                      No se encontraron empleados
                    </p>
                  ) : (
                    empleadosFiltrados.map((emp) => (
                      <button
                        key={emp.id}
                        type="button"
                        className="w-full text-left px-4 py-2 hover:bg-muted/50 transition-colors text-sm"
                        onClick={() => handleSelectEmpleado(emp)}
                      >
                        <span className="font-medium">
                          {emp.apellido_paterno} {emp.apellido_materno}
                        </span>
                        , {emp.nombres_empleado}
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload form */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <FileUp className="h-5 w-5 text-purple-600" />
            Formulario de Subida
          </CardTitle>
          <CardDescription>
            Complete los datos del documento institucional a subir
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Row 1: Tipo + Nombre */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="tipo_documento">Tipo de documento *</Label>
                <Select
                  value={form.tipo_documento}
                  onValueChange={handleTipoChange}
                >
                  <SelectTrigger id="tipo_documento">
                    <SelectValue placeholder="Seleccionar tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(TIPOS_INSTITUCIONALES_UPLOAD).map(([val, label]) => (
                      <SelectItem key={val} value={val}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="nombre_documento">Nombre del documento</Label>
                <Input
                  id="nombre_documento"
                  value={form.nombre_documento}
                  onChange={(e) => updateForm('nombre_documento', e.target.value)}
                  placeholder="Se sugiere automaticamente al elegir tipo"
                />
              </div>
            </div>

            {/* Descripcion */}
            <div className="space-y-2">
              <Label htmlFor="descripcion">Descripcion</Label>
              <Textarea
                id="descripcion"
                value={form.descripcion}
                onChange={(e) => updateForm('descripcion', e.target.value)}
                placeholder="Descripcion adicional del documento..."
                rows={3}
              />
            </div>

            {/* Row 2: Fecha emision + Periodo */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="fecha_emision">Fecha de emision</Label>
                <Input
                  id="fecha_emision"
                  type="date"
                  value={form.fecha_emision}
                  onChange={(e) => updateForm('fecha_emision', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="periodo">Periodo</Label>
                <Input
                  id="periodo"
                  value={form.periodo}
                  onChange={(e) => updateForm('periodo', e.target.value)}
                  placeholder="Ej: 2026-01 (para boletas de pago)"
                />
              </div>
            </div>

            {/* File input */}
            <div className="space-y-2">
              <Label htmlFor="archivos">Archivos *</Label>
              <Input
                id="archivos"
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                onChange={handleFileChange}
              />
              <p className="text-xs text-muted-foreground">
                PDF, JPG, PNG, DOC, DOCX. Puede seleccionar multiples archivos.
              </p>
            </div>

            {/* Selected files list */}
            {form.archivos.length > 0 && (
              <div className="space-y-2">
                <Label>Archivos seleccionados ({form.archivos.length})</Label>
                <div className="space-y-1">
                  {form.archivos.map((file, index) => (
                    <div
                      key={`${file.name}-${index}`}
                      className="flex items-center justify-between p-2 border rounded-md bg-muted/20 text-sm"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <FileText className="h-4 w-4 text-muted-foreground shrink-0" />
                        <span className="truncate">{file.name}</span>
                        <span className="text-xs text-muted-foreground shrink-0">
                          ({(file.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(index)}
                        className="shrink-0"
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Submit */}
            <div className="flex justify-end pt-2">
              <Button type="submit" disabled={!canSubmit || uploadMutation.isPending} size="lg">
                {uploadMutation.isPending ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Subir Documento{form.archivos.length > 1 ? 's' : ''}
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Confirm dialog */}
      <ConfirmDialog
        open={confirmOpen}
        empleadoNombre={empleadoNombreCompleto}
        tipoLabel={TIPOS_INSTITUCIONALES_UPLOAD[form.tipo_documento] ?? form.tipo_documento}
        cantidadArchivos={form.archivos.length}
        onConfirm={handleConfirmUpload}
        onCancel={() => setConfirmOpen(false)}
        submitting={uploadMutation.isPending}
      />
    </div>
  )
}
