# N07. Aportes a Pensiones y Salud — AFP, ONP, EsSalud, EPS, SCTR

> Motor de cálculo de aportes previsionales y de salud. Todo lo que va al trabajador como descuento obligatorio (aportes del trabajador) y todo lo que paga el empleador por cuenta del trabajador (aportes del empleador).

---

## 1. Sistema Privado de Pensiones (SPP / AFP)

### 1.1 Marco normativo
- D.L. 25897 (Ley del SPP).
- D.S. 054-97-EF (TUO SPP).
- Reglamento de la Ley SPP.
- Ley 32123 (2024) — Reforma pensional en implementación progresiva.
- Regulación SBS (circulares, licitaciones trienales de afiliación nuevos trabajadores).

### 1.2 AFPs autorizadas (2026)

| AFP | Comisión por flujo | Comisión sobre saldo (anual) |
|---|---|---|
| AFP Integra | 1.55% | 1.00% |
| Prima AFP | 1.60% | 1.25% |
| Profuturo AFP | 1.69% | **0.68%** (licitación 2025-2027) |
| Habitat AFP | 1.47% | 1.25% |

**Nota 2025-2027**: Profuturo ganó la séptima licitación SBS. Todos los **nuevos afiliados al SPP** entre 01/06/2025 y 31/05/2027 se incorporan obligatoriamente a Profuturo.

### 1.3 Componentes del descuento AFP

El descuento mensual del trabajador incluye:

| Componente | Tasa | Base |
|---|---|---|
| **Aporte obligatorio al fondo** | 10% | Remuneración asegurable |
| **Comisión AFP** | Variable (ver tabla) | Flujo o saldo según elección del afiliado |
| **Prima SISCO** (Seguro Invalidez, Sobrevivencia, Gastos Sepelio) | 1.37% | Remuneración asegurable, con tope RMA |

### 1.4 Remuneración Máxima Asegurable (RMA) — tope prima SISCO

La RMA se actualiza trimestralmente por la SBS:

| Trimestre | RMA |
|---|---|
| Ene-Mar 2026 | S/ 12,394.32 |
| **Abr-Jun 2026** | **S/ 12,598.91** |

La prima SISCO aplica solo hasta este tope (el exceso no paga prima, pero sí aporte al fondo y comisión).

### 1.5 Comisión por flujo vs. Comisión sobre saldo

- **Por flujo**: % sobre la remuneración mensual. Solo afiliados antes del 01/02/2013 pueden mantenerla.
- **Sobre saldo (mixta)**: % anual sobre el fondo acumulado. Default para nuevos afiliados.
- Cambio permitido cada 3 años (ventana anual).

### 1.6 Archivo AFPnet — columnas del Excel

Layout exigido por AFPnet (25 columnas):

1. CUSPP (Código Único de Identificación SPP)
2. Tipo documento
3. Número documento
4. Apellido paterno
5. Apellido materno
6. Nombres
7. Fecha nacimiento
8. Sexo
9. Relación laboral (S/N)
10. Fecha inicio relación en el período
11. Fecha fin relación en el período
12. Días laborados
13. Días subsidiados
14. Días no laborados
15. Motivo excepción aporte (S/L/C/P/O)
16. Remuneración asegurable
17. Aportes voluntarios con fin previsional
18. Aportes voluntarios sin fin previsional
19. Aporte del empleador
20. Aporte complementario riesgo Ley 27252
21. Tipo trabajo (N/C/M/P)
22-25. Campos adicionales según versión

### 1.7 Procesos AFPnet
- **DNP** (Declaración sin Pago): declaración de meses sin aporte.
- **DYP** (Declaración y Pago): declaración con pago efectivo.

---

## 2. Sistema Nacional de Pensiones (SNP / ONP)

### 2.1 Marco normativo
- D.L. 19990 (creación del SNP).
- D.S. 054-97-EF.
- Administración por ONP.

### 2.2 Aporte

| Concepto | Valor |
|---|---|
| Aporte del trabajador | **13%** |
| Base | Remuneración asegurable (sin tope) |
| Base mínima | RMV |
| Declaración | PLAME mensual |

### 2.3 Pensión máxima SNP
**S/ 1,000** desde 31/12/2025 (aumentada por D.S. 330-2025-EF, anteriormente S/ 893).

### 2.4 Cambio de sistema (SNP ↔ SPP)
- Una vez afiliado al SPP, es **irreversible** el cambio a SNP (salvo excepciones muy puntuales).
- Jóvenes recién incorporados al mercado laboral pueden elegir entre SNP y SPP en primera vez.

---

## 3. EsSalud — Seguridad Social en Salud

### 3.1 Marco normativo
- Ley 26790.
- D.S. 009-97-SA.
- Administración por EsSalud.

### 3.2 Aportes

