from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from typing import List, Dict, Optional
from app.core.database import get_collection
from app.services.embeddings import embedding_service
from app.services.documents import document_service
from app.core.config import settings
import uuid
import logging
import requests

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG operations."""
    
    def __init__(self):
        self.collection = get_collection()
        self.llm = None  # Will be initialized lazily on first use
        self._model_name = getattr(settings, 'OLLAMA_MODEL', None)  # None means auto-detect
        self._base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def _check_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self._base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama connection check failed: {e}")
            return False
    
    def _get_available_models(self) -> List[str]:
        """Get list of available Ollama models."""
        try:
            response = requests.get(f"{self._base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                return models
        except Exception as e:
            logger.error(f"Error fetching Ollama models: {e}")
        return []
    
    def _detect_model(self) -> str:
        """Auto-detect and return the best available model."""
        # Check if Ollama is running
        if not self._check_ollama_connection():
            raise ConnectionError(
                f"Cannot connect to Ollama at {self._base_url}. "
                "Make sure Ollama is running: 'ollama serve'"
            )
        
        # Get available models
        available_models = self._get_available_models()
        
        if not available_models:
            raise ValueError(
                "No Ollama models found. Please download a model first:\n"
                "  ollama pull llama3\n"
                "  or\n"
                "  ollama pull mistral\n"
                "  or\n"
                "  ollama pull llama2"
            )
        
        # If specific model requested, use it if available
        if self._model_name:
            if self._model_name in available_models:
                logger.info(f"Using requested model: {self._model_name}")
                return self._model_name
            else:
                logger.warning(
                    f"Requested model '{self._model_name}' not found. "
                    f"Available models: {', '.join(available_models)}"
                )
        
        # Auto-select best model (prefer llama3, then mistral, then llama2, then first available)
        preferred_order = ['llama3', 'mistral', 'llama2', 'llama3.2', 'phi3']
        for preferred in preferred_order:
            if preferred in available_models:
                logger.info(f"Auto-selected model: {preferred}")
                return preferred
        
        # Use first available model
        selected = available_models[0]
        logger.info(f"Using first available model: {selected}")
        return selected
    
    def _get_llm(self):
        """Lazy initialization of Ollama LLM with auto-detection."""
        if self.llm is None:
            try:
                # Auto-detect model if not specified or if specified model not available
                model_name = self._detect_model()
                
                logger.info(f"Initializing Ollama with model: {model_name}")
                # Use lower temperature for more factual, accurate responses
                temperature = getattr(settings, 'RAG_TEMPERATURE', 0.2)
                self.llm = ChatOllama(
                    model=model_name,
                    temperature=temperature,
                    base_url=self._base_url,
                    timeout=120.0  # Increase timeout for slower systems
                )
                logger.info(f"✓ Ollama LLM initialized successfully with model: {model_name}")
            except ConnectionError as e:
                logger.error(str(e))
                raise
            except ValueError as e:
                logger.error(str(e))
                raise
            except Exception as e:
                logger.error(f"Error initializing Ollama: {e}")
                logger.error("Troubleshooting:")
                logger.error("  1. Make sure Ollama is running: 'ollama serve'")
                logger.error("  2. Check if you have models: 'ollama list'")
                logger.error("  3. Download a model: 'ollama pull llama3'")
                raise
        return self.llm
    
    def ingest_document(self, file_path: str, file_hash: Optional[str] = None) -> Dict:
        """Process and ingest document into vector database."""
        # Extract text from document
        document_chunks = document_service.process_document(file_path)
        
        all_texts = []
        all_metadatas = []
        all_ids = []
        
        for chunk in document_chunks:
            # Split into smaller chunks
            texts = self.text_splitter.split_text(chunk["text"])
            
            for i, text in enumerate(texts):
                if text.strip():  # Only add non-empty chunks
                    chunk_id = str(uuid.uuid4())
                    all_texts.append(text)
                    metadata = {
                        "source": chunk["source"],
                        "page": str(chunk["page"]),
                        "type": chunk["type"],
                        "chunk_index": str(i)
                    }
                    # Add file hash if provided (for change detection)
                    if file_hash:
                        metadata["file_hash"] = file_hash
                    all_metadatas.append(metadata)
                    all_ids.append(chunk_id)
        
        if not all_texts:
            raise ValueError("No text extracted from document")
        
        # Generate embeddings
        embeddings = embedding_service.embed_documents(all_texts)
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=all_texts,
            metadatas=all_metadatas,
            ids=all_ids
        )
        
        return {
            "status": "success",
            "chunks_ingested": len(all_texts),
            "source": document_chunks[0]["source"] if document_chunks else "unknown"
        }
    
    def query(self, user_query: str, top_k: Optional[int] = None) -> Dict:
        """Query RAG system and generate response."""
        # Check if collection has documents
        collection_count = self.collection.count()
        
        # If no documents, use basic chat mode (Ollama only)
        if collection_count == 0:
            return self._basic_chat(user_query)
        
        # Get configuration values
        default_top_k = getattr(settings, 'RAG_TOP_K', 5)
        similarity_threshold = getattr(settings, 'RAG_SIMILARITY_THRESHOLD', 0.3)
        max_context_length = getattr(settings, 'RAG_MAX_CONTEXT_LENGTH', 4000)
        
        top_k = top_k or default_top_k
        
        # Generate query embedding
        query_embedding = embedding_service.embed_text(user_query)
        
        # Search in ChromaDB - retrieve more than needed for filtering
        search_k = min(top_k * 2, collection_count)  # Get 2x for filtering
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=search_k
        )
        
        # Extract relevant context with similarity filtering
        contexts = []
        citations = []
        total_context_length = 0
        
        if results["documents"] and len(results["documents"][0]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if "distances" in results else None
                
                # Calculate similarity score (1 - distance, where distance is typically 0-2)
                # For cosine similarity, distance of 0 = perfect match, 2 = opposite
                if distance is not None:
                    # Normalize distance to similarity score (0-1)
                    # Cosine distance ranges from 0 to 2, so similarity = 1 - (distance/2)
                    similarity_score = 1 - (distance / 2.0)
                    
                    # Filter by similarity threshold
                    if similarity_score < similarity_threshold:
                        logger.debug(f"Skipping low-relevance chunk (similarity: {similarity_score:.3f} < {similarity_threshold})")
                        continue
                else:
                    similarity_score = None
                
                # Check context length limit
                doc_length = len(doc)
                if total_context_length + doc_length > max_context_length and contexts:
                    logger.debug(f"Reached context length limit ({max_context_length}), stopping retrieval")
                    break
                
                contexts.append(doc)
                total_context_length += doc_length
                
                citations.append({
                    "source": metadata.get("source", "Unknown"),
                    "page": metadata.get("page", "N/A"),
                    "excerpt": doc[:200] + "..." if len(doc) > 200 else doc,
                    "relevance_score": round(similarity_score, 3) if similarity_score is not None else None
                })
                
                # Stop if we have enough high-quality contexts
                if len(contexts) >= top_k:
                    break
        
        if not contexts:
            return {
                "answer": "I couldn't find relevant information in the uploaded documents to answer your question. The documents may not contain information about this topic, or the question might need to be rephrased. Please try:\n\n1. Rephrasing your question with different keywords\n2. Asking a more specific question\n3. Uploading additional relevant documents",
                "citations": [],
                "sources_count": 0
            }
        
        # Create prompt with context - improved for accuracy
        # Build context with source information
        context_parts = []
        for i, ctx in enumerate(contexts):
            source_name = citations[i]['source'] if i < len(citations) else "Unknown"
            context_parts.append(f"[Context {i+1} from {source_name}]:\n{ctx}")
        context_text = "\n\n".join(context_parts)
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert AI assistant specializing in cybersecurity compliance and insider risk evaluation for cooperatives in Nepal. 
You analyze regulations and cybersecurity frameworks to provide accurate, explainable guidance.

CRITICAL INSTRUCTIONS:
1. ONLY use information from the provided context documents to answer the question
2. If the context doesn't contain enough information to fully answer the question, clearly state what information is missing
3. DO NOT make up or infer information that is not explicitly stated in the context
4. Be specific and cite which document/source your information comes from
5. If you're uncertain, say so clearly
6. Be precise, factual, and professional"""),
            ("human", """Use ONLY the following context from uploaded documents to answer the question. Do not use any external knowledge.

Context Documents:
{context}

User Question: {question}

Instructions:
- Answer based ONLY on the context provided above
- If the context doesn't contain the answer, say "The provided documents do not contain information about [topic]. Please try rephrasing your question or upload relevant documents."
- Be specific and reference which document your information comes from
- Provide a clear, accurate answer based solely on the context""")
        ])
        
        # Generate response using Ollama
        # ChatOllama works with ChatPromptTemplate directly
        try:
            messages = prompt_template.format_messages(
                context=context_text,
                question=user_query
            )
            
            llm = self._get_llm()  # Lazy initialization
            response = llm.invoke(messages)
            # ChatOllama returns AIMessage object with content attribute
            answer = response.content if hasattr(response, 'content') else str(response)
        except ConnectionError as e:
            logger.error(f"Ollama connection error: {e}")
            answer = f"❌ Cannot connect to Ollama. Please make sure Ollama is running:\n\n1. Open a terminal and run: ollama serve\n2. Keep that terminal open\n3. Try your question again"
        except ValueError as e:
            logger.error(f"Ollama model error: {e}")
            answer = f"❌ Model error: {str(e)}\n\nPlease download a model:\n  ollama pull llama3\n  or\n  ollama pull mistral"
        except Exception as e:
            logger.error(f"Error generating response from Ollama: {e}")
            answer = f"I apologize, but I encountered an error: {str(e)}\n\nPlease check:\n1. Ollama is running: 'ollama serve'\n2. You have a model: 'ollama list'\n3. If not, download one: 'ollama pull llama3'"
        
        return {
            "answer": answer,
            "citations": citations,
            "sources_count": len(citations)
        }
    
    def _basic_chat(self, user_query: str) -> Dict:
        """Basic chat mode when no documents are available - uses Ollama directly."""
        try:
            llm = self._get_llm()  # Lazy initialization
            
            # Create a simple prompt for general chat
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are Sahakari Bot, a helpful AI assistant specializing in cybersecurity compliance and insider risk evaluation for cooperatives in Nepal. 
You provide friendly, professional assistance. If asked about compliance or regulations, mention that you can provide more detailed answers once documents are uploaded."""),
                ("human", "{question}")
            ])
            
            messages = prompt_template.format_messages(question=user_query)
            response = llm.invoke(messages)
            answer = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "answer": answer,
                "citations": [],
                "sources_count": 0
            }
        except ConnectionError as e:
            logger.error(f"Ollama connection error: {e}")
            return {
                "answer": f"❌ Cannot connect to Ollama. Please make sure Ollama is running:\n\n1. Open a terminal and run: ollama serve\n2. Keep that terminal open\n3. Try your question again",
                "citations": [],
                "sources_count": 0
            }
        except ValueError as e:
            logger.error(f"Ollama model error: {e}")
            return {
                "answer": f"❌ Model error: {str(e)}\n\nPlease download a model:\n  ollama pull llama3\n  or\n  ollama pull mistral",
                "citations": [],
                "sources_count": 0
            }
        except Exception as e:
            logger.error(f"Error in basic chat: {e}")
            return {
                "answer": f"I apologize, but I encountered an error: {str(e)}\n\nPlease check:\n1. Ollama is running: 'ollama serve'\n2. You have a model: 'ollama list'\n3. If not, download one: 'ollama pull llama3'",
                "citations": [],
                "sources_count": 0
            }


rag_service = RAGService()
