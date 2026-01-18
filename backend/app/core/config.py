from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[3]


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
    
    # RAG Accuracy Settings
    RAG_TOP_K: int = 5  # Number of chunks to retrieve
    RAG_SIMILARITY_THRESHOLD: float = 0.3  # Minimum similarity score (0-1, lower = more strict)
    RAG_TEMPERATURE: float = 0.2  # Lower = more factual, less creative (0.0-1.0)
    RAG_MAX_CONTEXT_LENGTH: int = 4000  # Maximum characters in context to prevent overflow
    RAG_OUT_OF_DOMAIN_MESSAGE: str = (
        "I can help with cybersecurity compliance, insider risk management, "
        "cooperative regulation in Nepal, governance/audit, data privacy, and network security. "
        "Your question appears outside this scope. Please ask a question related to those areas."
    )
    RAG_DOMAIN_KEYWORDS: List[str] = [
        "cybersecurity", "cyber security", "information security", "infosec",
        "compliance", "regulation", "regulatory", "policy", "policies",
        "insider risk", "insider threat", "insider",
        "cooperative", "co-operative", "nepal", "sahakari",
        "governance", "audit", "auditing", "assurance",
        "data privacy", "privacy", "personal data", "pii",
        "network security", "network", "firewall", "access control",
        "risk", "risk management", "vulnerability", "assessment", "rating",
        "incident", "breach", "response", "controls", "framework"
    ]
    RAG_GREETING_KEYWORDS: List[str] = [
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
        "greetings"
    ]
    
    # Documents
    DOCUMENTS_DIR: str = str(PROJECT_ROOT / "data" / "documents")  # Folder for documents (PDF, CSV, TXT, Excel)
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB (for reference)
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".xlsx", ".xls", ".csv", ".txt"]
    CSV_MAX_ROWS: int = 5000  # Limit CSV rows to process per file
    CSV_CHUNK_ROWS: int = 1000  # CSV chunk size for incremental processing
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env file (like OPENAI_API_KEY)

settings = Settings()

# Create required directories
os.makedirs(settings.CHROMA_DIR, exist_ok=True)
docs_dir = Path(settings.DOCUMENTS_DIR).resolve()
os.makedirs(docs_dir, exist_ok=True)
settings.DOCUMENTS_DIR = str(docs_dir)