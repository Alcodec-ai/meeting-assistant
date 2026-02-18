from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system: str = "") -> str:
        """Generate a text response from the LLM."""
        ...

    async def summarize(self, transcript: str) -> dict:
        """Generate a meeting summary from a transcript.

        Returns dict with keys: full_summary, key_points, decisions
        """
        system = (
            "Sen bir toplantı asistanısın. Verilen toplantı transkriptini analiz et. "
            "Yanıtını kesinlikle JSON formatında ver, başka bir şey yazma."
        )
        prompt = f"""Aşağıdaki toplantı transkriptini analiz et ve JSON formatında yanıt ver:

{{
    "full_summary": "Toplantının kapsamlı özeti (2-3 paragraf)",
    "key_points": ["Önemli nokta 1", "Önemli nokta 2", ...],
    "decisions": ["Alınan karar 1", "Alınan karar 2", ...]
}}

TRANSKRİPT:
{transcript}"""
        response = await self.generate(prompt, system)
        import json

        # Try to parse JSON from the response
        try:
            # Handle potential markdown code blocks
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "full_summary": response,
                "key_points": [],
                "decisions": [],
            }

    async def extract_tasks(self, transcript: str, participants: list[str]) -> list[dict]:
        """Extract action items / tasks from a transcript.

        Returns list of dicts with keys: title, description, assignee, priority
        """
        participants_str = ", ".join(participants) if participants else "Belirtilmemiş"
        system = (
            "Sen bir toplantı asistanısın. Verilen toplantı transkriptinden görevleri çıkar. "
            "Yanıtını kesinlikle JSON formatında ver, başka bir şey yazma."
        )
        prompt = f"""Aşağıdaki toplantı transkriptinden aksiyon maddelerini (görevleri) çıkar.
Katılımcılar: {participants_str}

Her görev için JSON formatında yanıt ver:
[
    {{
        "title": "Görev başlığı",
        "description": "Görev açıklaması",
        "assignee": "Sorumlu kişinin adı veya null",
        "priority": "low|medium|high"
    }}
]

TRANSKRİPT:
{transcript}"""
        response = await self.generate(prompt, system)
        import json

        try:
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(text)
        except json.JSONDecodeError:
            return []
