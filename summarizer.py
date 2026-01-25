"""Gemini-based summarization and action item extraction."""

import os
from dataclasses import dataclass

import google.generativeai as genai


DEFAULT_SUMMARY_PROMPT = """Identify and list the pain points, problems, or challenges mentioned by the user/customer in this recording.

Format as bullet points:
- [Pain point 1]
- [Pain point 2]
- etc.

Be specific and capture the exact issues they're facing. If no clear pain points are mentioned, note that."""


@dataclass
class SummaryResult:
    """Result from summarization."""
    summary: str
    next_steps: list[str]


def get_gemini_client():
    """Initialize and return the Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-pro")


def summarize_transcript(transcript: str, summary_prompt: str | None = None) -> SummaryResult:
    """Generate summary and next steps from a transcript.

    Args:
        transcript: The transcribed text
        summary_prompt: Custom prompt for the summary section (optional)

    Returns:
        SummaryResult with summary and next_steps
    """
    model = get_gemini_client()

    summary_instruction = summary_prompt or DEFAULT_SUMMARY_PROMPT

    prompt = f"""Analyze the following voice recording transcript and provide:

1. Summary section based on this instruction:
{summary_instruction}

2. A list of action items / next steps mentioned or implied in the recording. Be specific and actionable.

Format your response EXACTLY as follows (use these exact headers):

## Summary
[Your summary here based on the instruction above]

## Next Steps
- [Action item 1]
- [Action item 2]
- [Action item 3]
(list all relevant action items)

If there are no clear action items, write "- No specific action items identified"

---
TRANSCRIPT:
{transcript}
"""

    response = model.generate_content(prompt)
    text = response.text

    # Parse the response
    summary = ""
    next_steps = []

    # Split by sections
    if "## Summary" in text and "## Next Steps" in text:
        parts = text.split("## Next Steps")
        summary_part = parts[0].replace("## Summary", "").strip()
        next_steps_part = parts[1].strip() if len(parts) > 1 else ""

        summary = summary_part

        # Parse next steps (bullet points)
        for line in next_steps_part.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                next_steps.append(line[2:])
            elif line.startswith("* "):
                next_steps.append(line[2:])
    else:
        # Fallback: use the whole response as summary
        summary = text
        next_steps = ["Unable to parse action items - see summary"]

    return SummaryResult(summary=summary, next_steps=next_steps)
