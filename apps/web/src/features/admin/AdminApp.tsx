import { Navigate, Route, Routes } from 'react-router-dom'

import { AdminLayout } from './components/AdminLayout'
import { AdminLoginGate } from './components/AdminLoginGate'

// Page imports — added in Tasks 4-6 (placeholders OK in Task 3)
const TenantsListPage = () => <div>Tenants list (C.7 Task 4)</div>
const CreateTenantPage = () => <div>Create tenant (C.7 Task 5)</div>
const TenantDetailPage = () => <div>Tenant detail (C.7 Task 5)</div>
const SupportSessionsListPage = () => <div>Support sessions (C.7 Task 6)</div>

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
