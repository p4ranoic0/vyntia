import { Progress } from '@/components/ui/progress'

interface OnboardingProgressBarProps {
  porcentaje: number
}

export function OnboardingProgressBar({ porcentaje }: OnboardingProgressBarProps) {
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-center text-sm">
        <span className="font-medium text-foreground">Progreso de onboarding</span>
        <span className="text-muted-foreground font-semibold">{porcentaje}%</span>
      </div>
      <Progress value={porcentaje} className="h-2" />
    </div>
  )
}
