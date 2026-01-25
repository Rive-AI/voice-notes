"""FastAPI backend for voice recording transcription."""

import os
import tempfile
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from google_docs import create_voice_note_doc
from summarizer import summarize_transcript
from transcriber import transcribe_audio

# Load environment variables
load_dotenv()

app = FastAPI(title="Voice Notes Transcriber")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supported audio formats
SUPPORTED_FORMATS = {".m4a", ".mp3", ".wav", ".webm", ".ogg", ".mp4", ".aac"}


@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Transcribe an uploaded audio file and generate summary.

    Returns:
        JSON with transcript, summary, and next_steps
    """
    # Validate file extension
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Supported: {', '.join(SUPPORTED_FORMATS)}"
        )

    # Save uploaded file temporarily
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    try:
        content = await file.read()
        temp_file.write(content)
        temp_file.close()

        # Transcribe the audio
        transcript = transcribe_audio(temp_file.name)

        if not transcript:
            raise HTTPException(
                status_code=400,
                detail="Could not transcribe audio. The recording may be too quiet or unclear."
            )

        # Generate summary and next steps
        result = summarize_transcript(transcript)

        return {
            "transcript": transcript,
            "summary": result.summary,
            "next_steps": result.next_steps
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp file
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)


class ExportRequest(BaseModel):
    transcript: str
    summary: str
    next_steps: list[str]


class ResummarizeRequest(BaseModel):
    transcript: str
    summary_prompt: str | None = None


@app.post("/api/resummarize")
async def resummarize(request: ResummarizeRequest):
    """Re-summarize a transcript with a custom prompt."""
    try:
        result = summarize_transcript(request.transcript, request.summary_prompt)
        return {
            "summary": result.summary,
            "next_steps": result.next_steps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/google-docs")
async def export_to_google_docs(request: ExportRequest):
    """Export transcript to Google Docs."""
    try:
        title = f"Voice Note - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        doc_url = create_voice_note_doc(
            title=title,
            transcript=request.transcript,
            summary=request.summary,
            next_steps=request.next_steps,
        )
        return {"url": doc_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Serve the frontend."""
    # Handle both local and Vercel paths
    import os
    static_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_path):
        return FileResponse(static_path)
    return FileResponse("static/index.html")


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
