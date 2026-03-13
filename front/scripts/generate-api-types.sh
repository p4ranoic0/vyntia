#!/bin/bash
# Script para generar tipos desde OpenAPI schema
# Uso: npm run generate:api

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
SCHEMA_URL="$BACKEND_URL/api/schema/"

echo "🔄 Descargando OpenAPI schema desde: $SCHEMA_URL"

# Descargar schema
curl -s "$SCHEMA_URL" > openapi-schema.json

if [ $? -eq 0 ]; then
  echo "✅ Schema descargado"
  
  # Generar tipos usando openapi-typescript
  echo "🔨 Generando tipos..."
  npx openapi-typescript-codegen --config openapi.config.json
  
  if [ $? -eq 0 ]; then
    echo "✅ Tipos generados exitosamente"
    rm openapi-schema.json
  else
    echo "❌ Error al generar tipos"
    exit 1
  fi
else
  echo "❌ Error al descargar schema. Verifica que el backend esté corriendo en $BACKEND_URL"
  exit 1
fi
