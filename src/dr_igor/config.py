from functools import lru_cache
from typing import Optional

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    PYDANTIC_SETTINGS_AVAILABLE = True
except ImportError:
    # Fallback para quando pydantic_settings não está disponível
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class SettingsConfigDict(dict):
        pass

    PYDANTIC_SETTINGS_AVAILABLE = False

if PYDANTIC_SETTINGS_AVAILABLE:
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

        openai_api_key: Optional[str] = None
        openai_model: str = "gpt-4o-mini"
        openai_whisper_model: str = "whisper-1"
        evolution_base_url: Optional[str] = None
        evolution_api_key: Optional[str] = None
        google_service_account_json: Optional[str] = None
        google_sheet_id: Optional[str] = None
        dashboard_webhook_url: Optional[str] = None
        rag_top_k: int = 3
        allow_origin_regex: str = ".*"
        notes_dir: Optional[str] = None
else:
    class Settings(BaseSettings):
        def __init__(self, **kwargs):
            # Defaults para todos os campos
            self.openai_api_key: Optional[str] = None
            self.openai_model: str = "gpt-4o-mini"
            self.openai_whisper_model: str = "whisper-1"
            self.evolution_base_url: Optional[str] = None
            self.evolution_api_key: Optional[str] = None
            self.google_service_account_json: Optional[str] = None
            self.google_sheet_id: Optional[str] = None
            self.dashboard_webhook_url: Optional[str] = None
            self.rag_top_k: int = 3
            self.allow_origin_regex: str = ".*"
            self.notes_dir: Optional[str] = None

            # Fallback manual
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)

@lru_cache
def get_settings() -> Settings:
    return Settings()
