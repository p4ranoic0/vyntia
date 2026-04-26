# A07. Strategy Pattern para Regímenes Laborales

> Cada régimen laboral peruano tiene reglas de cálculo propias (CTS, gratificaciones, aportes, vacaciones). El patrón Strategy encapsula cada régimen como una clase intercambiable, manteniendo el núcleo del motor de planilla limpio.

---

## 1. Problema

El Perú tiene al menos **13 regímenes laborales** activos, cada uno con sus propias reglas:

| Régimen | Base legal | Particularidad clave |
|---|---|---|
| 728 General | D.S. 003-97-TR | Régimen privado estándar |
| MYPE Microempresa | D.L. 1086 / D.S. 013-2013-PRODUCE | Sin CTS ni gratif; 15 días vacaciones |
| MYPE Pequeña Empresa | D.L. 1086 | CTS 15 días/año, gratif ½ sueldo |
| Agrario Ley 31110 | Ley 31110 + D.S. 005-2021-MIDAGRI | Dos sistemas de pago (RD consolidada o tradicional) |
| Construcción Civil | Ley 727 + Negociación FTCCP-CAPECO | Jornales por categoría + BUC + CONAFOVICER |
| Minero | D.S. 014-92-EM | Base 125% RMV + bonif altura/subsuelo |
| Textil/Confecciones | D.S. 008-2018-MTPE | Incentivos fiscales y laborales específicos |
| Pesquero | D.S. 014-78-TR, D.L. 22342 | Sistema de pago por retribución |
| Hogar (Ley 31047) | Ley 31047 | RMV, CTS 15 días, gratif ½ sueldo |
| 276 Carrera Administrativa | D.Leg. 276 | URP, bonificaciones personal/familiar/diferencial, 14 niveles |
| CAS | D.Leg. 1057 + Ley 31131 | Aguinaldos en lugar de gratif, sin CTS, 30 días vac |
| Servir Ley 30057 | Ley 30057 + Reglamento | Transición desde 276/728/CAS |
| Exportación no tradicional | Ley 22342 | Contratos temporales por exportación |

Sin patrón Strategy, el código del motor de planilla se convierte en un laberinto de `if/else` insostenible.

---

## 2. Diseño del Strategy

### 2.1 Interfaz base

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class ContextoCalculo:
    tenant_id: str
    empleado_id: str
    periodo: str                    # "2026-04"
    fecha_inicio_periodo: date
    fecha_fin_periodo: date
    remuneracion_computable: Decimal
    dias_trabajados: int
    dias_no_laborados: int
    tiene_asignacion_familiar: bool
    parametros_vigentes: dict       # RMV, UIT, tasas AFP/ONP, etc.
    historial_sueldo: list          # para cálculos con promedio

@dataclass
class ConceptoCalculado:
    codigo_plame: str               # referencia a Tabla 22 SUNAT
    descripcion: str
    monto: Decimal
    es_ingreso: bool
    es_descuento: bool
    afecta_quinta: bool
    afecta_essalud: bool
    afecta_afp_onp: bool

class RegimenLaboralStrategy(ABC):
    """Contrato que todo régimen debe implementar."""
    
    @property
    @abstractmethod
    def codigo(self) -> str: ...
    
    @abstractmethod
    def calcular_remuneracion_basica(self, ctx: ContextoCalculo) -> ConceptoCalculado: ...
    
    @abstractmethod
    def calcular_asignacion_familiar(self, ctx: ContextoCalculo) -> list[ConceptoCalculado]: ...
    
    @abstractmethod
    def calcular_gratificacion(self, ctx: ContextoCalculo) -> list[ConceptoCalculado]: ...
    
    @abstractmethod
    def calcular_cts(self, ctx: ContextoCalculo) -> list[ConceptoCalculado]: ...
    
    @abstractmethod
    def calcular_vacaciones(self, ctx: ContextoCalculo) -> list[ConceptoCalculado]: ...
    
    @abstractmethod
    def calcular_aportes_salud(self, ctx: ContextoCalculo) -> list[ConceptoCalculado]: ...
    
    @abstractmethod
    def calcular_horas_extras(self, ctx: ContextoCalculo) -> list[ConceptoCalculado]: ...
    
    @abstractmethod
    def dias_vacaciones_anuales(self) -> int: ...
    
    @abstractmethod
    def jornada_maxima_diaria(self) -> int: ...
    
    @abstractmethod
    def aplica_remuneracion_minima(self) -> bool: ...
