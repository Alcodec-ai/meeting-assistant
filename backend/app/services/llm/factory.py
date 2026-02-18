from app.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.claude_provider import ClaudeProvider
from app.services.llm.ollama_provider import OllamaProvider
from app.services.llm.openai_provider import OpenAIProvider

_PROVIDERS: dict[str, type[LLMProvider]] = {
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
}


def get_llm_provider(provider_name: str | None = None) -> LLMProvider:
    name = provider_name or settings.llm_provider
    provider_class = _PROVIDERS.get(name)
    if not provider_class:
        raise ValueError(
            f"Bilinmeyen LLM provider: {name}. "
            f"Desteklenen: {', '.join(_PROVIDERS.keys())}"
        )
    return provider_class()
