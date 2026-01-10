from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sahakari Bot"
    
    # Security
    SECRET_KEY: str = "sahakari-bot-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Ollama (Local LLM)
    OLLAMA_MODEL: Optional[str] = None  # None = auto-detect, or specify: "llama3", "mistral", "llama2", etc.
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Embeddings (Sentence Transformers)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Free, local embeddings
    
    # ChromaDB
    CHROMA_DIR: str = "./chroma_db"
    COLLECTION_NAME: str = "sahakari_docs"
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    EXISTING_DOCS_DIR: str = "./data/documents"  # Folder for existing PDF/Excel files
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".xlsx", ".xls"]
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env file (like OPENAI_API_KEY)

settings = Settings()

# Create required directories
os.makedirs(settings.CHROMA_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EXISTING_DOCS_DIR, exist_ok=True)