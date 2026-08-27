from collections.abc import Mapping
from typing import TypedDict


class Indicator(TypedDict):
    nombre: str
    formula: str
    valor: float | None
    interpretacion: str
    nivel_riesgo: str


def _value(data: Mapping[str, float], *names: str) -> float | None:
    for name in names:
        value = data.get(name)
        if value is not None:
            return float(value)
    return None


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(numerator / denominator, 4)


def _indicator(
    name: str,
    formula: str,
    value: float | None,
    interpretation: str,
    risk: str,
) -> Indicator:
    return {
        "nombre": name,
        "formula": formula,
        "valor": value,
        "interpretacion": interpretation,
        "nivel_riesgo": risk,
    }


def calculate_indicators(data: Mapping[str, float]) -> dict[str, Indicator]:
    """Calcula siete indicadores y devuelve una ficha explicable para cada uno."""
    current_assets = _value(data, "activos_corrientes", "activo_corriente")
    current_liabilities = _value(data, "pasivos_corrientes", "pasivo_corriente")
    inventory = _value(data, "inventarios", "inventario")
    assets = _value(data, "activos")
    liabilities = _value(data, "pasivos")
    equity = _value(data, "patrimonio")
    revenue = _value(data, "ingresos")
    net_income = _value(data, "utilidad_neta")
    previous_revenue = _value(data, "ingresos_periodo_anterior")
    contingencies = _value(data, "contingencias", "provisiones")

    current_ratio = _ratio(current_assets, current_liabilities)
    acid_ratio = _ratio(
        current_assets - inventory if current_assets is not None and inventory is not None else None,
        current_liabilities,
    )
    debt_ratio = _ratio(liabilities, assets)
    solvency_ratio = _ratio(assets, liabilities)
    net_margin = _ratio(net_income, revenue)
    roa = _ratio(net_income, assets)
    roe = _ratio(net_income, equity)
    revenue_variation = _ratio(
        revenue - previous_revenue if revenue is not None and previous_revenue is not None else None,
        previous_revenue,
    )
    contingency_ratio = _ratio(contingencies, assets)

    return {
        "liquidez_corriente": _indicator(
            "Liquidez corriente", "Activos corrientes / Pasivos corrientes", current_ratio,
            "Capacidad de cubrir obligaciones de corto plazo.",
            "no evaluable" if current_ratio is None else "bajo" if current_ratio >= 1.5 else "medio" if current_ratio >= 1 else "alto",
        ),
        "prueba_acida": _indicator(
            "Prueba ácida", "(Activos corrientes - Inventarios) / Pasivos corrientes", acid_ratio,
            "Capacidad de pago corriente sin depender de vender inventarios.",
            "no evaluable" if acid_ratio is None else "bajo" if acid_ratio >= 1 else "medio" if acid_ratio >= 0.7 else "alto",
        ),
        "endeudamiento": _indicator(
            "Endeudamiento", "Pasivos / Activos", debt_ratio,
            "Proporción de los activos financiada con deuda.",
            "no evaluable" if debt_ratio is None else "bajo" if debt_ratio <= 0.5 else "medio" if debt_ratio <= 0.7 else "alto",
        ),
        "solvencia": _indicator(
            "Ratio de solvencia", "Activos / Pasivos", solvency_ratio,
            "Cobertura total de las obligaciones con los activos.",
            "no evaluable" if solvency_ratio is None else "bajo" if solvency_ratio >= 2 else "medio" if solvency_ratio >= 1.5 else "alto",
        ),
        "margen_neto": _indicator(
            "Margen neto", "Utilidad neta / Ingresos", net_margin,
            "Porcentaje de ingresos que se convierte en utilidad neta.",
            "no evaluable" if net_margin is None else "bajo" if net_margin >= 0.1 else "medio" if net_margin >= 0.05 else "alto",
        ),
        "roa": _indicator(
            "ROA", "Utilidad neta / Activos", roa,
            "Rentabilidad generada por el total de activos.",
            "no evaluable" if roa is None else "bajo" if roa >= 0.1 else "medio" if roa >= 0.05 else "alto",
        ),
        "roe": _indicator(
            "ROE", "Utilidad neta / Patrimonio", roe,
            "Rentabilidad obtenida sobre el capital propio.",
            "no evaluable" if roe is None else "bajo" if roe >= 0.15 else "medio" if roe >= 0.08 else "alto",
        ),
        "variacion_ingresos": _indicator(
            "Variación de ingresos", "(Ingresos actuales - Ingresos periodo anterior) / Ingresos periodo anterior", revenue_variation,
            "Cambio porcentual de los ingresos frente al periodo anterior.",
            "no evaluable" if revenue_variation is None else "alto" if revenue_variation < -0.10 else "medio" if revenue_variation < 0 else "bajo",
        ),
        "contingencias": _indicator(
            "Contingencias", "Contingencias / Activos", contingency_ratio,
            "Peso relativo de contingencias o provisiones frente a los activos.",
            "no evaluable" if contingency_ratio is None else "alto" if contingency_ratio >= 0.10 else "medio" if contingency_ratio > 0 else "bajo",
        ),
    }
