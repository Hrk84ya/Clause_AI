from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""

    # Database
    database_url: str = "postgresql+asyncpg://legaluser:changeme@postgres:5432/legalanalyzer"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Security
    jwt_secret: str = "change-this-to-a-random-64-char-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # File Storage
    upload_dir: str = "/data/uploads"
    faiss_dir: str = "/data/faiss"
    max_upload_size_mb: int = 20

    # App
    app_env: str = "development"
    log_level: str = "DEBUG"
    cors_origins: str = "http://localhost:3000"

    # Postgres (for docker compose)
    postgres_user: str = "legaluser"
    postgres_password: str = "changeme"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
