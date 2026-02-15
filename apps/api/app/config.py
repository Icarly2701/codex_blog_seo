from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    cors_origins: str = "http://localhost:3000"

    # Render injects env vars directly. Local dev can still use .env in CWD.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
