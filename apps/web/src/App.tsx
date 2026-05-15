import LoginForm from '@/features/auth/components/LoginForm'
import { LoadingSpinner } from '@/shared/components/LoadingSpinner'
import AdminLayout from '@/shared/layout/AdminLayout'
import { Layout } from '@/shared/layout/Layout'
import { Toaster } from '@/shared/ui/toaster'
import { Toaster as SonnerToaster } from 'sonner'
import { AuthProvider } from '@/features/auth/context/AuthContext'
import { ThemeProvider } from '@/shared/context/ThemeContext'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { onboardingService } from '@/features/onboarding/services/onboardingService'
import { useQuery } from '@tanstack/react-query'
import AccessDeniedPage from '@/shared/pages/AccessDeniedPage'
import AdminDashboard from '@/features/identity/pages/AdminDashboard'
import HROverviewDashboard from '@/features/employees/pages/HROverviewDashboard'
import { AreaFormPage } from '@/features/organization/pages/AreaFormPage'
import { AreasListPage } from '@/features/organization/pages/AreasListPage'
import { AreasManagementPage } from '@/features/organization/pages/AreasManagementPage'
import ChangePasswordPage from '@/features/auth/pages/ChangePasswordPage'
import ContratosPage from '@/features/contracts/pages/ContratosPage'
import ConfiguracionEmpresaPage from '@/features/organization/pages/ConfiguracionEmpresaPage'
import PlantillasDocumentosPage from '@/features/documents/pages/PlantillasDocumentosPage'
import { Dashboard } from '@/shared/pages/Dashboard'
import { Empleados } from '@/features/employees/pages/Empleados'
import DatosAcademicosPage from '@/features/employees/pages/DatosAcademicosPage'
import DatosFamiliaresPage from '@/features/employees/pages/DatosFamiliaresPage'
import DatosLaboralesPage from '@/features/employees/pages/DatosLaboralesPage'
import DatosPersonalesPage from '@/features/employees/pages/DatosPersonalesPage'
import EmpleadoReportPage from '@/features/employees/pages/EmpleadoReportPage'
import GestionDocumentosPage from '@/features/documents/pages/GestionDocumentosPage'
import LegajoPage from '@/features/documents/pages/LegajoPage'
import OnboardingAdminPage from '@/features/onboarding/pages/OnboardingAdminPage'
import OnboardingPage from '@/features/onboarding/pages/OnboardingPage'
import BoletasPagoPage from '@/features/payroll/pages/BoletasPagoPage'
import ConfiguracionRemuneracionesPage from '@/features/payroll/pages/ConfiguracionRemuneracionesPage'
import ConfiguracionUitPage from '@/features/payroll/pages/ConfiguracionUitPage'
import DescuentosMasivosPage from '@/features/payroll/pages/DescuentosMasivosPage'
import PlanillasMensualesPage from '@/features/payroll/pages/PlanillasMensualesPage'
import ProcesoPlanillasPage from '@/features/payroll/pages/ProcesoPlanillasPage'
import RemuneracionesHomePage from '@/features/payroll/pages/RemuneracionesHomePage'
import ReportesRemuneracionesPage from '@/features/payroll/pages/ReportesRemuneracionesPage'
import ResetPasswordPage from '@/features/auth/pages/ResetPasswordPage'
import PermissionsPage from '@/features/identity/pages/PermissionsPage'
import RolePermissionsPage from '@/features/identity/pages/RolePermissionsPage'
import RolesPage from '@/features/identity/pages/RolesPage'
import {
    RoleManagement,
    ChangePassword as UsersChangePassword,
    UsersForm,
    UsersList,
    UsersManagement
} from '@/features/identity/pages'
import ConfiguracionPage from '@/features/time-off/pages/ConfiguracionPage'
import NuevaSolicitudPage from '@/features/time-off/pages/NuevaSolicitudPage'
import PeriodosPage from '@/features/time-off/pages/PeriodosPage'
import ReportesPage from '@/features/time-off/pages/ReportesPage'
import SolicitudesPage from '@/features/time-off/pages/SolicitudesPage'
import VacacionesManagementPage from '@/features/time-off/pages/VacacionesManagementPage'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React, { Suspense, lazy } from 'react'
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import { AdminApp } from '@/features/admin'
import { TenantProvider, useTenant } from '@/shared/tenant'
import { ActivationPage, ImpersonationBanner } from '@/features/tenancy'
import { WorkspacesPage } from '@/features/workspace-switcher'

