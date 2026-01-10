from sentence_transformers import SentenceTransformer
from app.core.config import settings
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers (free, local)."""
    
    def __init__(self):
        self.model = None  # Lazy initialization
        self._model_name = getattr(settings, 'EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    
    def _get_model(self):
        """Lazy initialization of embedding model."""
        if self.model is None:
            # Using all-MiniLM-L6-v2: Fast, good quality, 384 dimensions
            # Downloads automatically on first use (~80MB)
            logger.info(f"Loading embedding model: {self._model_name}")
            try:
                self.model = SentenceTransformer(self._model_name)
                logger.info(f"✓ Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading embedding model: {e}")
                raise
        return self.model
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        model = self._get_model()  # Lazy initialization
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (batch processing)."""
        model = self._get_model()  # Lazy initialization
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()


embedding_service = EmbeddingService()
