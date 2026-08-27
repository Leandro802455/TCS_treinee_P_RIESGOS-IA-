from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Literal, TypedDict


Severity = Literal["BAJA", "MEDIA", "ALTA", "CRÍTICA"]


class Alert(TypedDict):
    indicador: str
    valor: float
    umbral: float
    severidad: Severity
    descripcion: str
    recomendacion: str


@dataclass(frozen=True)
class AlertRule:
    """Regla configurable para un indicador financiero."""

    indicator: str
    threshold: float
    severity: Severity
    description: str
    recommendation: str
    comparator: Callable[[float, float], bool]


def _greater_than(value: float, threshold: float) -> bool:
    return value > threshold


def _less_than(value: float, threshold: float) -> bool:
    return value < threshold


# Se evalúan en orden de severidad: la primera regla activada gana.
DEFAULT_ALERT_RULES: tuple[AlertRule, ...] = (
    AlertRule("endeudamiento", 0.85, "CRÍTICA", "Endeudamiento crítico: más del 85% de los activos se financia con deuda.", "Reestructurar deuda y limitar nuevo financiamiento.", _greater_than),
    AlertRule("endeudamiento", 0.70, "ALTA", "Endeudamiento alto: los pasivos superan el 70% de los activos.", "Reducir deuda y revisar la estructura de capital.", _greater_than),
    AlertRule("endeudamiento", 0.50, "MEDIA", "Endeudamiento moderado-alto: más de la mitad de los activos se financia con deuda.", "Monitorear el apalancamiento y el calendario de pagos.", _greater_than),
    AlertRule("endeudamiento", 0.40, "BAJA", "Endeudamiento con señal preventiva, superior al 40%.", "Mantener control periódico del apalancamiento.", _greater_than),
    AlertRule("liquidez_corriente", 0.80, "CRÍTICA", "Liquidez corriente crítica para cubrir obligaciones de corto plazo.", "Priorizar caja y renegociar vencimientos inmediatos.", _less_than),
    AlertRule("liquidez_corriente", 1.00, "ALTA", "Liquidez corriente insuficiente para cubrir obligaciones de corto plazo.", "Fortalecer capital de trabajo y controlar pagos.", _less_than),
    AlertRule("liquidez_corriente", 1.50, "MEDIA", "Liquidez corriente ajustada.", "Dar seguimiento al capital de trabajo.", _less_than),
    AlertRule("liquidez_corriente", 2.00, "BAJA", "Liquidez corriente con señal preventiva.", "Mantener una reserva de liquidez adecuada.", _less_than),
    AlertRule("prueba_acida", 0.50, "CRÍTICA", "Prueba ácida crítica: la empresa depende fuertemente de vender inventarios.", "Acelerar cobros y reducir obligaciones de corto plazo.", _less_than),
    AlertRule("prueba_acida", 0.70, "ALTA", "Prueba ácida baja y capacidad limitada de pago inmediato.", "Mejorar caja y rotación de cuentas por cobrar.", _less_than),
    AlertRule("prueba_acida", 1.00, "MEDIA", "Prueba ácida ajustada.", "Vigilar la dependencia de inventarios para pagar deudas.", _less_than),
    AlertRule("prueba_acida", 1.20, "BAJA", "Prueba ácida con señal preventiva.", "Conservar políticas prudentes de liquidez.", _less_than),
    AlertRule("solvencia", 1.00, "CRÍTICA", "Solvencia crítica: los activos no cubren las obligaciones.", "Revisar urgentemente la estructura financiera.", _less_than),
    AlertRule("solvencia", 1.50, "ALTA", "Solvencia baja frente al total de obligaciones.", "Fortalecer patrimonio y reducir pasivos.", _less_than),
    AlertRule("solvencia", 2.00, "MEDIA", "Solvencia ajustada.", "Controlar el crecimiento de las obligaciones.", _less_than),
    AlertRule("solvencia", 2.50, "BAJA", "Solvencia con señal preventiva.", "Mantener seguimiento de la cobertura de deuda.", _less_than),
    AlertRule("margen_neto", 0.00, "CRÍTICA", "Margen neto negativo o nulo.", "Revisar costos, precios y fuentes de pérdida.", _less_than),
    AlertRule("margen_neto", 0.03, "ALTA", "Margen neto muy bajo, inferior al 3%.", "Implementar medidas para recuperar rentabilidad.", _less_than),
    AlertRule("margen_neto", 0.05, "MEDIA", "Margen neto bajo, inferior al 5%.", "Controlar gastos y mejorar el margen operativo.", _less_than),
    AlertRule("margen_neto", 0.10, "BAJA", "Margen neto con señal preventiva, inferior al 10%.", "Monitorear la rentabilidad por periodo.", _less_than),
    AlertRule("roa", 0.00, "CRÍTICA", "ROA negativo o nulo.", "Revisar el rendimiento y uso de los activos.", _less_than),
    AlertRule("roa", 0.03, "ALTA", "ROA muy bajo, inferior al 3%.", "Mejorar la productividad de los activos.", _less_than),
    AlertRule("roa", 0.05, "MEDIA", "ROA bajo, inferior al 5%.", "Analizar activos improductivos y costos.", _less_than),
    AlertRule("roa", 0.10, "BAJA", "ROA con señal preventiva, inferior al 10%.", "Dar seguimiento al retorno de los activos.", _less_than),
    AlertRule("roe", 0.00, "CRÍTICA", "ROE negativo o nulo.", "Revisar la generación de valor para los accionistas.", _less_than),
    AlertRule("roe", 0.05, "ALTA", "ROE muy bajo, inferior al 5%.", "Recuperar rentabilidad sobre el patrimonio.", _less_than),
    AlertRule("roe", 0.08, "MEDIA", "ROE bajo, inferior al 8%.", "Evaluar la eficiencia del capital propio.", _less_than),
    AlertRule("roe", 0.15, "BAJA", "ROE con señal preventiva, inferior al 15%.", "Monitorear el retorno para los accionistas.", _less_than),
    AlertRule("variacion_ingresos", -0.20, "CRÍTICA", "Caída crítica de ingresos superior al 20% frente al periodo anterior.", "Investigar la caída y ajustar el plan financiero.", _less_than),
    AlertRule("variacion_ingresos", -0.10, "ALTA", "Caída significativa de ingresos frente al periodo anterior.", "Analizar causas comerciales y proteger el flujo de caja.", _less_than),
    AlertRule("variacion_ingresos", 0.00, "MEDIA", "Los ingresos disminuyeron frente al periodo anterior.", "Dar seguimiento a ventas y márgenes.", _less_than),
    AlertRule("contingencias", 0.10, "ALTA", "Contingencias relevantes frente al total de activos.", "Cuantificar escenarios y revisar coberturas y provisiones.", _greater_than),
    AlertRule("contingencias", 0.00, "MEDIA", "Existen contingencias o provisiones registradas.", "Monitorear su evolución y probabilidad de materialización.", _greater_than),
)


def detect_alerts(
    indicators: Mapping[str, Mapping[str, object]],
    rules: tuple[AlertRule, ...] = DEFAULT_ALERT_RULES,
) -> list[Alert]:
    """Evalúa indicadores contra reglas configurables y devuelve alertas explicables."""
    alerts: list[Alert] = []
    evaluated: set[str] = set()
    for rule in rules:
        if rule.indicator in evaluated:
            continue
        value = indicators.get(rule.indicator, {}).get("valor")
        if isinstance(value, (int, float)) and rule.comparator(float(value), rule.threshold):
            alerts.append({
                "indicador": rule.indicator,
                "valor": float(value),
                "umbral": rule.threshold,
                "severidad": rule.severity,
                "descripcion": rule.description,
                "recomendacion": rule.recommendation,
            })
            evaluated.add(rule.indicator)
    return alerts
