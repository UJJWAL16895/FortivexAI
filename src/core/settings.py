from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8-sig", hide_input_in_errors=True, extra="ignore"
    )

    agent_mode: Literal["mock", "live"] = "mock"
    gemini_api_key: SecretStr | None = None
    openai_api_key: SecretStr | None = None
    gemini_model: str = ""
    gemini_fallback_model: str = ""
    openai_model: str = ""
    gemini_thinking: Literal["minimal", "low", "off"] = "minimal"
    gemini_fallback_thinking: Literal["minimal", "low", "off"] = "minimal"
    gemini_rpm: int = Field(default=8, ge=1, le=1000)
    gemini_daily: int = Field(default=60, ge=1, le=100000)
    gemini_tpm: int = Field(default=12000, ge=1, le=10000000)
    allow_fallback_demo: bool = False
    gemini_stt_model: str = "gemini-3.5-transcribe"
    gemini_tts_model: str = "gemini-3.8-flash-tts"
    voice_tts: Literal["edge", "gemini", "browser"] = "edge"
    voice_stt: Literal["local", "gemini"] = "gemini"
    whisper_en_model: Literal["base", "small"] = "small"
    knowledge_embeddings: bool = False
    crm_path: str = "data/runtime/crm.sqlite3"
    public_demo: bool = False
    public_live_enabled: bool = False
    public_access_code: SecretStr | None = None
    public_requests_per_minute: int = Field(default=20, ge=1, le=1000)
    public_daily_request_cap: int = Field(default=250, ge=1, le=10000)

    @model_validator(mode="after")
    def validate_live_config(self) -> Self:
        if self.public_demo:
            self.voice_stt = "gemini"
            self.knowledge_embeddings = False
            self.allow_fallback_demo = False
            if not self.public_live_enabled:
                self.agent_mode = "mock"
            if self.agent_mode == "live":
                access = (
                    self.public_access_code.get_secret_value() if self.public_access_code else ""
                )
                if not 16 <= len(access.encode()) <= 256:
                    raise ValueError("Public live mode requires a strong PUBLIC_ACCESS_CODE")
        if self.agent_mode == "live":
            key = self.gemini_api_key.get_secret_value().strip() if self.gemini_api_key else ""
            if not key or key.startswith("replace_with_"):
                raise ValueError("Live mode requires GEMINI_API_KEY in the local .env")
            if not self.gemini_model.strip():
                raise ValueError("Live mode requires GEMINI_MODEL from the authenticated catalog")
            if self.gemini_fallback_model and self.gemini_fallback_model == self.gemini_model:
                raise ValueError("GEMINI_FALLBACK_MODEL must differ from GEMINI_MODEL")
        return self
