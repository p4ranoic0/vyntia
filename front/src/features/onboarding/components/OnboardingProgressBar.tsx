import { Progress } from '@/components/ui/progress'

interface OnboardingProgressBarProps {
  progreso_porcentaje?: number   // upload completion
  progreso_aprobado?: number     // RRHH-approved completion
  estado_onboarding?: string
  // Legacy prop alias — kept for backward compatibility
  porcentaje?: number
}

export function OnboardingProgressBar({
  progreso_porcentaje,
  progreso_aprobado,
  porcentaje,
}: OnboardingProgressBarProps) {
  // Support legacy call sites that pass porcentaje instead of progreso_porcentaje
  const uploaded = progreso_porcentaje ?? porcentaje ?? 0
  const approved = progreso_aprobado ?? 0

  return (
    <div className="space-y-3">
      <div className="space-y-1.5">
        <div className="flex justify-between items-center text-sm">
          <span className="font-medium text-foreground">Documentos subidos</span>
          <span className="text-muted-foreground font-semibold">{uploaded}%</span>
        </div>
        <Progress value={uploaded} className="h-2" />
      </div>
      <div className="space-y-1.5">
        <div className="flex justify-between items-center text-sm">
          <span className="font-medium text-green-700">Documentos aprobados</span>
          <span className="text-green-700 font-semibold">{approved}%</span>
        </div>
        <Progress value={approved} className="h-2 [&>div]:bg-green-500" />
      </div>
      <p className="text-xs text-muted-foreground">
        {uploaded}% subido — {approved}% aprobado
      </p>
    </div>
  )
}
