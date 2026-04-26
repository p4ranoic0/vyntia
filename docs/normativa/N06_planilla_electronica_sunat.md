# N06 — Planilla Electrónica SUNAT (T-Registro + PLAME)

> **Norma marco:** R.M. 121-2011-TR + modificatorias (R.M. 107-2014-TR, R.M. 260-2016-TR, **R.M. 170-2023-TR**)
> **Criticidad:** CRÍTICA — ningún software de RRHH puede operar en Perú sin esta integración.

---

## 1. Componentes del sistema

### 1.1 T-Registro
Registro nacional de información laboral. Contiene datos **estáticos**:
- Empleadores
- Establecimientos
- Trabajadores
- Pensionistas
- Prestadores de servicios (4ta categoría)
- Personal en modalidades formativas (practicantes)
- Personal de terceros
- Derechohabientes

**Eventos declarables:**
- Alta de nuevo trabajador (plazo: hasta el primer día de prestación)
- Modificación de datos contractuales
- Baja de trabajador (plazo: hasta el día en que se produce el término)

### 1.2 PLAME (Planilla Mensual de Pagos)
Formulario Virtual **0601**. Contiene datos **dinámicos mensuales**:
- Remuneraciones pagadas
- Aportes retenidos
- Tributos
- Descuentos
- Días laborados/subsidiados

**Plazo:** según cronograma SUNAT por último dígito de RUC (entre el 11 y el 24 del mes siguiente generalmente).

### 1.3 PVS (Programa Validador de SUNAT)
Software gratuito que valida los archivos .txt antes de su envío. Valida:
1. Número exacto de campos por estructura
2. Tipo y longitud de cada dato
3. Existencia del valor en tabla paramétrica referenciada
4. Habilitación del valor para el sector del empleador
5. Obligatoriedad según estructura
6. No duplicidad en estructuras 4/5/6/9/10

Los errores tienen prefijo según estructura: `EPR`, `E04`, `E05`, etc.

---

## 2. Anexos de la norma

### 2.1 Anexo 1 — Contenido de la Planilla Electrónica
Define **qué información** se debe incluir (campos, obligatoriedad, reglas).

### 2.2 Anexo 2 — Tablas Paramétricas (catálogos maestros)
Define **qué valores válidos** puede tomar cada campo. **Esta es la tabla más crítica para el diseño del sistema.**

### 2.3 Anexo 3 — Estructura de archivos de importación
Define el **formato físico** de los archivos .txt para carga masiva al PDT PLAME.

---

## 3. TABLAS PARAMÉTRICAS COMPLETAS (Anexo 2)

### 3.1 Tabla 1 — Tipo de Documento de Identidad
| Código | Descripción |
|--------|-------------|
| 00 | Otros |
| 01 | DNI |
| 04 | Carnet de Extranjería |
| 06 | RUC |
| 07 | Pasaporte |
| 08 | Permiso Temporal de Permanencia (PTP) |
| 10 | Doc. Trib. No Dom. Sin Ruc |
| 11 | Partida de Nacimiento |
| 12 | Otros documentos |

### 3.2 Tabla 2 — Tipo de Pago
| Código | Descripción |
|--------|-------------|
| 01 | Remuneración |
| 02 | Pensión |
| 03 | Pago por 4ta categoría |
| 04 | Subsidio por descanso médico |
| 05 | Subsidio por maternidad |
| (...) | (varios subsidios específicos) |

### 3.3 Tabla 3 — Tipo de Establecimiento
| Código | Descripción |
|--------|-------------|
| 01 | Administrativo |
| 02 | Productivo |
| 03 | De servicios |

### 3.4 Tabla 6 — Situación Educativa
| Código | Descripción |
|--------|-------------|
| 01 | Con instrucción |
| 02 | Sin instrucción |
| 03 | Analfabeto |

