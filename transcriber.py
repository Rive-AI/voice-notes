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
    # Set max_output_tokens high enough for long recordings (1hr+ ≈ 20k+ tokens)
    generation_config = genai.types.GenerationConfig(max_output_tokens=65536)
    response = model.generate_content([
        """Transcribe this audio recording accurately.

Instructions:
- Transcribe in the SAME LANGUAGE as the audio (e.g. if spoken in Chinese, transcribe in Chinese; if in English, transcribe in English)
- If there are multiple speakers, label them as "Speaker 1:", "Speaker 2:", etc.
- If there's only one speaker, transcribe without speaker labels
- Use proper punctuation
- Output only the transcription, no commentary or notes

CRITICAL RULES - you must follow these exactly:
- Do NOT hallucinate or invent words that were not spoken
- Do NOT repeat any word, phrase, or sentence more than it was actually said
- If audio is silent, inaudible, or unclear, write [inaudible] — do not fill it with repeated words
- If someone says "嗯" once, write it once — do not repeat it dozens of times
- Only transcribe what was genuinely spoken""",
        audio_file
    ], generation_config=generation_config)

    return response.text.strip()
