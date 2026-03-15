import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Plus, Trash2, Upload, X } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { DocumentUploadZone } from './DocumentUploadZone'
import { DocumentPreviewModal } from './DocumentPreviewModal'
import {
  getFamiliares,
  createFamiliar,
  deleteFamiliar,
} from '../services/onboardingDataService'
import { subirDocumento } from '../services/onboardingUploadService'
import { cn } from '@/lib/utils'

interface OnboardingTabFamiliarProps {
  empleadoId: number
  docs?: import('../types/onboarding').DocumentInfo[]
}

type Parentesco = 'hijo' | 'hija' | 'conyuge' | 'conviviente' | 'padre' | 'madre'

interface FamiliarFormState {
  nombres_familiar: string
  apellido_paterno: string
  apellido_materno: string
  parentesco: Parentesco | ''
  fecha_nacimiento: string
  numero_documento: string
}

const EMPTY_FORM: FamiliarFormState = {
  nombres_familiar: '',
  apellido_paterno: '',
  apellido_materno: '',
  parentesco: '',
  fecha_nacimiento: '',
  numero_documento: '',
}

function getRequiredDocs(parentesco: string): Array<{ tipoDocumento: string; label: string }> {
  if (parentesco === 'hijo' || parentesco === 'hija' || parentesco === 'padre' || parentesco === 'madre') {
    return [
      { tipoDocumento: 'dni_familiar', label: 'DNI del familiar' },
      { tipoDocumento: 'certificado_nacimiento', label: 'Partida de nacimiento' },
    ]
  }
  if (parentesco === 'conyuge' || parentesco === 'conviviente') {
    return [
      { tipoDocumento: 'dni_familiar', label: 'DNI del familiar' },
      { tipoDocumento: 'acta_matrimonio', label: 'Acta de matrimonio / Cert. union de hecho' },
    ]
  }
  return [{ tipoDocumento: 'dni_familiar', label: 'DNI del familiar' }]
}

function getDocTypes(parentesco: string): Array<{ tipo: string; label: string }> {
  if (['hijo', 'hija'].includes(parentesco)) {
    return [
      { tipo: 'dni_familiar', label: 'DNI del familiar' },
      { tipo: 'certificado_nacimiento', label: 'Partida de nacimiento' },
    ]
  }
  if (['conyuge', 'conviviente'].includes(parentesco)) {
    return [
      { tipo: 'dni_familiar', label: 'DNI del familiar' },
      { tipo: 'acta_matrimonio', label: 'Acta de matrimonio / Cert. union de hecho' },
    ]
  }
  return [
    { tipo: 'dni_familiar', label: 'DNI del familiar' },
    { tipo: 'certificado_nacimiento', label: 'Partida de nacimiento' },
  ]
}

interface CompactDropZoneProps {
  onFileSelected: (file: File) => void
  disabled?: boolean
}

