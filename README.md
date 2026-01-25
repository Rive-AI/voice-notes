# Voice Notes Transcriber

A web app that transcribes voice recordings and generates summaries with action items.

## Features

- Upload audio recordings from your phone
- Automatic transcription using Google Cloud Speech-to-Text
- AI-generated summary and next steps using Google Gemini
- Mobile-friendly interface
- Copy-to-clipboard functionality

## Prerequisites

- Python 3.10+
- ffmpeg (for audio conversion)
- Google Cloud account with Speech-to-Text API enabled
- Google Gemini API key

## Setup

### 1. Install ffmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### 2. Install Python dependencies

```bash
cd voice_notes
pip install -r requirements.txt
```

### 3. Configure Google Cloud Speech-to-Text

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the "Cloud Speech-to-Text API"
4. Create a service account:
   - Go to IAM & Admin > Service Accounts
   - Create service account
   - Grant "Cloud Speech Client" role
   - Create and download JSON key
5. Save the JSON key file somewhere secure

### 4. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create an API key
3. Copy the key

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:
```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
GEMINI_API_KEY=your_gemini_api_key_here
```

## Running

```bash
cd voice_notes
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

To access from your phone, use your computer's local IP address (e.g., http://192.168.1.100:8000).

## Supported Audio Formats

- M4A (iPhone voice memos)
- MP3
- WAV
- WebM
- OGG
- AAC
- MP4

## API

### POST /api/transcribe

Upload an audio file for transcription and summarization.

**Request:** `multipart/form-data` with `file` field

**Response:**
```json
{
  "transcript": "Full transcribed text...",
  "summary": "2-3 paragraph summary...",
  "next_steps": [
    "Action item 1",
    "Action item 2"
  ]
}
```
