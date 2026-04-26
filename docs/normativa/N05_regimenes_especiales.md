# N05. Regímenes Laborales Especiales

> Conjunto de regímenes sectoriales peruanos con reglas propias de cálculo, beneficios y jornadas. Cada uno requiere una **estrategia específica** en el motor de planilla (patrón Strategy — ver A07).

---

## 1. MYPE — Ley 32353 (Régimen Integral)

### 1.1 Base normativa
- Ley 32353 (vigente 2025) — Nuevo Régimen Integral MYPE, reemplaza normativa anterior (D.L. 1086 / D.S. 013-2013-PRODUCE).
- Acreditación vía REMYPE (Registro Nacional MYPE).

### 1.2 Categorización

| Categoría | Ventas anuales | Trabajadores |
|---|---|---|
| **Microempresa** | Hasta 150 UIT | 1 a 10 |
| **Pequeña Empresa** | Hasta 1,700 UIT | 1 a 100 |

### 1.3 Beneficios laborales por categoría

| Beneficio | Microempresa | Pequeña Empresa | General 728 |
|---|---|---|---|
| Remuneración | ≥ RMV (S/ 1,130) | ≥ RMV | ≥ RMV |
| Jornada máxima | 48h/sem | 48h/sem | 48h/sem |
| Vacaciones | 15 días/año | 15 días/año | 30 días/año |
| Gratificaciones | **No aplica** | ½ sueldo × 2/año | 1 sueldo × 2/año |
| CTS | **No aplica** | 15 días/año (máx 90) | 1 sueldo/año |
| Asig. Familiar | No | No | Sí (S/ 113) |
| EsSalud | SIS (Estado) / EsSalud opcional | EsSalud 9% | EsSalud 9% |
| Seguro de Vida | No | Sí | Sí |
| Pensiones | SNP/SPP (opcional en Micro) | Obligatorio | Obligatorio |
| Indemnización despido arbitrario | 10 rem/año (máx 90) | 20 rem/año (máx 120) | 1.5 rem/año (máx 12) |

### 1.4 Impacto en el SaaS
- Strategies `RegimenMYPEMicro` y `RegimenMYPEPequena` con cálculos diferenciados.
- Validación de acreditación REMYPE vigente antes de aplicar beneficios reducidos.
- Alerta al superar umbrales de ventas/trabajadores para migración automática al régimen general.

---

## 2. Régimen Agrario — Ley 31110

### 2.1 Base normativa
- Ley 31110 (31/12/2020) — Régimen Laboral Agrario y de Incentivos.
- D.S. 005-2021-MIDAGRI — Reglamento.
- Vigencia progresiva de beneficios hasta 2030.

### 2.2 Dos sistemas de pago a elección del empleador

**Sistema 1 — Consolidado (RD)**

Remuneración Diaria consolida gratificaciones, CTS y vacaciones:

```
RD = RB + (RB × 16.66%) + (RB × 9.72%)
```

Donde:
- **RB** = Remuneración Básica Diaria ≥ RMV/30
- **16.66%** = gratificación proporcional
- **9.72%** = CTS proporcional

El pago mensual = RD × días efectivamente trabajados.

**Sistema 2 — Tradicional**

Idéntico al régimen 728: pagos separados de gratificaciones (jul/dic), CTS (may/nov), vacaciones al goce.

### 2.3 BETA — Bonificación Especial por Trabajo Agrario
- **30% de la RMV** mensual (S/ 339 con RMV S/ 1,130).
- Afecta a tributos y aportes.
- Aplica en ambos sistemas de pago.

### 2.4 Otros aspectos
- Vacaciones: 30 días anuales (igualado al régimen general por Ley 31110).
- EsSalud: 9% estándar.
- Seguro de Salud Agrario (alternativa EPS).
- Impuesto a la Renta empresarial: 15% hasta 2035.

### 2.5 Impacto en el SaaS
- Strategy `RegimenAgrarioLey31110` parametrizable con `sistema_pago` (CONSOLIDADO | TRADICIONAL).
- Cada empleado lleva la marca de qué sistema lo rige (la ley permite coexistencia dentro de la misma empresa).
- BETA calculado automáticamente.
- Módulo de campañas con presupuesto de jornales.