```

### 2.2 Implementación 728 General

```python
class Regimen728General(RegimenLaboralStrategy):
    codigo = "728_GENERAL"
    
    def calcular_remuneracion_basica(self, ctx):
        return ConceptoCalculado(
            codigo_plame="0100",
            descripcion="Remuneración básica",
            monto=ctx.remuneracion_computable * Decimal(ctx.dias_trabajados) / Decimal(30),
            es_ingreso=True, es_descuento=False,
            afecta_quinta=True, afecta_essalud=True, afecta_afp_onp=True
        )
    
    def calcular_asignacion_familiar(self, ctx):
        if not ctx.tiene_asignacion_familiar:
            return []
        rmv = ctx.parametros_vigentes["rmv"]
        return [ConceptoCalculado(
            codigo_plame="0110",
            descripcion="Asignación familiar",
            monto=rmv * Decimal("0.10"),
            es_ingreso=True, es_descuento=False,
            afecta_quinta=True, afecta_essalud=True, afecta_afp_onp=True
        )]
    
    def calcular_gratificacion(self, ctx):
        # Fiestas Patrias (jul) y Navidad (dic). Meses del semestre.
        mes = int(ctx.periodo.split("-")[1])
        if mes not in (7, 12):
            return []
        meses_semestre = self._meses_trabajados_semestre(ctx)
        grati = ctx.remuneracion_computable * Decimal(meses_semestre) / Decimal(6)
        bonificacion_extra = grati * Decimal("0.09")  # 9% EsSalud Ley 30334
        return [
            ConceptoCalculado("0301", "Gratificación Ley 27735", grati, True, False, True, False, False),
            ConceptoCalculado("0312", "Bonif. Extraord. Ley 29351", bonificacion_extra, True, False, True, False, False),
        ]
    
    def calcular_cts(self, ctx):
        # Depósito mayo (semestre nov-abr) y noviembre (semestre may-oct)
        mes = int(ctx.periodo.split("-")[1])
        if mes not in (5, 11):
            return []
        remu_comp = ctx.remuneracion_computable + (ctx.ultima_gratificacion / Decimal(6))
        meses = self._meses_semestre_cts(ctx)
        dias = self._dias_semestre_cts(ctx)
        cts = (remu_comp / Decimal(12) * Decimal(meses)) + (remu_comp / Decimal(360) * Decimal(dias))
        return [ConceptoCalculado("0904", "CTS", cts, False, False, False, False, False)]
    
    def dias_vacaciones_anuales(self): return 30
    def jornada_maxima_diaria(self): return 8
    def aplica_remuneracion_minima(self): return True
```

### 2.3 Implementación 276 Carrera Administrativa

```python
class Regimen276CarreraAdministrativa(RegimenLaboralStrategy):
    codigo = "276"
    
    def calcular_remuneracion_basica(self, ctx):
        # Base: URP × factor de nivel + MUC (Monto Único Consolidado DS 320-2022-EF)
        nivel_276 = ctx.datos_empleado.get("nivel_276")
        urp = ctx.parametros_vigentes["urp"]
        factor_nivel = self._obtener_factor_nivel_276(nivel_276)
        muc = ctx.parametros_vigentes["muc_276"].get(nivel_276, Decimal("0"))
        basico = (urp * factor_nivel + muc) * Decimal(ctx.dias_trabajados) / Decimal(30)
        return ConceptoCalculado(
            "2001", f"Remuneración 276 Nivel {nivel_276}",
            basico, True, False, True, True, True
        )
    
    def calcular_bonificacion_personal(self, ctx):
        """5% del haber básico por cada quinquenio de servicios."""
        años = ctx.datos_empleado.get("años_servicio", 0)
        quinquenios = años // 5
        if quinquenios == 0:
            return []
        basico = self.calcular_remuneracion_basica(ctx).monto
        monto = basico * Decimal("0.05") * Decimal(quinquenios)
        return [ConceptoCalculado("2005", f"Bonif. Personal ({quinquenios} quinq.)", monto,
                                   True, False, True, True, True)]
    
    def calcular_bonificacion_familiar(self, ctx):
        """Ley 25129 - monto fijo histórico (3 soles originalmente, puede variar)."""
        if not ctx.tiene_asignacion_familiar:
            return []
        # El monto 276 es distinto al 728 (régimen público histórico)
        return [ConceptoCalculado("2006", "Bonif. Familiar",
                                   Decimal("3.00"), True, False, True, True, True)]
    
    def calcular_bonificacion_diferencial(self, ctx):
        """Compensa cargo directivo o condiciones excepcionales. Art. 53 DLeg 276."""
        bon_dif = ctx.datos_empleado.get("bonif_diferencial_monto", Decimal("0"))
        if bon_dif == 0:
            return []
        return [ConceptoCalculado("2009", "Bonif. Diferencial", bon_dif,
                                   True, False, True, True, True)]
    
    def calcular_gratificacion(self, ctx):
        """Aguinaldos Fiestas Patrias y Navidad por DS anual (históricamente S/ 300)."""
        mes = int(ctx.periodo.split("-")[1])
        if mes not in (7, 12):
            return []
        monto_aguinaldo = ctx.parametros_vigentes["aguinaldo_276"]  # ej. 300
        return [ConceptoCalculado("2020", f"Aguinaldo {'FP' if mes == 7 else 'Nav'}",
                                   monto_aguinaldo, True, False, False, False, False)]
    
    def calcular_cts(self, ctx):
        """Se paga al cese: 100% remuneración total × año de servicio (Art. 54 c modificado Ley 32199)."""
        if not ctx.es_cese:
            return []
        años = ctx.años_servicio_completos
        fraccion = ctx.meses_adicionales / Decimal(12)
        remu_total = ctx.remuneracion_total  # incluye bonificaciones
        cts = remu_total * (Decimal(años) + fraccion)
        return [ConceptoCalculado("2030", "CTS 276", cts, False, False, False, False, False)]
    
    def dias_vacaciones_anuales(self): return 30
    def jornada_maxima_diaria(self): return 8  # usualmente 7h45 efectivas
    def aplica_remuneracion_minima(self): return True  # solo como piso
