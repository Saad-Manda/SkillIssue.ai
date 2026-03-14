from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent



class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillIssue.ai"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://ziya:password@localhost:5432/skillissue"
    MODEL: str = "models/gemini-2.5-flash"
    GOOGLE_API_KEY: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    model_config = SettingsConfigDict(env_file = BASE_DIR / ".env")


settings = Settings()