// B.6 OrgChart — lazy-loaded so @xyflow/react (~150 KB) stays off other routes.
const OrgChartPage = lazy(() => import('@/features/organization/pages/OrgChartPage'))

// B.7 CCF (Ley 30709 compliance) — lazy-loaded compensation admin pages.
const CCFListPage = lazy(() => import('@/features/compensation/pages/CCFListPage'))
const CCFEditorPage = lazy(() => import('@/features/compensation/pages/CCFEditorPage'))

// B.8 CPE/CAP/MPP (Ley 30057 SERVIR + DL 276/728) — public-sector gated.
const PositionRegisterListPage = lazy(
  () => import('@/features/organization/pages/PositionRegisterListPage'),
)
const PositionRegisterEditorPage = lazy(
  () => import('@/features/organization/pages/PositionRegisterEditorPage'),
)

// B.9 Selección (Module 03.1) — HR admin pages.
const RequisitionListPage = lazy(
  () => import('@/features/recruitment/pages/RequisitionListPage'),
)
const JobPostingEditorPage = lazy(
  () => import('@/features/recruitment/pages/JobPostingEditorPage'),
)
const CandidateDashboardPage = lazy(
  () => import('@/features/recruitment/pages/CandidateDashboardPage'),
)

// B.10 Vinculación + T-Registro (Module 03.2) — HR admin pages.
const TRegistroListPage = lazy(
  () => import('@/features/contracts/pages/TRegistroListPage'),
)
const DocumentSignatureListPage = lazy(
  () => import('@/features/documents/pages/DocumentSignatureListPage'),
)
const HiringBundleListPage = lazy(
  () => import('@/features/documents/pages/HiringBundleListPage'),
)

// B.11 Inducción + Período de prueba (Modules 03.3 + 03.4) — HR admin pages.
const InductionPlanListPage = lazy(
  () => import('@/features/onboarding/pages/InductionPlanListPage'),
)
const ProbationPeriodListPage = lazy(
  () => import('@/features/contracts/pages/ProbationPeriodListPage'),
)

// B.12 Legajos digitales completos (Module 03.5) — HR admin pages.
const DigitalDossierListPage = lazy(
  () => import('@/features/documents/pages/DigitalDossierListPage'),
)


const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

/** Ruta protegida que requiere rol de admin/rrhh */
function AdminRoute({ children }: Readonly<{ children: React.ReactNode }>) {
  const { isAuthenticated, isLoading, isAdminOrRRHH } = useAuth()

  if (isLoading) return <LoadingSpinner />
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (!isAdminOrRRHH()) return <Navigate to="/acceso-denegado" replace />

  return <>{children}</>
}

/** Ruta que redirige empleados con onboarding activo hacia /onboarding */
function OnboardingRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuth()
  const { data: onboarding, isLoading } = useQuery({
    queryKey: ['mi-onboarding'],
    queryFn: () => onboardingService.getMiOnboarding(),
    enabled: user?.tipo_usuario === 'empleado',
    retry: false,
    staleTime: 30_000,
  })

  if (user?.tipo_usuario !== 'empleado') return <>{children}</>
  if (isLoading) return <div className="flex items-center justify-center h-screen"><span className="text-muted-foreground">Cargando...</span></div>
  if (onboarding && onboarding.estado_onboarding !== 'completado') {
    return <Navigate to="/onboarding" replace />
  }
  return <>{children}</>
}

/** Ruta que evita que empleados con onboarding completado accedan a /onboarding */
function OnboardingGuard({ children }: { children: React.ReactNode }) {
  const { user } = useAuth()
  const { data: onboarding, isLoading } = useQuery({
    queryKey: ['mi-onboarding'],
    queryFn: () => onboardingService.getMiOnboarding(),
    enabled: user?.tipo_usuario === 'empleado',
    retry: false,
    staleTime: 30_000,
  })

  if (user?.tipo_usuario !== 'empleado') return <Navigate to="/" replace />
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <span className="text-muted-foreground">Cargando...</span>
      </div>
    )
  }
  if (onboarding?.estado_onboarding === 'completado') {
    return <Navigate to="/" replace />
  }
  return <>{children}</>
}

