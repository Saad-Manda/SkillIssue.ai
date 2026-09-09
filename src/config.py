from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent



class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillIssue.ai"
    DEBUG: bool = False
    DATABASE_URL: str
    MODEL: str 
    GOOGLE_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    GROQ_API_KEY_1: str | None = None
    GROQ_API_KEY_2: str | None = None
    GROQ_API_KEY_3: str | None = None
    GROQ_API_KEY_4: str | None = None
    OPENAI_API_KEY: str | None = None
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRY_MINUTES: int
    JWT_API_KEY: str
    MONGO_DB: str
    ATLAS_DB_URI: str
    COLLECTION_NAME: str
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(env_file = BASE_DIR / ".env", extra="ignore")


settings = Settings()
