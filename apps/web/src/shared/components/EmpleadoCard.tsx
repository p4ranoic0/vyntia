import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { cn, getInitials } from '@/lib/utils';
import { Briefcase, Mail, MapPin, Phone } from 'lucide-react';
import React from 'react';

interface EmpleadoCardProps {
  empleado: {
    nombres_empleado?: string;
    apellido_paterno?: string;
    apellido_materno?: string;
    email_corporativo?: string;
    telefono_corporativo?: string;
    cargo?: string;
    area?: string;
    estado?: 'activo' | 'inactivo' | 'suspendido' | 'cesado';
    foto_url?: string;
  };
  variant?: 'default' | 'compact' | 'detailed';
  className?: string;
  onClick?: () => void;
}

const estadoConfig = {
  activo: { label: 'Activo', className: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' },
  inactivo: { label: 'Inactivo', className: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300' },
  suspendido: { label: 'Suspendido', className: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300' },
  cesado: { label: 'Cesado', className: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' },
};

export const EmpleadoCard: React.FC<EmpleadoCardProps> = ({
  empleado,
  variant = 'default',
  className,
  onClick,
}) => {
  const nombreCompleto = `${empleado.apellido_paterno || ''} ${empleado.apellido_materno || ''}, ${empleado.nombres_empleado || ''}`.trim();
  const iniciales = getInitials(
    empleado.nombres_empleado || '',
    empleado.apellido_paterno || ''
  );

  const estado = empleado.estado || 'activo';
  const estadoInfo = estadoConfig[estado];

  if (variant === 'compact') {
    return (
      <div
        className={cn(
          'flex items-center gap-3 p-3 rounded-lg hover:bg-accent cursor-pointer transition-colors',
          className
        )}
        onClick={onClick}
      >
        <Avatar className="h-10 w-10">
          <AvatarImage src={empleado.foto_url} alt={nombreCompleto} />
          <AvatarFallback>{iniciales}</AvatarFallback>
        </Avatar>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">{nombreCompleto}</p>
          <p className="text-xs text-muted-foreground truncate">{empleado.cargo}</p>
        </div>
        <Badge variant="outline" className={estadoInfo.className}>
          {estadoInfo.label}
        </Badge>
      </div>
    );
  }

  return (
    <Card
      className={cn(
        'hover:shadow-md transition-shadow cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start gap-4">
          <Avatar className="h-16 w-16">
            <AvatarImage src={empleado.foto_url} alt={nombreCompleto} />
            <AvatarFallback className="text-lg">{iniciales}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-lg truncate">{nombreCompleto}</h3>
            <div className="flex items-center gap-2 mt-1">
              <Briefcase className="h-4 w-4 text-muted-foreground" />
              <p className="text-sm text-muted-foreground truncate">{empleado.cargo}</p>
            </div>
            <Badge variant="outline" className={cn('mt-2', estadoInfo.className)}>
              {estadoInfo.label}
            </Badge>
          </div>
        </div>
      </CardHeader>

      {variant === 'detailed' && (
        <CardContent className="pt-0 space-y-2">
          {empleado.area && (
            <div className="flex items-center gap-2 text-sm">
              <MapPin className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Área:</span>
              <span className="font-medium">{empleado.area}</span>
            </div>
          )}
          {empleado.email_corporativo && (
            <div className="flex items-center gap-2 text-sm">
              <Mail className="h-4 w-4 text-muted-foreground" />
              <a
                href={`mailto:${empleado.email_corporativo}`}
                className="text-primary hover:underline truncate"
                onClick={(e) => e.stopPropagation()}
              >
                {empleado.email_corporativo}
              </a>
            </div>
          )}
          {empleado.telefono_corporativo && (
            <div className="flex items-center gap-2 text-sm">
              <Phone className="h-4 w-4 text-muted-foreground" />
              <a
                href={`tel:${empleado.telefono_corporativo}`}
                className="text-primary hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                {empleado.telefono_corporativo}
              </a>
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
};

export default EmpleadoCard;
