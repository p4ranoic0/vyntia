"""Servicio para procesar archivos Excel de descuentos masivos."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Tuple

from django.db import transaction
from django.utils import timezone

try:
    from openpyxl import load_workbook
    from openpyxl.utils.exceptions import InvalidFileException

    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

from apps.payroll.models import (
    ConceptoPlanilla,
    ConfiguracionRemuneracion,
    DescuentoMasivo,
    DetallePlanilla,
)
from apps.employees.models import Empleado


class DescuentoMasivoService:
    """Servicio para procesar descuentos masivos desde archivos Excel."""

    # Columnas esperadas en el Excel
    COLUMNAS_REQUERIDAS = ["dni", "monto"]
    COLUMNAS_OPCIONALES = ["observacion", "cuotas"]

    def __init__(self):
        if not OPENPYXL_AVAILABLE:
            raise ImportError(
                "openpyxl no está instalado. Ejecuta: pip install openpyxl"
            )

    def procesar_descuento_masivo(self, descuento_masivo_id: int) -> Dict[str, Any]:
        """
        Procesa un descuento masivo cargado.

        Args:
            descuento_masivo_id: ID del descuento masivo

        Returns:
            Diccionario con resultados del procesamiento
        """
        descuento = DescuentoMasivo.objects.select_related(
            "configuracion_concepto"
        ).get(descuento_masivo_id=descuento_masivo_id)

        if descuento.estado != "pendiente":
            raise ValueError(
                f"El descuento masivo ya fue procesado (estado: {descuento.estado})"
            )

        try:
            # Leer y validar archivo Excel
            registros, errores = self._leer_archivo_excel(descuento.archivo_origen.path)

            if not registros and errores:
                descuento.estado = "procesado"
                descuento.errores_log = "\n".join(errores)
                descuento.total_registros = 0
                descuento.registros_error = len(errores)
                descuento.fecha_procesado = timezone.now()
                descuento.save()
                return {
                    "success": False,
                    "message": "No se pudieron leer registros del archivo",
                    "errores": errores,
                }

            # Procesar cada registro
            resultado = self._aplicar_descuentos(descuento, registros)

            # Actualizar estado del descuento masivo
            with transaction.atomic():
                descuento.total_registros = len(registros)
                descuento.registros_procesados = resultado["procesados"]
                descuento.registros_error = resultado["errores_count"]
                descuento.monto_total = resultado["monto_total"]
                descuento.errores_log = (
                    "\n".join(resultado["errores"]) if resultado["errores"] else None
                )
                descuento.estado = "procesado"
                descuento.fecha_procesado = timezone.now()
                descuento.save()

            return {
                "success": True,
                "message": f"Procesados {resultado['procesados']} de {len(registros)} registros",
                "total_registros": len(registros),
                "registros_procesados": resultado["procesados"],
                "registros_error": resultado["errores_count"],
                "monto_total": str(resultado["monto_total"]),
                "errores": resultado["errores"],
            }

        except Exception as e:
            descuento.estado = "procesado"
            descuento.errores_log = f"Error al procesar: {str(e)}"
            descuento.fecha_procesado = timezone.now()
            descuento.save()
            raise

    def _leer_archivo_excel(
        self, archivo_path: str
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Lee el archivo Excel y extrae los datos.

        Formato esperado:
        - Fila 1: Encabezados (DNI, MONTO, OBSERVACION, CUOTAS)
        - Filas siguientes: Datos

        Returns:
            Tupla de (lista de registros, lista de errores)
        """
        registros = []
        errores = []

        try:
            wb = load_workbook(archivo_path, read_only=True, data_only=True)
            ws = wb.active

            # Leer encabezados de la primera fila
            headers = []
            for cell in ws[1]:
                if cell.value:
                    headers.append(str(cell.value).lower().strip())

            # Validar columnas requeridas
            if "dni" not in headers:
                errores.append("Columna 'DNI' no encontrada en el archivo")
                return [], errores

            if "monto" not in headers:
                errores.append("Columna 'MONTO' no encontrada en el archivo")
                return [], errores

            # Mapear índices de columnas
            col_dni = headers.index("dni")
            col_monto = headers.index("monto")
            col_observacion = (
                headers.index("observacion") if "observacion" in headers else None
            )
            col_cuotas = headers.index("cuotas") if "cuotas" in headers else None

            # Leer datos (desde fila 2)
            for idx, row in enumerate(
                ws.iter_rows(min_row=2, values_only=True), start=2
            ):
                if not row or not any(row):  # Fila vacía
                    continue

                try:
                    dni = str(row[col_dni]).strip() if row[col_dni] else None
                    monto = row[col_monto]

                    if not dni:
                        errores.append(f"Fila {idx}: DNI vacío")
                        continue

                    if not monto:
                        errores.append(f"Fila {idx}: Monto vacío para DNI {dni}")
                        continue

                    # Convertir monto a Decimal
                    try:
                        monto_decimal = Decimal(str(monto))
                        if monto_decimal <= 0:
                            errores.append(
                                f"Fila {idx}: Monto debe ser mayor a 0 para DNI {dni}"
                            )
                            continue
                    except (ValueError, TypeError):
                        errores.append(
                            f"Fila {idx}: Monto inválido '{monto}' para DNI {dni}"
                        )
                        continue

                    registro = {
                        "dni": dni,
                        "monto": monto_decimal,
                        "observacion": (
                            str(row[col_observacion])
                            if col_observacion and row[col_observacion]
                            else None
                        ),
                        "cuotas": (
                            int(row[col_cuotas])
                            if col_cuotas and row[col_cuotas]
                            else 1
                        ),
                        "fila": idx,
                    }

                    registros.append(registro)

                except Exception as e:
                    errores.append(f"Fila {idx}: Error al procesar - {str(e)}")
                    continue

            wb.close()

        except InvalidFileException:
            errores.append("El archivo no es un Excel válido")
        except FileNotFoundError:
            errores.append("Archivo no encontrado")
        except Exception as e:
            errores.append(f"Error al leer archivo: {str(e)}")

        return registros, errores

    def _aplicar_descuentos(
        self, descuento_masivo: DescuentoMasivo, registros: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aplica los descuentos a los detalles de planilla correspondientes.

        Args:
            descuento_masivo: Instancia de DescuentoMasivo
            registros: Lista de registros leídos del Excel

        Returns:
            Diccionario con estadísticas del procesamiento
        """
        procesados = 0
        errores = []
        monto_total = Decimal("0.00")

        # Obtener periodo de la planilla (si aplica)
        periodo = descuento_masivo.periodo

        for registro in registros:
            try:
                dni = registro["dni"]
                monto = registro["monto"]
                observacion = registro.get("observacion")
                cuotas = registro.get("cuotas", 1)
                fila = registro.get("fila", "?")

                # Buscar empleado por DNI
                try:
                    empleado = Empleado.objects.get(numero_documento=dni)
                except Empleado.DoesNotExist:
                    errores.append(f"Fila {fila}: Empleado con DNI {dni} no encontrado")
                    continue

                # Buscar detalle de planilla del empleado para el periodo
                detalles = DetallePlanilla.objects.filter(
                    planilla__periodo=periodo, empleado=empleado
                )

                if not detalles.exists():
                    errores.append(
                        f"Fila {fila}: No hay planilla para empleado {dni} en periodo {periodo}"
                    )
                    continue

                # Si hay múltiples planillas (por modalidad), tomar la primera activa
                detalle = detalles.first()

                # Crear ConceptoPlanilla para el descuento
                with transaction.atomic():
                    concepto = ConceptoPlanilla.objects.create(
                        detalle_planilla=detalle,
                        configuracion_concepto=descuento_masivo.configuracion_concepto,
                        tipo="descuento",
                        codigo=descuento_masivo.configuracion_concepto.codigo,
                        nombre=descuento_masivo.configuracion_concepto.nombre,
                        monto=monto,
                        observaciones=f"{observacion or ''} [Descuento masivo ID: {descuento_masivo.descuento_masivo_id}]".strip(),
                    )

                    # Actualizar totales del detalle
                    detalle.otros_descuentos += monto
                    detalle.total_descuentos += monto
                    detalle.neto_pagar = (
                        detalle.total_haberes - detalle.total_descuentos
                    )
                    detalle.save()

                procesados += 1
                monto_total += monto

            except Exception as e:
                errores.append(
                    f"Fila {registro.get('fila', '?')}: Error al aplicar descuento - {str(e)}"
                )
                continue

        return {
            "procesados": procesados,
            "errores_count": len(errores),
            "monto_total": monto_total,
            "errores": errores,
        }

    def anular_descuento_masivo(self, descuento_masivo_id: int) -> Dict[str, Any]:
        """
        Anula un descuento masivo y revierte los conceptos aplicados.

        Args:
            descuento_masivo_id: ID del descuento masivo

        Returns:
            Diccionario con resultado de la anulación
        """
        descuento = DescuentoMasivo.objects.get(descuento_masivo_id=descuento_masivo_id)

        if descuento.estado == "anulado":
            raise ValueError("El descuento masivo ya está anulado")

        try:
            with transaction.atomic():
                # Obtener conceptos asociados por observaciones (incluye ID del descuento)
                conceptos = ConceptoPlanilla.objects.filter(
                    observaciones__contains=f"[Descuento masivo ID: {descuento.descuento_masivo_id}]"
                ).select_related("detalle_planilla")

                conceptos_eliminados = 0
                for concepto in conceptos:
                    detalle = concepto.detalle_planilla

                    # Revertir montos del detalle
                    detalle.otros_descuentos -= concepto.monto
                    detalle.total_descuentos -= concepto.monto
                    detalle.neto_pagar = (
                        detalle.total_haberes - detalle.total_descuentos
                    )
                    detalle.save()

                    # Eliminar concepto
                    concepto.delete()
                    conceptos_eliminados += 1

                # Marcar descuento como anulado
                descuento.estado = "anulado"
                descuento.save()

            return {
                "success": True,
                "message": f"Descuento masivo anulado. Se eliminaron {conceptos_eliminados} conceptos",
                "conceptos_eliminados": conceptos_eliminados,
            }

        except Exception as e:
            raise Exception(f"Error al anular descuento masivo: {str(e)}")
