import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
import os

# Disable telemetry noise
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(
    path=settings.CHROMA_DIR,
    settings=ChromaSettings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)


def get_collection():
    """Get or create the ChromaDB collection with optimized HNSW parameters."""
    try:
        collection = chroma_client.get_collection(name=settings.COLLECTION_NAME)
    except:
        # Create collection with optimized HNSW parameters for small to medium collections
        collection = chroma_client.create_collection(
            name=settings.COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine",
                "hnsw:construction_ef": 100,  # Lower for faster indexing
                "hnsw:search_ef": 100,        # Lower for faster search
                "hnsw:M": 16                  # Lower for small collections
            }
        )
    return collection
