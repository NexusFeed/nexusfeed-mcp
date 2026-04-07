from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mcp_api_base_url: str = "http://localhost:8000"
    mcp_api_key: str  # required — fails loudly if MCP_API_KEY is not set


settings = Settings()
