from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from app.database import Base

class MeetingDocument(Base):
    __tablename__ = "meeting_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    meeting_url = Column(String, nullable=False)
    audio_url = Column(String, nullable=False)
    document_url = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
