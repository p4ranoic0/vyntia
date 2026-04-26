# N09. Impuesto a la Renta de 5ta Categoría

> Retención mensual y regularización anual del impuesto a la renta sobre remuneraciones de trabajadores dependientes. Uno de los cálculos más complejos de la planilla peruana por su proyección anual y las variaciones en los meses finales del año.

---

## 1. Marco normativo

- **Decreto Legislativo 774** (Ley del Impuesto a la Renta).
- **TUO aprobado por D.S. 179-2004-EF** y modificatorias.
- **Reglamento D.S. 122-94-EF**.
- **D.Leg. 1258** (2016) — deducciones adicionales de hasta 3 UIT.
- Resoluciones SUNAT anuales sobre formato de declaración.

---

## 2. Conceptos clave

### 2.1 ¿Qué es la Renta de 5ta categoría?
Rentas derivadas del trabajo personal en relación de dependencia: sueldos, salarios, asignaciones, emolumentos, primas, dietas, gratificaciones, bonificaciones, aguinaldos, comisiones, compensaciones en dinero o en especie, gastos de representación y, en general, toda retribución por servicios personales.

### 2.2 Base imponible
Suma de conceptos remunerativos y no remunerativos afectos a renta 5ta, **netos** de conceptos legalmente inafectos (ej. CTS, asignaciones específicas no remunerativas, gratificaciones extraordinarias en ciertos casos).

### 2.3 Periodicidad
- **Retención mensual** por el empleador (como pago a cuenta).
- **Regularización anual** del propio trabajador si tiene otras rentas 5ta o si aplica deducción adicional 3 UIT.

---

## 3. Parámetros vigentes

### 3.1 UIT (Unidad Impositiva Tributaria)

| Año | UIT |
|---|---|
| 2025 | S/ 5,350 |
| **2026** | **S/ 5,500** (D.S. 301-2025-EF) |

### 3.2 Deducción fija de 7 UIT

| Año | 7 UIT |
|---|---|
| 2025 | S/ 37,450 |
| **2026** | **S/ 38,500** |

Esta deducción es automática: **si la RBA proyectada es menor o igual a 7 UIT, no hay retención**.

### 3.3 Deducción adicional de hasta 3 UIT (D.Leg. 1258)

**Solo aplica en la regularización anual**, nunca en la retención mensual.

| Año | 3 UIT |
|---|---|
| 2025 | S/ 16,050 |
| **2026** | **S/ 16,500** |

Gastos deducibles:
- Arrendamiento de inmuebles: 30% del gasto.
- Servicios de médicos y odontólogos: 30%.
- Servicios profesionales de 13 categorías específicas: 30%.
- Aportes EsSalud del trabajador del hogar: 100%.
- Restaurantes, hoteles, alojamiento: 15%.
- Guías oficiales de turismo: 50%.

---

## 4. Escala progresiva

Escala vigente 2025-2026:

| Tramo (UIT) | Tasa |
|---|---|
| Hasta 5 UIT | **8%** |
| Más de 5 UIT hasta 20 UIT | **14%** |
| Más de 20 UIT hasta 35 UIT | **17%** |
| Más de 35 UIT hasta 45 UIT | **20%** |
| Más de 45 UIT | **30%** |

### 4.1 Valores en soles 2026

| Tramo | Desde | Hasta | Tasa |
|---|---|---|---|
| 1er | S/ 0 | S/ 27,500 | 8% |
| 2do | S/ 27,500 | S/ 110,000 | 14% |
| 3er | S/ 110,000 | S/ 192,500 | 17% |
| 4to | S/ 192,500 | S/ 247,500 | 20% |
| 5to | S/ 247,500 | + | 30% |

---

## 5. Cálculo de la retención mensual

### 5.1 Paso 1: Remuneración Bruta Anual (RBA)

```
RBA = Rem. mensual × meses restantes del año (incluido el actual)
    + Rem. percibidas en meses anteriores del mismo año
    + Gratificaciones ordinarias del año (jul y dic, proyectadas o percibidas)
    + Bonificación extraordinaria Ley 30334 (proyectada)
    + Otros ingresos regulares proyectables
```