| Tipo de trabajador | Tasa | Base |
|---|---|---|
| Régimen general 728 | **9%** empleador | Remuneración (mínimo RMV) |
| MYPE Micro | 0 empleador (trabajador va al SIS — Estado paga) | N/A |
| MYPE Pequeña | 9% empleador | Remuneración |
| CAS | 9% empleador | Retribución |
| 276 | 9% empleador | Remuneración total |
| 30057 | 9% empleador | Compensación económica |
| Hogar | 9% empleador | Remuneración |
| Agrario 31110 | 9% empleador | Remuneración |

**Base mínima**: RMV (aún si el empleado ganó menos en el período).

### 3.3 Subsidios EsSalud

| Subsidio | Condición | Monto |
|---|---|---|
| **Incapacidad temporal** | Descanso médico >20 días | Promedio de 4 últimas rem.; empleador paga primeros 20 días, EsSalud paga desde día 21 hasta 340/año |
| **Maternidad** | Gestación y post-parto | 98 días (49 pre + 49 post); 128 días con parto múltiple o discapacidad del bebé |
| **Lactancia** | Al nacer hijo | S/ 820 pago único |
| **Sepelio** | Fallecimiento del asegurado | Hasta S/ 2,070 |
| **Incapacidad temporal por COVID / otros** | Normativa específica | Variable |

### 3.4 CITT (Certificado de Incapacidad Temporal para el Trabajo)
Documento electrónico emitido por EsSalud que sustenta el descanso médico y habilita el subsidio.

### 3.5 Latencia
Al cesar, el ex-trabajador mantiene cobertura por **2 meses** por cada 5 meses de aportes continuos inmediatamente previos, **máximo 12 meses**.

---

## 4. EPS (Entidades Prestadoras de Salud) — alternativa a EsSalud

### 4.1 Marco normativo
- Ley 26790 (Art. 15).
- Supervisión por SUSALUD.

### 4.2 Mecánica
- EPS privadas autorizadas (Rímac EPS, Pacífico EPS, Mapfre Perú EPS, Sanitas Perú).
- Contrato voluntario del empleador con EPS.
- Trabajador mantiene cobertura EsSalud (capa compleja: enfermedades catastróficas, gestación, maternidad), EPS cubre capa simple (consultas ambulatorias, emergencias).

### 4.3 Crédito EPS
**2.25% de la remuneración asegurable** es **crédito** contra el aporte EsSalud del empleador:
- Aporte total empleador = 9%.
- Crédito EPS aplicable = 2.25% (efectivo pagado a EsSalud = 6.75%).
- **Tope del crédito**: 10 RMV × número de trabajadores cubiertos por EPS.

### 4.4 Impacto en el SaaS
- Marcador por empleado "cobertura EPS sí/no".
- Cálculo automático del crédito EPS y del monto neto a EsSalud.
- Factura EPS como egreso separado.

---

## 5. SCTR — Seguro Complementario de Trabajo de Riesgo

### 5.1 Marco normativo
- Ley 26790 (Art. 19).
- D.S. 003-98-SA (Reglamento).
- Normas técnicas de actividades riesgosas (minería, construcción, pesca, manufactura química).

### 5.2 Obligatoriedad
Para trabajadores que realizan actividades calificadas como **de alto riesgo** (listado en D.S. 003-98-SA y normas conexas):
- Minería (todas las fases).
- Construcción civil.
- Hidrocarburos.
- Electricidad.
- Industria química.
- Pesca.
- Transporte de mercaderías peligrosas.
- Otras actividades declaradas.

### 5.3 Dos coberturas obligatorias
- **SCTR Salud**: accidentes de trabajo y enfermedades profesionales.
- **SCTR Pensiones**: invalidez parcial/total permanente, sobrevivencia.

Contratadas con EsSalud / EPS (salud) y con AFP / compañía de seguros autorizada (pensiones).

### 5.4 Costos
Tasa según nivel de riesgo de la actividad (fijada por SBS/SUNAT tarifa específica). Cargada al empleador, adicional al EsSalud y AFP regulares.

### 5.5 Impacto en el SaaS
- Marcador por puesto "requiere SCTR".
- Cálculo de aporte SCTR Salud + SCTR Pensiones como conceptos separados de planilla.
- Cobertura completa automática para sectores minero y construcción.

---

## 6. Aportes obligatorios del empleador (no relacionados con AFP/ONP/Salud)

### 6.1 SENATI
- **0.75%** sobre la planilla, si el empleador es de **industria manufacturera** con más de 20 trabajadores.
- Destino: SENATI (Servicio Nacional de Adiestramiento en Trabajo Industrial).

### 6.2 SENCICO
- **0.2%** sobre la planilla, si el empleador es del **sector construcción**.
- Destino: SENCICO (Servicio Nacional de Capacitación para la Industria de la Construcción).

### 6.3 CONAFOVICER
- **2%** sobre el jornal básico semanal, si es **construcción civil**.
- Descuento del trabajador (no es aporte patronal).

