import { useEffect, useRef } from 'react'
import { animate, stagger, utils } from 'animejs'

// Hook para animaciones de entrada
export function useEntranceAnimation({
  trigger = true,
  delay = 0,
  duration = 600,
  easing = 'easeOutQuart',
  direction = 'up'
} = {}) {
  const elementRef = useRef<HTMLElement>(null)

  useEffect(() => {
    if (!trigger || !elementRef.current) return

    const element = elementRef.current
    
    // Configuración inicial basada en la dirección
    const initialTransform = {
      up: { translateY: 50, opacity: 0 },
      down: { translateY: -50, opacity: 0 },
      left: { translateX: 50, opacity: 0 },
      right: { translateX: -50, opacity: 0 },
      scale: { scale: 0.8, opacity: 0 },
      rotate: { rotate: 180, scale: 0.8, opacity: 0 }
    }

    // Aplicar estado inicial
    utils.set(element, initialTransform[direction as keyof typeof initialTransform])

    // Animar a estado final
    animate(element, {
      translateX: 0,
      translateY: 0,
      scale: 1,
      rotate: 0,
      opacity: 1,
      duration,
      delay,
      ease: easing
    })
  }, [trigger, delay, duration, easing, direction])

  return elementRef
}

// Hook para animaciones de hover
export function useHoverAnimation({
  scale = 1.05,
  duration = 200,
  easing = 'easeOutQuart'
} = {}) {
  const elementRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const element = elementRef.current
    if (!element) return

    const handleMouseEnter = () => {
      animate(element, {
        scale,
        duration,
        ease: easing
      })
    }

    const handleMouseLeave = () => {
      animate(element, {
        scale: 1,
        duration,
        ease: easing
      })
    }

    element.addEventListener('mouseenter', handleMouseEnter)
    element.addEventListener('mouseleave', handleMouseLeave)

    return () => {
      element.removeEventListener('mouseenter', handleMouseEnter)
      element.removeEventListener('mouseleave', handleMouseLeave)
    }
  }, [scale, duration, easing])

  return elementRef
}

// Hook para animaciones de lista escalonadas
export function useStaggerAnimation({
  trigger = true,
  delay = 100,
  duration = 600,
  easing = 'easeOutQuart'
} = {}) {
  const containerRef = useRef<HTMLElement>(null)

  useEffect(() => {
    if (!trigger || !containerRef.current) return

    const children = containerRef.current.children
    
    // Configurar estado inicial
    utils.set(children, {
      translateY: 30,
      opacity: 0
    })

    // Animar con retraso escalonado
    animate(children, {
      translateY: 0,
      opacity: 1,
      duration,
      delay: stagger(delay),
      ease: easing
    })
  }, [trigger, delay, duration, easing])

  return containerRef
}

// Hook para animaciones de carga
export function useLoadingAnimation() {
  const elementRef = useRef<HTMLElement>(null)

  const startLoading = () => {
    if (!elementRef.current) return

    animate(elementRef.current, {
      rotate: '1turn',
      duration: 1000,
      loop: true,
      ease: 'linear'
    })
  }

  const stopLoading = () => {
    if (elementRef.current) {
      utils.remove(elementRef.current)
    }
  }

  return { elementRef, startLoading, stopLoading }
}

// Hook para animaciones de progreso
export function useProgressAnimation(progress: number) {
  const elementRef = useRef<HTMLElement>(null)

  useEffect(() => {
    if (!elementRef.current) return

    animate(elementRef.current, {
      width: `${progress}%`,
      duration: 800,
      ease: 'easeOutQuart'
    })
  }, [progress])

  return elementRef
}

// Hook para animaciones de notificaciones
export function useNotificationAnimation({
  show = false,
  position = 'top-right'
} = {}) {
  const elementRef = useRef<HTMLElement>(null)

  useEffect(() => {
    if (!elementRef.current) return

    const element = elementRef.current
    
    if (show) {
      // Animación de entrada
      utils.set(element, {
        translateX: position.includes('right') ? 100 : -100,
        opacity: 0
      })
      
      animate(element, {
        translateX: 0,
        opacity: 1,
        duration: 400,
        ease: 'easeOutBack'
      })
    } else {
      // Animación de salida
      animate(element, {
        translateX: position.includes('right') ? 100 : -100,
        opacity: 0,
        duration: 300,
        ease: 'easeInQuart'
      })
    }
  }, [show, position])

  return elementRef
}

// Utilidad para animaciones personalizadas
export function animateElement({
  target,
  properties,
  duration = 600,
  delay = 0,
  easing = 'easeOutQuart',
  complete
}: {
  target: string | HTMLElement | HTMLElement[]
  properties: Record<string, any>
  duration?: number
  delay?: number
  easing?: string
  complete?: () => void
}) {
  return animate(target, {
    ...properties,
    duration,
    delay,
    ease: easing,
    complete
  })
}