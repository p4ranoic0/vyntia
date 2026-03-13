import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowRight, Calculator, FileSpreadsheet, FileText, Landmark, Settings, Upload } from 'lucide-react'
import { Link } from 'react-router-dom'

const options = [
  {
    title: 'Planillas Mensuales',
    description: 'Consulta consolidada por periodo y modalidad.',
    path: '/remuneraciones/planillas-mensuales',
    icon: FileSpreadsheet,
  },
  {
    title: 'Proceso de Planillas',
    description: 'Base de calculo usando datos personales y laborales del empleado.',
    path: '/remuneraciones/proceso-planillas',
    icon: Calculator,
  },
  {
    title: 'Boletas de Pago',
    description: 'Gestion y consulta de boletas por periodo.',
    path: '/remuneraciones/boletas-pago',
    icon: FileText,
  },
  {
    title: 'Descuentos Masivos',
    description: 'Carga y procesa descuentos masivos desde archivos Excel.',
    path: '/remuneraciones/descuentos-masivos',
    icon: Upload,
  },
  {
    title: 'Reportes',
    description: 'Reportes mensuales por planilla, banco y sistema pensionario.',
    path: '/remuneraciones/reportes',
    icon: FileText,
  },
  {
    title: 'Configuracion',
    description: 'Tabla maestra de AFP, ingresos y descuentos.',
    path: '/remuneraciones/configuracion',
    icon: Settings,
  },
  {
    title: 'Configuración UIT',
    description: 'Gestiona valores anuales de la Unidad Impositiva Tributaria.',
    path: '/remuneraciones/configuracion-uit',
    icon: Landmark,
  },
]

export default function RemuneracionesHomePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Remuneraciones</h1>
        <p className="text-muted-foreground mt-1">
          Módulo integral para proceso, consulta y reportes de planillas mensuales.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {options.map((option) => {
          const Icon = option.icon
          return (
            <Card key={option.path} className="border-border/60">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Icon className="h-5 w-5" />
                  {option.title}
                </CardTitle>
                <CardDescription>{option.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild className="w-full">
                  <Link to={option.path}>
                    Ir al módulo
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