### 6.4 Seguro de Vida Ley 29549
- Obligatorio desde el primer día (modificación Ley 29549).
- Cobertura mínima: **16 remuneraciones** en caso de muerte natural; **32 rem.** muerte accidental; **32 rem.** invalidez total y permanente por accidente.
- Prima variable por aseguradora.

---

## 7. Mapa de conceptos PLAME — Tabla 22 SUNAT (aportes y descuentos)

### 7.1 Descuentos del trabajador (rubro 06)

| Código | Concepto |
|---|---|
| 0601 | Aporte obligatorio AFP (10% fondo) |
| 0602 | Aportes voluntarios AFP con fin previsional |
| 0603 | Aportes voluntarios AFP sin fin previsional |
| 0605 | Renta de 5ta categoría (retención) |
| 0606 | Prima de seguro AFP (SISCO 1.37%) |
| 0607 | Aporte SNP – ONP (13%) |
| 0608 | Aportes voluntarios empleador SPP |
| 0609 | Aportes voluntarios SPP (cuenta separada) |

### 7.2 Aportes del empleador (rubro 08)

| Código | Concepto |
|---|---|
| 0801 | Aporte EsSalud (9%) |
| 0803 | SCTR Salud |
| 0804 | SCTR Pensiones |
| 0805 | SENATI (0.75%) |
| 0806 | SENCICO (0.2%) |
| 0807 | Seguro Agrario |
| 0809 | Prima seguro vida Ley 29549 |

Cada concepto tiene su matriz de afectación (SI/NO) contra: renta 5ta, EsSalud, AFP/ONP, CTS, gratif, vacaciones.

---

## 8. Reforma Pensional Ley 32123 (en implementación)

### 8.1 Puntos clave
- Unifica progresivamente SNP y SPP en un sistema multipilar.
- Pensión mínima garantizada por el Estado (Pensión por Consumo, Pensión Social).
- Aportes obligatorios de trabajadores independientes (cronograma progresivo).
- AFPs pueden convertirse en entidades financieras diversificadas (aprobación SBS 2025).
- Período de transición prolongado (10+ años).

### 8.2 Implicaciones para el SaaS
- Seguimiento de cronograma de entrada en vigencia de cada disposición.
- Módulo para trabajadores independientes (freelancers, 4ta categoría) con aportes obligatorios.
- Posibilidad de cambio de AFP a banco/aseguradora (futuro).

---

## 9. Impacto integral en el SaaS

### 9.1 Entidades
- `ParametrosPensionales` (tasas AFP, RMA, comisión vigente por trimestre).
- `ConceptoPlanilla` mapeado a Tabla 22.
- `AportesPeriodo` (matriz de aportes calculados por trabajador y período).
- `SCTRConfiguracion` por puesto.

### 9.2 Procesos
- Carga de tasas AFP desde SBS (scraper automático mensual).
- Actualización de RMA trimestral.
- Cálculo de crédito EPS con topes.
- Generación archivo AFPnet .xlsx con 25 columnas.
- Declaración PLAME mensual.

### 9.3 Validaciones críticas
- Base mínima EsSalud = RMV.
- Trabajador en SPP no puede retroceder a SNP (excepción puntual).
- SCTR obligatorio según CIIU del puesto.
- Tope RMA para prima SISCO aplicado correctamente.

---

## 10. Referencias oficiales

- [SBS — SPP](https://www.sbs.gob.pe/)
- [AFPnet](https://www.afpnet.com.pe/)
- [ONP](https://www.onp.gob.pe/)
- [EsSalud](https://www.essalud.gob.pe/)
- [SUSALUD — EPS autorizadas](https://www.susalud.gob.pe/)
- [SUNAT — Tabla 22 PLAME](https://orientacion.sunat.gob.pe/sites/default/files/inline-files/Tabla%20N22%20Definici%C3%B3n%20Conceptos%20Plame_011025.pdf)

---

## 11. Checklist

- [ ] Tabla `parametros_pensionales` con históricos y versión vigente
- [ ] Tasas AFP actualizadas automáticamente desde SBS
- [ ] RMA trimestral actualizada
- [ ] Cálculo correcto: aporte fondo + comisión + prima SISCO con tope
- [ ] Archivo AFPnet .xlsx con 25 columnas generado sin errores
- [ ] DNP y DYP soportados
- [ ] EsSalud 9% con base mínima RMV
- [ ] Crédito EPS con tope 10 RMV por trabajador
- [ ] SCTR automático para sectores de riesgo
- [ ] SENATI/SENCICO según CIIU del empleador
- [ ] Seguro Vida Ley 29549 desde primer día
- [ ] Reporte mensual EsSalud SCTR (PDT)
- [ ] Mapping completo Tabla 22 SUNAT en conceptos del sistema
