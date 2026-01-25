"""Google Docs export functionality using application default credentials."""

import os
from datetime import datetime

import google.auth
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Scopes needed for Google Docs
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive.file"]


def get_credentials():
    """Get credentials from application default credentials."""
    credentials, project = google.auth.default(scopes=SCOPES)

    # Refresh if needed
    if credentials.expired:
        credentials.refresh(Request())

    return credentials


def create_voice_note_doc(
    title: str,
    transcript: str,
    summary: str,
    next_steps: list[str],
) -> str:
    """Create a Google Doc with the voice note content.

    Returns:
        URL of the created document
    """
    credentials = get_credentials()
    service = build("docs", "v1", credentials=credentials)

    # Create the document
    doc = service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    # Build the content
    requests = []

    # Build full text
    sections = [
        ("Summary\n\n", True),
        (summary + "\n\n", False),
        ("Next Steps\n\n", True),
    ]

    # Add next steps as bullet points
    next_steps_text = ""
    for step in next_steps:
        next_steps_text += f"• {step}\n"
    next_steps_text += "\n"

    sections.append((next_steps_text, False))
    sections.append(("Full Transcript\n\n", True))
    sections.append((transcript + "\n", False))

    # Insert all text first
    full_text = ""
    for text, _ in sections:
        full_text += text

    requests.append({
        "insertText": {
            "location": {"index": 1},
            "text": full_text,
        }
    })

    # Apply heading formatting
    idx = 1
    for text, is_heading in sections:
        if is_heading:
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": idx, "endIndex": idx + len(text)},
                    "paragraphStyle": {"namedStyleType": "HEADING_1"},
                    "fields": "namedStyleType",
                }
            })
        idx += len(text)

    # Execute the requests
    service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"