---

## 3. Régimen Construcción Civil

### 3.1 Base normativa
- Ley 727 (1991) y normativa conexa.
- Convenio Colectivo anual **FTCCP – CAPECO** (renovado cada pliego).
- D.S. 011-79-VC y modificatorias.

### 3.2 Categorías de trabajador

| Categoría | Función |
|---|---|
| **Operario** | Oficios especializados (albañil, carpintero, fierrero, electricista) |
| **Oficial** | Ayudante calificado |
| **Peón** | Labores no calificadas |

Cada categoría tiene **jornal básico diferenciado** fijado anualmente.

### 3.3 Beneficios y bonificaciones

| Concepto | Fórmula |
|---|---|
| **BUC (Bonificación Unificada de Construcción)** | 32% del jornal básico del Operario (aplica a todos) |
| **CONAFOVICER** | 2% del jornal básico semanal |
| **Bonificación por altura** | 5-7% del jornal (edificios desde 4-5 pisos o 10m) |
| **Bonificación por movilidad** | 50% jornal/día trabajado |
| **Dominical** | 1 jornal por cada 6 días trabajados |
| **Vacaciones** | 10% sobre jornales ganados |
| **CTS** | 15% sobre jornales |
| **Gratificaciones** | 40 jornales (Fiestas Patrias) + 40 jornales (Navidad) |

### 3.4 SCTR
Obligatorio (Pensión y Salud) dada la actividad de alto riesgo.

### 3.5 Impacto en el SaaS
- Strategy `RegimenConstruccionCivil` con parámetros anuales del pliego FTCCP-CAPECO.
- Estructura multi-obra con geofencing por obra.
- Contratos sujetos a modalidad "obra determinada".
- Certificados semanales de aporte CONAFOVICER.
- Libro de obra electrónico.

---

## 4. Régimen Minero

### 4.1 Base normativa
- D.S. 014-92-EM (Texto Único Ordenado Ley General de Minería).
- D.S. 055-2010-EM (Reglamento SSO minería).
- Convenios colectivos por empresa/sindicato minero.

### 4.2 Remuneración mínima
**Base = 125% de la RMV** (S/ 1,412.50 con RMV S/ 1,130).

### 4.3 Bonificaciones específicas

| Concepto | Aplicación |
|---|---|
| **Bonif. por altura** | >2,500 msnm; escala incremental por altitud |
| **Bonif. por subsuelo** | Labores en interior mina |
| **Condiciones insalubres** | Exposición a polvos, químicos, radiación |
| **Turno nocturno** | Recargo según pliego |

### 4.4 Turnos especiales
- Sistema 14×7, 20×10 con traslados desde ciudad → campamento.
- Jornadas atípicas reguladas.
- Compensación de días en campamento.

### 4.5 SCTR
Obligatorio con cobertura amplia (invalidez, sobrevivencia, gastos curativos).

### 4.6 Impacto en el SaaS
- Strategy `RegimenMinero`.
- Configurador de bonificaciones por altitud + exposición.
- Plantillas de turnos 14×7, 20×10.
- Reports específicos OSINERGMIN, MEM.
- Módulo SST reforzado: EMO diferenciado por altitud.

---

## 5. Régimen de Trabajadoras y Trabajadores del Hogar — Ley 31047

### 5.1 Base normativa
- Ley 31047 (2020) — Ley de las Trabajadoras y Trabajadores del Hogar.
- Reglamento D.S. 009-2020-TR.

### 5.2 Beneficios

| Concepto | Regla |
|---|---|
| Remuneración | Acuerdo; no menor a RMV |
| Jornada | Máx 48h/sem |
| Vacaciones | 15 días por año completo |
| CTS | Equivalente a ½ sueldo por año |
| Gratificaciones | ½ sueldo en Fiestas Patrias + ½ en Navidad |
| EsSalud | Obligatorio (empleador aporta 9%) |
| Pensiones | Obligatorio (AFP u ONP) |
| Contrato | Escrito, registrado (T-Registro) |

