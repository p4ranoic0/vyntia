import { cn } from '@/shared/utils/cn'
import { VyntiaLogo } from './VyntiaLogo'

interface VyntiaWordmarkProps {
  readonly className?: string
  readonly logoSize?: number
  readonly hideText?: boolean
}

/**
 * VYNTIA wordmark — logo + nombre. Usado en sidebar header y login.
 */
export function VyntiaWordmark({
  className,
  logoSize = 32,
  hideText = false,
}: VyntiaWordmarkProps) {
  return (
    <div className={cn('flex items-center gap-2 min-w-0', className)}>
      <VyntiaLogo size={logoSize} />
      {!hideText && (
        <span className="text-lg sm:text-xl font-bold tracking-tight text-foreground truncate">
          VYNTIA
        </span>
      )}
    </div>
  )
}
