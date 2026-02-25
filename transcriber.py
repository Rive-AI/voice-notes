"""Audio transcription using Google Gemini."""

import mimetypes
import os

import google.generativeai as genai

MIME_TYPE_MAP = {
    ".m4a": "audio/mp4",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".webm": "audio/webm",
    ".ogg": "audio/ogg",
    ".mp4": "audio/mp4",
    ".aac": "audio/aac",
}


def transcribe_audio(file_path: str) -> str:
    """Transcribe an audio file using Google Gemini.

    Args:
        file_path: Path to the audio file

    Returns:
        Transcribed text
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-pro")

    # Determine MIME type from file extension
    ext = os.path.splitext(file_path)[1].lower()
    mime_type = MIME_TYPE_MAP.get(ext) or mimetypes.guess_type(file_path)[0]

    # Upload the audio file with explicit mime_type
    audio_file = genai.upload_file(file_path, mime_type=mime_type)

    # Transcribe with speaker diarization
    response = model.generate_content([
        """Transcribe this ENTIRE audio recording from start to finish with high accuracy.

CRITICAL: You must transcribe the COMPLETE recording. Do not stop early or summarize.

Instructions:
- Transcribe EVERY word from beginning to end
- Transcribe in the SAME LANGUAGE as the audio (e.g. if spoken in Chinese, transcribe in Chinese; if spoken in English, transcribe in English)
- If there are multiple speakers, label them as "Speaker 1:", "Speaker 2:", etc.
- Include filler words like "um", "uh" if significant
- Use proper punctuation and capitalization
- Preserve the natural flow of conversation
- Output only the transcription, no commentary or notes

Format for multiple speakers:
Speaker 1: Hello, how are you?
Speaker 2: I'm doing well, thanks for asking.

If there's only one speaker, transcribe without speaker labels.

START TRANSCRIBING NOW - include everything until the recording ends:""",
        audio_file
    ])

    return response.text.strip()
