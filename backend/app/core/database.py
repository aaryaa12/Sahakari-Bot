import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
import os

# Ensure persist directory exists
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(
    path=settings.CHROMA_PERSIST_DIRECTORY,
    settings=ChromaSettings(
        anonymized_telemetry=False
    )
)

def get_collection():
    """Get or create the ChromaDB collection."""
    try:
        collection = chroma_client.get_collection(name=settings.COLLECTION_NAME)
    except:
        collection = chroma_client.create_collection(name=settings.COLLECTION_NAME)
    return collection
