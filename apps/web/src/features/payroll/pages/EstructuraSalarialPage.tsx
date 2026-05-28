import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui/table'
import { employeesService, type Employee } from '@/features/employees/services/employeesService'
import { useQuery } from '@tanstack/react-query'
import { DollarSign, History, Plus } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import { useCompensationHistory, useCompensationsList, useCreateCompensation } from '../hooks/useCompensations'
import { type Compensation, type CompensationCreate } from '../services/compensationsService'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function formatCurrency(value?: string | null): string {
  if (value == null) return '-'
  const num = parseFloat(value)
  if (isNaN(num)) return value
  return new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(num)
}

const SOURCE_BADGE: Record<string, string> = {
  MIGRATION: 'bg-gray-100 text-gray-800',
  MANUAL: 'bg-blue-100 text-blue-800',
  CONTRACT_AMENDMENT: 'bg-purple-100 text-purple-800',
}
const SOURCE_LABEL: Record<string, string> = {
  MIGRATION: 'Migración',
  MANUAL: 'Manual',
  CONTRACT_AMENDMENT: 'Adenda',
}

const REGIMEN_LABELS: Record<string, string> = {
  '728': 'Ley 728',
  '276': 'D.L. 276',
  '1057': 'CAS 1057',
  'practicas': 'Prácticas',
}

const PENSION_LABELS: Record<string, string> = {
  ONP: 'ONP',
  AFP_INTEGRA: 'AFP Integra',
  AFP_PRIMA: 'AFP Prima',
  AFP_PROFUTURO: 'AFP Profuturo',
  AFP_HABITAT: 'AFP Hábitat',
}

// ---------------------------------------------------------------------------
// History Dialog
// ---------------------------------------------------------------------------

interface HistoryDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  employeeId: string | null
  employeeName: string
}

