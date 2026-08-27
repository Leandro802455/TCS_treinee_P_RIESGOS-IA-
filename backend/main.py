from pathlib import Path
from tempfile import NamedTemporaryFile

import pymupdf
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from .agent.llm_client import RESPONSE_MODES
from .agent.qa import answer_question_stream
from .agent.storage import AnalysisRepository
from .workflow.graph import analyze_pdf

load_dotenv()
app = FastAPI(title="Agente de Riesgo Financiero", version="0.1.0")
analysis_repository = AnalysisRepository()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analizar")
async def analyze(file: UploadFile = File(...)) -> dict:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")
    content = await file.read()
    with NamedTemporaryFile(suffix=".pdf", delete=False) as temporary:
        temporary.write(content)
        path = Path(temporary.name)
    try:
        result = analyze_pdf(str(path))
        final_response = result["final_response"]
        analysis_repository.save_analysis(file.filename or "documento.pdf", final_response)
        return final_response
    except (FileNotFoundError, ValueError, pymupdf.FileDataError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    finally:
        path.unlink(missing_ok=True)


@app.post("/preguntar")
async def ask_question(
    file: UploadFile = File(...),
    pregunta: str = Form(...),
    modo: str = Form("equilibrado"),
) -> StreamingResponse:
    """Emite la respuesta de Groq por fragmentos y termina con la fuente."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")
    if not pregunta.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")
    if modo not in RESPONSE_MODES:
        raise HTTPException(status_code=400, detail="El modo debe ser: rapido, equilibrado o avanzado")

    content = await file.read()
    with NamedTemporaryFile(suffix=".pdf", delete=False) as temporary:
        temporary.write(content)
        path = Path(temporary.name)
    try:
        stream = answer_question_stream(path, pregunta, modo)

        def stream_and_cleanup():
            try:
                yield from stream
            except Exception:
                yield "No fue posible completar la respuesta del agente."
            finally:
                path.unlink(missing_ok=True)

        return StreamingResponse(stream_and_cleanup(), media_type="text/plain; charset=utf-8")
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