### 3.5 Tabla 7 — Nivel Educativo
| Código | Descripción |
|--------|-------------|
| 01 | Inicial |
| 02 | Primaria incompleta |
| 03 | Primaria completa |
| 04 | Secundaria incompleta |
| 05 | Secundaria completa |
| 06 | Superior No universitaria incompleta |
| 07 | Superior No universitaria completa |
| 08 | Superior Universitaria incompleta |
| 09 | Superior Universitaria completa |
| 10 | Maestría |
| 11 | Doctorado |

### 3.6 Tabla 8 — Tipo de Trabajador / Pensionista / Prestador
**CRÍTICA** — define el comportamiento del motor de cálculo. Algunos códigos clave:

| Código | Descripción | Régimen |
|--------|-------------|---------|
| 10 | Indeterminado D.Leg. 728 | 728 |
| 11 | A plazo fijo D.Leg. 728 | 728 |
| 12 | Régimen especial construcción civil | Construcción |
| 13 | Régimen especial minero | Minero |
| 14 | Régimen especial trabajador del hogar | Hogar |
| 15 | Pescador-artesanal D.Leg. 728 | Pesquero |
| 17 | Artistas | 728 |
| 18 | Trabajador agrario (Ley 31110) | Agrario |
| 19 | Trabajador agrario acuícola | Agrario |
| 20 | Funcionario, empleado o servidor sector público CAP | Público |
| 21 | Magistrado | Público |
| 22 | Docente universitario | Público |
| 23 | Profesional de la salud sector público | Público |
| 24 | Docente Ley 29944 (Reforma magisterial) | Público |
| 25 | Auxiliar de educación | Público |
| 27 | CAS (D.Leg. 1057) | CAS |
| 36 | Trabajadores MYPE Micro | MYPE Micro |
| 37 | Trabajadores MYPE Pequeña | MYPE Pequeña |
| 55 | Pensionista régimen 20530 | Pensionista |
| 56 | Pensionista D.L. 19990 | Pensionista |
| 57 | Pensionista militar policial | Pensionista |
| 64-67 | Diversos sector público | Público |
| 70 | Practicante pre-profesional | Formación laboral |
| 71 | Practicante profesional | Formación laboral |
| 72 | Aprendiz SENATI | Formación laboral |
| 73 | Capacitación laboral juvenil | Formación laboral |
| 75 | Pasantía | Formación laboral |
| 82-91 | Régimen servicio civil 30057 (tipos varios) | SERVIR |
| 98 | Otros sector público | Público |

### 3.7 Tabla 9 — Ocupación
Usa clasificación **CIUO-08** (Clasificación Internacional Uniforme de Ocupaciones, versión 2008). Códigos de 4 dígitos.

### 3.8 Tabla 10 — Categoría Ocupacional
| Código | Descripción |
|--------|-------------|
| 01 | Ejecutivo |
| 02 | Empleado |
| 03 | Obrero |

### 3.9 Tabla 11 — Régimen Pensionario
| Código | Descripción |
|--------|-------------|
| 03 | D.L. 20530 (cédula viva) |
| 04 | D.L. 19990 - ONP |
| 10 | Régimen militar policial |
| 11 | Otros |
| 13 | Sistema de Desgravamen (SDR) |
| 21 | AFP INTEGRA |
| 22 | AFP PRIMA |
| 23 | AFP PROFUTURO |
| 25 | AFP HABITAT |
| 32 | No pensionable (ej. CAS antiguos) |
| 99 | Sin régimen pensionario |

### 3.10 Tabla 12 — Tipo de Contrato de Trabajo
| Código | Descripción |
|--------|-------------|
| 01 | Indeterminado D.Leg. 728 |
| 02 | A plazo fijo - Naturaleza temporal |
| 03 | A plazo fijo - Naturaleza accidental |
| 04 | A plazo fijo - Obra o servicio |
| 05 | Tiempo parcial (<4h diarias) |
| 06 | D.Leg. 276 |
| 07 | CAS |
| 08 | Trabajador del Hogar |
| 09 | Construcción civil - obra |
| 10 | Agrario |
| 11 | Minero |
| 12 | Pesquero |
| (...) | (resto según subtipos) |
| 23-27 | Modalidades formativas |
| 28 | Ley 30057 Servicio Civil |

