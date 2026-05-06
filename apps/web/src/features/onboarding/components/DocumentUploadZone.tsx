import { useDropzone } from 'react-dropzone'
import { toast } from 'sonner'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Upload, FileText, AlertCircle } from 'lucide-react'
import { useState } from 'react'
import { TipoDocumento, DocumentInfo, UploadDocumentResponse } from '../types/onboarding'
import { uploadDocument, uploadFoto } from '../services/onboardingUploadService'
import { useQueryClient } from '@tanstack/react-query'
import { cn } from '@/shared/utils/cn'
import { DocumentPreviewModal } from './DocumentPreviewModal'

interface DocumentUploadZoneProps {
  tipoDocumento: TipoDocumento
  label: string
  acceptImages?: boolean // true only for profile photo
  existingDoc?: DocumentInfo | null
  empleadoId: number
  onUploadSuccess?: (result: UploadDocumentResponse) => void
}

export function DocumentUploadZone({
  tipoDocumento, label, acceptImages = false, existingDoc, onUploadSuccess
}: DocumentUploadZoneProps) {
  const [uploading, setUploading] = useState(false)
  const [showReplace, setShowReplace] = useState(false)
  const [localOverrideEmpty, setLocalOverrideEmpty] = useState(false)
  const [pendingFile, setPendingFile] = useState<File | null>(null)
  const [isPreviewOpen, setIsPreviewOpen] = useState(false)
  const [isViewOpen, setIsViewOpen] = useState(false)
  const queryClient = useQueryClient()

  const handleUpload = async (file: File) => {
    setUploading(true)
    try {
      let result: UploadDocumentResponse
      if (acceptImages) {
        result = await uploadFoto(file)
      } else {
        result = await uploadDocument(tipoDocumento, file, label)
      }
      toast.success('Documento enviado correctamente')
      queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
      queryClient.invalidateQueries({ queryKey: ['legajo-docs'] })
      onUploadSuccess?.(result)
      setShowReplace(false)
      setLocalOverrideEmpty(false)
    } catch (error: unknown) {
      if (error && typeof error === 'object' && 'code' in error && (error as { code?: string }).code === 'ERR_NETWORK') {
        toast.error('Sin conexion. Verifica tu internet.')
      } else if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { status?: number; data?: { message?: string } } }
        if (axiosError.response?.status === 400) {
          toast.warning(axiosError.response?.data?.message ?? 'Error al subir el documento. Intenta nuevamente.')
        } else {
          toast.error('Error al subir el documento. Intenta nuevamente.')
        }
      } else {
        toast.error('Error al subir el documento. Intenta nuevamente.')
      }
    } finally {
      setUploading(false)
    }
  }

  const handlePreviewConfirm = () => {
    if (pendingFile) {
      handleUpload(pendingFile)
      setIsPreviewOpen(false)
      setPendingFile(null)
    }
  }

  const handlePreviewCancel = () => {
    setIsPreviewOpen(false)
    setPendingFile(null)
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: acceptImages
      ? { 'image/jpeg': ['.jpg', '.jpeg'], 'image/png': ['.png'] }
      : { 'application/pdf': ['.pdf'] },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
    disabled: uploading,
    onDropAccepted: (files) => {
      setPendingFile(files[0])
      setIsPreviewOpen(true)
    },
    onDropRejected: (rejections) => {
      const code = rejections[0]?.errors[0]?.code
      if (code === 'file-too-large') {
        toast.error('El archivo supera el limite de 10MB')
      } else if (code === 'file-invalid-type') {
        if (acceptImages) {
          toast.error('Formato no valido — solo JPG o PNG')
        } else {
          toast.error('Formato no valido — solo PDF')
        }
      } else {
        toast.error('Archivo no permitido')
      }
    },
  })

  const estadoBadge = (estado: string) => {
    if (estado === 'aprobado') return <Badge className="bg-green-100 text-green-800">Aprobado</Badge>
    if (estado === 'rechazado') return <Badge className="bg-red-100 text-red-800">Rechazado</Badge>
    return <Badge className="bg-yellow-100 text-yellow-800">Pendiente revision</Badge>
  }

  // When doc exists in rejected state and user clicked "Corregir y reenviar": show dropzone
  // When doc exists in replace mode: show dropzone
  // When doc exists and neither override nor replace: show info card
  if (existingDoc && !showReplace && !localOverrideEmpty) {
    return (
      <>
        <DocumentPreviewModal
          file={null}
          archivoUrl={existingDoc?.archivo_url}
          label={existingDoc?.nombre_documento ?? label}
          isOpen={isViewOpen}
          isViewOnly={true}
          onConfirm={() => setIsViewOpen(false)}
          onCancel={() => setIsViewOpen(false)}
        />
        <div className="rounded-lg border border-border p-4 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">{existingDoc.nombre_documento}</span>
              {existingDoc.fecha_subida && (
                <span className="text-muted-foreground">
                  {new Date(existingDoc.fecha_subida).toLocaleDateString('es-PE')}
                </span>
              )}
            </div>
            {estadoBadge(existingDoc.estado_documento)}
          </div>
          {existingDoc.estado_documento === 'rechazado' && existingDoc.observaciones && (
            <div className="flex items-start gap-2 text-sm text-red-700 bg-red-50 rounded p-2">
              <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <span>{existingDoc.observaciones}</span>
            </div>
          )}
          <div className="flex items-center gap-2 mt-2">
            {existingDoc.archivo_url && (
              <Button
                variant="ghost"
                size="sm"
                type="button"
                onClick={() => setIsViewOpen(true)}
              >
                Ver documento
              </Button>
            )}
            {existingDoc.estado_documento === 'rechazado' ? (
              <Button
                variant="outline"
                size="sm"
                className="border-red-300 text-red-600 hover:bg-red-50"
                onClick={() => setLocalOverrideEmpty(true)}
              >
                Corregir y reenviar
              </Button>
            ) : (
              <Button variant="outline" size="sm" onClick={() => setShowReplace(true)}>
                Reemplazar
              </Button>
            )}
          </div>
        </div>
      </>
    )
  }

  // Dropzone state
  return (
    <>
      <DocumentPreviewModal
        file={pendingFile}
        label={label}
        isOpen={isPreviewOpen}
        isUploading={uploading}
        onConfirm={handlePreviewConfirm}
        onCancel={handlePreviewCancel}
      />
      <div
        {...getRootProps()}
        className={cn(
          "rounded-lg border-2 border-dashed p-6 text-center cursor-pointer transition-colors",
          isDragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 hover:bg-muted/50",
          uploading && "opacity-50 cursor-not-allowed"
        )}
      >
        <input {...getInputProps()} />
        <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
        <p className="text-sm font-medium">{label}</p>
        <p className="text-xs text-muted-foreground mt-1">
          {isDragActive
            ? "Suelte el archivo aqui"
            : uploading
            ? "Subiendo..."
            : `Arrastre o haga clic — ${acceptImages ? 'JPG/PNG' : 'PDF'}, max. 10 MB`
          }
        </p>
        {(showReplace || localOverrideEmpty) && (
          <Button
            variant="ghost"
            size="sm"
            className="mt-2"
            onClick={(e) => {
              e.stopPropagation()
              setShowReplace(false)
              setLocalOverrideEmpty(false)
            }}
          >
            Cancelar
          </Button>
        )}
      </div>
    </>
  )
}
