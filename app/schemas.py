from pydantic import BaseModel

class MeetingRequest(BaseModel):
    user_id: str
    meeting_url: str

class MeetingResponse(BaseModel):
    user_id: str
    meeting_url: str
    document_url: str
    meeting_transcription: str  # novo campo

class StopResponse(BaseModel):
    status: str
