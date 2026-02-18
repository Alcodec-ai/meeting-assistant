"""Task extraction service - extracts action items from meeting transcripts."""

from app.services.llm.factory import get_llm_provider


async def extract_tasks(transcript_text: str, participant_names: list[str]) -> list[dict]:
    """Extract tasks/action items from transcript text.

    Returns list of dicts with: title, description, assignee, priority
    """
    llm = get_llm_provider()
    return await llm.extract_tasks(transcript_text, participant_names)
