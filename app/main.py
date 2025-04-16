from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, schemas, orchestrator

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
