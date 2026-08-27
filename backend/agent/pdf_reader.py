from pathlib import Path
import re

import pymupdf


FINANCIAL_FIELDS = {
    "activos": r"activos\s*(?:totales)?\s*[:=]\s*([\d.,]+)",
    "activos_corrientes": r"activos\s+corrientes?\s*[:=]\s*([\d.,]+)",
    "pasivos": r"pasivos\s*(?:totales)?\s*[:=]\s*([\d.,]+)",
    "pasivos_corrientes": r"pasivos\s+corrientes?\s*[:=]\s*([\d.,]+)",
    "inventarios": r"inventarios?\s*[:=]\s*([\d.,]+)",
    "patrimonio": r"patrimonio\s*[:=]\s*([\d.,]+)",
    "ingresos": r"ingresos\s*(?:totales)?\s*[:=]\s*([\d.,]+)",
    "ingresos_periodo_anterior": r"ingresos\s+(?:del\s+)?(?:periodo|año)\s+anterior\s*[:=]\s*([\d.,]+)",
    "activos_periodo_anterior": r"activos\s+(?:del\s+)?(?:periodo|año)\s+anterior\s*[:=]\s*([\d.,]+)",
    "pasivos_periodo_anterior": r"pasivos\s+(?:del\s+)?(?:periodo|año)\s+anterior\s*[:=]\s*([\d.,]+)",
    "utilidad_neta": r"utilidad\s+neta\s*[:=]\s*([\d.,]+)",
    "efectivo": r"efectivo\s*[:=]\s*([\d.,]+)",
    "cuentas_por_cobrar": r"cuentas\s+por\s+cobrar\s*[:=]\s*([\d.,]+)",
    "deuda_corto_plazo": r"deuda\s+(?:de corto plazo|corto plazo)\s*[:=]\s*([\d.,]+)",
    "contingencias": r"contingencias?\s*[:=]\s*([\d.,]+)",
    "provisiones": r"provisiones?\s*[:=]\s*([\d.,]+)",
}


def extract_text(pdf_path: str | Path) -> str:
    """Extrae texto de todas las páginas de un PDF."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el PDF: {path}")
    with pymupdf.open(path) as document:
        return "\n".join(page.get_text() for page in document)


def _parse_amount(value: str) -> float:
    """Acepta formatos simples como 1.234,56 y 1234.56."""
    value = value.strip().replace(" ", "")
    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        value = value.replace(",", ".")
    return float(value)


def extract_financial_data(text: str) -> dict[str, float]:
    """Obtiene las variables financieras etiquetadas en el texto extraído."""
    data: dict[str, float] = {}
    normalized = " ".join(text.lower().split())
    for field, pattern in FINANCIAL_FIELDS.items():
        match = re.search(pattern, normalized)
        if match:
            data[field] = _parse_amount(match.group(1))
    return data
