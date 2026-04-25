# C02. Paquetes Sectoriales

> Cinco verticales donde la complejidad normativa peruana es tal que un paquete preconfigurado (templates + workflows + tablas paramétricas sectoriales) supera por mucho a cualquier competidor genérico.

---

## 1. Paquete Minería

### 1.1 Dolor del cliente
- Régimen minero (D.S. 014-92-EM) con 125% RMV como base mínima.
- Bonificaciones específicas: altura (>2,500 msnm), subsuelo, condiciones insalubres.
- Sistema de turnos 14×7, 20×10 con compensaciones distintas.
- SCTR obligatorio (Pensión y Salud) con cobertura diferenciada.
- Control extremo de SST: Ley 29783 + D.S. 055-2010-EM + Reglamento interno de la entidad.
- Desplazamientos entre operaciones, campamentos, oficinas administrativas.
- Exámenes médicos ocupacionales más frecuentes (altura).
- Capacitación obligatoria IPERC, rescate, primeros auxilios.

### 1.2 Configuración preconfigurada
- Régimen minero activo con motor de bonificaciones automático.
- Turnos 14×7 y 20×10 con plantillas rotativas y bloqueo de horas extras.
- Submódulos SST adicionales: reporte mensual ESSALUD SCTR, libro de accidentes minero, estadísticas IPERC por operación.
- Templates de contratos sujetos a modalidad para operación específica.
- Geofencing obligatorio para marcaciones en sitio de operación.
- Alertas de vencimiento de EMO diferenciado por altitud y exposición.
- Reports específicos: OSINERGMIN, MEM, mina + campamento.
- Integración opcional con sistemas de control de acceso (torniquetes, biometría en campamento).

### 1.3 Clientes típicos
Medianas y grandes mineras, contratistas mineros, empresas de explosivos, logística minera.

---

## 2. Paquete Construcción Civil

### 2.1 Dolor del cliente
- Régimen de Construcción Civil: jornales diferenciados por categoría (Operario, Oficial, Peón) con bonificaciones móviles.
- Pliego de convenio colectivo anual FTCCP-CAPECO cambia tarifas.
- **BUC** (Bonificación Unificada de Construcción): 32% del jornal básico del Operario.
- **CONAFOVICER**: aporte 2% sobre jornal básico semanal.
- **Bonif. por altura** (5 pisos o 10m): 5-7% jornal.
- **Bonif. por movilidad**: 50% jornal/día (solo días efectivamente trabajados).
- Dominical, compensación pérdida del dominical.
- Rotación alta entre obras; contratos por obra determinada.
- SCTR obligatorio.

### 2.2 Configuración preconfigurada
- Categorías Operario / Oficial / Peón con jornal base vigente.
- Tabla paramétrica actualizable anualmente con el pliego FTCCP-CAPECO.
- Cálculo automático de BUC, CONAFOVICER, movilidad, altura, dominical.
- Estructura multi-obra con geofencing por obra.
- Contratos sujetos a modalidad "obra determinada" con cierre automático al fin de obra.
- Libro de obra electrónico integrable.
- Certificados semanales de aporte CONAFOVICER.

### 2.3 Clientes típicos
Constructoras medianas/grandes, contratistas de obras, concesionarias viales.

---

## 3. Paquete Agroindustrial

### 3.1 Dolor del cliente
- Ley 31110 régimen agrario con **dos sistemas de pago** a elección del empleador:
  - **Consolidado**: Remuneración Diaria (RD) = RB + 16.66% gratif + 9.72% CTS (todo junto).
  - **Tradicional**: pagos separados al estilo 728.
- **BETA** (Bonificación Especial Trabajo Agrario) = 30% RMV.
- IR reducido al 15% hasta 2035 (beneficio fiscal).
- EsSalud agrario: 9% con tope especial.
- Campañas estacionales con alta rotación.
- Jornadas atípicas (siembra, cosecha).

### 3.2 Configuración preconfigurada
- Régimen 31110 con selección de sistema de pago por empleado (algunos en consolidado, otros en tradicional — permitido por ley).
- Cálculo automático de RD para consolidado, incluyendo BETA.
- Módulo de campañas con presupuesto de jornales.
- Gestión de cuadrillas y pago por productividad opcional (por kilos, cajas, surcos).
- Reportes para MIDAGRI y SUNAT específicos.
- Contratos por campaña con cierre automático.

### 3.3 Clientes típicos
Grandes agroexportadoras (arándano, uva, palta, espárrago), packing houses, fundos.

---

## 4. Paquete Retail y Restauración

### 4.1 Dolor del cliente
- Alta rotación y volumen de colaboradores part-time.
- Turnos rotativos y horarios escalonados con picos de feriados/fin de semana.
- Múltiples sedes con biométrica/QR por tienda.
- Propinas (no remunerativas) con tratamiento especial.
- Comisiones por venta variable.
- Control de hurtos internos (investigaciones laborales).
- Capacitación obligatoria continua (servicio al cliente, inocuidad alimentaria en food).

### 4.2 Configuración preconfigurada
- Turnos drag-and-drop con autoservicio de intercambio.
- Control de horas con alertas antes de exceder las 48h semanales.
- Fórmulas de comisiones configurables por tienda/categoría.
- Gestión de propinas separada de remuneración.
- LMS con cursos obligatorios y certificaciones.
- Aplicación móvil lightweight para colaborador de tienda.
- Dashboard por tienda (supervisores).
- Integración con POS para importar ventas al cálculo de comisiones.

