import json
import os

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(
    page_title="Agente de Riesgo Financiero",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

LOGO_URL = "https://www.datocms-assets.com/2885/1618591052-tcs-logo-colour-rgb.png"
API_URL = os.getenv("API_URL", "http://localhost:8001")

MODE_LABELS = {
    "⚡ Rápido": "rapido",
    "⚖️ Equilibrado": "equilibrado",
    "🧠 Razonamiento avanzado": "avanzado",
}
MODE_DETAILS = {
    "rapido": ("Rápido", "GPT-OSS 20B", "Consultas simples y ágiles"),
    "equilibrado": ("Equilibrado", "GPT-OSS 120B", "Balance entre velocidad y profundidad"),
    "avanzado": ("Avanzado", "GPT-OSS 120B", "Mayor razonamiento para consultas complejas"),
}
RISK_STYLES = {
    "BAJO": ("low", "BAJO", "Riesgo controlado"),
    "MEDIO": ("medium", "MEDIO", "Requiere seguimiento"),
    "ALTO": ("high", "ALTO", "Requiere atención"),
    "CRÍTICO": ("critical", "CRÍTICO", "Acción prioritaria"),
}


st.markdown(
    """
    <style>
    :root {
        --navy: #0F2A5C;
        --blue: #2E6FF2;
        --ink: #17233B;
        --muted: #6B7280;
        --light: #F4F6FA;
        --line: #E3E8F2;
        --white: #FFFFFF;
    }
    .stApp { background: #F7F9FC; color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { background: var(--navy); border-right: 0; }
    [data-testid="stSidebar"] > div:first-child { padding: 1.5rem 1.15rem; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    /* Keep text readable inside the light Streamlit controls. */
    [data-testid="stSidebar"] [data-testid="stFileUploaderFile"] { background: #FFFFFF !important; border: 1px solid #C9D5EA !important; border-radius: 9px !important; }
    [data-testid="stSidebar"] [data-testid="stFileUploaderFile"] * { color: var(--navy) !important; }
    [data-testid="stSidebar"] [data-testid="stFileUploaderFileName"] { color: var(--navy) !important; font-weight: 700 !important; }
    [data-testid="stSidebar"] [data-testid="stFileUploaderFileData"] { color: var(--muted) !important; }
    [data-testid="stSidebar"] [data-baseweb="select"] > div { background: #FFFFFF !important; border: 2px solid #B9C9E4 !important; border-radius: 9px !important; min-height: 2.6rem; }
    [data-testid="stSidebar"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] *,
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] input { color: var(--navy) !important; }
    [data-testid="stSidebar"] [data-baseweb="select"]:focus-within > div { border-color: #8FB3FF !important; box-shadow: 0 0 0 3px rgba(143,179,255,.24) !important; }
    [data-baseweb="popover"] [role="option"] { color: var(--navy) !important; background: #FFFFFF !important; }
    [data-baseweb="popover"] [role="option"] * { color: var(--navy) !important; }
    [data-baseweb="popover"] [role="option"]:hover { background: #EAF0FF !important; }
    [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small { color: #C8D3E8 !important; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.16); }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] { background: rgba(255,255,255,.08); border: 1px dashed #8FA6D4; }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] { color: #E8EEF9; }
    [data-testid="stSidebar"] .stRadio label, [data-testid="stSidebar"] .stSelectbox label { color: #D8E1F0 !important; font-size: .78rem; font-weight: 600; }
    [data-testid="stSidebar"] div[role="radiogroup"] { gap: .25rem; }
    [data-testid="stSidebar"] div[role="radiogroup"] label { padding: .35rem .55rem; border-radius: 8px; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: rgba(255,255,255,.1); }
    .brand-lockup { display: flex; align-items: center; gap: .8rem; margin-bottom: 1.2rem; }
    .brand-lockup img { width: 92px; height: auto; background: white; border-radius: 6px; padding: 6px; }
    .brand-lockup strong { color: white; font-size: .92rem; line-height: 1.15; }
    .brand-lockup span { color: #B8C7E1; font-size: .68rem; display: block; margin-top: .2rem; }
    .main-header { background: white; border: 1px solid var(--line); border-radius: 16px; padding: 1.25rem 1.5rem; margin: .25rem 0 1.5rem; box-shadow: 0 8px 28px rgba(15,42,92,.06); display: flex; align-items: center; gap: 1.2rem; }
    .main-header img { width: 130px; max-height: 52px; object-fit: contain; }
    .main-header h1 { margin: 0; color: var(--navy); font-size: 1.65rem; letter-spacing: 0; }
    .main-header p { margin: .25rem 0 0; color: var(--muted); font-size: .92rem; }
    .section-title { color: var(--navy); font-size: 1.2rem; font-weight: 700; margin: 1.5rem 0 .75rem; }
    .eyebrow { color: var(--blue); font-size: .72rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; margin-bottom: .3rem; }
    .risk-card { border-radius: 16px; padding: 1.45rem 1.6rem; color: white; box-shadow: 0 12px 28px rgba(15,42,92,.12); margin-bottom: 1rem; }
    .risk-card.low { background: linear-gradient(135deg, #168A68, #21A77F); }
    .risk-card.medium { background: linear-gradient(135deg, #B7791F, #D69E2E); }
    .risk-card.high { background: linear-gradient(135deg, #C04A45, #E46761); }
    .risk-card.critical { background: linear-gradient(135deg, #8F2634, #C43B4D); }
    .risk-card .label { opacity: .82; font-size: .72rem; letter-spacing: .1em; font-weight: 700; }
    .risk-card .level { font-size: 2rem; font-weight: 800; margin: .25rem 0; }
    .risk-card .hint { opacity: .9; font-size: .86rem; }
    .indicator-card, .alert-card, .recommendation-card, .empty-panel { background: white; border: 1px solid var(--line); border-radius: 13px; box-shadow: 0 5px 18px rgba(15,42,92,.045); }
    .indicator-card { min-height: 175px; padding: 1rem; margin-bottom: 1rem; transition: transform .18s ease, box-shadow .18s ease; }
    .indicator-card:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(15,42,92,.1); }
    .indicator-card .name { color: var(--navy); font-weight: 700; font-size: .9rem; }
    .indicator-card .value { color: var(--ink); font-size: 1.75rem; font-weight: 800; margin: .7rem 0 .35rem; }
    .badge { display: inline-block; border-radius: 999px; padding: .2rem .55rem; font-size: .68rem; font-weight: 700; text-transform: uppercase; }
    .badge.low { background: #DDF5EC; color: #087452; } .badge.medium { background: #FFF2D4; color: #956515; } .badge.high { background: #FFE3E1; color: #A33430; } .badge.critical { background: #FADCE1; color: #8F2634; }
    .indicator-card .description { color: var(--muted); font-size: .76rem; line-height: 1.35; margin-top: .65rem; }
    .alert-card { padding: 1rem 1.1rem; margin: .55rem 0; border-left: 4px solid var(--blue); }
    .alert-card.high { border-left-color: #E46761; } .alert-card.critical { border-left-color: #8F2634; background: #FFF8F8; } .alert-card.medium { border-left-color: #D69E2E; } .alert-card.low { border-left-color: #21A77F; }
    .alert-card .alert-head { display: flex; justify-content: space-between; gap: .5rem; align-items: center; }
    .alert-card strong { color: var(--navy); font-size: .9rem; }
    .alert-card p { color: var(--muted); font-size: .82rem; margin: .55rem 0 0; }
    .alert-card small { color: var(--muted); }
    .recommendation-card { padding: .85rem 1rem; margin: .5rem 0; color: var(--ink); font-size: .88rem; }
    .recommendation-card span { color: var(--blue); font-weight: 800; margin-right: .5rem; }
    .empty-panel { padding: 3.5rem 1.5rem; text-align: center; border-style: dashed; }
    .empty-panel .empty-icon { font-size: 2.3rem; margin-bottom: .5rem; }
    .empty-panel h2 { color: var(--navy); margin: .25rem 0; }
    .empty-panel p { color: var(--muted); margin: .35rem 0 1.3rem; }
    .feature-row { display: flex; justify-content: center; gap: 1.5rem; color: var(--muted); font-size: .8rem; flex-wrap: wrap; }
    .stButton > button { border-radius: 9px; min-height: 2.65rem; font-weight: 700; border: 1px solid var(--line); }
    .stButton > button[kind="primary"] { background: var(--blue); border-color: var(--blue); box-shadow: 0 5px 12px rgba(46,111,242,.2); }
    .stButton > button[kind="primary"]:hover { background: #1E56C9; border-color: #1E56C9; }
    [data-testid="stChatMessage"] { border-radius: 12px; border: 1px solid var(--line); padding: .7rem 1rem; }
    [data-testid="stChatMessage"] p { font-size: .9rem; }
    @media (max-width: 700px) { .main-header { padding: 1rem; } .main-header img { width: 92px; } .main-header h1 { font-size: 1.2rem; } .risk-card .level { font-size: 1.6rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_state() -> None:
    defaults = {
        "analysis_result": None,
        "analysis_error": None,
        "uploaded_file_bytes": None,
        "uploaded_file_name": None,
        "chat_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_header() -> None:
    st.markdown(
        f"<div class='main-header'><img src='{LOGO_URL}' alt='TCS'><div><div class='eyebrow'>Corporate financial intelligence</div><h1>Agente de Riesgo Financiero</h1><p>Análisis inteligente de estados financieros</p></div></div>",
        unsafe_allow_html=True,
    )


def render_sidebar() -> tuple[str, str]:
    with st.sidebar:
        st.markdown(
            f"<div class='brand-lockup'><img src='{LOGO_URL}' alt='TCS'><div><strong>Agente de Riesgo<br>Financiero</strong><span>Financial intelligence</span></div></div>",
            unsafe_allow_html=True,
        )
        st.caption("Una lectura clara y explicable de la salud financiera.")
        st.divider()

        uploaded = st.file_uploader("Documento financiero", type="pdf", key="financial_pdf")
        if uploaded:
            st.session_state.uploaded_file_bytes = uploaded.getvalue()
            st.session_state.uploaded_file_name = uploaded.name
        if st.session_state.uploaded_file_name:
            st.success(f"Documento cargado\n\n{st.session_state.uploaded_file_name}\n\nTipo: PDF")
        else:
            st.caption("Aún no has cargado un documento.")

        st.divider()
        pagina = st.radio("Navegación", ["Análisis", "Preguntas"], key="navigation")
        st.divider()
        modo_seleccionado = st.selectbox("Modo de respuesta", list(MODE_LABELS), index=1, key="response_mode")
        modo = MODE_LABELS[modo_seleccionado]
        st.caption(f"{MODE_DETAILS[modo][1]} · {MODE_DETAILS[modo][2]}")
        st.divider()
        st.markdown("**Estado del servicio**")
        st.caption(f"● Backend configurado\n\n{API_URL}")
    return pagina, modo


def render_empty_state() -> None:
    st.markdown(
        """<div class='empty-panel'><div class='empty-icon'>▣</div><h2>Agente de Riesgo Financiero</h2><p>Analiza tu estado financiero utilizando inteligencia artificial.</p><div class='feature-row'><span>✓ Indicadores financieros</span><span>✓ Alertas de riesgo</span><span>✓ Recomendaciones inteligentes</span></div></div>""",
        unsafe_allow_html=True,
    )


def render_risk_card(result: dict) -> None:
    level = result.get("nivel_riesgo", "no evaluable").upper()
    style, label, hint = RISK_STYLES.get(level, ("medium", level, "Revisar información disponible"))
    st.markdown(f"<div class='risk-card {style}'><div class='label'>NIVEL GENERAL DE RIESGO</div><div class='level'>{label}</div><div class='hint'>{hint}</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Lectura ejecutiva</div>", unsafe_allow_html=True)
    st.info(result.get("resumen", "No se generó una explicación."))


def render_indicators(indicators: dict) -> None:
    st.markdown("<div class='section-title'>Indicadores financieros</div>", unsafe_allow_html=True)
    if not indicators:
        st.info("No hay indicadores calculados para mostrar.")
        return
    columns = st.columns(min(4, max(1, len(indicators))))
    for index, indicator in enumerate(indicators.values()):
        value = indicator.get("valor")
        risk = indicator.get("nivel_riesgo", "no evaluable").upper()
        risk_class = RISK_STYLES.get(risk, ("medium", risk, ""))[0]
        formatted = "N/A" if value is None else f"{value:.4f}"
        with columns[index % len(columns)]:
            st.markdown(
                f"<div class='indicator-card'><div class='name'>{indicator.get('nombre', 'Indicador')}</div><div class='value'>{formatted}</div><span class='badge {risk_class}'>{risk}</span><div class='description'>{indicator.get('interpretacion', '')}</div></div>",
                unsafe_allow_html=True,
            )
    with st.expander("Ver fórmulas y detalle técnico"):
        for indicator in indicators.values():
            st.markdown(f"**{indicator.get('nombre', 'Indicador')}** · Fórmula: `{indicator.get('formula', 'N/A')}`")


def render_alerts(alerts: list[dict]) -> None:
    st.markdown("<div class='section-title'>Alertas y señales de riesgo</div>", unsafe_allow_html=True)
    if not alerts:
        st.success("No se detectaron alertas con las reglas configuradas.")
        return
    for alert in alerts:
        severity = alert.get("severidad", "MEDIA")
        risk_class = RISK_STYLES.get(severity, ("medium", severity, ""))[0]
        st.markdown(
            f"<div class='alert-card {risk_class}'><div class='alert-head'><strong>{alert.get('indicador', 'Indicador')}</strong><span class='badge {risk_class}'>{severity}</span></div><p>{alert.get('descripcion', '')}</p><small>Umbral de referencia: {alert.get('umbral', 'N/A')}</small></div>",
            unsafe_allow_html=True,
        )


def render_recommendations(recommendations: list[str]) -> None:
    st.markdown("<div class='section-title'>Recomendaciones del agente</div>", unsafe_allow_html=True)
    for index, recommendation in enumerate(recommendations, start=1):
        st.markdown(f"<div class='recommendation-card'><span>{index:02d}</span>{recommendation}</div>", unsafe_allow_html=True)


def analyze_document() -> None:
    if st.button("Analizar documento", type="primary", use_container_width=True, key="analyze_document"):
        with st.spinner("Analizando documento..."):
            try:
                response = requests.post(
                    f"{API_URL}/analizar",
                    files={"file": (
                        st.session_state.uploaded_file_name,
                        st.session_state.uploaded_file_bytes,
                        "application/pdf",
                    )},
                    timeout=60,
                )
                if response.ok:
                    st.session_state.analysis_result = response.json()
                    st.session_state.analysis_error = None
                else:
                    st.session_state.analysis_result = None
                    st.session_state.analysis_error = response.json().get("detail", "No se pudo analizar el documento.")
            except requests.RequestException:
                st.session_state.analysis_result = None
                st.session_state.analysis_error = "No se pudo conectar con el backend."


def render_analysis() -> None:
    st.markdown("<div class='eyebrow'>Portfolio overview</div><h2 style='color:#0F2A5C;margin-top:0'>Análisis del estado financiero</h2>", unsafe_allow_html=True)
    if st.session_state.uploaded_file_name:
        st.caption(f"Documento activo · {st.session_state.uploaded_file_name}")
        analyze_document()
        if st.session_state.analysis_result:
            result = st.session_state.analysis_result
            render_risk_card(result)
            render_indicators(result.get("indicadores", {}))
            render_alerts(result.get("alertas", []))
            render_recommendations(result.get("recomendaciones", []))
            with st.expander("Ver fuentes y contexto utilizado"):
                st.json(result.get("contexto", []))
        elif st.session_state.analysis_error:
            st.error(st.session_state.analysis_error)
    else:
        render_empty_state()


def render_chat(mode: str) -> None:
    st.markdown("<div class='eyebrow'>Document intelligence</div><h2 style='color:#0F2A5C;margin-top:0'>Asistente financiero</h2><p style='color:#6B7280'>Realiza preguntas sobre el estado financiero analizado.</p>", unsafe_allow_html=True)
    if not st.session_state.uploaded_file_name:
        render_empty_state()
        return
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("fuente"):
                st.caption(f"Fuente: {message['fuente']}")
            if message["role"] == "assistant" and message.get("modo"):
                st.caption(f"Modo: {message['modo']} · {message.get('modelo', '')}")
    pregunta = st.chat_input("Escribe tu pregunta sobre el estado financiero...", key="financial_question")
    if not pregunta:
        return
    st.session_state.chat_history.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)
    with st.chat_message("assistant"):
        with st.spinner("Consultando el documento..."):
            text = ""
            source = None
            try:
                with requests.post(
                    f"{API_URL}/preguntar",
                    files={"file": (st.session_state.uploaded_file_name, st.session_state.uploaded_file_bytes, "application/pdf")},
                    data={"pregunta": pregunta, "modo": mode},
                    timeout=60,
                    stream=True,
                ) as response:
                    if not response.ok:
                        text = "No se pudo obtener una respuesta del backend."
                    else:
                        placeholder = st.empty()
                        for fragment in response.iter_content(chunk_size=None, decode_unicode=True):
                            if not fragment:
                                continue
                            text += fragment.decode("utf-8", errors="replace") if isinstance(fragment, bytes) else fragment
                            body, separator, source = text.partition("[FUENTE]:")
                            placeholder.markdown(body if separator else text)
                        text = body.strip() if source else text.strip()
                        if source:
                            source = source.strip()
            except requests.RequestException:
                text = "No se pudo conectar con el backend."
            mode_name, model_name, _ = MODE_DETAILS[mode]
            if source:
                st.caption(f"Fuente: {source}")
            st.caption(f"Modo: {mode_name} · {model_name}")
            st.session_state.chat_history.append({"role": "assistant", "content": text, "fuente": source, "modo": mode_name, "modelo": model_name})


initialize_state()
page, selected_mode = render_sidebar()
render_header()
if page == "Análisis":
    render_analysis()
else:
    render_chat(selected_mode)