### 5.3 Impacto en el SaaS
- Strategy `RegimenHogarLey31047`.
- Útil en segmentos "familias y profesionales" como micro-plan.

---

## 6. Régimen Pesquero

### 6.1 Base normativa
- D.S. 014-78-TR y modificatorias.
- D.L. 22342 (pesca de consumo humano indirecto).
- Convenio colectivo FETRAPEP.

### 6.2 Sistema de pago por participación
Pago por **retribución** calculada sobre el volumen pescado + beneficios proporcionales.

### 6.3 Impacto en el SaaS
- Strategy `RegimenPesquero` (roadmap — generar cuando haya clientes demandándolo).

---

## 7. Régimen Textil y Confecciones

### 7.1 Base normativa
- D.S. 008-2018-MTPE — beneficios fiscales y laborales.
- Aplicable a empresas del sector de confección y textil.

### 7.2 Beneficios
Similar al régimen general 728 con incentivos fiscales sectoriales (tasa IR reducida por calificación especial).

### 7.3 Impacto en el SaaS
- Strategy `RegimenTextil` (extensión menor sobre 728).

---

## 8. Régimen de Exportación No Tradicional — Ley 22342

### 8.1 Aplicación
- Empresas cuya producción se destina principalmente a exportación no tradicional.
- Permite contratos sujetos a modalidad de duración flexible.

### 8.2 Particularidad
Derechos laborales idénticos al régimen 728, pero con mayor flexibilidad en contratación temporal.

---

## 9. Régimen de Trabajadores Extranjeros — D.Leg. 689

### 9.1 Reglas
- Tope del **20% del personal y 30% de la masa salarial** puede ser extranjero.
- Excepciones: CAN, MERCOSUR, cónyuges/hijos de peruanos, inversionistas (≥5 UIT), profesionales técnicos, multinacionales.
- Contratos escritos aprobados por MTPE.
- Residencia migratoria vigente (Calidad Migratoria Trabajador).

### 9.2 Régimen laboral aplicable
Una vez aprobado el contrato, el extranjero queda bajo el régimen 728 (o régimen especial si corresponde al sector).

---

## 10. Matriz comparativa de regímenes

| Régimen | Base salarial | CTS | Gratif | Vacaciones | Beneficio exclusivo |
|---|---|---|---|---|---|
| 728 General | RMV | 1 sueldo/año | 2 sueldos/año | 30 días | — |
| MYPE Micro | RMV | 0 | 0 | 15 días | SIS/EsSalud opcional |
| MYPE Pequeña | RMV | 15 días/año | ½ × 2 | 15 días | Seguro vida |
| Agrario (consolidado) | RB + 16.66% + 9.72% | Incluido | Incluido | 30 días | BETA 30% RMV |
| Construcción | Jornal × categoría | 15% jornales | 40+40 jornales | 10% jornales | BUC 32%, CONAFOVICER |
| Minero | 125% RMV | Régimen general | Régimen general | Régimen general | Bonif. altura/subsuelo |
| Hogar Ley 31047 | RMV (mínimo) | ½ sueldo/año | ½ × 2 | 15 días | — |
| Pesquero | Participación | Proporcional | Proporcional | 30 días | Sistema retribución |
| Textil 008-2018 | RMV | 1 sueldo/año | 2 sueldos/año | 30 días | IR reducido |
| Exportación No Trad. | RMV | 1 sueldo/año | 2 sueldos/año | 30 días | Flexibilidad contrato |

---

## 11. Checklist de implementación en el SaaS

- [ ] Strategy Pattern implementado para cada régimen como clase independiente
- [ ] Factory configurable por tenant y por empleado
- [ ] Parámetros anuales de pliegos actualizables sin redeploy (FTCCP-CAPECO, minero)
- [ ] Coexistencia de múltiples regímenes dentro del mismo tenant
- [ ] Validación REMYPE vigente antes de aplicar beneficios MYPE
- [ ] Alertas automáticas por umbral (MYPE que supera ventas UIT)
- [ ] Validación contratos extranjeros contra límites D.Leg. 689
- [ ] Módulos sectoriales específicos (minería, construcción, agro) como add-ons comerciales
