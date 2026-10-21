from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    TEMP_TOKEN_EXPIRE_MINUTES: int = 5
    FRONTEND_URL: str = "http://localhost:3000"
    PREVIEW_MODE: bool = False
    SESSION_SECRET: str | None = None
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama3-8b-8192"
    OCR_ENABLED: bool = False

    @model_validator(mode="after")
    def resolve_jwt_secret(self):
        """Use JWT_SECRET; fall back to SESSION_SECRET if it is unset or too short."""
        secret = self.JWT_SECRET or ""
        if len(secret) < 32:
            secret = self.SESSION_SECRET or ""
        if len(secret) < 32:
            raise ValueError(
                "JWT_SECRET or SESSION_SECRET must be at least 32 characters long. "
                "Set one of them in the workspace Secrets panel or in backend/.env."
            )
        self.JWT_SECRET = secret
        return self


settings = Settings()