function AppRoutes() {
  const { isAuthenticated, isLoading, user } = useAuth()
  const tenant = useTenant()

  // Branch by tenant host type (unified replacement for the C.7 isAdminHost()
  // early return). Providers (QueryClient/Theme/Tenant/Auth/Router) remain
  // shared from App().
  if (tenant.type === 'admin') {
    return <AdminApp />
  }
  if (tenant.type === 'app') {
    return (
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="*" element={<WorkspacesPage />} />
      </Routes>
    )
  }
  if (tenant.type === 'www') {
    return (
      <div className="p-8 text-center">
        <h1 className="text-2xl font-semibold">VYNTIA</h1>
        <p className="mt-2 text-sm text-muted-foreground">Inicia sesión en tu workspace.</p>
      </div>
    )
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/activate" element={<ActivationPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="*" element={<LoginForm />} />
      </Routes>
    )
  }

  // Forzar cambio de password si es requerido
  if (user?.requiere_cambio_password) {
    return (
      <Layout>
        <ImpersonationBanner />
        <Routes>
          <Route path="/cambiar-password" element={<ChangePasswordPage />} />
          <Route path="*" element={<Navigate to="/cambiar-password" replace />} />
        </Routes>
      </Layout>
    )
  }

  return (
    <Layout>
      <ImpersonationBanner />
      <Routes>
        {/* Activacion de invitaciones (tambien accesible autenticado) */}
        <Route path="/activate" element={<ActivationPage />} />

        {/* --- Rutas comunes (todos los usuarios autenticados) --- */}
        <Route path="/" element={<OnboardingRoute><Dashboard /></OnboardingRoute>} />
        <Route path="/dashboard" element={<OnboardingRoute><Dashboard /></OnboardingRoute>} />
        <Route path="/cambiar-password" element={<ChangePasswordPage />} />
        <Route path="/acceso-denegado" element={<AccessDeniedPage />} />

        {/* Vacaciones - usuario normal (solicitar, ver mis solicitudes) */}
        <Route path="/vacaciones" element={<VacacionesManagementPage />} />
        <Route path="/vacaciones/nueva-solicitud" element={<NuevaSolicitudPage />} />
        <Route path="/vacaciones/solicitudes" element={<SolicitudesPage />} />

        {/* Legajo Digital - el usuario puede ver su propio legajo */}
        <Route path="/legajo" element={<LegajoPage />} />
        <Route path="/legajo/:empleadoId" element={<LegajoPage />} />

        {/* Datos del propio empleado (sin :id = datos propios) */}
        <Route path="/empleados/datos-personales" element={<DatosPersonalesPage />} />
        <Route path="/empleados/datos-laborales" element={<DatosLaboralesPage />} />
        <Route path="/empleados/datos-academicos" element={<DatosAcademicosPage />} />
        <Route path="/empleados/datos-familiares" element={<DatosFamiliaresPage />} />

        {/* Onboarding - empleado nuevo */}
        <Route path="/onboarding" element={
          <OnboardingGuard>
            <OnboardingPage />
          </OnboardingGuard>
        } />

        {/* --- Rutas de Administracion (solo admin/rrhh) --- */}
        <Route path="/admin" element={
          <AdminRoute>
            <AdminLayout>
              <AdminDashboard />
            </AdminLayout>
          </AdminRoute>
        } />

        {/* Panel de métricas RRHH */}
        <Route path="/rrhh/panel" element={
          <AdminRoute>
            <HROverviewDashboard />
          </AdminRoute>
        } />

        {/* Empleados - gestion admin */}
        <Route path="/empleados" element={
          <AdminRoute><Empleados /></AdminRoute>
        } />
        <Route path="/empleados/reporte/:id" element={
          <AdminRoute><EmpleadoReportPage /></AdminRoute>
        } />

        {/* Onboarding - gestion admin */}
        <Route path="/onboarding/admin" element={
          <AdminRoute><OnboardingAdminPage /></AdminRoute>
        } />

        {/* Legajo Digital - gestion admin */}
        <Route path="/legajo/gestion" element={
          <AdminRoute><GestionDocumentosPage /></AdminRoute>
        } />

        {/* Contratos y Adendas - gestion admin */}
        <Route path="/contratos" element={
          <AdminRoute><ContratosPage /></AdminRoute>
        } />

        <Route path="/plantillas-documentos" element={
          <AdminRoute><AdminLayout><PlantillasDocumentosPage /></AdminLayout></AdminRoute>
        } />

        <Route path="/configuracion/empresa" element={
          <AdminRoute><AdminLayout><ConfiguracionEmpresaPage /></AdminLayout></AdminRoute>
        } />

        <Route path="/empleados/datos-personales/:id" element={
          <AdminRoute><DatosPersonalesPage /></AdminRoute>
        } />
        <Route path="/empleados/datos-laborales/:id" element={
          <AdminRoute><DatosLaboralesPage /></AdminRoute>
        } />
        <Route path="/empleados/datos-academicos/:id" element={
          <AdminRoute><DatosAcademicosPage /></AdminRoute>
        } />
        <Route path="/empleados/datos-familiares/:id" element={
          <AdminRoute><DatosFamiliaresPage /></AdminRoute>
        } />

        {/* Usuarios */}
        <Route path="/usuarios" element={<AdminRoute><Navigate to="/usuarios/listado" replace /></AdminRoute>} />
        <Route path="/usuarios/listado" element={<AdminRoute><UsersList /></AdminRoute>} />
        <Route path="/usuarios/crear" element={<AdminRoute><UsersForm /></AdminRoute>} />
        <Route path="/usuarios/editar/:id" element={<AdminRoute><UsersForm /></AdminRoute>} />
        <Route path="/usuarios/gestion/:id" element={<AdminRoute><UsersManagement /></AdminRoute>} />
        <Route path="/usuarios/cambiar-password/:id" element={<AdminRoute><UsersChangePassword /></AdminRoute>} />
        <Route path="/usuarios/roles/:id" element={<AdminRoute><RoleManagement /></AdminRoute>} />

        {/* Seguridad */}
        <Route path="/seguridad/permisos" element={<AdminRoute><PermissionsPage /></AdminRoute>} />
        <Route path="/seguridad/roles" element={<AdminRoute><RolesPage /></AdminRoute>} />
        <Route path="/seguridad/roles-permisos" element={<AdminRoute><RolePermissionsPage /></AdminRoute>} />

        {/* Areas */}
        <Route path="/areas/listado" element={<AdminRoute><AreasListPage /></AdminRoute>} />
        <Route path="/areas/crear" element={<AdminRoute><AreaFormPage /></AdminRoute>} />
        <Route path="/areas/editar/:id" element={<AdminRoute><AreaFormPage /></AdminRoute>} />
        <Route path="/areas/gestion" element={<AdminRoute><AreasManagementPage /></AdminRoute>} />

        {/* Organization — OrgChart (B.6) */}
        <Route
          path="/organizacion/orgchart"
          element={
            <Suspense fallback={<LoadingSpinner />}>
              <OrgChartPage />
            </Suspense>
          }
        />

        {/* Compensation — CCF (Ley 30709, B.7) */}
        <Route
          path="/compensacion/ccf"
          element={
            <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <CCFListPage />
              </Suspense>
            </AdminRoute>
          }
        />
        <Route
          path="/compensacion/ccf/:id"
          element={
            <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <CCFEditorPage />
              </Suspense>
            </AdminRoute>
          }
        />

        {/* Organization — CPE/CAP + MPP (Ley 30057 SERVIR + DL 276/728, B.8) */}
        <Route
          path="/organizacion/registros/:type"
          element={
            <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <PositionRegisterListPage />
              </Suspense>
            </AdminRoute>
          }
        />
        <Route
          path="/organizacion/registros/:type/:id"
          element={
            <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <PositionRegisterEditorPage />
              </Suspense>
            </AdminRoute>
          }
        />

        {/* Selección — Module 03.1 (B.9) */}
        <Route
          path="/seleccion/requisiciones"
          element={
            <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <RequisitionListPage />
              </Suspense>
            </AdminRoute>
          }
        />
        <Route
          path="/seleccion/convocatorias"
          element={
            <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <JobPostingEditorPage />
              </Suspense>
            </AdminRoute>
          }
        />
        <Route
          path="/seleccion/convocatorias/:id/candidatos"
          element={
            <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <CandidateDashboardPage />
              </Suspense>
            </AdminRoute>
          }
        />

        {/* Vinculación + T-Registro — Module 03.2 (B.10) */}
        <Route
          path="/vinculacion/t-registro"
          element={
            <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <TRegistroListPage />
              </Suspense>
            </AdminRoute>
          }
        />
        <Route
          path="/vinculacion/firmas"
          element={
            <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <DocumentSignatureListPage />
              </Suspense>
            </AdminRoute>
          }
        />
        <Route
          path="/vinculacion/bundles"
          element={
            <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <HiringBundleListPage />
              </Suspense>
            </AdminRoute>
          }
        />

        {/* Inducción + Período de prueba — Modules 03.3 + 03.4 (B.11) */}
        <Route
          path="/induccion"
          element={
            <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <InductionPlanListPage />
              </Suspense>
            </AdminRoute>
          }
        />
        <Route
          path="/periodo-prueba"
          element={
            <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <ProbationPeriodListPage />
              </Suspense>
            </AdminRoute>
          }
        />

        {/* Legajos digitales — Module 03.5 (B.12) */}
        <Route
          path="/legajos-digitales"
          element={
            <AdminRoute>
              <Suspense fallback={<LoadingSpinner />}>
                <DigitalDossierListPage />
              </Suspense>
            </AdminRoute>
          }
        />

        {/* Vacaciones - gestion admin */}
        <Route path="/vacaciones/periodos" element={<AdminRoute><PeriodosPage /></AdminRoute>} />
        <Route path="/vacaciones/reportes" element={<AdminRoute><ReportesPage /></AdminRoute>} />
        <Route path="/vacaciones/configuracion" element={<AdminRoute><ConfiguracionPage /></AdminRoute>} />

        {/* Remuneraciones - modulo principal y submenus */}
        <Route path="/remuneraciones" element={<AdminRoute><RemuneracionesHomePage /></AdminRoute>} />
        <Route path="/remuneraciones/planillas-mensuales" element={<AdminRoute><PlanillasMensualesPage /></AdminRoute>} />
        <Route path="/remuneraciones/proceso-planillas" element={<AdminRoute><ProcesoPlanillasPage /></AdminRoute>} />
        <Route path="/remuneraciones/boletas-pago" element={<AdminRoute><BoletasPagoPage /></AdminRoute>} />
        <Route path="/remuneraciones/descuentos-masivos" element={<AdminRoute><DescuentosMasivosPage /></AdminRoute>} />
        <Route path="/remuneraciones/reportes" element={<AdminRoute><ReportesRemuneracionesPage /></AdminRoute>} />
        <Route path="/remuneraciones/configuracion" element={<AdminRoute><ConfiguracionRemuneracionesPage /></AdminRoute>} />
        <Route path="/remuneraciones/configuracion-uit" element={<AdminRoute><ConfiguracionUitPage /></AdminRoute>} />

        {/* Desplazamiento - en desarrollo */}
        <Route
          path="/desplazamiento"
          element={
            <AdminRoute>
              <div className="flex flex-col items-center justify-center h-64 gap-3 text-muted-foreground">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
                <h2 className="text-xl font-semibold text-foreground">Desplazamiento</h2>
                <p className="text-sm">Modulo en desarrollo</p>
              </div>
            </AdminRoute>
          }
        />

        <Route
          path="/ubicaciones"
          element={
            <AdminRoute>
              <div className="text-center py-8">
                <h2 className="text-2xl font-bold">Ubicaciones</h2>
                <p className="text-muted-foreground mt-2">Modulo en desarrollo</p>
              </div>
            </AdminRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light" storageKey="hr-system-theme">
        <TenantProvider>
          <AuthProvider>
            <Router>
              <AppRoutes />
              <Toaster />
              <SonnerToaster richColors position="top-right" />
            </Router>
          </AuthProvider>
        </TenantProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App