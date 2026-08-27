from backend.agent.alertas import AlertRule, detect_alerts


def test_alert_contains_required_fields_and_severity():
    alerts = detect_alerts({"endeudamiento": {"valor": 0.8}})

    assert len(alerts) == 1
    assert set(alerts[0]) == {
        "indicador", "valor", "umbral", "severidad", "descripcion", "recomendacion",
    }
    assert alerts[0]["indicador"] == "endeudamiento"
    assert alerts[0]["severidad"] == "ALTA"
    assert alerts[0]["umbral"] == 0.70


def test_rules_return_the_most_severe_matching_alert_per_indicator():
    values = {
        "endeudamiento": {"valor": 0.9},
        "liquidez_corriente": {"valor": 0.6},
        "prueba_acida": {"valor": 0.6},
        "solvencia": {"valor": 0.8},
        "margen_neto": {"valor": 0.01},
        "roa": {"valor": 0.01},
        "roe": {"valor": 0.01},
    }
    alerts = detect_alerts(values)

    assert {alert["severidad"] for alert in alerts} == {"CRÍTICA", "ALTA"}
    assert len(alerts) == len(values)


def test_missing_values_do_not_create_alerts():
    assert detect_alerts({"endeudamiento": {"valor": None}, "roa": {}}) == []


def test_rules_are_configurable():
    custom_rule = AlertRule(
        "endeudamiento", 0.30, "MEDIA", "Regla personalizada", "Revisar deuda", lambda value, threshold: value > threshold
    )

    alerts = detect_alerts({"endeudamiento": {"valor": 0.4}}, rules=(custom_rule,))

    assert alerts[0]["umbral"] == 0.30
    assert alerts[0]["descripcion"] == "Regla personalizada"


def test_no_alerts_for_healthy_metrics():
    assert detect_alerts({
        "endeudamiento": {"valor": 0.3},
        "liquidez_corriente": {"valor": 2.1},
        "prueba_acida": {"valor": 1.3},
        "solvencia": {"valor": 3.0},
        "margen_neto": {"valor": 0.2},
        "roa": {"valor": 0.15},
        "roe": {"valor": 0.2},
    }) == []
