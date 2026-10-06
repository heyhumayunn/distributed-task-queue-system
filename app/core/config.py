import os

try:
    from pydantic_settings import BaseSettings
    class Settings(BaseSettings):
        REDIS_URL: str = "redis://localhost:6379"
        DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dtq"
        DEBUG: bool = False
        NUM_WORKERS: int = 4
        ALLOWED_ORIGINS: list = ["*"]

        class Config:
            env_file = ".env"

    settings = Settings()
except ImportError:
    class Settings:
        REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
        DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/dtq")
        DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
        NUM_WORKERS: int = int(os.getenv("NUM_WORKERS", "4"))
        ALLOWED_ORIGINS: list = ["*"]

    settings = Settings()
