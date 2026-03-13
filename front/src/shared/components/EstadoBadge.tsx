import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { AlertCircle, CheckCircle2, Circle, Clock, XCircle } from 'lucide-react';
import React from 'react';

export type EstadoType =
  | 'activo'
  | 'inactivo'
  | 'pendiente'
  | 'aprobado'
  | 'rechazado'
  | 'proceso'
  | 'vigente'
  | 'vencido'
  | 'por_vencer'
  | 'suspendido'
  | 'cesado';

interface EstadoBadgeProps {
  estado: EstadoType;
  showIcon?: boolean;
  size?: 'sm' | 'default' | 'lg';
  className?: string;
}

const estadoConfig: Record<
  EstadoType,
  {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    className: string;
  }
> = {
  activo: {
    label: 'Activo',
    icon: CheckCircle2,
    className: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  },
  inactivo: {
    label: 'Inactivo',
    icon: Circle,
    className: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
  },
  pendiente: {
    label: 'Pendiente',
    icon: Clock,
    className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
  },
  aprobado: {
    label: 'Aprobado',
    icon: CheckCircle2,
    className: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  },
  rechazado: {
    label: 'Rechazado',
    icon: XCircle,
    className: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
  },
  proceso: {
    label: 'En Proceso',
    icon: AlertCircle,
    className: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  },
  vigente: {
    label: 'Vigente',
    icon: CheckCircle2,
    className: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  },
  vencido: {
    label: 'Vencido',
    icon: XCircle,
    className: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
  },
  por_vencer: {
    label: 'Por Vencer',
    icon: AlertCircle,
    className: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
  },
  suspendido: {
    label: 'Suspendido',
    icon: AlertCircle,
    className: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
  },
  cesado: {
    label: 'Cesado',
    icon: XCircle,
    className: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
  },
};

const sizeClasses = {
  sm: 'text-xs px-2 py-0.5',
  default: 'text-sm px-2.5 py-0.5',
  lg: 'text-base px-3 py-1',
};

const iconSizeClasses = {
  sm: 'h-3 w-3',
  default: 'h-4 w-4',
  lg: 'h-5 w-5',
};

export const EstadoBadge: React.FC<EstadoBadgeProps> = ({
  estado,
  showIcon = true,
  size = 'default',
  className,
}) => {
  const config = estadoConfig[estado];
  const Icon = config.icon;

  return (
    <Badge
      variant="outline"
      className={cn(config.className, sizeClasses[size], 'font-medium', className)}
    >
      {showIcon && <Icon className={cn(iconSizeClasses[size], 'mr-1')} />}
      {config.label}
    </Badge>
  );
};

export default EstadoBadge;
