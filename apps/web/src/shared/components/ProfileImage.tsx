import React from 'react'
import { User } from 'lucide-react'
import { cn } from '@/shared/utils/cn'

interface ProfileImageProps {
  src?: string | null
  alt?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizeClasses = {
  sm: 'w-8 h-8',
  md: 'w-12 h-12',
  lg: 'w-16 h-16'
}

const iconSizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8'
}

export function ProfileImage({ src, alt = 'Foto de perfil', size = 'md', className }: ProfileImageProps) {
  const [imageError, setImageError] = React.useState(false)
  
  const handleImageError = () => {
    setImageError(true)
  }
  
  if (!src || imageError) {
    return (
      <div 
        className={cn(
          'rounded-full bg-muted flex items-center justify-center border-2 border-border',
          sizeClasses[size],
          className
        )}
      >
        <User className={cn('text-muted-foreground', iconSizeClasses[size])} />
      </div>
    )
  }
  
  return (
    <img
      src={src}
      alt={alt}
      className={cn(
        'rounded-full object-cover border-2 border-border',
        sizeClasses[size],
        className
      )}
      onError={handleImageError}
    />
  )
}