function HistoryDialog({ open, onOpenChange, employeeId, employeeName }: HistoryDialogProps) {
  const { data: history = [], isLoading } = useCompensationHistory(employeeId ?? undefined)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Historial de compensaciones</DialogTitle>
          <DialogDescription>{employeeName || 'Empleado'}</DialogDescription>
        </DialogHeader>
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner />
          </div>
        ) : history.length === 0 ? (
          <p className="text-center text-muted-foreground py-8">Sin historial registrado.</p>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Vigencia desde</TableHead>
                  <TableHead>Vigencia hasta</TableHead>
                  <TableHead>Sueldo</TableHead>
                  <TableHead>Régimen</TableHead>
                  <TableHead>Pensión</TableHead>
                  <TableHead>Fuente</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {history.map((c) => (
                  <TableRow key={c.id}>
                    <TableCell>{formatDate(c.valid_from)}</TableCell>
                    <TableCell>{c.valid_to ? formatDate(c.valid_to) : '∞'}</TableCell>
                    <TableCell className="font-medium">{formatCurrency(c.base_salary)}</TableCell>
                    <TableCell>{REGIMEN_LABELS[c.regimen_laboral] ?? c.regimen_laboral}</TableCell>
                    <TableCell>{PENSION_LABELS[c.pension_regime] ?? c.pension_regime}</TableCell>
                    <TableCell>
                      <Badge className={SOURCE_BADGE[c.source] ?? 'bg-gray-100 text-gray-800'}>
                        {SOURCE_LABEL[c.source] ?? c.source}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}

// ---------------------------------------------------------------------------
// Create Dialog
// ---------------------------------------------------------------------------

const EMPTY_FORM: Partial<CompensationCreate> = {
  source: 'MANUAL',
  has_family_allowance: false,
  afp_commission_type: '',
  cuspp: '',
  eps_provider: '',
  cci: '',
  bank_code: '',
  bank_account: '',
  permission_level: 6,
  valid_to: null,
  contract_snapshot: null,
}

interface CreateDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  employees: Employee[]
}

function CreateCompensationDialog({ open, onOpenChange, employees }: CreateDialogProps) {
  const [form, setForm] = useState<Partial<CompensationCreate>>(EMPTY_FORM)
  const createMutation = useCreateCompensation()

  const handleChange = (field: keyof CompensationCreate, value: string | number | boolean | null) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const resetForm = () => setForm(EMPTY_FORM)

  const handleSubmit = () => {
    if (!form.employee || !form.valid_from || !form.base_salary || !form.regimen_laboral || !form.pension_regime || !form.health_regime) {
      toast.error('Completa todos los campos obligatorios')
      return
    }
    createMutation.mutate(form as CompensationCreate, {
      onSuccess: () => {
        toast.success('Compensación creada exitosamente')
        resetForm()
        onOpenChange(false)
      },
      onError: (err: Error) => {
        toast.error(err.message || 'Error al crear compensación')
      },
    })
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) resetForm()
        onOpenChange(v)
      }}
    >
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Nueva versión de compensación</DialogTitle>
          <DialogDescription>Registra una nueva versión salarial para un empleado.</DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {/* Empleado */}
          <div className="grid gap-2">
            <Label htmlFor="comp-employee">Empleado *</Label>
            <Select value={form.employee ?? ''} onValueChange={(v) => handleChange('employee', v)}>
              <SelectTrigger id="comp-employee">
                <SelectValue placeholder="Seleccionar empleado" />
              </SelectTrigger>
              <SelectContent>
                {employees.map((emp) => (
                  <SelectItem key={emp.id} value={String(emp.id)}>
                    {emp.nombres} {emp.ape_paterno} {emp.ape_materno}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Fechas de vigencia */}
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="comp-valid-from">Vigencia desde *</Label>
              <Input
                id="comp-valid-from"
                type="date"
                value={form.valid_from ?? ''}
                onChange={(e) => handleChange('valid_from', e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="comp-valid-to">Vigencia hasta</Label>
              <Input
                id="comp-valid-to"
                type="date"
                value={form.valid_to ?? ''}
                onChange={(e) => handleChange('valid_to', e.target.value || null)}
              />
            </div>
          </div>

          {/* Sueldo base */}
          <div className="grid gap-2">
            <Label htmlFor="comp-base-salary">Sueldo base (S/) *</Label>
            <Input
              id="comp-base-salary"
              type="number"
              min="0"
              step="0.01"
              value={form.base_salary ?? ''}
              onChange={(e) => handleChange('base_salary', e.target.value)}
              placeholder="Ej: 3000.00"
            />
          </div>

          {/* Régimen y Pensión */}
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="comp-regimen">Régimen laboral *</Label>
              <Select value={form.regimen_laboral ?? ''} onValueChange={(v) => handleChange('regimen_laboral', v)}>
                <SelectTrigger id="comp-regimen">
                  <SelectValue placeholder="Seleccionar" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="728">Ley 728</SelectItem>
                  <SelectItem value="276">D.L. 276</SelectItem>
                  <SelectItem value="1057">CAS 1057</SelectItem>
                  <SelectItem value="practicas">Prácticas</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="comp-pension">Régimen de pensión *</Label>
              <Select value={form.pension_regime ?? ''} onValueChange={(v) => handleChange('pension_regime', v)}>
                <SelectTrigger id="comp-pension">
                  <SelectValue placeholder="Seleccionar" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ONP">ONP</SelectItem>
                  <SelectItem value="AFP_INTEGRA">AFP Integra</SelectItem>
                  <SelectItem value="AFP_PRIMA">AFP Prima</SelectItem>
                  <SelectItem value="AFP_PROFUTURO">AFP Profuturo</SelectItem>
                  <SelectItem value="AFP_HABITAT">AFP Hábitat</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Salud */}
          <div className="grid gap-2">
            <Label htmlFor="comp-health">Seguro de salud *</Label>
            <Select value={form.health_regime ?? ''} onValueChange={(v) => handleChange('health_regime', v)}>
              <SelectTrigger id="comp-health">
                <SelectValue placeholder="Seleccionar" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ESSALUD">EsSalud</SelectItem>
                <SelectItem value="EPS">EPS</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Opcionales: AFP comisión, CUSPP, EPS proveedor */}
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="comp-afp-commission">Tipo comisión AFP</Label>
              <Input
                id="comp-afp-commission"
                value={form.afp_commission_type ?? ''}
                onChange={(e) => handleChange('afp_commission_type', e.target.value)}
                placeholder="FLUJO / MIXTA / SALDO"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="comp-cuspp">CUSPP</Label>
              <Input
                id="comp-cuspp"
                value={form.cuspp ?? ''}
                onChange={(e) => handleChange('cuspp', e.target.value)}
                placeholder="Código AFP"
              />
            </div>
          </div>

          {/* Bancario */}
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="comp-bank-account">N. cuenta bancaria</Label>
              <Input
                id="comp-bank-account"
                value={form.bank_account ?? ''}
                onChange={(e) => handleChange('bank_account', e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="comp-cci">CCI</Label>
              <Input
                id="comp-cci"
                value={form.cci ?? ''}
                onChange={(e) => handleChange('cci', e.target.value)}
              />
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={createMutation.isPending}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit} disabled={createMutation.isPending}>
            {createMutation.isPending ? (
              <>
                <LoadingSpinner className="mr-2 h-4 w-4" />
                Guardando...
              </>
            ) : (
              <>
                <Plus className="mr-2 h-4 w-4" />
                Crear compensación
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function EstructuraSalarialPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [historyEmployee, setHistoryEmployee] = useState<{ id: string; name: string } | null>(null)

  const { data: compensations = [], isLoading, error } = useCompensationsList()

  const { data: employees = [] } = useQuery<Employee[]>({
    queryKey: ['employees-list'],
    queryFn: () => employeesService.getAll(),
  })

  // Build employee name map
  const employeeMap = new Map<string, string>(
    employees.map((e) => [String(e.id), `${e.nombres} ${e.ape_paterno} ${e.ape_materno}`.trim()])
  )

  const handleRowClick = (comp: Compensation) => {
    const name = employeeMap.get(String(comp.employee)) ?? comp.employee
    setHistoryEmployee({ id: String(comp.employee), name })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-600 mb-2">Error al cargar la estructura salarial</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Estructura salarial</h1>
          <p className="text-muted-foreground">
            Versiones de compensación por empleado — fuente de verdad para planilla
          </p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Nueva versión
        </Button>
      </div>

      {/* Table */}
      <Card>
        <CardHeader>
          <CardTitle>Compensaciones ({compensations.length})</CardTitle>
          <CardDescription>Haz clic en una fila para ver el historial completo del empleado</CardDescription>
        </CardHeader>
        <CardContent>
          {compensations.length === 0 ? (
            <div className="text-center py-12">
              <DollarSign className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium">No hay registros de estructura salarial</p>
              <p className="text-muted-foreground">
                Crea el primer registro usando el botón "Nueva versión".
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Empleado</TableHead>
                    <TableHead>Vigencia desde</TableHead>
                    <TableHead>Vigencia hasta</TableHead>
                    <TableHead className="text-right">Sueldo</TableHead>
                    <TableHead>Régimen</TableHead>
                    <TableHead>Pensión</TableHead>
                    <TableHead>Fuente</TableHead>
                    <TableHead>Historial</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {compensations.map((comp) => (
                    <TableRow
                      key={comp.id}
                      className="cursor-pointer"
                      onClick={() => handleRowClick(comp)}
                    >
                      <TableCell className="font-medium">
                        {employeeMap.get(String(comp.employee)) ?? comp.employee}
                      </TableCell>
                      <TableCell>{formatDate(comp.valid_from)}</TableCell>
                      <TableCell>{comp.valid_to ? formatDate(comp.valid_to) : '∞'}</TableCell>
                      <TableCell className="text-right">{formatCurrency(comp.base_salary)}</TableCell>
                      <TableCell>{REGIMEN_LABELS[comp.regimen_laboral] ?? comp.regimen_laboral}</TableCell>
                      <TableCell>{PENSION_LABELS[comp.pension_regime] ?? comp.pension_regime}</TableCell>
                      <TableCell>
                        <Badge className={SOURCE_BADGE[comp.source] ?? 'bg-gray-100 text-gray-800'}>
                          {SOURCE_LABEL[comp.source] ?? comp.source}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleRowClick(comp)
                          }}
                        >
                          <History className="mr-1 h-3 w-3" />
                          Ver
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Dialog */}
      <CreateCompensationDialog
        open={isCreateOpen}
        onOpenChange={setIsCreateOpen}
        employees={employees}
      />

      {/* History Dialog */}
      {historyEmployee && (
        <HistoryDialog
          open={historyEmployee !== null}
          onOpenChange={(v) => { if (!v) setHistoryEmployee(null) }}
          employeeId={historyEmployee.id}
          employeeName={historyEmployee.name}
        />
      )}
    </div>
  )
}