```

### 2.4 Implementación CAS

```python
class RegimenCAS(RegimenLaboralStrategy):
    codigo = "CAS"
    
    def calcular_remuneracion_basica(self, ctx):
        # La retribución CAS se pacta en el contrato, no tiene estructura salarial
        basico = ctx.remuneracion_computable * Decimal(ctx.dias_trabajados) / Decimal(30)
        return ConceptoCalculado("0100", "Retribución CAS", basico,
                                  True, False, True, True, True)
    
    def calcular_gratificacion(self, ctx):
        """Aguinaldos FP y Navidad (monto fijo por DS anual)."""
        mes = int(ctx.periodo.split("-")[1])
        if mes not in (7, 12):
            return []
        return [ConceptoCalculado("0302", "Aguinaldo CAS",
                                   ctx.parametros_vigentes["aguinaldo_cas"],
                                   True, False, False, False, False)]
    
    def calcular_cts(self, ctx):
        return []  # CAS no tiene CTS
    
    def dias_vacaciones_anuales(self): return 30
    def jornada_maxima_diaria(self): return 8
    def aplica_remuneracion_minima(self): return True
```

### 2.5 Implementación Régimen Agrario (Ley 31110) — dos sistemas

El caso más complejo porque admite dos modalidades a elección del empleador:

```python
class RegimenAgrarioLey31110(RegimenLaboralStrategy):
    codigo = "AGRARIO_31110"
    
    def __init__(self, sistema_pago: str):
        """
        sistema_pago: 'CONSOLIDADO' (RD incluye grati+CTS+vac)
                      'TRADICIONAL' (pagos separados al régimen 728)
        """
        assert sistema_pago in ("CONSOLIDADO", "TRADICIONAL")
        self.sistema_pago = sistema_pago
    
    def calcular_remuneracion_basica(self, ctx):
        if self.sistema_pago == "CONSOLIDADO":
            # Remuneración Diaria (RD) = RB + 16.66% grati + 9.72% CTS
            # RB no menor a la RMV/30
            rb = max(ctx.remuneracion_base_diaria, ctx.parametros_vigentes["rmv"] / Decimal(30))
            rd = rb + (rb * Decimal("0.1666")) + (rb * Decimal("0.0972"))
            monto = rd * Decimal(ctx.dias_trabajados)
            return ConceptoCalculado("0100", "Remuneración Diaria Agraria (consolidada)",
                                      monto, True, False, True, True, True)
        else:
            # Sistema tradicional = régimen 728 idéntico
            return Regimen728General().calcular_remuneracion_basica(ctx)
    
    def calcular_gratificacion(self, ctx):
        if self.sistema_pago == "CONSOLIDADO":
            return []  # ya incluida en RD
        return Regimen728General().calcular_gratificacion(ctx)
    
    def calcular_cts(self, ctx):
        if self.sistema_pago == "CONSOLIDADO":
            return []  # ya incluida en RD
        return Regimen728General().calcular_cts(ctx)
    
    def calcular_beta(self, ctx):
        """Bonificación Especial por Trabajo Agrario = 30% RMV."""
        return [ConceptoCalculado("0115", "BETA",
                                   ctx.parametros_vigentes["rmv"] * Decimal("0.30"),
                                   True, False, True, True, True)]
    
    def dias_vacaciones_anuales(self):
        return 30  # igual que general tras Ley 31110
