"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    frontend_url: str = "http://localhost:5173"
    api_url: str = "http://localhost:8000"

    gemini_api_key: str = ""
    gemini_fast_model: str = "gemini-2.5-flash"
    gemini_reasoning_model: str = ""

    database_url: str = ""
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "claim-evidence"

    max_clarifications: int = 3
    max_upload_mb: int = 15
    demo_mode: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()