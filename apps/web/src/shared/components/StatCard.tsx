import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';
import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: LucideIcon;
  trend?: {
    value: number;
    label: string;
    isPositive?: boolean;
  };
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
  className?: string;
}

const variantStyles = {
  default: {
    card: 'border-border',
    icon: 'text-muted-foreground bg-muted',
    value: 'text-foreground',
  },
  primary: {
    card: 'border-primary/20 bg-primary/5',
    icon: 'text-primary bg-primary/10',
    value: 'text-primary',
  },
  success: {
    card: 'border-green-200 bg-green-50 dark:border-green-900 dark:bg-green-950',
    icon: 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900',
    value: 'text-green-700 dark:text-green-400',
  },
  warning: {
    card: 'border-orange-200 bg-orange-50 dark:border-orange-900 dark:bg-orange-950',
    icon: 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900',
    value: 'text-orange-700 dark:text-orange-400',
  },
  danger: {
    card: 'border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950',
    icon: 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900',
    value: 'text-red-700 dark:text-red-400',
  },
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  description,
  icon: Icon,
  trend,
  variant = 'default',
  className,
}) => {
  const styles = variantStyles[variant];

  return (
    <Card className={cn(styles.card, className)}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <div className="mt-2 flex items-baseline gap-2">
              <p className={cn('text-3xl font-bold', styles.value)}>{value}</p>
              {trend && (
                <span
                  className={cn(
                    'text-sm font-medium',
                    trend.isPositive ? 'text-green-600' : 'text-red-600'
                  )}
                >
                  {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
                </span>
              )}
            </div>
            {description && (
              <p className="mt-1 text-sm text-muted-foreground">{description}</p>
            )}
            {trend?.label && (
              <p className="mt-2 text-xs text-muted-foreground">{trend.label}</p>
            )}
          </div>
          {Icon && (
            <div className={cn('rounded-lg p-3', styles.icon)}>
              <Icon className="h-6 w-6" />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default StatCard;
