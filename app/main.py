from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, orchestrator

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir chamadas de qualquer domínio
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos os headers
)

# Dependency
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
            async for message in orchestrator.stream_recording(meeting_url):
                yield f"data: {message}\n\n"
                # Verifica se a mensagem final foi recebida
                if '"event": "completed"' in message:
                    data = eval(message.split("data: ")[1])  # Converte a string JSON para dict
                    gs_uri = data.get("gs_uri")
                    public_url = data.get("public_url")
                    recording_id = data.get("recording_id")
                    if gs_uri:
                        # Mensagem intermediária indicando que o gs_uri está sendo enviado para o transcriber
                        yield f"data: {{'event': 'sending_to_transcriber', 'gs_uri': '{gs_uri}'}}\n\n"
                        pdf_url = await orchestrator.transcribe_audio(gs_uri)
                        meeting = models.MeetingDocument(
                            user_id=user_id,
                            meeting_url=meeting_url,
                            audio_url=public_url,
                            document_url=pdf_url
                        )
                        db.add(meeting)
                        db.commit()
                        yield f"data: {{'event': 'transcription_completed', 'pdf_url': '{pdf_url}'}}\n\n"

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