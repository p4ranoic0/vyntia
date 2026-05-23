import { useRef, useState } from 'react'
import { AlertCircle, CheckCircle2, FileText, Upload } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetFooter,
    SheetHeader,
    SheetTitle,
} from '@/shared/ui/sheet'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/shared/ui/table'
import {
    BatchImportResult,
    employeesService,
} from '@/features/employees/services/employeesService'

interface BatchImportDrawerProps {
  open: boolean
  onClose: () => void
  onImported: () => void
}

const REQUIRED_COLUMNS = [
  'numero_documento',
  'tipo_documento',
  'nombres_empleado',
  'apellido_paterno',
  'apellido_materno',
  'fecha_nacimiento',
  'correo_personal',
  'regimen_laboral',
  'fecha_ingreso',
  'sueldo_basico',
  'area_id',
]

/** Aplana un dict de errores DRF (posiblemente anidado) a un string legible. */
function flattenErrors(errors: Record<string, unknown>): string {
  const parts: string[] = []
  for (const [field, val] of Object.entries(errors)) {
    if (Array.isArray(val)) {
      parts.push(`${field}: ${val.join(', ')}`)
    } else if (val && typeof val === 'object') {
      parts.push(`${field}: ${flattenErrors(val as Record<string, unknown>)}`)
    } else {
      parts.push(`${field}: ${String(val)}`)
    }
  }
  return parts.join(' · ')
}

export function BatchImportDrawer({ open, onClose, onImported }: BatchImportDrawerProps) {
  const [file, setFile] = useState<File | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<BatchImportResult | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const reset = () => {
    setFile(null)
    setResult(null)
    setLoading(false)
    setDragOver(false)
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  const pickFile = (f: File | null | undefined) => {
    if (!f) return
    if (!f.name.toLowerCase().endsWith('.csv')) {
      toast.error('El archivo debe tener extensión .csv')
      return
    }
    setFile(f)
    setResult(null)
  }

  const handleImport = async () => {
    if (!file) return
    setLoading(true)
    try {
      const res = await employeesService.batchImport(file)
      setResult(res)
      if (res.errors.length === 0) {
        toast.success(`${res.created} empleado(s) importado(s) correctamente.`)
        onImported()
      } else {
        toast.error(
          `Importación rechazada: ${res.errors.length} fila(s) con errores. No se creó ningún empleado.`,
        )
      }
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al importar el archivo')
    } finally {
      setLoading(false)
    }
  }

  const importedOk = result !== null && result.errors.length === 0

  return (
    <Sheet open={open} onOpenChange={(v) => !v && handleClose()}>
      <SheetContent className="w-full sm:max-w-xl overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Importar empleados desde CSV</SheetTitle>
          <SheetDescription>
            Carga masiva. La validación es todo-o-nada: si alguna fila tiene
            errores, no se crea ningún empleado y verás el detalle por fila.
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-4 py-4">
          {/* Columnas esperadas */}
          <div className="rounded-md border bg-muted/40 p-3 text-xs">
            <p className="mb-1 font-medium">Columnas requeridas (cabecera CSV):</p>
            <code className="block break-words text-muted-foreground">
              {REQUIRED_COLUMNS.join(', ')}
            </code>
          </div>

          {/* Drop-zone */}
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault()
              setDragOver(true)
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault()
              setDragOver(false)
              pickFile(e.dataTransfer.files?.[0])
            }}
            className={`flex w-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
              dragOver ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'
            }`}
          >
            {file ? (
              <>
                <FileText className="h-8 w-8 text-primary" />
                <p className="text-sm font-medium">{file.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(file.size / 1024).toFixed(1)} KB · click para cambiar
                </p>
              </>
            ) : (
              <>
                <Upload className="h-8 w-8 text-muted-foreground" />
                <p className="text-sm font-medium">
                  Arrastra un CSV aquí o haz click para seleccionar
                </p>
                <p className="text-xs text-muted-foreground">Solo archivos .csv</p>
              </>
            )}
            <input
              ref={inputRef}
              type="file"
              accept=".csv,text/csv"
              className="hidden"
              onChange={(e) => pickFile(e.target.files?.[0])}
            />
          </button>

          {/* Resultado OK */}
          {importedOk && (
            <div className="flex items-center gap-2 rounded-md border border-green-600/30 bg-green-50 p-3 text-sm text-green-700">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span>{result.created} empleado(s) importado(s) correctamente.</span>
            </div>
          )}

          {/* Tabla de errores */}
          {result !== null && result.errors.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm font-medium text-destructive">
                <AlertCircle className="h-4 w-4" />
                {result.errors.length} fila(s) con errores — no se creó ningún empleado
              </div>
              <div className="overflow-x-auto rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[80px]">Fila</TableHead>
                      <TableHead>Errores</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {result.errors.map((rowError) => (
                      <TableRow key={rowError.row}>
                        <TableCell className="font-mono">{rowError.row}</TableCell>
                        <TableCell className="text-xs text-destructive">
                          {flattenErrors(rowError.errors)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}
        </div>

        <SheetFooter className="gap-2">
          <Button variant="outline" onClick={handleClose} disabled={loading}>
            {importedOk ? 'Cerrar' : 'Cancelar'}
          </Button>
          <Button onClick={handleImport} disabled={!file || loading || importedOk}>
            {loading ? 'Importando...' : 'Importar'}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
