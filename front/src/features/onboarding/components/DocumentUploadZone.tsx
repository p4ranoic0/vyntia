import { useDropzone } from 'react-dropzone'
import { toast } from 'sonner'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Upload, FileText, AlertCircle } from 'lucide-react'
import { useState } from 'react'
import { TipoDocumento, DocumentInfo, UploadDocumentResponse } from '../types/onboarding'
import { uploadDocument, uploadFoto } from '../services/onboardingUploadService'
import { useQueryClient } from '@tanstack/react-query'
import { cn } from '@/lib/utils'
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
  const [pendingFile, setPendingFile] = useState<File | null>(null)
  const [isPreviewOpen, setIsPreviewOpen] = useState(false)
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
      toast.success(`${label} subido exitosamente`)
      queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
      onUploadSuccess?.(result)
      setShowReplace(false)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      toast.error(msg ?? `Error al subir ${label}`)
    } finally {
      setUploading(false)
    }
  }

  const handlePreviewConfirm = () => {
    if (pendingFile) {
      handleUpload(pendingFile)  // existing upload function — no changes needed inside
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
    onDropRejected: ([rejection]) => {
      const code = rejection.errors[0]?.code
      if (code === 'file-too-large') toast.error('El archivo supera los 10 MB permitidos')
      else toast.error(acceptImages ? 'Solo se permiten imágenes JPG o PNG' : 'Solo se permiten archivos PDF')
    },
  })

  const estadoBadge = (estado: string) => {
    if (estado === 'aprobado') return <Badge className="bg-green-100 text-green-800">Aprobado</Badge>
    if (estado === 'rechazado') return <Badge className="bg-red-100 text-red-800">Rechazado</Badge>
    return <Badge className="bg-yellow-100 text-yellow-800">Pendiente revisión</Badge>
  }

  // When doc exists and not in replace mode: show info card
  if (existingDoc && !showReplace) {
    return (
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
        <Button variant="outline" size="sm" onClick={() => setShowReplace(true)}>
          Reemplazar
        </Button>
      </div>
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
            ? "Suelte el archivo aquí"
            : uploading
            ? "Subiendo..."
            : `Arrastre o haga clic — ${acceptImages ? 'JPG/PNG' : 'PDF'}, máx. 10 MB`
          }
        </p>
        {showReplace && (
          <Button variant="ghost" size="sm" className="mt-2" onClick={(e) => { e.stopPropagation(); setShowReplace(false) }}>
            Cancelar
          </Button>
        )}
      </div>
    </>
  )
}