### 3.11 Tabla 13 — Régimen de Salud
| Código | Descripción |
|--------|-------------|
| 01 | EsSalud |
| 02 | EsSalud Agrario |
| 03 | EsSalud Pesquero |
| 04 | EsSalud + EPS |
| 05 | SIS |
| 12 | Sin régimen de salud (prestadores 4ta) |
| 41 | EsSalud Agrario Acuícola |

### 3.12 Tabla 17 — Motivo del Fin del Período / Cese
| Código | Descripción | Genera liquidación |
|--------|-------------|---------------------|
| 01 | Renuncia | SÍ |
| 02 | Despido | SÍ |
| 03 | Término de contrato | SÍ |
| 04 | Fallecimiento | SÍ (a herederos) |
| 05 | Jubilación | SÍ |
| 06 | Cese colectivo | SÍ |
| 07 | Invalidez absoluta permanente | SÍ |
| 08 | Mutuo disenso | SÍ |
| 09 | Causas relativas a empresa | SÍ |
| 11 | Despido arbitrario | SÍ + indemnización |
| 12 | Despido por falta grave | SÍ (sin indem) |
| (...) | (más códigos específicos) |

### 3.13 Tabla 18 — Tipo de Jornada Laboral
| Código | Descripción |
|--------|-------------|
| 1 | Jornada regular diurna |
| 2 | Jornada regular nocturna |
| 3 | Jornada atípica |
| 4 | Jornada reducida (<4h) |

### 3.14 Tabla 20 — Discapacidad
| Código | Descripción |
|--------|-------------|
| 0 | No tiene discapacidad |
| 1 | Tiene discapacidad |

### 3.15 Tabla 21 — Tipo de Suspensión de la Relación Laboral
| Código | Descripción | Pagada |
|--------|-------------|--------|
| 11 | Maternidad | Subsidio EsSalud |
| 12 | Incapacidad temporal | 1-20 días empleador, 21+ EsSalud |
| 13 | Caso fortuito / fuerza mayor | Empleador |
| 14 | Vacaciones anuales | Empleador |
| 15 | Licencia con goce | Empleador |
| 21 | Licencia sin goce | NO |
| 22 | Huelga | NO |
| 23 | Sanción disciplinaria | NO |
| 24 | Inasistencia injustificada | NO |
| (...) | (más códigos) |

### 3.16 Tabla 22 — Ingresos, Tributos y Descuentos
**LA TABLA MÁS CRÍTICA.** Contiene 100+ conceptos clasificados en rubros. Cada concepto tiene su matriz de afectación (SÍ/NO) a cada tributo/aporte.

#### Estructura por rubros:
- **0100** — Ingresos
- **0300** — Otros conceptos
- **0400** — (reservado)
- **0500** — Indemnizaciones
- **0600** — Tributos y aportes del trabajador
- **0700** — Descuentos
- **0800** — Aportes del empleador
- **2000** — Conceptos sector público (D.Leg. 276)

#### Ejemplos críticos (código · afecta Renta 5ta · afecta AFP/ONP · afecta EsSalud · afecta CTS):

