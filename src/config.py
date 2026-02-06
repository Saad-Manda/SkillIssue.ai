from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent



class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillIssue.ai"
    DEBUG: bool = False
    DATABASE_URL: str = ""
    model_config = SettingsConfigDict(env_file = BASE_DIR / ".env")


settings = Settings()
