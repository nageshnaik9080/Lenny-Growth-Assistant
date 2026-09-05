from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    cors_origins: str = "https://lenny-frontend.onrender.com,https://lenny-frontend-20wq.onrender.com"

    default_llm_provider: str = "anthropic"
    ollama_base_url: str = "http://localhost:11434"  # local only; not used on Render
    ollama_model: str = "llama3.2:3b"               # local only; not used on Render

    cloud_provider: str = "anthropic"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    retrieval_top_k: int = 5
    retrieval_threshold: float = 0.65
    max_history_messages: int = 12
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
