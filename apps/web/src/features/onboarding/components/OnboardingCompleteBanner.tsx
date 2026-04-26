import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

export function OnboardingCompleteBanner() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
    queryClient.invalidateQueries({ queryKey: ['auth-user'] })
  }, [queryClient])

  return (
    <Card className="border-green-200 bg-green-50">
      <CardContent className="pt-8 pb-8 flex flex-col items-center text-center gap-4">
        <CheckCircle className="h-16 w-16 text-green-600" />
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-green-900">¡Onboarding completado!</h2>
          <p className="text-green-700 max-w-sm">
            Tu información ha sido verificada por RRHH. Serás redirigido al portal principal.
          </p>
        </div>
        <Button
          className="mt-2 min-h-[44px] px-8 bg-green-700 hover:bg-green-800 text-white"
          onClick={() => navigate('/')}
        >
          Ir al portal
        </Button>
      </CardContent>
    </Card>
  )
}
