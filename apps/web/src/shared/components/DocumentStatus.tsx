import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import { File, FileCheck, FileWarning, FileX } from 'lucide-react';
import React from 'react';

export type DocumentStatusType = 'vigente' | 'vencido' | 'por_vencer' | 'no_presenta';

interface DocumentStatusProps {
  status: DocumentStatusType;
  documentName?: string;
  expirationDate?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

const statusConfig: Record<
  DocumentStatusType,
  {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    color: string;
    bgColor: string;
  }
> = {
  vigente: {
    label: 'Vigente',
    icon: FileCheck,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950',
  },
  vencido: {
    label: 'Vencido',
    icon: FileX,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950',
  },
  por_vencer: {
    label: 'Por Vencer',
    icon: FileWarning,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 dark:bg-orange-950',
  },
  no_presenta: {
    label: 'No Presenta',
    icon: File,
    color: 'text-gray-500',
    bgColor: 'bg-gray-50 dark:bg-gray-900',
  },
};

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-5 w-5',
  lg: 'h-6 w-6',
};

export const DocumentStatus: React.FC<DocumentStatusProps> = ({
  status,
  documentName,
  expirationDate,
  size = 'md',
  showLabel = false,
  className,
}) => {
  const config = statusConfig[status];
  const Icon = config.icon;

  const content = (
    <div className={cn('flex items-center gap-2', className)}>
      <div
        className={cn(
          'rounded-full p-1.5',
          config.bgColor
        )}
      >
        <Icon className={cn(sizeClasses[size], config.color)} />
      </div>
      {showLabel && (
        <span className={cn('text-sm font-medium', config.color)}>
          {config.label}
        </span>
      )}
    </div>
  );

  if (documentName || expirationDate) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            {content}
          </TooltipTrigger>
          <TooltipContent>
            <div className="space-y-1">
              {documentName && (
                <p className="font-medium">{documentName}</p>
              )}
              <p className="text-sm">
                Estado: <span className={cn('font-medium', config.color)}>{config.label}</span>
              </p>
              {expirationDate && (
                <p className="text-sm text-muted-foreground">
                  {status === 'vencido' ? 'Venció' : 'Vence'}: {expirationDate}
                </p>
              )}
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return content;
};

export default DocumentStatus;
