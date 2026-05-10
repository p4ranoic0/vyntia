import { useRef, useState } from 'react'
import { AlertCircle, CheckCircle2, Download, FileSpreadsheet, Upload } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'

import { ccfService, type CCFImportResult } from '../services/ccfService'

interface CCFExcelImporterProps {
  /** Called when an import succeeds, with the new ccf_id. Parent can navigate. */
  onImportSuccess?: (ccfId: string) => void
}

export function CCFExcelImporter({ onImportSuccess }: CCFExcelImporterProps) {
  const [title, setTitle] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<CCFImportResult | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  async function handleDownloadTemplate() {
    try {
      const blob = await ccfService.downloadTemplate()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'ccf_template.xlsx'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (e) {
      toast.error(`Error descargando plantilla: ${e instanceof Error ? e.message : 'desconocido'}`)
    }
  }

  async function handleUpload() {
    if (!title.trim()) {
      toast.error('Ingrese el título del CCF')
      return
    }
    if (!file) {
      toast.error('Seleccione un archivo .xlsx')
      return
    }
    setSubmitting(true)
    setResult(null)
    try {
      const r = await ccfService.uploadCCFExcel(file, title.trim())
      setResult(r)
      if (r.success && r.ccf_id) {
        toast.success(
          `Importadas ${r.categories_created} categorías + ${r.bands_created} bandas`,
        )
        onImportSuccess?.(r.ccf_id)
      } else {
        toast.error(
          r.fatal_error
            ? `Error: ${r.fatal_error}`
            : `${r.row_errors.length} errores en filas. Revise el reporte.`,
        )
      }
    } catch (e) {
      toast.error(`Error: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <FileSpreadsheet className="h-5 w-5 text-green-700" />
          Importación masiva desde Excel
        </CardTitle>
        <CardDescription>
          Cargue categorías + bandas + scores desde plantilla .xlsx. Importación
          atómica — un error en cualquier fila aborta toda la importación.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Button variant="outline" size="sm" onClick={handleDownloadTemplate}>
            <Download className="h-4 w-4 mr-2" />
            Descargar plantilla
          </Button>
        </div>

        <div className="space-y-2">
          <Label htmlFor="ccf-title">Título del nuevo CCF *</Label>
          <Input
            id="ccf-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="CCF 2026 (importado)"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="ccf-file">Archivo .xlsx *</Label>
          <Input
            id="ccf-file"
            ref={inputRef}
            type="file"
            accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          {file && (
            <p className="text-xs text-muted-foreground">
              Archivo seleccionado: <span className="font-mono">{file.name}</span>
              {' '}({Math.round(file.size / 1024)} KB)
            </p>
          )}
        </div>

        <Button onClick={handleUpload} disabled={submitting || !file || !title.trim()}>
          <Upload className="h-4 w-4 mr-2" />
          {submitting ? 'Importando...' : 'Importar CCF'}
        </Button>

        {result && (
          <div
            className={`rounded-md border p-4 text-sm space-y-2 ${
              result.success
                ? 'border-green-300 bg-green-50'
                : 'border-red-300 bg-red-50'
            }`}
          >
            <div className="flex items-center gap-2 font-medium">
              {result.success ? (
                <CheckCircle2 className="h-4 w-4 text-green-700" />
              ) : (
                <AlertCircle className="h-4 w-4 text-red-700" />
              )}
              {result.success
                ? `Import exitoso (${result.categories_created} categorías).`
                : result.fatal_error
                  ? `Error fatal: ${result.fatal_error}`
                  : `${result.row_errors.length} fila(s) con errores.`}
            </div>

            {result.success && (
              <ul className="text-xs text-muted-foreground space-y-0.5 ml-6 list-disc">
                <li>{result.categories_created} categorías</li>
                <li>{result.bands_created} bandas salariales</li>
                <li>{result.scores_created} scores de factor</li>
              </ul>
            )}

            {result.row_errors.length > 0 && (
              <details className="mt-2" open>
                <summary className="cursor-pointer text-xs font-medium">
                  Ver errores por fila ({result.row_errors.length})
                </summary>
                <ul className="mt-2 space-y-1 text-xs">
                  {result.row_errors.map((err, idx) => (
                    <li key={idx} className="font-mono">
                      Fila {err.row}
                      {err.code ? ` (${err.code})` : ''}: {err.error}
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
