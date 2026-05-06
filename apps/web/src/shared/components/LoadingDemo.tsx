import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import { Separator } from '@/shared/ui/separator'
import { LoadingSpinner } from './LoadingSpinner'
import { LoadingPage } from './LoadingPage'
import { LoadingSkeleton } from './LoadingSkeleton'
import { useLoading } from './useLoading'
import { useLoadingWithDelay } from './useLoadingWithDelay'
import { Play, Pause, RotateCcw } from 'lucide-react'

/**
 * Página de demostración de todos los componentes de loading
 * Muestra ejemplos interactivos de cada componente y hook
 */
const LoadingDemo: React.FC = () => {
  const [showFullPageLoading, setShowFullPageLoading] = useState(false)
  
  // Hooks de loading para demostración
  const { isLoading: basicLoading, startLoading: startBasic, stopLoading: stopBasic } = useLoading()
  const { isLoading: delayedLoading, startLoading: startDelayed, stopLoading: stopDelayed } = useLoadingWithDelay(2000)
  const { isLoading: quickLoading, startLoading: startQuick, stopLoading: stopQuick } = useLoadingWithDelay(500)

  const handleBasicDemo = () => {
    startBasic()
    setTimeout(() => stopBasic(), 3000)
  }

  const handleDelayedDemo = () => {
    startDelayed()
    setTimeout(() => stopDelayed(), 5000)
  }

  const handleQuickDemo = () => {
    startQuick()
    setTimeout(() => stopQuick(), 2000)
  }

  const handleFullPageDemo = () => {
    setShowFullPageLoading(true)
    setTimeout(() => setShowFullPageLoading(false), 4000)
  }

  return (
    <div className="container mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Sistema de Loading
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Demostración interactiva de todos los componentes de loading disponibles en el sistema.
          Cada componente está diseñado para ser reutilizable y estéticamente atractivo.
        </p>
      </div>

      {/* LoadingSpinner Demos */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            LoadingSpinner
          </CardTitle>
          <CardDescription>
            Spinner de carga con diferentes tamaños y variantes
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Tamaños */}
          <div>
            <h4 className="font-semibold mb-3">Tamaños disponibles</h4>
            <div className="flex items-center gap-6">
              <div className="text-center space-y-2">
                <LoadingSpinner size="sm" />
                <Badge variant="outline">Small</Badge>
              </div>
              <div className="text-center space-y-2">
                <LoadingSpinner size="md" />
                <Badge variant="outline">Medium</Badge>
              </div>
              <div className="text-center space-y-2">
                <LoadingSpinner size="lg" />
                <Badge variant="outline">Large</Badge>
              </div>
            </div>
          </div>

          <Separator />

          {/* Con texto */}
          <div>
            <h4 className="font-semibold mb-3">Con texto personalizado</h4>
            <div className="space-y-4">
              <LoadingSpinner text="Cargando datos..." />
              <LoadingSpinner text="Procesando información..." size="lg" />
              <LoadingSpinner text="Guardando cambios..." size="sm" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* LoadingSkeleton Demos */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            LoadingSkeleton
          </CardTitle>
          <CardDescription>
            Esqueletos de carga para diferentes tipos de contenido
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Variantes */}
          <div>
            <h4 className="font-semibold mb-3">Variantes disponibles</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-2">
                <LoadingSkeleton variant="text" />
                <Badge variant="outline">Text</Badge>
              </div>
              <div className="space-y-2">
                <LoadingSkeleton variant="card" />
                <Badge variant="outline">Card</Badge>
              </div>
              <div className="space-y-2">
                <LoadingSkeleton variant="avatar" />
                <Badge variant="outline">Avatar</Badge>
              </div>
              <div className="space-y-2">
                <LoadingSkeleton variant="button" />
                <Badge variant="outline">Button</Badge>
              </div>
            </div>
          </div>

          <Separator />

          {/* Múltiples líneas */}
          <div>
            <h4 className="font-semibold mb-3">Múltiples líneas</h4>
            <div className="space-y-4">
              <LoadingSkeleton variant="text" lines={3} />
              <LoadingSkeleton variant="text" lines={5} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Hooks Demos */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            Hooks de Loading
          </CardTitle>
          <CardDescription>
            Hooks para gestionar estados de carga de forma reactiva
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* useLoading básico */}
          <div className="space-y-3">
            <h4 className="font-semibold">useLoading (básico)</h4>
            <div className="flex items-center gap-4">
              <Button 
                onClick={handleBasicDemo}
                disabled={basicLoading}
                className="flex items-center gap-2"
              >
                {basicLoading ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                {basicLoading ? 'Cargando...' : 'Iniciar Demo (3s)'}
              </Button>
              {basicLoading && <LoadingSpinner size="sm" />}
            </div>
          </div>

          <Separator />

          {/* useLoadingWithDelay */}
          <div className="space-y-3">
            <h4 className="font-semibold">useLoadingWithDelay</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Delay: 500ms</p>
                <div className="flex items-center gap-4">
                  <Button 
                    onClick={handleQuickDemo}
                    disabled={quickLoading}
                    size="sm"
                    className="flex items-center gap-2"
                  >
                    {quickLoading ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    {quickLoading ? 'Cargando...' : 'Demo Rápido'}
                  </Button>
                  {quickLoading && <LoadingSpinner size="sm" />}
                </div>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Delay: 2000ms</p>
                <div className="flex items-center gap-4">
                  <Button 
                    onClick={handleDelayedDemo}
                    disabled={delayedLoading}
                    size="sm"
                    className="flex items-center gap-2"
                  >
                    {delayedLoading ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    {delayedLoading ? 'Cargando...' : 'Demo Lento'}
                  </Button>
                  {delayedLoading && <LoadingSpinner size="sm" />}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* LoadingPage Demo */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
            LoadingPage
          </CardTitle>
          <CardDescription>
            Página de carga completa que cubre toda la pantalla
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Este componente muestra una página de carga completa con overlay.
              Ideal para transiciones entre páginas o procesos largos.
            </p>
            <Button 
              onClick={handleFullPageDemo}
              disabled={showFullPageLoading}
              className="flex items-center gap-2"
            >
              {showFullPageLoading ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {showFullPageLoading ? 'Mostrando...' : 'Mostrar LoadingPage (4s)'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Casos de uso */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
            Casos de Uso Recomendados
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-semibold text-blue-600">LoadingSpinner</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• Botones con acciones async</li>
                <li>• Formularios enviándose</li>
                <li>• Búsquedas en tiempo real</li>
                <li>• Carga de datos pequeños</li>
              </ul>
            </div>
            <div className="space-y-3">
              <h4 className="font-semibold text-purple-600">LoadingSkeleton</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• Listas de elementos</li>
                <li>• Tarjetas de contenido</li>
                <li>• Perfiles de usuario</li>
                <li>• Tablas de datos</li>
              </ul>
            </div>
            <div className="space-y-3">
              <h4 className="font-semibold text-green-600">useLoading</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• Control manual de estados</li>
                <li>• Operaciones síncronas</li>
                <li>• Estados simples</li>
              </ul>
            </div>
            <div className="space-y-3">
              <h4 className="font-semibold text-orange-600">LoadingPage</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• Navegación entre páginas</li>
                <li>• Inicialización de app</li>
                <li>• Procesos largos</li>
                <li>• Autenticación</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* LoadingPage overlay */}
      {showFullPageLoading && (
        <LoadingPage 
          message="Demostrando LoadingPage..."
          description="Este es un ejemplo de carga de página completa"
        />
      )}
    </div>
  )
}

export default LoadingDemo