import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useState } from 'react'

export default function BoletasPagoPage() {
  const [periodo, setPeriodo] = useState('')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Boletas de Pago</h1>
        <p className="text-muted-foreground mt-1">
          Consulta y emision de boletas por periodo de planilla.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Generacion por periodo</CardTitle>
          <CardDescription>
            Selecciona un periodo para preparar la emision o descarga masiva de boletas.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-[1fr_auto_auto]">
          <div className="space-y-2">
            <Label htmlFor="periodo-boleta">Periodo</Label>
            <Input id="periodo-boleta" type="month" value={periodo} onChange={(e) => setPeriodo(e.target.value)} />
          </div>
          <div className="self-end">
            <Button variant="outline">Vista previa</Button>
          </div>
          <div className="self-end">
            <Button>Generar boletas</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
