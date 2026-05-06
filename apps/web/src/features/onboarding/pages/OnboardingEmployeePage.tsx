import { useQuery } from '@tanstack/react-query'
import { onboardingService } from '@/services/onboardingService'
import { apiClient } from '@/shared/api/api'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/shared/ui/tabs'
import { Skeleton } from '@/shared/ui/skeleton'
import { OnboardingProgressBar } from '../components/OnboardingProgressBar'
import { OnboardingCompleteBanner } from '../components/OnboardingCompleteBanner'
import { OnboardingTabPersonal } from '../components/OnboardingTabPersonal'
import { OnboardingTabFamiliar } from '../components/OnboardingTabFamiliar'
import { OnboardingTabAcademico } from '../components/OnboardingTabAcademico'
import { OnboardingTabLaboral } from '../components/OnboardingTabLaboral'
import { OnboardingSectionStatus } from '../components/OnboardingSectionStatus'
import { DocumentInfo } from '../types/onboarding'

export function OnboardingEmployeePage() {
  const { data: onboarding, isLoading: loadingOnboarding } = useQuery({
    queryKey: ['mi-onboarding'],
    queryFn: () => onboardingService.getMiOnboarding(),
    retry: false,
  })

  const empleadoId = onboarding?.empleado

  const { data: docsRaw, isLoading: loadingDocs } = useQuery({
    queryKey: ['legajo-docs', empleadoId],
    queryFn: async () => {
      const res = await apiClient.get('/api/v1/documents/documents/', {
        params: { empleado: empleadoId, es_version_actual: 'true', page_size: 50 },
      })
      // Unwrap paginated APIResponse: { success, data: { results: [...] }, meta: { pagination } }
      const raw = res.data
      return (raw?.data?.results ?? raw?.data ?? raw?.results ?? []) as DocumentInfo[]
    },
    enabled: !!empleadoId,
  })

  const { data: empleadoData } = useQuery({
    queryKey: ['empleado-data', empleadoId],
    queryFn: async () => {
      const res = await apiClient.get(`/api/v1/employees/${empleadoId}/`)
      return res.data?.data ?? res.data
    },
    enabled: !!empleadoId,
  })

  const docs: DocumentInfo[] = docsRaw ?? []

  const isLoading = loadingOnboarding || (!!empleadoId && loadingDocs)

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto p-6 space-y-4">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (onboarding?.estado_onboarding === 'completado') {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <OnboardingCompleteBanner />
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      {onboarding && (
        <OnboardingProgressBar
          progreso_porcentaje={onboarding.progreso_porcentaje}
          progreso_aprobado={(onboarding as Record<string, unknown>).progreso_aprobado as number | undefined}
        />
      )}
      <div className="mb-4">
        <OnboardingSectionStatus docs={docs} />
      </div>
      <Tabs defaultValue="personal">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="personal">Personal</TabsTrigger>
          <TabsTrigger value="familiar">Familiar</TabsTrigger>
          <TabsTrigger value="academico">Académico</TabsTrigger>
          <TabsTrigger value="laboral">Laboral</TabsTrigger>
        </TabsList>
        <TabsContent value="personal" className="mt-6">
          {empleadoId && (
            <OnboardingTabPersonal
              empleadoId={empleadoId}
              docs={docs}
              initialValues={empleadoData as Record<string, unknown> | undefined}
            />
          )}
        </TabsContent>
        <TabsContent value="familiar" className="mt-6">
          {empleadoId && (
            <OnboardingTabFamiliar empleadoId={empleadoId} docs={docs} />
          )}
        </TabsContent>
        <TabsContent value="academico" className="mt-6">
          {empleadoId && (
            <OnboardingTabAcademico empleadoId={empleadoId} docs={docs} />
          )}
        </TabsContent>
        <TabsContent value="laboral" className="mt-6">
          {empleadoId && (
            <OnboardingTabLaboral empleadoId={empleadoId} docs={docs} />
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