| Código | Concepto | 5ta | AFP | EsSalud | CTS |
|--------|----------|-----|-----|---------|-----|
| **INGRESOS (0100)** | | | | | |
| 0101 | Remuneración básica | SÍ | SÍ | SÍ | SÍ |
| 0102 | Alimentación principal - especie | SÍ | SÍ | SÍ | SÍ |
| 0103 | Comisiones regulares | SÍ | SÍ | SÍ | SÍ* |
| 0104 | Asignación familiar | SÍ | SÍ | SÍ | SÍ |
| 0105 | Remuneración en especie | SÍ | SÍ | SÍ | SÍ |
| 0106 | Horas extras | SÍ | SÍ | SÍ | SÍ* |
| 0107 | Vacaciones | SÍ | SÍ | SÍ | NO |
| 0108 | Reintegros | SÍ | SÍ | SÍ | (según concepto) |
| 0109 | Gratificación Fiestas Patrias | SÍ | SÍ | NO** | NO |
| 0110 | Gratificación Navidad | SÍ | SÍ | NO** | NO |
| 0111 | Gratificación trunca | SÍ | SÍ | NO** | NO |
| 0112 | Bonif. riesgo caja | SÍ | SÍ | SÍ | SÍ |
| 0113 | Bonif. por turno nocturno | SÍ | SÍ | SÍ | SÍ |
| 0114 | Asignación por escolaridad | SÍ | SÍ | SÍ | SÍ |
| 0115 | Movilidad supeditada a asistencia | NO | NO | NO | NO |
| 0116 | Refrigerio (no principal) | NO | NO | NO | NO |
| 0117 | Condiciones de trabajo | NO | NO | NO | NO |
| 0118 | Canasta navideña | NO (hasta limite) | NO | NO | NO |
| 0119 | Remuneración vacaciones truncas | SÍ | SÍ | SÍ | NO |
| 0120 | CTS | NO*** | NO | NO | NO |
| 0121 | Participación utilidades | SÍ | SÍ | NO | NO |
| **INDEMNIZACIONES (0500)** | | | | | |
| 0501 | Indemnización por vacaciones no gozadas | SÍ (parte) | NO | NO | NO |
| 0502 | Indemnización por retención indebida | NO | NO | NO | NO |
| 0503 | Indemnización por despido arbitrario | NO | NO | NO | NO |
| 0504 | Indemnización por resolución de contrato | NO | NO | NO | NO |
| **TRIBUTOS TRABAJADOR (0600)** | | | | | |
| 0601 | Aporte obligatorio AFP - Fondo | — | — | — | — |
| 0602 | Aporte obligatorio ONP | — | — | — | — |
| 0605 | Retención Renta 5ta Categoría | — | — | — | — |
| 0606 | Comisión / prima AFP | — | — | — | — |
| 0607 | Aporte voluntario con fin previsional | — | — | — | — |
| 0608 | Aporte voluntario sin fin previsional | — | — | — | — |
| **DESCUENTOS (0700)** | | | | | |
| 0701 | Descuento por tardanzas | — | — | — | — |
| 0702 | Descuento por inasistencias | — | — | — | — |
| 0703 | Adelanto de remuneración | — | — | — | — |
| 0704 | Préstamo empresa | — | — | — | — |
| 0705 | Descuento judicial | — | — | — | — |
| 0706 | Cuota sindical | — | — | — | — |
| **APORTES EMPLEADOR (0800)** | | | | | |
| 0801 | Aporte EsSalud (9%) | — | — | — | — |
| 0803 | Aporte SCTR | — | — | — | — |
| 0805 | Aporte SENATI | — | — | — | — |
| 0807 | Aporte EsSalud agrario | — | — | — | — |
| **SECTOR PÚBLICO (2000)** | | | | | |
| 2001 | Haber básico D.Leg. 276 | SÍ | SÍ | SÍ | (276) |
| 2002 | Bonificación personal | SÍ | SÍ | SÍ | (276) |
| 2003 | Bonificación familiar (pública) | SÍ | SÍ | SÍ | (276) |
| 2004 | Bonificación diferencial | SÍ | SÍ | SÍ | (276) |
| 2005 | Aguinaldo Fiestas Patrias | SÍ | SÍ | NO | NO |
| 2006 | Aguinaldo Navidad | SÍ | SÍ | NO | NO |
| 2007 | Escolaridad | SÍ | SÍ | SÍ | (276) |
| (...) | (más conceptos específicos) | | | | |

