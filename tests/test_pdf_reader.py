from pathlib import Path

import pytest

from backend.agent.pdf_reader import extract_financial_data, extract_text


SAMPLE_PDF = Path("data/ejemplo_financiero.pdf")


def test_extracts_synthetic_pdf_text_and_financial_values():
    text = extract_text(SAMPLE_PDF)
    data = extract_financial_data(text)

    assert text
    assert data["activos"] == 100000
    assert data["pasivos"] == 70000
    assert data["utilidad_neta"] == 3000


def test_extracts_prior_period_and_contingency_fields():
    data = extract_financial_data(
        "Activos: 1000 Ingresos: 800 Ingresos periodo anterior: 1000 "
        "Contingencias: 100 Pasivos: 500"
    )

    assert data["ingresos_periodo_anterior"] == 1000
    assert data["contingencias"] == 100


def test_invalid_pdf_raises_an_error(tmp_path):
    invalid_pdf = tmp_path / "invalid.pdf"
    invalid_pdf.write_bytes(b"not a PDF")

    with pytest.raises(Exception):
        extract_text(invalid_pdf)
