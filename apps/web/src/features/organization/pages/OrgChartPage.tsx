import { Suspense, lazy } from 'react'
import { Card, CardContent } from '@/shared/ui/card'
import { Skeleton } from '@/shared/ui/skeleton'

const OrgChartCanvas = lazy(() => import('../components/OrgChartCanvas'))

function OrgChartLoading() {
  return (
    <Card className="m-4">
      <CardContent className="p-6 space-y-4">
        <Skeleton className="h-8 w-1/2" />
        <Skeleton className="h-[600px] w-full" />
      </CardContent>
    </Card>
  )
}

/**
 * OrgChart page — interactive organizational chart.
 *
 * Backend per B.6 #103: drag-drop reorganization for HR users; read-only
 * viewer for employees. Powered by @xyflow/react + dagre auto-layout per
 * ADR-B.8. Lazy-loaded to keep the ~150 KB xyflow bundle off other routes.
 */
export default function OrgChartPage() {
  return (
    <div className="flex flex-col h-full min-h-[calc(100vh-4rem)]">
      <div className="border-b bg-white px-6 py-4">
        <h1 className="text-2xl font-bold">Organigrama</h1>
        <p className="text-sm text-muted-foreground">
          Estructura jerárquica de la organización. RRHH puede arrastrar para reorganizar.
        </p>
      </div>
      <div className="flex-1 relative">
        <Suspense fallback={<OrgChartLoading />}>
          <OrgChartCanvas />
        </Suspense>
      </div>
    </div>
  )
}
