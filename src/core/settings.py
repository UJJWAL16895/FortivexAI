from typing import Literal, Self

from pydantic import SecretStr, model_validator
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

    @model_validator(mode="after")
    def validate_live_config(self) -> Self:
        if self.agent_mode == "live":
            key = self.gemini_api_key.get_secret_value().strip() if self.gemini_api_key else ""
            if not key or key.startswith("replace_with_"):
                raise ValueError("Live mode requires GEMINI_API_KEY in the local .env")
            if not self.gemini_model.strip():
                raise ValueError("Live mode requires GEMINI_MODEL from the authenticated catalog")
            if self.gemini_fallback_model and self.gemini_fallback_model == self.gemini_model:
                raise ValueError("GEMINI_FALLBACK_MODEL must differ from GEMINI_MODEL")
        return self
