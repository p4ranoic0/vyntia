import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shared/ui/table'
import { useState } from 'react'

const reportes = [
  'Reporte por bancos y modalidad',
  'Reporte de descuentos por modalidad',
  'Reporte por sistema de pensiones',
  'Exportacion AFP (Excel)',
  'Exportacion PDT (Excel)',
]

const columnasReferenciaPdf = [
  'Area / Apellidos y nombres',
  'DNI',
  'Meta',
  'Fecha de ingreso',
  'Sistema de pensiones',
  'Tipo seguro',
  'Remuneracion fija',
  'Aporte obligatorio',
  'Comision variable',
  'Total AFP',
  'Descuento deducible',
  'Neto a pagar',
  'Essalud',
]

export default function ReportesRemuneracionesPage() {
  const [periodo, setPeriodo] = useState('')
  const [tipoReporte, setTipoReporte] = useState(reportes[0])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Reportes de Remuneraciones</h1>
        <p className="text-muted-foreground mt-1">
          Reporteria mensual de planillas alineada al formato de referencia de planilla CAS.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Parametros de reporte</CardTitle>
          <CardDescription>Selecciona tipo y periodo para exportar.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <div className="space-y-2">
            <Label htmlFor="periodo-reporte">Periodo</Label>
            <Input id="periodo-reporte" type="month" value={periodo} onChange={(e) => setPeriodo(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Tipo de reporte</Label>
            <Select value={tipoReporte} onValueChange={setTipoReporte}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {reportes.map((r) => (
                  <SelectItem value={r} key={r}>{r}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-end gap-2">
            <Button variant="outline" className="flex-1">Exportar Excel</Button>
            <Button className="flex-1">Generar</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Columnas base del reporte mensual</CardTitle>
          <CardDescription>Vista de referencia del layout mensual de planilla.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>#</TableHead>
                <TableHead>Campo</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {columnasReferenciaPdf.map((col, index) => (
                <TableRow key={col}>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>{col}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
