from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent



class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillIssue.ai"
    DEBUG: bool = False
    DATABASE_URL: str
    MODEL: str = "models/gemini-2.5-flash"
    GOOGLE_API_KEY: str
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRY_MINUTES: int
    JWT_API_KEY: str
    MONGO_DB: str
    ATLAS_DB_URI: str
    model_config = SettingsConfigDict(env_file = BASE_DIR / ".env")


settings = Settings()
