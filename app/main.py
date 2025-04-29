from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, orchestrator
import json

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Orquestrador Maria",
    description="API para orquestrar gravações e transcrições de reuniões.",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/orquestrar", response_class=StreamingResponse)
async def orquestrar(meeting_url: str, user_id: str, db: Session = Depends(get_db)):
    try:
        async def event_stream():
            async for raw in orchestrator.stream_recording(meeting_url):
                # 1) Limpa prefixo "data: " que já vem do record API
                if raw.startswith("data:"):
                    payload = raw[len("data:"):].strip()
                else:
                    payload = raw

                # 2) Reenvia no formato SSE correto
                yield f"data: {payload}\n\n"

                # 3) Parse JSON e trata evento "completed"
                obj = json.loads(payload)
                if obj.get("event") == "completed":
                    gs_uri      = obj["gs_uri"]
                    public_url  = obj["public_url"]
                    recording_id = obj["recording_id"]

                    # 4) Mensagem intermediária antes de transcrever
                    yield f"data: {{\"event\": \"sending_to_transcriber\", \"gs_uri\": \"{gs_uri}\"}}\n\n"

                    # 5) Chama transcriber
                    pdf_url = await orchestrator.transcribe_audio(gs_uri)

                    # 6) Persiste no banco
                    meeting = models.MeetingDocument(
                        user_id=user_id,
                        meeting_url=meeting_url,
                        audio_url=public_url,
                        document_url=pdf_url
                    )
                    db.add(meeting)
                    db.commit()

                    # 7) Evento final
                    yield f"data: {{\"event\": \"transcription_completed\", \"pdf_url\": \"{pdf_url}\"}}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop/{recording_id}")
async def stop(recording_id: str):
    try:
        result = await orchestrator.stop_recording(recording_id)
        return {"status": result.get("status", "unknown")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))