from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI
    OPENAI_API_KEY: str

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    COLLECTION_NAME: str = "sahakari_compliance_docs"

    # Application
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sahakari Bot"
    VERSION: str = "1.0.0"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000"
    ]

    # File upload
    UPLOAD_DIR: str = "./data/documents"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".xlsx", ".xls"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
