from backend.agent.indicadores import calculate_indicators


def test_calculates_required_indicators_with_metadata():
    indicators = calculate_indicators(
        {
            "activos_corrientes": 600,
            "pasivos_corrientes": 300,
            "inventarios": 100,
            "activos": 1000,
            "pasivos": 600,
            "patrimonio": 400,
            "ingresos": 500,
            "utilidad_neta": 50,
        }
    )

    assert set(indicators) == {
        "liquidez_corriente", "prueba_acida", "endeudamiento", "solvencia",
        "margen_neto", "roa", "roe", "variacion_ingresos", "contingencias",
    }
    assert indicators["liquidez_corriente"]["valor"] == 2.0
    assert indicators["prueba_acida"]["valor"] == 1.6667
    assert indicators["endeudamiento"]["valor"] == 0.6
    assert indicators["solvencia"]["valor"] == 1.6667
    assert indicators["margen_neto"]["valor"] == 0.1
    assert indicators["roa"]["valor"] == 0.05
    assert indicators["roe"]["valor"] == 0.125
    assert all(set(item) == {"nombre", "formula", "valor", "interpretacion", "nivel_riesgo"} for item in indicators.values())


def test_missing_data_is_not_treated_as_zero():
    indicators = calculate_indicators({"activos": 1000, "pasivos": 500})

    assert indicators["liquidez_corriente"]["valor"] is None
    assert indicators["liquidez_corriente"]["nivel_riesgo"] == "no evaluable"
    assert indicators["endeudamiento"]["valor"] == 0.5
    assert indicators["margen_neto"]["valor"] is None


def test_zero_denominator_is_safe():
    indicators = calculate_indicators(
        {"activos_corrientes": 100, "pasivos_corrientes": 0, "activos": 0, "pasivos": 0, "ingresos": 0, "patrimonio": 0}
    )

    assert all(item["valor"] is None for item in indicators.values())
    assert all(item["nivel_riesgo"] == "no evaluable" for item in indicators.values())


def test_variation_and_contingencies_are_calculated_when_available():
    indicators = calculate_indicators({
        "ingresos": 800,
        "ingresos_periodo_anterior": 1000,
        "contingencias": 100,
        "activos": 1000,
    })

    assert indicators["variacion_ingresos"]["valor"] == -0.2
    assert indicators["contingencias"]["valor"] == 0.1
