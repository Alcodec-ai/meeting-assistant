"""Meeting summarization service."""

from app.services.llm.factory import get_llm_provider


async def generate_summary(transcript_text: str) -> dict:
    """Generate a summary from transcript text.

    Returns dict with: full_summary, key_points, decisions
    """
    llm = get_llm_provider()
    return await llm.summarize(transcript_text)