```

---

## 3. Factory para resolver el Strategy

```python
class RegimenFactory:
    _registry: dict[str, type[RegimenLaboralStrategy]] = {
        "728_GENERAL": Regimen728General,
        "MYPE_MICRO": RegimenMYPEMicro,
        "MYPE_PEQUENA": RegimenMYPEPequena,
        "AGRARIO_31110": RegimenAgrarioLey31110,
        "CONSTRUCCION_CIVIL": RegimenConstruccionCivil,
        "MINERO": RegimenMinero,
        "HOGAR_31047": RegimenHogarLey31047,
        "276": Regimen276CarreraAdministrativa,
        "CAS": RegimenCAS,
        "SERVIR_30057": RegimenServirLey30057,
        # ... resto
    }
    
    @classmethod
    def obtener(cls, codigo_regimen: str, **kwargs) -> RegimenLaboralStrategy:
        if codigo_regimen not in cls._registry:
            raise ValueError(f"Régimen no soportado: {codigo_regimen}")
        return cls._registry[codigo_regimen](**kwargs)
    
    @classmethod
    def registrar(cls, codigo: str, clase: type[RegimenLaboralStrategy]):
        """Permite agregar regímenes sin tocar el core (ej. regímenes sectoriales futuros)."""
        cls._registry[codigo] = clase
```

---

## 4. Motor de planilla orquestador

```python
class MotorPlanilla:
    def __init__(self, repositorio, factory):
        self.repo = repositorio
        self.factory = factory
    
    def calcular_recibo(self, ctx: ContextoCalculo) -> list[ConceptoCalculado]:
        regimen = self.factory.obtener(
            ctx.datos_empleado["regimen"],
            **ctx.datos_empleado.get("regimen_parametros", {})
        )
        
        conceptos = []
        # Orden de cálculo importante: primero ingresos, luego descuentos basados en totales
        conceptos.append(regimen.calcular_remuneracion_basica(ctx))
        conceptos.extend(regimen.calcular_asignacion_familiar(ctx))
        conceptos.extend(regimen.calcular_gratificacion(ctx))
        conceptos.extend(regimen.calcular_horas_extras(ctx))
        conceptos.extend(regimen.calcular_vacaciones(ctx))
        
        # Aportes y descuentos basados en el bruto calculado
        bruto = sum(c.monto for c in conceptos if c.es_ingreso)
        ctx.bruto_mensual = bruto
        conceptos.extend(regimen.calcular_aportes_salud(ctx))
        conceptos.extend(self._calcular_aportes_pensionarios(ctx))
        conceptos.extend(self._calcular_renta_5ta(ctx))
        conceptos.extend(self._calcular_descuentos_adicionales(ctx))
        
        return conceptos
```

---

## 5. Testing — tabla de verificación por régimen

Cada régimen tiene un test de golden master con valores verificados por la consultora laboral:

```python
@pytest.mark.parametrize("regimen,escenario,esperado", [
    ("728_GENERAL", "basico_1500_afp_con_af", {"neto": Decimal("1382.50"), ...}),
    ("MYPE_MICRO", "basico_rmv_sin_af", {"neto": Decimal("1130.00"), "cts": 0, "grati": 0}),
    ("AGRARIO_31110_CONS", "rd_50_dias_trabajados", {"rd_total": ..., "beta": ...}),
    ("276", "profesional_nivel_sps_5_quinquenios", {"basico": ..., "bonif_personal": ...}),
    ("CAS", "retribucion_2500_aguinaldo_julio", {"bruto": ..., "aguinaldo": Decimal("300")}),
])
def test_calculo_por_regimen(regimen, escenario, esperado):
    ctx = cargar_escenario(escenario)
    conceptos = motor.calcular_recibo(ctx)
    verificar(conceptos, esperado)
```

---

## 6. Evolución a regímenes futuros

La reforma pensional Ley 32123, la futura reforma del régimen agrario, o la transición Servir 30057 introducirán cambios. El patrón Strategy los absorbe con:

1. Nueva clase `RegimenXYZ` que herede de `RegimenLaboralStrategy`.
2. Registrarla en el factory.
3. Migrar empleados del régimen antiguo al nuevo con eventos `EmployeeRegimenChanged` en el event store.
4. El motor automáticamente usa la nueva estrategia desde la fecha efectiva.

---

## 7. Checklist

- [ ] Interfaz `RegimenLaboralStrategy` con todos los métodos necesarios
- [ ] Al menos 7 regímenes implementados para MVP: 728, MYPE Pequeña, CAS, 276, Agrario, Construcción Civil, Hogar
- [ ] Factory configurable por tenant vía tabla `regimenes_activos`
- [ ] Tests de golden master con valores verificados
- [ ] Documentación por régimen con referencia normativa
- [ ] Parámetros vigentes (RMV, UIT, URP, etc.) cargados desde `parametros_vigentes` por fecha
- [ ] Cambio de régimen de un empleado registrado como evento
