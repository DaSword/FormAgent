from pydantic_settings import BaseSettings
from os import getenv

class Settings(BaseSettings):
    PROJECT_NAME: str = "Doc Extractor Agent"
    API_V1_STR: str = "/api/v1"
    
    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None
    GCS_BUCKET_NAME: str = "doc-extractor-bucket"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/doc_extractor"

    LLM_MODEL: str = "gemini-2.5-flash"
    LLM_API_KEY: str = getenv("GOOGLE_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()