function CompactDropZone({ onFileSelected, disabled }: CompactDropZoneProps) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'], 'image/*': ['.jpg', '.jpeg', '.png'] },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
    disabled,
    onDropAccepted: ([file]) => onFileSelected(file),
    onDropRejected: ([rejection]) => {
      const code = rejection.errors[0]?.code
      if (code === 'file-too-large') toast.error('El archivo supera los 10 MB permitidos')
      else toast.error('Solo se permiten PDF o imagenes')
    },
  })

  return (
    <div
      {...getRootProps()}
      className={cn(
        'rounded border border-dashed p-3 text-center cursor-pointer transition-colors',
        isDragActive ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50 hover:bg-muted/50',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <input {...getInputProps()} />
      <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
        <Upload className="h-3 w-3" />
        <span>{isDragActive ? 'Suelte el archivo aqui' : 'Arrastra el archivo aqui o haz clic'}</span>
      </div>
    </div>
  )
}

export function OnboardingTabFamiliar({ empleadoId }: OnboardingTabFamiliarProps) {
  const queryClient = useQueryClient()
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [form, setForm] = useState<FamiliarFormState>(EMPTY_FORM)
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null)

  // Two-phase upload state
  const [pendingDoc, setPendingDoc] = useState<{ file: File; tipo: string; label: string } | null>(null)
  const [stagedFile, setStagedFile] = useState<File | null>(null)
  const [stagedFileMeta, setStagedFileMeta] = useState<{ tipo: string; label: string } | null>(null)
  const [isDocPreviewOpen, setIsDocPreviewOpen] = useState(false)

  const { data: familiares = [], isLoading } = useQuery({
    queryKey: ['familiares', empleadoId],
    queryFn: () => getFamiliares(empleadoId),
  })

  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => createFamiliar(data),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ['familiares', empleadoId] })
      queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
      queryClient.invalidateQueries({ queryKey: ['legajo-docs', empleadoId] })
      if (pendingDoc) {
        try {
          await subirDocumento(empleadoId, pendingDoc.tipo, 'familiar', pendingDoc.label, pendingDoc.file)
          toast.success('Registro y documento guardados')
        } catch {
          toast.warning('Registro guardado. Error al subir documento — puede subirlo luego.')
        }
        setPendingDoc(null)
      } else {
        toast.success('Familiar agregado exitosamente')
      }
      setForm(EMPTY_FORM)
      setIsAddDialogOpen(false)
    },
    onError: () => {
      toast.error('Error al agregar familiar')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteFamiliar(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['familiares', empleadoId] })
      queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
      queryClient.invalidateQueries({ queryKey: ['legajo-docs', empleadoId] })
      toast.success('Familiar eliminado')
      setDeleteConfirmId(null)
    },
    onError: () => {
      toast.error('Error al eliminar familiar')
    },
  })

  const handleSubmit = () => {
    if (!form.parentesco || !form.nombres_familiar || !form.apellido_paterno) {
      toast.error('Complete los campos requeridos: nombres, apellido paterno y parentesco')
      return
    }
    createMutation.mutate({
      empleado: empleadoId,
      nombres_familiar: form.nombres_familiar,
      apellido_paterno: form.apellido_paterno,
      apellido_materno: form.apellido_materno,
      parentesco: form.parentesco,
      fecha_nacimiento: form.fecha_nacimiento || null,
      numero_documento: form.numero_documento,
    })
  }

  const handleFileSelected = (file: File, tipo: string, label: string) => {
    setStagedFile(file)
    setStagedFileMeta({ tipo, label })
    setIsDocPreviewOpen(true)
  }

  const handlePreviewConfirm = () => {
    if (stagedFile && stagedFileMeta) {
      setPendingDoc({ file: stagedFile, tipo: stagedFileMeta.tipo, label: stagedFileMeta.label })
    }
    setStagedFile(null)
    setStagedFileMeta(null)
    setIsDocPreviewOpen(false)
  }

  const handlePreviewCancel = () => {
    setStagedFile(null)
    setStagedFileMeta(null)
    setIsDocPreviewOpen(false)
  }

  const handleDialogClose = () => {
    setPendingDoc(null)
    setStagedFile(null)
    setStagedFileMeta(null)
    setIsDocPreviewOpen(false)
    setForm(EMPTY_FORM)
    setIsAddDialogOpen(false)
  }

  const handleUploadSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['familiares', empleadoId] })
    queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
    queryClient.invalidateQueries({ queryKey: ['legajo-docs', empleadoId] })
  }

  const applicableDocTypes = getDocTypes(form.parentesco ?? '')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-medium">Datos Familiares</h3>
          <p className="text-sm text-muted-foreground">Agregue la informacion de sus dependientes</p>
        </div>
        <Button onClick={() => setIsAddDialogOpen(true)} size="sm">
          <Plus className="h-4 w-4 mr-2" />
          Agregar dependiente
        </Button>
      </div>

      {isLoading && (
        <p className="text-sm text-muted-foreground">Cargando familiares...</p>
      )}

      {!isLoading && familiares.length === 0 && (
        <p className="text-sm text-muted-foreground text-center py-8">
          No ha agregado familiares aun. Use el boton "Agregar dependiente" para comenzar.
        </p>
      )}

      <div className="space-y-4">
        {familiares.map((familiar: Record<string, unknown>) => {
          const familiarId = familiar.familiar_id as number
          const parentesco = (familiar.parentesco as string) ?? ''
          const requiredDocs = getRequiredDocs(parentesco)
          return (
            <Card key={familiarId} className="border">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sm">
                      {familiar.nombres_familiar as string} {familiar.apellido_paterno as string} {familiar.apellido_materno as string}
                    </p>
                    <p className="text-xs text-muted-foreground capitalize">
                      {parentesco}
                      {familiar.fecha_nacimiento ? ` · Nac. ${familiar.fecha_nacimiento as string}` : ''}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-destructive hover:text-destructive"
                    onClick={() => setDeleteConfirmId(familiarId)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-3 pt-0">
                {requiredDocs.map((doc) => (
                  <DocumentUploadZone
                    key={`${familiarId}-${doc.tipoDocumento}`}
                    tipoDocumento={doc.tipoDocumento as import('../types/onboarding').TipoDocumento}
                    label={doc.label}
                    empleadoId={empleadoId}
                    onUploadSuccess={handleUploadSuccess}
                  />
                ))}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Add Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={(open) => { if (!open) handleDialogClose() }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Agregar dependiente</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2">
                <Label htmlFor="nombres_familiar">Nombres *</Label>
                <Input
                  id="nombres_familiar"
                  value={form.nombres_familiar}
                  onChange={(e) => setForm(f => ({ ...f, nombres_familiar: e.target.value }))}
                  placeholder="Nombres"
                />
              </div>
              <div>
                <Label htmlFor="apellido_paterno">Apellido paterno *</Label>
                <Input
                  id="apellido_paterno"
                  value={form.apellido_paterno}
                  onChange={(e) => setForm(f => ({ ...f, apellido_paterno: e.target.value }))}
                  placeholder="Apellido paterno"
                />
              </div>
              <div>
                <Label htmlFor="apellido_materno">Apellido materno</Label>
                <Input
                  id="apellido_materno"
                  value={form.apellido_materno}
                  onChange={(e) => setForm(f => ({ ...f, apellido_materno: e.target.value }))}
                  placeholder="Apellido materno"
                />
              </div>
              <div>
                <Label htmlFor="parentesco">Parentesco *</Label>
                <Select
                  value={form.parentesco}
                  onValueChange={(val) => setForm(f => ({ ...f, parentesco: val as Parentesco }))}
                >
                  <SelectTrigger id="parentesco">
                    <SelectValue placeholder="Seleccionar" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="hijo">Hijo</SelectItem>
                    <SelectItem value="hija">Hija</SelectItem>
                    <SelectItem value="conyuge">Conyuge</SelectItem>
                    <SelectItem value="conviviente">Conviviente</SelectItem>
                    <SelectItem value="padre">Padre</SelectItem>
                    <SelectItem value="madre">Madre</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="fecha_nacimiento">Fecha de nacimiento</Label>
                <Input
                  id="fecha_nacimiento"
                  type="date"
                  value={form.fecha_nacimiento}
                  onChange={(e) => setForm(f => ({ ...f, fecha_nacimiento: e.target.value }))}
                />
              </div>
              <div className="col-span-2">
                <Label htmlFor="numero_documento">N. de documento (DNI)</Label>
                <Input
                  id="numero_documento"
                  value={form.numero_documento}
                  onChange={(e) => setForm(f => ({ ...f, numero_documento: e.target.value }))}
                  placeholder="Numero de documento"
                  maxLength={12}
                />
              </div>
            </div>

            {/* Documentos (opcional) */}
            {form.parentesco && (
              <div className="space-y-2">
                <Label className="text-sm font-medium">Documentos (opcional)</Label>
                <p className="text-xs text-muted-foreground">Puede subir un documento ahora o hacerlo luego desde la tarjeta del familiar.</p>
                {applicableDocTypes.map((docType) => (
                  <div key={docType.tipo} className="space-y-1">
                    <p className="text-xs text-muted-foreground">{docType.label}</p>
                    {pendingDoc?.tipo === docType.tipo ? (
                      <div className="flex items-center gap-2 rounded border border-primary/30 bg-primary/5 px-3 py-2">
                        <span className="flex-1 text-xs truncate">{pendingDoc.file.name}</span>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="h-5 w-5 p-0"
                          onClick={() => setPendingDoc(null)}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ) : (
                      <CompactDropZone
                        onFileSelected={(file) => handleFileSelected(file, docType.tipo, docType.label)}
                        disabled={createMutation.isPending}
                      />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={handleDialogClose}>
              Cancelar
            </Button>
            <Button onClick={handleSubmit} disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Guardando...' : 'Guardar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Document Preview Modal (outside add dialog) */}
      <DocumentPreviewModal
        file={stagedFile}
        archivoUrl={null}
        label={stagedFileMeta?.label ?? 'Vista previa'}
        isOpen={isDocPreviewOpen}
        onConfirm={handlePreviewConfirm}
        onCancel={handlePreviewCancel}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmId !== null} onOpenChange={(open) => { if (!open) setDeleteConfirmId(null) }}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Confirmar eliminacion</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Esta accion eliminara al familiar y sus documentos asociados. Esta seguro?
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirmId(null)}>
              Cancelar
            </Button>
            <Button
              variant="destructive"
              onClick={() => { if (deleteConfirmId !== null) deleteMutation.mutate(deleteConfirmId) }}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
