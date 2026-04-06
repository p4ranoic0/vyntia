from app_rrhh.services.planilla_calculo_service import PlanillaCalculoService
from app_rrhh.models import DetallePlanilla, PlanillaMensual
import traceback

try:
    service = PlanillaCalculoService()
    result = service.calcular_planilla(3)
    print("Resultado del calculo:")
    print("  Success:", result.get("success", "N/A"))
    print("  Message:", result.get("message", "N/A"))
    if "error" in result:
        print("  Error:", result["error"])
    if "data" in result:
        for k, v in result["data"].items():
            print(f"  {k}: {v}")
except Exception as e:
    print("Exception:", e)
    traceback.print_exc()

print()
print("=== Detalle values after calculation ===")
planilla = PlanillaMensual.objects.get(planilla_id=3)
print("Planilla estado:", planilla.estado)
print("Planilla total_haberes:", planilla.total_haberes)
print("Planilla total_descuentos:", planilla.total_descuentos)
print("Planilla total_neto:", planilla.total_neto)

for d in DetallePlanilla.objects.filter(planilla=planilla):
    print()
    print(f"--- {d.empleado.nombres_empleado} {d.empleado.apellido_paterno} ---")
    print(f"  Rem Basica:    S/ {d.remuneracion_basica}")
    print(f"  Asig Familiar: S/ {d.asignacion_familiar}")
    print(f"  Total Haberes: S/ {d.total_haberes}")
    print(f"  Sist Pension:  {d.sistema_pensiones}")
    print(f"  Tipo Comision: {d.tipo_comision_afp}")
    print(f"  AFP Obligat:   S/ {d.aporte_afp_obligatorio}")
    print(f"  Comision AFP:  S/ {d.comision_afp}")
    print(f"  Prima Seguro:  S/ {d.prima_seguro_afp}")
    print(f"  Total AFP:     S/ {d.total_afp}")
    print(f"  Aporte ONP:    S/ {d.aporte_onp}")
    print(f"  ESSALUD:       S/ {d.essalud}")
    print(f"  Renta 5ta:     S/ {d.renta_quinta_categoria}")
    print(f"  Total Desc:    S/ {d.total_descuentos}")
    print(f"  Neto Pagar:    S/ {d.neto_pagar}")
