import httpx

RECORD_API = "http://34.95.216.110:8000/gravar"
TRANSCRIBE_API = "https://maria-production.up.railway.app/process-audio"  # ajuste conforme onde está rodando

async def process_meeting(meeting_url: str) -> str:
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.get(RECORD_API, params={"url": meeting_url})
        response.raise_for_status()
        return response.json()["url_bucket"]

async def transcribe_audio(audio_url: str) -> str:
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            TRANSCRIBE_API,
            json={"audio_url": audio_url}
        )
        response.raise_for_status()
        return response.json()["pdf_url"]
