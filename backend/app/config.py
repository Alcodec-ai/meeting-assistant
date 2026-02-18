from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Meeting Assistant"
    database_url: str = "postgresql+asyncpg://meeting_user:meeting_pass@localhost:5432/meeting_assistant"
    redis_url: str = "redis://localhost:6379/0"
    upload_dir: str = "uploads"

    # LLM Configuration
    llm_provider: str = "claude"  # claude | openai | ollama
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # Whisper Configuration
    whisper_model: str = "large-v3"
    whisper_language: str = "tr"
    hf_token: str = ""  # HuggingFace token for pyannote

    model_config = {"env_file": ".env", "env_prefix": "MA_"}


settings = Settings()
