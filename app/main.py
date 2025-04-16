from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Importar o middleware de CORS
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, schemas, orchestrator

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

@app.post("/orquestrar", response_model=schemas.MeetingResponse)
async def orquestrar(req: schemas.MeetingRequest, db: Session = Depends(get_db)):
    try:
        audio_url = await orchestrator.process_meeting(req.meeting_url)
        pdf_url = await orchestrator.transcribe_audio(audio_url)

        meeting = models.MeetingDocument(
            user_id=req.user_id,
            meeting_url=req.meeting_url,
            audio_url=audio_url,
            document_url=pdf_url
        )
        db.add(meeting)
        db.commit()

        return schemas.MeetingResponse(
            user_id=req.user_id,
            meeting_url=req.meeting_url,
            document_url=pdf_url
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))