### 4.3 Clientes típicos
Cadenas retail, franquicias food & beverage, supermercados, cines, farmacias.

---

## 5. Paquete Sector Público (GovTech)

### 5.1 Dolor del cliente
- Conviven hasta **4 regímenes simultáneos**: DL 276 (carrera administrativa), DL 1057 (CAS), Ley 30057 (Servir — transición), Ley 29849 (CAS indeterminado en algunos casos).
- Sistema Único de Remuneraciones (SUR) con URP + MUC según DS 320-2022-EF.
- Bonificaciones personal (5%/quinquenio), familiar (histórica S/ 3), diferencial (cargo directivo o condición excepcional).
- Aguinaldos fijos por DS anual (no gratificaciones equivalentes).
- **23 procesos SERVIR** a cubrir (ver imágenes Modelo Gestión RRHH).
- **7 subsistemas** del Sistema Administrativo de Gestión de Recursos Humanos.
- **Tribunal del Servicio Civil** como segunda instancia administrativa.
- **PAD** (Procedimiento Administrativo Disciplinario) con etapas, plazos y tipos de falta muy definidos.
- Desplazamientos: rotación, encargatura, destaque, comisión, designación, transferencia, permuta.
- Declaración Jurada de Bienes y Rentas periódica.
- Obligación de **AIRHSP** (Aplicativo Informático de Recursos Humanos Sector Público).
- Cultura y Clima Organizacional regulado por RPE 150-2017-SERVIR.
- Comunicación Interna regulada por RPE 151-2017-SERVIR.
- Compliance con SERVIR + MEF + Contraloría + Defensoría.

### 5.2 Configuración preconfigurada
- Régimen 276 completo (14 niveles, 3 grupos, URP + MUC + bonificaciones).
- Régimen CAS con aguinaldos.
- Módulo de transición a Ley 30057 (Servir) con plan de migración.
- Workflow de PAD con 4 fases (preliminar, instructiva, sancionadora, apelación Tribunal).
- Catálogo de desplazamientos con validación de requisitos por tipo.
- Legajo electrónico con secciones normativas (nombramientos, ascensos, sanciones, felicitaciones).
- Generador de Declaraciones Juradas de Bienes y Rentas.
- Plan anual de Cultura y Clima con template RPE 150-2017.
- Plan anual de Comunicación Interna con template RPE 151-2017.
- Módulo de evaluación por competencias alineado al Modelo Servir.
- Reporte AIRHSP.
- Auditoría externa anual incluida.
- Tribunal del Servicio Civil como rol especial con acceso read-only a expedientes.
- Integración opcional con PIDE (Plataforma de Interoperabilidad del Estado) cuando disponible.

### 5.3 Clientes típicos
Ministerios, gobiernos regionales, municipalidades, organismos técnicos especializados, hospitales públicos, universidades públicas, empresas estatales.

---

## 6. Elementos comunes a todos los paquetes

Cada paquete incluye:

- **Templates precargados** de contratos, boletas, certificados, reportes específicos del sector.
- **Workflows predefinidos** para los procesos más críticos del sector.
- **Tablas paramétricas sectoriales** (vigentes + histórico).
- **Playbook del consultor** para implementación.
- **Capacitación específica al cliente** (8-16 horas incluidas).
- **Soporte con experto sectorial** durante primer año.

---

## 7. Cómo se vende

Los paquetes no son un tier separado; son **add-ons al tier Pro/Enterprise/GovTech** que se combinan con el core. Un cliente constructora típico contrata:

> **Tier Pro + Paquete Construcción Civil + Firma electrónica + App móvil white-label**

El precio se estructura así:

- Base Pro por empleado/mes.
- Sobretasa del 15-25% por paquete sectorial activado.
- Add-ons individuales.

El paquete sectorial no añade empleados ni infra adicional; añade **templates, workflows, tablas paramétricas y horas de consultor sectorial** en el onboarding.

---

## 8. Roadmap de paquetes futuros

Según demanda del mercado peruano:

| Paquete | Cuándo sumar | Señal de mercado |
|---|---|---|
| **Pesquero** | Cuando haya 5+ leads | Clientes con régimen pesquero D.S. 014-78-TR |
| **Textil** | Cuando haya 5+ leads | Beneficios Ley 29360 / D.S. 008-2018-MTPE |
| **Salud** | Cuando haya 3+ hospitales privados | Colegios profesionales, RNE, jornadas 12×12 |
| **Educación privada** | Cuando haya 5+ colegios/IES | LEY 29944, jornadas docentes, aguinaldo especial |
| **Call Centers / BPO** | Cuando el vertical crezca | Turnos 7×24, métricas operativas, altos volúmenes |

---

## 9. Checklist por paquete

Para lanzar un paquete sectorial:

- [ ] Tablas paramétricas del sector cargadas y documentadas
- [ ] Workflows específicos diseñados y testeados con cliente piloto
- [ ] Templates de documentos validados por consultor laboral del sector
- [ ] Al menos 1 cliente piloto en producción con feedback estructurado
- [ ] Playbook de implementación (40-80 páginas)
- [ ] Capacitación interna del equipo de ventas y CS
- [ ] Casos de estudio publicados
- [ ] Materiales de marketing sectorial
