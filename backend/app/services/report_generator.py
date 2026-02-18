"""Progress report generation service."""

from app.services.llm.factory import get_llm_provider


async def generate_meeting_report(
    summary: dict,
    tasks: list[dict],
    meeting_title: str,
) -> dict:
    """Generate a progress report for a meeting.

    Returns a dict with report content.
    """
    llm = get_llm_provider()

    tasks_text = "\n".join(
        f"- [{t.get('status', 'pending')}] {t['title']} (Sorumlu: {t.get('assignee_name', 'Atanmamış')}, "
        f"Öncelik: {t.get('priority', 'medium')})"
        for t in tasks
    )

    prompt = f"""Aşağıdaki toplantı bilgilerine dayanarak bir ilerleme raporu oluştur.
JSON formatında yanıt ver:

{{
    "title": "Rapor başlığı",
    "summary": "Kısa özet",
    "task_overview": {{
        "total": toplam_görev_sayısı,
        "completed": tamamlanan,
        "in_progress": devam_eden,
        "pending": bekleyen
    }},
    "highlights": ["Öne çıkan madde 1", ...],
    "next_steps": ["Sonraki adım 1", ...],
    "risks": ["Risk/engel 1", ...]
}}

TOPLANTI: {meeting_title}

ÖZET:
{summary.get('full_summary', '')}

GÖREVLER:
{tasks_text}"""

    import json

    response = await llm.generate(
        prompt,
        system="Sen bir proje yönetim asistanısın. Yanıtını kesinlikle JSON formatında ver.",
    )

    try:
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    except json.JSONDecodeError:
        return {"title": meeting_title, "summary": response, "task_overview": {}}