**Notas:**
- *CTS computa promedio si concepto percibido ≥3 veces/semestre
- **Gratificaciones no afectan EsSalud desde Ley 30334 (bonif extraord 9% se paga al trabajador)
- ***CTS no es renta para 5ta porque es beneficio social

### 3.17 Tabla 23 — Tipo de Rubro (aplicable en estructuras adicionales)
### 3.18 Tabla 26 — Complementos de Documento
### 3.19 Tabla 27 — Clase de Prestador de Servicios
### 3.20 Tabla 37 — Organizaciones Sindicales de Servidores Públicos
Incorporada por R.M. 170-2023-TR para sector público.

---

## 4. Estructura Anexo 3 (archivos .txt)

### 4.1 Archivos que componen el paquete
1. `PLANI.txt` — datos del empleador y declaración
2. `JORNA.txt` — días laborados, horas, jornadas
3. `PDT.txt` — conceptos remunerativos por trabajador
4. `IMP.txt` — impuestos
5. `DERECH.txt` — derechohabientes
6. `PRACT.txt` — modalidades formativas
7. `CUART.txt` — prestadores 4ta categoría
8. `TERCE.txt` — personal de terceros
9. `EMPAL.txt` — empresas alquiladoras
10. `ESTAB.txt` — establecimientos

### 4.2 Formato común
- Archivo plano `.txt`
- Codificación ASCII
- Separador de campos: pipe `|`
- Separador de registros: salto de línea `\n`
- Fechas: `DD/MM/AAAA`
- Decimales: punto `.`, sin separador de miles
- Sin comillas alrededor de texto

### 4.3 Ejemplo de registro PLANI.txt (ilustrativo)
```
01|20123456789|4|2026|03|N|N|N|N|01|...
```
(El detalle completo del layout de cada archivo debe extraerse del Anexo 3 oficial SUNAT según su versión vigente.)

### 4.4 Consolidación
Los 10 archivos se comprimen en un **ZIP** que es lo que carga el PDT PLAME.

---

## 5. Integración técnica en el SaaS

### 5.1 Tablas internas (mapeo a Anexo 2)
Todas las tablas Anexo 2 deben existir como catálogos en la DB, pre-cargados en el sistema:

```sql
CREATE TABLE sunat_tables (
    id SERIAL PRIMARY KEY,
    table_number INT NOT NULL,        -- 1, 8, 11, 22, etc.
    code VARCHAR(10) NOT NULL,
    description TEXT NOT NULL,
    sector_allowed VARCHAR(100),      -- sectores donde aplica
    valid_from DATE,
    valid_to DATE,
    metadata JSONB,                   -- matriz de afectación para Tabla 22
    UNIQUE(table_number, code, valid_from)
);

-- Ejemplo de metadata para concepto 0101
-- {
--   "afecta_renta_5ta": true,
--   "afecta_afp": true,
--   "afecta_onp": true,
--   "afecta_essalud": true,
--   "afecta_cts": true,
--   "afecta_gratificacion": true
-- }
```

### 5.2 Servicio generador de archivos PLAME
```python
class PlameGenerator:
    def __init__(self, tenant_id, period):
        self.tenant_id = tenant_id
        self.period = period
        self.archivos = {}
    
    def generate(self) -> bytes:  # retorna ZIP
        self.archivos['PLANI.txt'] = self._generate_plani()
        self.archivos['JORNA.txt'] = self._generate_jornada()
        self.archivos['PDT.txt'] = self._generate_pdt()
        self.archivos['IMP.txt'] = self._generate_impuestos()
        self.archivos['DERECH.txt'] = self._generate_derechohabientes()
        # ... resto de archivos
        return self._package_zip()
    
    def validate_with_pvs(self, zip_bytes: bytes) -> list[ValidationError]:
        # Integración con PVS (si se puede via CLI) o reimplementar validaciones
        pass
```

