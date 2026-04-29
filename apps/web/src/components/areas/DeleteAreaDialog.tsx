import React from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Loader2, AlertTriangle } from 'lucide-react'

interface Area {
  id: number
  organo: string
  unidad_organica: string
  siglas: string
  descripcion?: string
  jefe?: string
  empleados_count?: number
  created_at?: string
  estado?: 'activa' | 'inactiva'
}

interface DeleteAreaDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  area: Area | null
  onConfirm: () => Promise<void>
  isLoading?: boolean
}

export function DeleteAreaDialog({ 
  open, 
  onOpenChange, 
  area, 
  onConfirm, 
  isLoading = false 
}: DeleteAreaDialogProps) {
  const handleConfirm = async () => {
    try {
      await onConfirm()
      onOpenChange(false)
    } catch (error) {
      // Error handling is done in the parent component
    }
  }

  if (!area) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-6 w-6 text-destructive" />
            <DialogTitle>Eliminar Área</DialogTitle>
          </div>
          <DialogDescription>
            Esta acción no se puede deshacer. Se eliminará permanentemente el área y todos sus datos asociados.
          </DialogDescription>
        </DialogHeader>
        
        <div className="py-4">
          <div className="bg-muted p-4 rounded-lg space-y-2">
            <p><strong>Órgano:</strong> {area.organo}</p>
            <p><strong>Unidad Orgánica:</strong> {area.unidad_organica}</p>
            <p><strong>Siglas:</strong> {area.siglas}</p>
            {area.jefe && (
              <p><strong>Jefe:</strong> {area.jefe}</p>
            )}
            {area.empleados_count !== undefined && (
              <p><strong>Empleados:</strong> {area.empleados_count}</p>
            )}
          </div>
          
          {(area.empleados_count || 0) > 0 && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                <strong>Advertencia:</strong> Esta área tiene {area.empleados_count} empleado(s) asignado(s). 
                Asegúrate de reasignar a los empleados antes de eliminar el área.
              </p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            Cancelar
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={handleConfirm}
            disabled={isLoading}
          >
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Eliminar Área
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}