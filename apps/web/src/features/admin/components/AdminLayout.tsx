import { Link, Outlet, useLocation } from 'react-router-dom'
import { Building2, LogOut, ShieldAlert } from 'lucide-react'

import { useAuth } from '@/features/auth/hooks/useAuth'
import { Button } from '@/shared/ui/button'

export function AdminLayout() {
  const { user, logout } = useAuth()
  const { pathname } = useLocation()

  const navItem = (path: string, label: string, Icon: typeof Building2) => {
    const active = pathname.startsWith(path)
    return (
      <Link
        to={path}
        className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors ${
          active ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'
        }`}
      >
        <Icon size={16} aria-hidden />
        <span>{label}</span>
      </Link>
    )
  }

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r bg-card p-4">
        <div className="mb-6 flex items-center gap-2 px-2 font-semibold">
          <ShieldAlert size={18} className="text-primary" />
          <span>VYNTIA Admin</span>
        </div>
        <nav className="space-y-1">
          {navItem('/admin/tenants', 'Tenants', Building2)}
          {navItem('/admin/support-sessions', 'Support Sessions', ShieldAlert)}
        </nav>
        <div className="mt-8 border-t pt-4 px-2 text-xs text-muted-foreground">
          {user?.email}
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="mt-2 w-full justify-start"
          onClick={() => logout()}
        >
          <LogOut size={14} className="mr-2" /> Cerrar sesión
        </Button>
      </aside>
      <main className="flex-1 overflow-auto p-8">
        <Outlet />
      </main>
    </div>
  )
}
