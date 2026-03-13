# Análisis del Sistema de Generación de Plantillas para Contratos

## Estado Actual

### Infraestructura Existente
- **Django Templates**: Configurado pero sin directorio específico
- **Documentos Digitales**: Sistema completo para gestión de archivos
- **Modelo ContratoAdenda**: Estructura unificada para contratos y adendas
- **Campo documento_adjunto**: Preparado para almacenar rutas de PDFs generados

### Librerías Disponibles
- **Django**: Sistema de templates nativo
- **Pillow**: Para procesamiento de imágenes
- **DRF**: Para APIs de generación

### Librerías Faltantes
- **ReportLab**: Para generación de PDFs
- **WeasyPrint**: Alternativa para HTML a PDF
- **Jinja2**: Templates más avanzados (opcional)

## Necesidades Identificadas

### Tipos de Documentos a Generar
1. **Contratos Iniciales**
   - Contrato CAS
   - Contrato 276
   - Contrato 728
   - Contrato Locación de Servicios

2. **Adendas**
   - Renovación
   - Modificación salarial
   - Cambio de área
   - Cambio de modalidad
   - Suspensión
   - Finalización

3. **Documentos Complementarios**
   - Certificados de trabajo
   - Constancias laborales
   - Reportes de contratos por área
   - Alertas de vencimiento

### Datos Requeridos para Plantillas
- **Empleado**: Datos personales, laborales, académicos
- **Contrato**: Fechas, salario, cargo, funciones
- **Área**: Información del área de trabajo
- **Empresa**: Datos institucionales
- **Jefe/Supervisor**: Datos del responsable

## Propuesta de Implementación

### 1. Estructura de Directorios
```
back/
├── templates/
│   ├── contratos/
│   │   ├── base_contrato.html
│   │   ├── contrato_cas.html
│   │   ├── contrato_276.html
│   │   ├── contrato_728.html
│   │   └── contrato_locacion.html
│   ├── adendas/
│   │   ├── base_adenda.html
│   │   ├── adenda_renovacion.html
│   │   ├── adenda_modificacion.html
│   │   └── adenda_finalizacion.html
│   ├── certificados/
│   │   ├── certificado_trabajo.html
│   │   └── constancia_laboral.html
│   └── reportes/
│       ├── reporte_contratos_area.html
│       └── alerta_vencimientos.html
├── static/
│   ├── css/
│   │   └── documentos.css
│   └── images/
│       └── logo_institucion.png
└── app_rrhh/
    ├── services/
    │   ├── __init__.py
    │   ├── template_service.py
    │   └── pdf_generator.py
    └── utils/
        ├── __init__.py
        └── document_utils.py
```

### 2. Servicios a Implementar

#### TemplateService
- Gestión de plantillas por tipo de documento
- Contexto de datos para renderizado
- Validación de datos requeridos

#### PDFGenerator
- Conversión de HTML a PDF
- Configuración de estilos y formato
- Gestión de archivos generados

#### DocumentUtils
- Utilidades para nombres de archivos
- Validación de plantillas
- Helpers para datos comunes

### 3. API Endpoints

```python
# Generar documento de contrato
POST /api/v1/rrhh/contratos/{id}/generar-documento/

# Generar adenda
POST /api/v1/rrhh/contratos/{id}/generar-adenda/

# Generar certificado
POST /api/v1/rrhh/empleados/{id}/generar-certificado/

# Previsualizar documento
GET /api/v1/rrhh/contratos/{id}/preview-documento/
```

### 4. Integración con DocumentosDigitales
- Almacenamiento automático de PDFs generados
- Versionado de documentos
- Metadatos de generación
- Relación con ContratoAdenda

## Beneficios Esperados

### Automatización
- Generación automática de contratos y adendas
- Reducción de errores manuales
- Consistencia en formato y contenido

### Eficiencia
- Tiempo reducido de generación
- Plantillas reutilizables
- Proceso estandarizado

### Trazabilidad
- Historial de documentos generados
- Versionado automático
- Auditoría de cambios

### Escalabilidad
- Fácil adición de nuevos tipos de documento
- Personalización por área o tipo de contrato
- Integración con flujos de aprobación

## Fases de Implementación

### Fase 1: Infraestructura Base
1. Instalación de librerías para PDF
2. Configuración de directorios de templates
3. Servicios base para generación

### Fase 2: Plantillas Básicas
1. Plantilla base para contratos
2. Plantillas específicas por tipo de contrato
3. Estilos CSS para documentos

### Fase 3: Integración
1. APIs de generación
2. Integración con DocumentosDigitales
3. Endpoints de previsualización

### Fase 4: Funcionalidades Avanzadas
1. Plantillas para adendas
2. Certificados y constancias
3. Reportes automatizados
4. Sistema de alertas

## Consideraciones Técnicas

### Rendimiento
- Generación asíncrona para documentos grandes
- Cache de plantillas compiladas
- Optimización de consultas a BD

### Seguridad
- Validación de permisos para generación
- Sanitización de datos de entrada
- Protección de archivos generados

### Mantenibilidad
- Separación clara de responsabilidades
- Documentación de plantillas
- Tests automatizados

## Próximos Pasos

1. **Instalar dependencias**: ReportLab o WeasyPrint
2. **Crear estructura de directorios**: Templates y servicios
3. **Implementar servicio base**: TemplateService
4. **Crear primera plantilla**: Contrato básico
5. **Desarrollar API**: Endpoint de generación
6. **Integrar con DocumentosDigitales**: Almacenamiento automático
7. **Testing**: Pruebas de generación y calidad
8. **Documentación**: Guías de uso y mantenimiento

Este análisis proporciona una hoja de ruta clara para implementar un sistema robusto y escalable de generación de documentos desde plantillas.