import React, { useState } from 'react'
import { 
  LoadingSpinner, 
  LoadingPage, 
  LoadingSection, 
  LoadingButton,
  Skeleton,
  UserCardSkeleton,
  TableSkeleton,
  FormSkeleton,
  StatsSkeleton,
  ListSkeleton,
  DashboardSkeleton,
  SidebarSkeleton,
  useLoading,
  useLoadingWithDelay
} from '@/shared/components'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui/tabs'
import { Badge } from '@/shared/ui/badge'

/**
 * Página de demostración de componentes de loading
 * Muestra todas las variantes y opciones disponibles
 */
export default function LoadingDemo() {
  const [selectedVariant, setSelectedVariant] = useState<'default' | 'dots' | 'pulse' | 'bounce' | 'rotate'>('default')
  const [selectedSize, setSelectedSize] = useState<'xs' | 'sm' | 'md' | 'lg' | 'xl'>('md')
  const [selectedColor, setSelectedColor] = useState<'primary' | 'secondary' | 'accent' | 'muted'>('primary')
  const [showFullScreen, setShowFullScreen] = useState(false)
  
  const { isLoading, toggleLoading } = useLoading()
  const { isLoading: isDelayLoading, simulateLoading } = useLoadingWithDelay(2000)

  const variants = ['default', 'dots', 'pulse', 'bounce', 'rotate'] as const
  const sizes = ['xs', 'sm', 'md', 'lg', 'xl'] as const
  const colors = ['primary', 'secondary', 'accent', 'muted'] as const

  if (showFullScreen) {
    return (
      <div className="relative">
        <LoadingPage 
          title="Cargando aplicación..."
          subtitle="Por favor espera mientras preparamos todo para ti"
          variant={selectedVariant}
        />
        <Button 
          className="absolute top-4 right-4 z-50"
          onClick={() => setShowFullScreen(false)}
        >
          Cerrar
        </Button>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold">Componentes de Loading</h1>
        <p className="text-muted-foreground text-lg">
          Sistema completo de componentes de carga reutilizables y elegantes
        </p>
      </div>

      <Tabs defaultValue="spinners" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="spinners">Spinners</TabsTrigger>
          <TabsTrigger value="skeletons">Skeletons</TabsTrigger>
          <TabsTrigger value="pages">Páginas</TabsTrigger>
          <TabsTrigger value="examples">Ejemplos</TabsTrigger>
        </TabsList>

        {/* Tab de Spinners */}
        <TabsContent value="spinners" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>LoadingSpinner - Configuración</CardTitle>
              <CardDescription>
                Personaliza el spinner con diferentes variantes, tamaños y colores
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Controles */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Variante</label>
                  <div className="flex flex-wrap gap-2">
                    {variants.map((variant) => (
                      <Badge 
                        key={variant}
                        variant={selectedVariant === variant ? 'default' : 'outline'}
                        className="cursor-pointer"
                        onClick={() => setSelectedVariant(variant)}
                      >
                        {variant}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Tamaño</label>
                  <div className="flex flex-wrap gap-2">
                    {sizes.map((size) => (
                      <Badge 
                        key={size}
                        variant={selectedSize === size ? 'default' : 'outline'}
                        className="cursor-pointer"
                        onClick={() => setSelectedSize(size)}
                      >
                        {size}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Color</label>
                  <div className="flex flex-wrap gap-2">
                    {colors.map((color) => (
                      <Badge 
                        key={color}
                        variant={selectedColor === color ? 'default' : 'outline'}
                        className="cursor-pointer"
                        onClick={() => setSelectedColor(color)}
                      >
                        {color}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>

              {/* Preview */}
              <div className="border rounded-lg p-8 bg-muted/5">
                <LoadingSpinner 
                  variant={selectedVariant}
                  size={selectedSize}
                  color={selectedColor}
                  text="Cargando contenido..."
                />
              </div>

              {/* Todas las variantes */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {variants.map((variant) => (
                  <div key={variant} className="text-center space-y-2">
                    <div className="border rounded-lg p-4 bg-muted/5">
                      <LoadingSpinner variant={variant} size="md" />
                    </div>
                    <p className="text-sm font-medium">{variant}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>LoadingButton</CardTitle>
              <CardDescription>
                Botones con estados de carga integrados
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-4">
                <LoadingButton 
                  isLoading={isLoading}
                  onClick={toggleLoading}
                  className="bg-primary text-primary-foreground px-4 py-2 rounded-md"
                >
                  {isLoading ? 'Cargando...' : 'Iniciar carga'}
                </LoadingButton>
                
                <LoadingButton 
                  isLoading={isDelayLoading}
                  onClick={simulateLoading}
                  variant="dots"
                  className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md"
                >
                  {isDelayLoading ? 'Procesando...' : 'Simular carga (2s)'}
                </LoadingButton>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab de Skeletons */}
        <TabsContent value="skeletons" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>UserCardSkeleton</CardTitle>
              </CardHeader>
              <CardContent>
                <UserCardSkeleton />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>FormSkeleton</CardTitle>
              </CardHeader>
              <CardContent>
                <FormSkeleton fields={3} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>ListSkeleton</CardTitle>
              </CardHeader>
              <CardContent>
                <ListSkeleton items={3} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>StatsSkeleton</CardTitle>
              </CardHeader>
              <CardContent>
                <StatsSkeleton items={2} />
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>TableSkeleton</CardTitle>
            </CardHeader>
            <CardContent>
              <TableSkeleton rows={3} columns={4} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab de Páginas */}
        <TabsContent value="pages" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>LoadingPage</CardTitle>
                <CardDescription>
                  Página de carga completa con diferentes variantes
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button onClick={() => setShowFullScreen(true)} className="w-full">
                  Ver LoadingPage completa
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>LoadingSection</CardTitle>
                <CardDescription>
                  Secciones de carga para contenido específico
                </CardDescription>
              </CardHeader>
              <CardContent>
                <LoadingSection 
                  title="Cargando datos..."
                  height="h-32"
                  variant={selectedVariant}
                />
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>DashboardSkeleton</CardTitle>
              <CardDescription>
                Skeleton completo para dashboard
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="max-h-96 overflow-y-auto">
                <DashboardSkeleton />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab de Ejemplos */}
        <TabsContent value="examples" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Código de Ejemplo</CardTitle>
              <CardDescription>
                Ejemplos de uso de los componentes de loading
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="bg-muted p-4 rounded-lg">
                  <h4 className="font-medium mb-2">Spinner básico:</h4>
                  <code className="text-sm">
                    {`<LoadingSpinner variant="dots" size="lg" color="primary" text="Cargando..." />`}
                  </code>
                </div>
                
                <div className="bg-muted p-4 rounded-lg">
                  <h4 className="font-medium mb-2">Página de carga:</h4>
                  <code className="text-sm">
                    {`<LoadingPage title="Cargando aplicación..." subtitle="Preparando contenido" />`}
                  </code>
                </div>
                
                <div className="bg-muted p-4 rounded-lg">
                  <h4 className="font-medium mb-2">Botón con loading:</h4>
                  <code className="text-sm">
                    {`<LoadingButton isLoading={isLoading} onClick={handleClick}>Guardar</LoadingButton>`}
                  </code>
                </div>
                
                <div className="bg-muted p-4 rounded-lg">
                  <h4 className="font-medium mb-2">Hook de loading:</h4>
                  <code className="text-sm">
                    {`const { isLoading, startLoading, stopLoading } = useLoading()`}
                  </code>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}