**Importante**: los **ingresos extraordinarios** (bono único, utilidades, reintegros, gratificación extraordinaria) **no se proyectan**. Se adicionan al mes en que se pagan.

### 5.2 Paso 2: Renta Neta Anual Proyectada (RNAP)

```
RNAP = RBA − 7 UIT
```

Si RNAP ≤ 0 → no hay retención.

### 5.3 Paso 3: Impuesto Anual Proyectado (IAP)

Aplicar la escala progresiva a la RNAP tramo por tramo.

### 5.4 Paso 4: Retención mensual

Dividir el IAP entre el **denominador mensual** según el mes:

| Mes | Denominador |
|---|---|
| Enero | 12 |
| Febrero | 12 |
| Marzo | 12 |
| Abril | 9 |
| Mayo | 8 |
| Junio | 8 |
| Julio | 8 |
| Agosto | 5 |
| Setiembre | 4 |
| Octubre | 4 |
| Noviembre | 4 |
| Diciembre | **Ajuste final** (ver abajo) |

### 5.5 Cálculo en diciembre (ajuste final)

```
Retención diciembre = IAP(definitivo) − Retenciones acumuladas ene-nov
```

No hay denominador; se regulariza hasta completar el impuesto definitivo del año.

---

## 6. Ejemplo práctico

**Trabajador** con sueldo S/ 4,500 mensual, asignación familiar S/ 113, ingresa el 1 de enero, sin otros ingresos variables.

**Paso 1 — RBA proyectada**:
- Sueldo mensual: 4,500 + 113 = 4,613
- RBA = 4,613 × 12 + 4,613 × 2 (gratif) + 4,613 × 2 × 9% (bonif 30334)
- RBA = 55,356 + 9,226 + 830.34 = **S/ 65,412.34**

**Paso 2 — RNAP**:
- RNAP = 65,412.34 − 38,500 = **S/ 26,912.34**

**Paso 3 — IAP**:
- 1er tramo: 26,912.34 × 8% = **S/ 2,152.99**
- (No alcanza 5 UIT = 27,500)

**Paso 4 — Retención de enero**:
- 2,152.99 ÷ 12 = **S/ 179.42**

---

## 7. Certificado de Rentas y Retenciones

### 7.1 Obligación
El empleador debe emitir **Certificado de Rentas y Retenciones** a cada trabajador dependiente:
- **Anual**: antes del 1 de marzo del año siguiente (por el ejercicio anterior).
- **Al cese**: si el trabajador cesa durante el año, al momento del cese.

### 7.2 Contenido
- Identificación del empleador y del trabajador.
- Total de rentas 5ta pagadas en el ejercicio.
- Total de retenciones efectuadas.
- Suma de aportes AFP/ONP, EsSalud (informativo).

### 7.3 Formato
Se usa el formato oficial SUNAT (actualmente vía SOL o PDT).

---

## 8. Regularización anual

### 8.1 ¿Quiénes deben regularizar?
- Trabajadores con **más de un empleador** en el año.
- Trabajadores que deseen aplicar la **deducción adicional de 3 UIT** (D.Leg. 1258).
- Casos con diferencias (retenciones insuficientes o en exceso).

### 8.2 Mecanismo
- SUNAT genera una declaración pre-elaborada con los datos de T-Registro + PLAME + recibos por honorarios (4ta categoría).
- El trabajador valida, ajusta y presenta.
- Pago del saldo deudor o devolución del saldo a favor.

### 8.3 Plazo
Campaña de renta anual de personas naturales: marzo-abril del año siguiente, según cronograma SUNAT.

---

## 9. Casos especiales

### 9.1 Trabajador con múltiples empleadores
- Cada empleador retiene como si fuera único.
- La regularización anual unifica todas las rentas y calcula el impuesto real.

### 9.2 Cese durante el año
- Empleador emite certificado.
- Trabajador ingresa a nuevo empleo o es independiente → consolidación en regularización anual.

### 9.3 Reintegro de remuneraciones
- Se considera del mes en que se paga.
- Genera retención adicional.

