import httpx
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

RECORD_API_BASE = "http://34.39.148.187:8000"

async def stream_recording(meeting_url: str) -> AsyncGenerator[str, None]:
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream("GET", f"{RECORD_API_BASE}/gravar", params={"url": meeting_url}) as response:
            async for line in response.aiter_lines():
                if line:
                    yield f"data: {line}\n\n"

async def stop_recording(recording_id: str) -> dict:
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(f"{RECORD_API_BASE}/stop/{recording_id}")
        response.raise_for_status()
        return response.json()

async def transcribe_audio(gs_uri: str) -> str:
    TRANSCRIBE_API = "https://maria-production.up.railway.app/process-audio"
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            TRANSCRIBE_API,
            json={"audio_url": gs_uri}
        )
        response.raise_for_status()
        return response.json()["pdf_url"]
