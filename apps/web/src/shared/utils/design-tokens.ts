/**
 * Design Tokens - Sistema de diseño VYNTIA
 *
 * Centraliza todos los valores de diseño reutilizables del sistema.
 */

// ============================================================================
// COLORES
// ============================================================================

export const colors = {
  // Estados de empleado
  empleado: {
    activo: "hsl(142, 76%, 36%)", // green-600
    inactivo: "hsl(0, 0%, 45%)", // gray-600
    suspendido: "hsl(25, 95%, 53%)", // orange-500
    cesado: "hsl(0, 72%, 51%)", // red-600
  },

  // Estados de solicitudes/trámites
  solicitud: {
    pendiente: "hsl(48, 96%, 53%)", // yellow-500
    aprobado: "hsl(142, 76%, 36%)", // green-600
    rechazado: "hsl(0, 72%, 51%)", // red-600
    proceso: "hsl(217, 91%, 60%)", // blue-500
  },

  // Estados de documentos
  documento: {
    vigente: "hsl(142, 76%, 36%)", // green-600
    vencido: "hsl(0, 72%, 51%)", // red-600
    porVencer: "hsl(25, 95%, 53%)", // orange-500
    noPresenta: "hsl(0, 0%, 45%)", // gray-600
  },

  // Prioridades
  prioridad: {
    alta: "hsl(0, 72%, 51%)", // red-600
    media: "hsl(25, 95%, 53%)", // orange-500
    baja: "hsl(142, 76%, 36%)", // green-600
  },
} as const;

// ============================================================================
// ESPACIADO
// ============================================================================

export const spacing = {
  xs: "0.25rem", // 4px
  sm: "0.5rem", // 8px
  md: "1rem", // 16px
  lg: "1.5rem", // 24px
  xl: "2rem", // 32px
  "2xl": "3rem", // 48px
  "3xl": "4rem", // 64px
} as const;

// ============================================================================
// TIPOGRAFÍA
// ============================================================================

export const typography = {
  fontSize: {
    xs: "0.75rem", // 12px
    sm: "0.875rem", // 14px
    base: "1rem", // 16px
    lg: "1.125rem", // 18px
    xl: "1.25rem", // 20px
    "2xl": "1.5rem", // 24px
    "3xl": "1.875rem", // 30px
    "4xl": "2.25rem", // 36px
  },

  fontWeight: {
    normal: "400",
    medium: "500",
    semibold: "600",
    bold: "700",
  },

  lineHeight: {
    tight: "1.25",
    normal: "1.5",
    relaxed: "1.75",
  },
} as const;

// ============================================================================
// BORDER RADIUS
// ============================================================================

export const borderRadius = {
  none: "0",
  sm: "0.125rem", // 2px
  base: "0.25rem", // 4px
  md: "0.375rem", // 6px
  lg: "0.5rem", // 8px
  xl: "0.75rem", // 12px
  "2xl": "1rem", // 16px
  full: "9999px",
} as const;

// ============================================================================
// SOMBRAS
// ============================================================================

export const shadows = {
  sm: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
  base: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
  md: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
  lg: "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
  xl: "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
} as const;

// ============================================================================
// TRANSICIONES
// ============================================================================

export const transitions = {
  fast: "150ms",
  base: "200ms",
  slow: "300ms",
  slower: "500ms",
} as const;

// ============================================================================
// Z-INDEX
// ============================================================================

export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1100,
  fixed: 1200,
  modalBackdrop: 1300,
  modal: 1400,
  popover: 1500,
  tooltip: 1600,
} as const;

// ============================================================================
// BREAKPOINTS
// ============================================================================

export const breakpoints = {
  sm: "640px",
  md: "768px",
  lg: "1024px",
  xl: "1280px",
  "2xl": "1536px",
} as const;

// ============================================================================
// ICONOS (tamaños estándar)
// ============================================================================

export const iconSizes = {
  xs: 12,
  sm: 16,
  base: 20,
  lg: 24,
  xl: 32,
  "2xl": 48,
} as const;
