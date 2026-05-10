import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, CheckCircle2 } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui/table'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/shared/ui/tabs'

import {
  ccfService,
  type CCF,
  type Category,
  type SalaryBand,
} from '../services/ccfService'
import { useTenantSector } from '../hooks/useTenantSector'
import { SalaryGapAuditPanel } from '../components/SalaryGapAuditPanel'
import { CCFExcelImporter } from '../components/CCFExcelImporter'

export default function CCFEditorPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const sector = useTenantSector()
  const [ccf, setCcf] = useState<CCF | null>(null)
  const [categories, setCategories] = useState<Category[]>([])
  const [bands, setBands] = useState<SalaryBand[]>([])
  const [loading, setLoading] = useState(true)
  const [approving, setApproving] = useState(false)

  useEffect(() => {
    if (!id) return
    let cancelled = false
    ;(async () => {
      try {
        const [ccfData, catData, bandsData] = await Promise.all([
          ccfService.getCCF(id),
          ccfService.listCategories(id),
          ccfService.listSalaryBands(),
        ])
        if (cancelled) return
        setCcf(ccfData)
        setCategories(catData)
        // Filter bands to those whose category belongs to this CCF
        const catIds = new Set(catData.map((c) => c.id))
        setBands(bandsData.filter((b) => catIds.has(b.category)))
      } catch (e) {
        if (cancelled) return
        toast.error(
          `Error cargando CCF: ${e instanceof Error ? e.message : 'desconocido'}`,
        )
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [id])

  if (sector === 'public') {
    return (
      <Card className="m-6">
        <CardHeader>
          <CardTitle>CCF no aplicable</CardTitle>
          <CardDescription>
            Su tenant es sector público. Use MPP/CPE (B.8) en su lugar.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (loading) {
    return <p className="p-6 text-muted-foreground">Cargando CCF…</p>
  }
  if (!ccf) {
    return (
      <Card className="m-6">
        <CardContent className="py-6 text-center text-muted-foreground">
          CCF no encontrado.
        </CardContent>
      </Card>
    )
  }

  async function handleApprove() {
    if (!ccf) return
    setApproving(true)
    try {
      const updated = await ccfService.approveCCF(ccf.id)
      setCcf(updated)
      toast.success('CCF aprobado')
    } catch (e) {
      toast.error(`Error aprobando: ${e instanceof Error ? e.message : 'desconocido'}`)
    } finally {
      setApproving(false)
    }
  }

  async function handleImportSuccess(newCcfId: string) {
    toast.success('CCF importado — redirigiendo…')
    navigate(`/compensacion/ccf/${newCcfId}`)
  }

  return (
    <div className="p-6 space-y-6">
      <header>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/compensacion/ccf')}
          className="mb-3"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Volver a CCFs
        </Button>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">{ccf.title}</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Versión {ccf.version} · {ccf.status_display}
              {ccf.effective_date && ` · efectivo desde ${ccf.effective_date}`}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={ccf.status === 'approved' ? 'default' : 'secondary'}>
              {ccf.status_display}
            </Badge>
            {ccf.status === 'draft' && (
              <Button onClick={handleApprove} disabled={approving}>
                <CheckCircle2 className="h-4 w-4 mr-2" />
                {approving ? 'Aprobando...' : 'Aprobar'}
              </Button>
            )}
          </div>
        </div>
      </header>

      <Tabs defaultValue="categories" className="space-y-4">
        <TabsList>
          <TabsTrigger value="categories">
            Categorías ({categories.length})
          </TabsTrigger>
          <TabsTrigger value="bands">
            Bandas salariales ({bands.length})
          </TabsTrigger>
          <TabsTrigger value="audit">Análisis brechas</TabsTrigger>
          <TabsTrigger value="import">Importar Excel</TabsTrigger>
        </TabsList>

        <TabsContent value="categories">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Categorías de este CCF</CardTitle>
              <CardDescription>
                Cada categoría se valoriza con metodología 4 factores (R.M.
                243-2018-TR). El total puntaje se recompone automáticamente.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {categories.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-6">
                  Sin categorías. Importe desde Excel o agregue manualmente
                  (formulario en B.7.1).
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Código</TableHead>
                      <TableHead>Nombre</TableHead>
                      <TableHead className="text-right">Exp. mín.</TableHead>
                      <TableHead className="text-right">Puntaje total</TableHead>
                      <TableHead>Estado</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {categories.map((cat) => (
                      <TableRow key={cat.id}>
                        <TableCell className="font-mono">{cat.code}</TableCell>
                        <TableCell>
                          <div className="font-medium">{cat.name}</div>
                          {cat.description && (
                            <div className="text-xs text-muted-foreground line-clamp-1">
                              {cat.description}
                            </div>
                          )}
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {cat.min_experience_years} años
                        </TableCell>
                        <TableCell className="text-right tabular-nums font-medium">
                          {cat.total_score}
                        </TableCell>
                        <TableCell>
                          {cat.is_active ? (
                            <Badge variant="outline" className="text-green-700">
                              Activa
                            </Badge>
                          ) : (
                            <Badge variant="secondary">Inactiva</Badge>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bands">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Bandas salariales</CardTitle>
              <CardDescription>
                Mínimo / punto medio / máximo por categoría (Ley 30709 § 4.1).
              </CardDescription>
            </CardHeader>
            <CardContent>
              {bands.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-6">
                  Sin bandas salariales registradas para este CCF.
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Categoría</TableHead>
                      <TableHead className="text-right">Mínimo</TableHead>
                      <TableHead className="text-right">Punto medio</TableHead>
                      <TableHead className="text-right">Máximo</TableHead>
                      <TableHead>Moneda</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {bands.map((band) => (
                      <TableRow key={band.id}>
                        <TableCell>
                          <div className="font-mono text-xs">{band.category_code}</div>
                          <div className="text-xs">{band.category_name}</div>
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {band.min_salary}
                        </TableCell>
                        <TableCell className="text-right tabular-nums font-medium">
                          {band.mid_salary}
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {band.max_salary}
                        </TableCell>
                        <TableCell>{band.currency}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audit">
          <SalaryGapAuditPanel ccfId={ccf.id} />
        </TabsContent>

        <TabsContent value="import">
          <CCFExcelImporter onImportSuccess={handleImportSuccess} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
