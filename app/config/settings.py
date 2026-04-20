from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Enterprise Policy Search"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/policy_search"

    gemini_api_key: str = ""
    embedding_model: str = "gemini-embedding-001"
    chat_model: str = "gemini-3.1-flash-lite-preview"

    chunk_size: int = 700
    chunk_overlap: int = 100
    top_k: int = 5
    fetch_k_multiplier: int = 3  # fetch this many × top_k candidates before reranking


settings = Settings()
