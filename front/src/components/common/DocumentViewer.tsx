import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Download, X } from 'lucide-react'

interface DocumentViewerProps {
  url: string
  nombre: string
  open: boolean
  onClose: () => void
}

export function DocumentViewer({ url, nombre, open, onClose }: DocumentViewerProps) {
  const extension = url.split('.').pop()?.toLowerCase() || ''
  const isImage = ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension)
  const isPdf = extension === 'pdf'
  const [blobUrl, setBlobUrl] = useState('')

  // Fetch PDF as blob to avoid X-Frame-Options cross-origin block
  useEffect(() => {
    if (!open || !isPdf) return

    let currentBlobUrl = ''
    let cancelled = false

    fetch(url, { credentials: 'include' })
      .then(r => r.blob())
      .then(blob => {
        if (cancelled) return
        currentBlobUrl = URL.createObjectURL(blob)
        setBlobUrl(currentBlobUrl)
      })
      .catch(() => {
        if (!cancelled) setBlobUrl('')
      })

    return () => {
      cancelled = true
      if (currentBlobUrl) URL.revokeObjectURL(currentBlobUrl)
      setBlobUrl('')
    }
  }, [open, url, isPdf])

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl h-[85vh] flex flex-col p-0">
        <DialogHeader className="px-6 pt-4 pb-2 flex flex-row items-center justify-between border-b">
          <DialogTitle className="text-sm font-medium truncate pr-4">{nombre}</DialogTitle>
          <div className="flex items-center gap-2 shrink-0">
            <Button variant="outline" size="sm" asChild>
              <a href={url} download target="_blank" rel="noopener noreferrer">
                <Download className="h-4 w-4 mr-1" />
                Descargar
              </a>
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>
        <div className="flex-1 overflow-hidden p-4">
          {isPdf ? (
            blobUrl ? (
              <iframe
                src={blobUrl}
                className="w-full h-full rounded border"
                title={nombre}
              />
            ) : (
              <div className="flex flex-col items-center justify-center h-full gap-4">
                <p className="text-muted-foreground text-sm">Cargando PDF...</p>
              </div>
            )
          ) : isImage ? (
            <div className="w-full h-full flex items-center justify-center bg-muted/30 rounded">
              <img
                src={url}
                alt={nombre}
                className="max-w-full max-h-full object-contain"
              />
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full gap-4">
              <p className="text-muted-foreground">Vista previa no disponible para este tipo de archivo.</p>
              <Button asChild>
                <a href={url} download target="_blank" rel="noopener noreferrer">
                  <Download className="h-4 w-4 mr-2" />
                  Descargar archivo
                </a>
              </Button>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
