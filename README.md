# Agente de Riesgo Financiero

Primera versión funcional de un sistema que extrae cifras de un estado financiero en PDF, calcula indicadores, detecta alertas, recupera contexto financiero y genera una evaluación explicable.

## Arquitectura

`PDF -> Extractor -> Calculadora -> Alertas -> RAG/Contexto -> Respuesta`

- `backend/agent`: lógica de dominio independiente de la interfaz.
- `backend/workflow`: orquestación lineal con LangGraph y estado `TypedDict`.
- `backend/main.py`: API FastAPI.
- `frontend/app.py`: interfaz Streamlit.
- `tests`: pruebas unitarias de indicadores, alertas y RAG.

El RAG usa TF-IDF contra una base de conocimiento local. La generación de respuesta usa exclusivamente Groq con el modelo `openai/gpt-oss-120b`. Si `GROQ_API_KEY` no está disponible, el sistema conserva un resumen determinista para permitir demos y pruebas offline.

## Instalación

Requiere Python 3.11 o superior.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configura `GROQ_API_KEY` en `.env` usando [.env.example](.env.example) como referencia. La aplicación la lee con `os.environ.get` y nunca la muestra. El texto enviado a Groq se limita a 12.000 caracteres para cuidar el límite de tokens por minuto del free tier.

## Ejecución

En una terminal, iniciar la API:

```powershell
uvicorn backend.main:app --reload --port 8001
```

En otra terminal, iniciar Streamlit:

```powershell
streamlit run frontend/app.py
```

Abrir la URL mostrada por Streamlit y cargar `data/ejemplo_financiero.pdf`. También se puede consultar `http://localhost:8001/docs`.

En la página `💬 Preguntas` se puede elegir entre tres modos Groq: `Rápido` usa `openai/gpt-oss-20b` con razonamiento bajo, `Equilibrado` usa `openai/gpt-oss-120b` con razonamiento medio y `Avanzado` usa el mismo modelo con razonamiento alto. Las respuestas llegan progresivamente mediante streaming y la fuente se muestra al finalizar. La selección usa los modelos disponibles para la clave Groq configurada.

## Pruebas

```powershell
pytest -q
python -m compileall -q backend frontend
```

## Formato esperado del PDF

El extractor busca etiquetas sencillas, por ejemplo: `Activos: 100000`, `Pasivos: 70000`, `Ingresos: 50000`, `Utilidad neta: 3000`, `Efectivo: 12000` y `Deuda corto plazo: 15000`. Los valores pueden usar punto decimal o formato europeo básico.

Los umbrales son didácticos y deben calibrarse con criterios contables y sectoriales antes de usar el sistema en producción.