### 5.3 Servicio T-Registro
```python
class TRegistroService:
    def register_alta(self, employee, contract):
        # Generar registro de alta en formato T-Registro
        # Validar localmente
        # Generar archivo
        # Retornar listo para carga manual en SUNAT Operaciones en Línea
        pass
    
    def register_baja(self, employee, termination_date):
        pass
    
    def register_modification(self, employee, changes):
        pass
```

### 5.4 Actualizaciones automáticas de catálogos
El sistema debe suscribirse a cambios normativos:
- Monitoreo de publicaciones en El Peruano / SUNAT
- Equipo legal valida y actualiza tablas
- Versionado de catálogos (valid_from/valid_to)
- Migración automática de conceptos antiguos a nuevos códigos

---

## 6. Cronograma de obligaciones mensuales

| Obligación | Plazo típico | Formato |
|-----------|--------------|---------|
| T-Registro (altas) | Antes del primer día de labor | .zip + portal SUNAT |
| T-Registro (bajas) | Día del cese | .zip + portal SUNAT |
| T-Registro (modificaciones) | Hasta 5 días después del hecho | .zip + portal SUNAT |
| PLAME (F.V. 0601) | Según último dígito RUC (11 al 24 del mes siguiente) | .zip + PDT PLAME |
| Pago de aportes (EsSalud, ONP) | Junto con declaración PLAME | NPS + bancos |
| AFPnet | Según cronograma AFP (similar PLAME) | .xlsx + portal AFPnet |

---

## 7. Errores comunes a prevenir

| Error | Causa | Mitigación en SaaS |
|-------|-------|---------------------|
| Concepto no mapeado a código SUNAT | Admin crea concepto sin mapeo | Campo obligatorio en formulario |
| Trabajador sin CUSPP en AFP | Alta incompleta | Validación cruzada con AFPnet |
| Declaración fuera de plazo | Olvido o error humano | Dashboards de vencimientos + alertas |
| Código de régimen pensionario incorrecto | Cambio de AFP no registrado | Integración SBS automática |
| Archivo PLAME rechazado | Error de formato | Validación previa con PVS embebido |
| Diferencia entre T-Registro y PLAME | Alta/baja no sincronizada | Eventos del sistema disparan ambos |

---

## 8. Referencias oficiales
- [SUNAT - Portal Planilla Electrónica](https://orientacion.sunat.gob.pe/planilla-electronica)
- [SUNAT - Tablas Paramétricas (online)](https://orientacion.sunat.gob.pe/7086-12-tablas-parametricas)
- [SUNAT - Tabla 22 PDF oficial](https://orientacion.sunat.gob.pe/sites/default/files/inline-files/Tabla%20N22%20Definici%C3%B3n%20Conceptos%20Plame_011025.pdf)
- [SUNAT - Cartilla PDT PLAME](http://contenido.app.sunat.gob.pe/insc/PLAME/CARTILLA_PDT+PLAME_12FEB2013.pdf)
- [SUNAT - Taller T-Registro + PVS](http://contenido.app.sunat.gob.pe/insc/PLAME/TALLER+TREGISTRO.pdf)
- [SERVIR - FAQ T-Registro y PLAME Sector Público](https://www.gob.pe/institucion/servir/informes-publicaciones/3204877)
- [R.M. 170-2023-TR (modificatoria)](https://www.contadoresyempresas.com.pe/modifican-anexos-de-la-norma-que-aprueba-la-informacion-de-la-planilla-electronica/)

---

## 9. Gaps de investigación para completar
- [ ] Descargar y transcribir el layout completo de Anexo 3 por archivo (PLANI, JORNA, PDT, etc.) con posiciones exactas
- [ ] Validar los 100+ códigos de Tabla 22 con matriz completa de afectación
- [ ] Obtener API de SUNAT si existe (actualmente solo archivos)
- [ ] Documentar exhaustivamente códigos de error del PVS
