import React, { useEffect, useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { FileText, X } from 'lucide-react'

interface DocumentPreviewModalProps {
  file: File | null
  archivoUrl?: string | null   // for already-uploaded docs (RRHH preview)
  label: string
  isOpen: boolean
  isUploading?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function DocumentPreviewModal({
  file,
  archivoUrl,
  label,
  isOpen,
  isUploading = false,
  onConfirm,
  onCancel,
}: DocumentPreviewModalProps) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isImage, setIsImage] = useState(false)

  useEffect(() => {
    if (!isOpen) return
    if (file) {
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      setIsImage(file.type.startsWith('image/'))
      return () => {
        URL.revokeObjectURL(url)
        setPreviewUrl(null)
      }
    } else if (archivoUrl) {
      setPreviewUrl(archivoUrl)
      setIsImage(/\.(jpg|jpeg|png)$/i.test(archivoUrl))
    }
  }, [file, archivoUrl, isOpen])

  const fileSize = file ? (file.size / 1024 / 1024).toFixed(2) : null

  return (
    <Dialog open={isOpen} onOpenChange={(open) => { if (!open) onCancel() }}>
      <DialogContent className="max-w-2xl max-h-[90vh] flex flex-col gap-4">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            {label}
            {fileSize && (
              <span className="text-sm font-normal text-muted-foreground ml-2">({fileSize} MB)</span>
            )}
          </DialogTitle>
        </DialogHeader>

        <div className="flex-1 min-h-0">
          {previewUrl ? (
            isImage ? (
              <img
                src={previewUrl}
                alt={label}
                className="w-full max-h-96 object-contain rounded border"
              />
            ) : (
              <iframe
                src={previewUrl}
                title={label}
                className="w-full h-96 border rounded"
              />
            )
          ) : (
            <div className="flex items-center justify-center h-48 bg-muted rounded border text-muted-foreground">
              Cargando vista previa...
            </div>
          )}
        </div>

        <DialogFooter className="flex gap-2 justify-end">
          <Button variant="outline" onClick={onCancel} disabled={isUploading}>
            <X className="h-4 w-4 mr-1" />
            Cancelar
          </Button>
          <Button onClick={onConfirm} disabled={isUploading}>
            {isUploading ? 'Enviando...' : 'Enviar documento'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
