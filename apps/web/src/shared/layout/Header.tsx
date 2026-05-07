import NotificationsBell from '@/shared/layout/NotificationsBell'
import { Avatar, AvatarFallback, AvatarImage } from '@/shared/ui/avatar'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/shared/ui/dropdown-menu'
import { Input } from '@/shared/ui/input'
import { useTheme } from '@/shared/context/ThemeContext'
import { useEntranceAnimation, useStaggerAnimation } from '@/shared/hooks/useAnimations'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useScrolled } from '@/shared/hooks/useScrolled'
import { cn, getInitials } from '@/shared/utils/cn'
import { Menu, Moon, Search, Shield, Sun, User } from 'lucide-react'
import React from 'react'
import { Link } from 'react-router-dom'

interface HeaderProps {
  onMenuToggle?: () => void
  isSidebarCollapsed?: boolean
}

export function Header({ onMenuToggle, isSidebarCollapsed }: HeaderProps) {
  const { user, logout, isAdminOrRRHH } = useAuth()
  const { theme, setTheme } = useTheme()
  const isScrolled = useScrolled(10)

  // Hooks de animacion
  const headerRef = useEntranceAnimation({ direction: 'top', duration: 500 })
  const actionsRef = useStaggerAnimation({ delay: 100, duration: 300 })

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  // Construir nombre del usuario desde datos de empleado o username
  const userName = user?.empleado
    ? `${user.empleado.nombres || ''} ${user.empleado.apellido_paterno || ''}`.trim()
    : user?.username || ''
  const userInitials = getInitials(userName || 'Usuario')

  const userRoleLabel = (() => {
    if (!user) return ''
    if (user.tipo_usuario === 'administrador') return 'Administrador'
    if (user.tipo_usuario === 'rrhh') return 'RRHH'
    if (user.tipo_usuario === 'jefe') return 'Jefe'
    if (user.tipo_usuario === 'empleado') return 'Empleado'
    return user.tipo_usuario || 'Usuario'
  })()

  return (
    <header
      ref={headerRef as React.RefObject<HTMLElement>}
      className={cn(
        "h-14 sm:h-16 bg-header-bg border-b border-header-border flex items-center justify-between px-3 sm:px-6 sticky top-0 z-30 animate-slide-in-top transition-shadow duration-200",
        isScrolled && "shadow-header"
      )}
    >
      {/* Left section */}
      <div className="flex items-center space-x-2 sm:space-x-4">
        {/* Mobile menu toggle */}
        {onMenuToggle && (
          <Button variant="ghost" size="icon" onClick={onMenuToggle} className="lg:hidden h-10 w-10 cursor-pointer">
            <Menu className="w-5 h-5" />
          </Button>
        )}

        {/* Search - hidden on mobile, shown on sm+ */}
        <div className="relative hidden sm:flex flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" aria-hidden="true" />
          <Input placeholder="Buscar..." aria-label="Buscar en el sistema" className="pl-10 pr-4 w-full bg-muted/40 border-0 focus-visible:bg-background focus-visible:border-primary/50" />
        </div>
      </div>

      {/* Right section */}
      <div
        ref={actionsRef as React.RefObject<HTMLDivElement>}
        className="flex items-center space-x-1 sm:space-x-3"
      >
        {/* Search icon for mobile */}
        <Button variant="ghost" size="icon" aria-label="Buscar" className="sm:hidden h-10 w-10 cursor-pointer">
          <Search className="w-5 h-5" aria-hidden="true" />
        </Button>

        {/* Theme toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          aria-label={theme === 'light' ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro'}
          className="h-10 w-10 cursor-pointer"
        >
          {theme === 'light' ? (
            <Moon className="w-5 h-5 transition-transform duration-300" />
          ) : (
            <Sun className="w-5 h-5 transition-transform duration-300" />
          )}
        </Button>

        {/* Notifications */}
        <div className="border-l border-border/50 pl-1 sm:pl-2">
          <NotificationsBell />
        </div>

        {/* User menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-10 rounded-full flex items-center gap-2 px-2 cursor-pointer">
              <Avatar className="h-8 w-8 ring-2 ring-border">
                <AvatarImage src="" alt={userName} />
                <AvatarFallback className="bg-primary text-primary-foreground text-xs font-medium">
                  {userInitials}
                </AvatarFallback>
              </Avatar>
              <div className="hidden md:flex flex-col items-start">
                <span className="text-sm font-medium leading-none">{userName}</span>
                <span className="text-[10px] text-muted-foreground leading-none mt-0.5">{userRoleLabel}</span>
              </div>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end" forceMount>
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">{userName}</p>
                <p className="text-xs leading-none text-muted-foreground">
                  {user?.email}
                </p>
                <Badge variant={isAdminOrRRHH() ? 'default' : 'secondary'} className="text-[10px] w-fit mt-1">
                  {userRoleLabel}
                </Badge>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild>
              <Link to="/empleados/datos-personales" className="cursor-pointer">
                <User className="mr-2 h-4 w-4" />
                <span>Mi Perfil</span>
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link to="/cambiar-password" className="cursor-pointer">
                <Shield className="mr-2 h-4 w-4" />
                <span>Cambiar Contrasena</span>
              </Link>
            </DropdownMenuItem>
            {isAdminOrRRHH() && (
              <>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link to="/admin" className="cursor-pointer">
                    <Shield className="mr-2 h-4 w-4" />
                    <span>Panel de Administracion</span>
                  </Link>
                </DropdownMenuItem>
              </>
            )}
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout} className="cursor-pointer text-destructive">
              <span>Cerrar sesion</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