### 9.4 Prácticas pre-profesionales y profesionales (Ley 28518)
- Las "subvenciones" NO son renta 5ta (son renta de 4ta si aplica, o exoneradas si cumplen ciertos requisitos).
- NO se retiene 5ta, NO se aporta EsSalud ni AFP/ONP obligatorio.

### 9.5 Extranjeros no domiciliados
- Retención **30%** sobre el monto bruto sin deducción.
- No aplica escala progresiva.
- Cambia a régimen de domiciliados tras 183 días de permanencia continua.

---

## 10. Conceptos NO afectos a renta 5ta

- **CTS**.
- **Gratificaciones extraordinarias** (aunque en ciertos casos sí, ver abajo).
- **Indemnizaciones** (por despido arbitrario, vacacionales, por muerte).
- **Condiciones de trabajo** (movilidad, refrigerio, ropa, EPP).
- **Subsidios** (por incapacidad, maternidad, lactancia, sepelio).
- **Bonificación extraordinaria Ley 30334** — **NO afecta a EsSalud/AFP/ONP pero SÍ a Renta 5ta**.
- **Movilidad supeditada a asistencia** (no sustituta).

### 10.1 Gratificaciones extraordinarias — caso de excepción
Las extraordinarias que se pagan con regularidad pueden ser recalificadas por SUNAT y generar renta 5ta. Las genuinamente extraordinarias (por un evento único) no afectan.

---

## 11. Impacto en el diseño del SaaS

### 11.1 Entidades
- `ParametroTributario` con UIT por año y escala vigente.
- `ProyeccionRenta5ta` calculada mes a mes por empleado.
- `RetencionMensual` con trazabilidad.
- `CertificadoRentasRetenciones` generable al cierre del ejercicio o cese.

### 11.2 Motor de cálculo
1. Al calcular la planilla mensual, proyectar RBA considerando el mes corriente.
2. Aplicar deducción de 7 UIT.
3. Calcular IAP con escala progresiva.
4. Dividir por denominador del mes.
5. Restar retenciones acumuladas del año y ajustar.

### 11.3 Consideraciones
- Cambio de UIT mid-year no existe (UIT es anual por D.S. de fin de año anterior).
- El motor debe manejar cambios retroactivos: ajuste de sueldo en marzo con efecto desde enero requiere recalcular desde enero.
- Eventos inmutables (Event Sourcing) permiten reconstruir el cálculo exacto de cualquier mes histórico.

### 11.4 Validaciones
- RBA ≥ 0.
- Retención mensual no puede ser negativa (si la regularización da negativa, se arrastra como crédito).
- Total retenido ≤ IAP del año (caso contrario, el exceso es devolución).
- Empleado en régimen CAS: misma mecánica.
- Empleado régimen 276: retiene 5ta sobre remuneración total excepto aguinaldos (que no afectan).

---

## 12. Referencias oficiales

- [SUNAT — Cálculo del impuesto](https://orientacion.sunat.gob.pe/3071-02-calculo-del-impuesto)
- [SUNAT — Cartilla Rentas Personas Naturales](https://renta.sunat.gob.pe/)
- [D.S. 301-2025-EF — UIT 2026](https://busquedas.elperuano.pe/)
- [D.Leg. 1258 — deducción 3 UIT](https://busquedas.elperuano.pe/)

---

## 13. Checklist

- [ ] Parámetros UIT por año cargados correctamente
- [ ] Escala progresiva actualizada y versionada
- [ ] Proyección de RBA con gratif y bonif 30334 automática
- [ ] Denominadores mensuales correctos (12, 9, 8, 5, 4)
- [ ] Ajuste de diciembre calcula impuesto definitivo
- [ ] Ingresos extraordinarios sumados al mes, no proyectados
- [ ] Certificado de Rentas y Retenciones generable anualmente y al cese
- [ ] Retenciones acumuladas trazables
- [ ] Extranjeros no domiciliados: 30% retención sin escala
- [ ] Deducción 3 UIT: NO aplica en retención mensual; informativa al trabajador
- [ ] Changes retroactivos (ajuste salarial mid-year) recalculan desde enero
- [ ] Integración PLAME con rubro 0605 (renta 5ta retención)
