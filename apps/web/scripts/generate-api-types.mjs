/**
 * OpenAPI Generator Script
 *
 * Genera TypeScript types desde el schema OpenAPI del backend
 *
 * Uso:
 * npm run generate:api
 *
 * Generará en: src/generated/api/
 */

import { execSync } from 'child_process'
import fs from 'fs'
import http from 'http'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const rootDir = path.join(__dirname, '..')
const generatedDir = path.join(rootDir, 'src', 'generated', 'api')
const schemaPath = path.join(rootDir, 'openapi-schema.json')

console.log('🔄 Generando tipos desde OpenAPI schema...')

// Crear directorio si no existe
if (!fs.existsSync(generatedDir)) {
  fs.mkdirSync(generatedDir, { recursive: true })
}

// Función para descargar el schema
function downloadSchema(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest)
    
    http.get(url, (response) => {
      response.pipe(file)
      file.on('finish', () => {
        file.close()
        resolve()
      })
    }).on('error', (err) => {
      fs.unlink(dest, () => {}) // Eliminar archivo parcial
      reject(err)
    })
  })
}

try {
  // Verificar si el schema existe
  if (!fs.existsSync(schemaPath)) {
    console.error('❌ No se encontró openapi-schema.json')
    console.log('💡 Genera el schema primero:')
    console.log('   cd ../back && python manage.py spectacular --file ../front/openapi-schema.json')
    process.exit(1)
  }
  
  console.log('✅ Schema encontrado')
  
  // Usar openapi-typescript-codegen con archivo local
  console.log('🔄 Generando tipos TypeScript...')
  execSync(
    `npx openapi-typescript-codegen --input ${schemaPath} --output src/generated/api --client axios`,
    { stdio: 'inherit', cwd: rootDir }
  )
  
  console.log(`✅ Tipos generados exitosamente en: src/generated/api/`)
  console.log('📝 Archivos generados:')
  console.log('   - models/ : Interfases para tipos de datos')
  console.log('   - services/ : Servicios para API calls')
  console.log('   - schemas/ : Esquemas JSON schema')
  console.log('')
  console.log('💡 Próximo paso: Importar tipos en features')
  console.log('   import type { Empleado } from "@/generated/api/models"')
} catch (error) {
  console.error('❌ Error al generar tipos:', error.message)
  process.exit(1)
}
