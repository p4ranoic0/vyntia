import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Separator } from '@/shared/ui/separator'
import { Building2, Save, Upload, X } from 'lucide-react'
import { toast } from 'sonner'
import { companyService, type ConfiguracionEmpresa } from '@/features/organization/services/companyService'

export default function ConfiguracionEmpresaPage() {
  const queryClient = useQueryClient()
  const logoInputRef = useRef<HTMLInputElement>(null)
  const [logoFile, setLogoFile] = useState<File | null>(null)
  const [logoPreview, setLogoPreview] = useState<string | null>(null)
  const [form, setForm] = useState<Partial<ConfiguracionEmpresa>>({})

  const { data: config, isLoading } = useQuery<ConfiguracionEmpresa>({
    queryKey: ['configuracion-empresa'],
    queryFn: () => companyService.get(),
  })

  useEffect(() => {
    if (config) {
      setForm(config)
      if (config.logo_url) setLogoPreview(config.logo_url)
    }
  }, [config])

  const mutation = useMutation({
    mutationFn: () => companyService.update(form, logoFile ?? undefined),
    onSuccess: (data) => {
      toast.success('Configuración guardada')
      queryClient.setQueryData(['configuracion-empresa'], data)
      setLogoFile(null)
    },
    onError: () => toast.error('Error al guardar la configuración'),
  })

  const handleField = (field: keyof ConfiguracionEmpresa, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLogoFile(file)
    setLogoPreview(URL.createObjectURL(file))
  }

  const handleRemoveLogo = () => {
    setLogoFile(null)
    setLogoPreview(null)
    setForm((prev) => ({ ...prev, logo: null, logo_url: null }))
    if (logoInputRef.current) logoInputRef.current.value = ''
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Building2 className="h-6 w-6" />
            Configuracion de la Institucion
          </h1>
          <p className="text-muted-foreground">
            Datos que aparecen en contratos, constancias y certificados generados
          </p>
        </div>
        <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
          <Save className="h-4 w-4 mr-2" />
          {mutation.isPending ? 'Guardando...' : 'Guardar Cambios'}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Logo */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Logo Institucional</CardTitle>
            <CardDescription>Se mostrara en el encabezado de los documentos</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {logoPreview ? (
              <div className="relative inline-block">
                <img
                  src={logoPreview}
                  alt="Logo"
                  className="max-h-32 max-w-full object-contain border rounded p-2"
                />
                <button
                  onClick={handleRemoveLogo}
                  className="absolute -top-2 -right-2 bg-destructive text-destructive-foreground rounded-full p-0.5"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ) : (
              <div className="h-32 border-2 border-dashed rounded flex items-center justify-center text-muted-foreground text-sm">
                Sin logo
              </div>
            )}
            <input
              ref={logoInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleLogoChange}
            />
            <Button variant="outline" size="sm" onClick={() => logoInputRef.current?.click()}>
              <Upload className="h-4 w-4 mr-2" />
              Subir Logo
            </Button>
          </CardContent>
        </Card>

        {/* Main info */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Datos Generales</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2 space-y-1">
                <Label>Nombre de la Institucion *</Label>
                <Input
                  value={form.nombre ?? ''}
                  onChange={(e) => handleField('nombre', e.target.value)}
                  placeholder="Ministerio / Entidad publica..."
                />
              </div>
              <div className="space-y-1">
                <Label>RUC *</Label>
                <Input
                  value={form.ruc ?? ''}
                  onChange={(e) => handleField('ruc', e.target.value)}
                  placeholder="20000000000"
                  maxLength={11}
                />
              </div>
              <div className="space-y-1">
                <Label>Resolucion de Creacion</Label>
                <Input
                  value={form.resolucion_creacion ?? ''}
                  onChange={(e) => handleField('resolucion_creacion', e.target.value)}
                  placeholder="R.M. N° 001-2024"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Address */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Direccion</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="col-span-2 space-y-1">
              <Label>Direccion</Label>
              <Input
                value={form.direccion ?? ''}
                onChange={(e) => handleField('direccion', e.target.value)}
                placeholder="Av. Abancay 123"
              />
            </div>
            <div className="space-y-1">
              <Label>Distrito</Label>
              <Input
                value={form.distrito ?? ''}
                onChange={(e) => handleField('distrito', e.target.value)}
                placeholder="Lima"
              />
            </div>
            <div className="space-y-1">
              <Label>Provincia</Label>
              <Input
                value={form.provincia ?? ''}
                onChange={(e) => handleField('provincia', e.target.value)}
                placeholder="Lima"
              />
            </div>
            <div className="space-y-1">
              <Label>Departamento</Label>
              <Input
                value={form.departamento ?? ''}
                onChange={(e) => handleField('departamento', e.target.value)}
                placeholder="Lima"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Contact */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Contacto</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="space-y-1">
              <Label>Telefono</Label>
              <Input
                value={form.telefono ?? ''}
                onChange={(e) => handleField('telefono', e.target.value)}
                placeholder="(01) 123-4567"
              />
            </div>
            <div className="space-y-1">
              <Label>Correo Institucional</Label>
              <Input
                type="email"
                value={form.email ?? ''}
                onChange={(e) => handleField('email', e.target.value)}
                placeholder="contacto@entidad.gob.pe"
              />
            </div>
            <div className="space-y-1">
              <Label>Sitio Web</Label>
              <Input
                value={form.web ?? ''}
                onChange={(e) => handleField('web', e.target.value)}
                placeholder="www.entidad.gob.pe"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Representative */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Representante Legal</CardTitle>
          <CardDescription>
            Datos de la autoridad que firma los documentos (contratos, constancias, certificados)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="col-span-2 space-y-1">
              <Label>Nombre Completo del Representante *</Label>
              <Input
                value={form.representante_legal ?? ''}
                onChange={(e) => handleField('representante_legal', e.target.value)}
                placeholder="Nombres y apellidos"
              />
            </div>
            <div className="space-y-1">
              <Label>DNI del Representante</Label>
              <Input
                value={form.dni_representante ?? ''}
                onChange={(e) => handleField('dni_representante', e.target.value)}
                placeholder="12345678"
                maxLength={8}
              />
            </div>
            <div className="col-span-2 md:col-span-3 space-y-1">
              <Label>Cargo del Representante *</Label>
              <Input
                value={form.cargo_representante ?? ''}
                onChange={(e) => handleField('cargo_representante', e.target.value)}
                placeholder="Director General / Gerente de RRHH / etc."
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Preview */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Vista previa del encabezado de documentos</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="border rounded p-6 bg-white text-black font-serif text-sm text-center space-y-1">
            {logoPreview && (
              <img src={logoPreview} alt="Logo" className="h-16 object-contain mx-auto mb-2" />
            )}
            <p className="font-bold text-lg uppercase">{form.nombre || 'NOMBRE DE LA INSTITUCION'}</p>
            <p><strong>RUC:</strong> {form.ruc || '00000000000'}</p>
            <p>{form.direccion || 'Direccion'}</p>
            <p>{[form.distrito, form.provincia, form.departamento].filter(Boolean).join(', ') || 'Distrito, Provincia, Departamento'}</p>
            <p>
              {form.telefono && <span><strong>Tel:</strong> {form.telefono}</span>}
              {form.telefono && form.email && ' | '}
              {form.email && <span><strong>Email:</strong> {form.email}</span>}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
