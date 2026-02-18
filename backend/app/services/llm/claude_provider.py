import anthropic

from app.config import settings
from app.services.llm.base import LLMProvider


class ClaudeProvider(LLMProvider):
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def generate(self, prompt: str, system: str = "") -> str:
        message = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system or "Sen yardımcı bir asistansın.",
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
