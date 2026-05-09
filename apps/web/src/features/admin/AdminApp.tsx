import { Navigate, Route, Routes } from 'react-router-dom'

import { AdminLayout } from './components/AdminLayout'
import { AdminLoginGate } from './components/AdminLoginGate'
import { CreateTenantPage } from './pages/CreateTenantPage'
import { SupportSessionsListPage } from './pages/SupportSessionsListPage'
import { TenantDetailPage } from './pages/TenantDetailPage'
import { TenantsListPage } from './pages/TenantsListPage'

/**
 * Top-level shell for admin.vyntia.pe.
 * 1. AdminLoginGate: requires authenticated + is_vyntia_staff
 * 2. AdminLayout: sidebar + outlet
 * 3. Admin routes
 */
export function AdminApp() {
  return (
    <AdminLoginGate>
      <Routes>
        <Route element={<AdminLayout />}>
          <Route path="/admin/tenants" element={<TenantsListPage />} />
          <Route path="/admin/tenants/new" element={<CreateTenantPage />} />
          <Route path="/admin/tenants/:id" element={<TenantDetailPage />} />
          <Route path="/admin/support-sessions" element={<SupportSessionsListPage />} />
          <Route path="*" element={<Navigate to="/admin/tenants" replace />} />
        </Route>
      </Routes>
    </AdminLoginGate>
  )
}
