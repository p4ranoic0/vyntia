import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { legajoService, TIPO_DOCUMENTO_LABELS } from '@/services/legajoService'
import { Eye, FileText, Loader2, Trash2, Upload } from 'lucide-react'
import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { toast } from 'sonner'

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

interface AdminDocUploadProps {
  empleadoId: string
  tipoDocumento: string
  categoria: string
  label?: string
  /** Existing document info */
  existing?: { id: string; nombre_documento: string; archivo?: string } | null
  onUploaded?: () => void
  onDeleted?: () => void
  acceptImages?: boolean
  compact?: boolean
}

export function AdminDocUpload({
  empleadoId,
  tipoDocumento,
  categoria,
  label,
  existing,
  onUploaded,
  onDeleted,
  acceptImages = false,
  compact = false,
}: AdminDocUploadProps) {
  const [uploading, setUploading] = useState(false)
  const displayLabel = label || TIPO_DOCUMENTO_LABELS[tipoDocumento] || tipoDocumento

  const handleUpload = useCallback(async (file: File) => {
    if (file.size > MAX_FILE_SIZE) {
      toast.error('El archivo no debe superar 10 MB')
      return
    }
    setUploading(true)
    try {
      await legajoService.create({
        empleado: empleadoId,
        tipo_documento: tipoDocumento,
        categoria,
        nombre_documento: displayLabel,
        archivo: file,
        estado_documento: 'activo',
        nivel_acceso: 'restringido',
      })
      toast.success(`${displayLabel} subido correctamente`)
      onUploaded?.()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al subir documento')
    } finally {
      setUploading(false)
    }
  }, [empleadoId, tipoDocumento, categoria, displayLabel, onUploaded])

  const handleDelete = useCallback(async () => {
    if (!existing) return
    if (!globalThis.confirm('¿Eliminar este documento?')) return
    try {
      await legajoService.delete(existing.id)
      toast.success('Documento eliminado')
      onDeleted?.()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al eliminar')
    }
  }, [existing, onDeleted])

  const acceptTypes: Record<string, string[]> = acceptImages
    ? { 'image/jpeg': ['.jpg', '.jpeg'], 'image/png': ['.png'], 'application/pdf': ['.pdf'] }
    : { 'application/pdf': ['.pdf'] }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: acceptTypes,
    maxFiles: 1,
    disabled: uploading,
    onDrop: (accepted) => {
      if (accepted.length > 0) handleUpload(accepted[0])
    },
  })

  if (existing) {
    return (
      <div className={cn(
        'flex items-center gap-2 rounded-md border bg-muted/30 px-3',
        compact ? 'py-1.5' : 'py-2',
      )}>
        <FileText className="h-4 w-4 text-green-600 shrink-0" />
        <span className="text-sm truncate flex-1">{existing.nombre_documento}</span>
        {existing.archivo && (
          <Button
            size="icon" variant="ghost" className="h-7 w-7"
            onClick={() => {
              if (existing.archivo) window.open(existing.archivo, '_blank')
            }}
          >
            <Eye className="h-3.5 w-3.5" />
          </Button>
        )}
        <Button
          size="icon" variant="ghost" className="h-7 w-7 text-destructive"
          onClick={handleDelete}
        >
          <Trash2 className="h-3.5 w-3.5" />
        </Button>
      </div>
    )
  }

  return (
    <div
      {...getRootProps()}
      className={cn(
        'flex items-center justify-center gap-2 rounded-md border-2 border-dashed cursor-pointer transition-colors',
        isDragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50',
        compact ? 'px-3 py-2' : 'px-4 py-3',
      )}
    >
      <input {...getInputProps()} />
      {uploading ? (
        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
      ) : (
        <Upload className="h-4 w-4 text-muted-foreground" />
      )}
      <span className="text-xs text-muted-foreground">
        {(() => {
          if (uploading) return 'Subiendo...'
          if (isDragActive) return 'Soltar aquí'
          return `${displayLabel} (${acceptImages ? 'PDF/IMG' : 'PDF'})`
        })()}
      </span>
    </div>
  )
}
