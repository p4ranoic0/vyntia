import { cn } from '@/lib/utils'

interface VyntiaLogoProps {
  readonly className?: string
  readonly size?: number
}

/**
 * VYNTIA logo (placeholder geometric mark — nodos conectados + violeta).
 * Definitive logo will replace this once branding deliverables arrive.
 */
export function VyntiaLogo({ className, size = 32 }: VyntiaLogoProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 64 64"
      width={size}
      height={size}
      role="img"
      aria-label="VYNTIA logo"
      className={cn('flex-shrink-0', className)}
    >
      <defs>
        <linearGradient id="vyntiaLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#6C63FF" />
          <stop offset="100%" stopColor="#3B82F6" />
        </linearGradient>
      </defs>
      <rect width="64" height="64" rx="14" fill="url(#vyntiaLogoGrad)" />
      <g fill="none" stroke="#FFFFFF" strokeWidth={2.4} strokeLinecap="round">
        <circle cx={20} cy={20} r={3.2} fill="#FFFFFF" stroke="none" />
        <circle cx={44} cy={20} r={3.2} fill="#FFFFFF" stroke="none" />
        <circle cx={32} cy={44} r={3.2} fill="#FFFFFF" stroke="none" />
        <path d="M20 20 Q32 8 44 20" />
        <path d="M44 20 Q50 36 32 44" />
        <path d="M32 44 Q14 36 20 20" />
      </g>
    </svg>
  )
}
