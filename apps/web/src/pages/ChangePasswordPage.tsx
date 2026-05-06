import React from 'react'
import ChangePasswordForm from '@/components/auth/ChangePasswordForm'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'

/**
 * Página para el cambio de contraseña del usuario
 * Contiene el formulario de cambio de contraseña con validaciones
 */
const ChangePasswordPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-md mx-auto">
        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-center">
              Cambiar Contraseña
            </CardTitle>
            <CardDescription className="text-center">
              Actualiza tu contraseña para mantener tu cuenta segura
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ChangePasswordForm />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default ChangePasswordPage