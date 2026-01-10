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
                self.llm = ChatOllama(
                    model=model_name,
                    temperature=0.7,
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
    
    def ingest_document(self, file_path: str) -> Dict:
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
                    all_metadatas.append({
                        "source": chunk["source"],
                        "page": str(chunk["page"]),
                        "type": chunk["type"],
                        "chunk_index": str(i)
                    })
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
    
    def query(self, user_query: str, top_k: int = 5) -> Dict:
        """Query RAG system and generate response."""
        # Check if collection has documents
        collection_count = self.collection.count()
        
        # If no documents, use basic chat mode (Ollama only)
        if collection_count == 0:
            return self._basic_chat(user_query)
        
        # Generate query embedding
        query_embedding = embedding_service.embed_text(user_query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection_count)
        )
        
        # Extract relevant context
        contexts = []
        citations = []
        
        if results["documents"] and len(results["documents"][0]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if "distances" in results else None
                
                contexts.append(doc)
                citations.append({
                    "source": metadata.get("source", "Unknown"),
                    "page": metadata.get("page", "N/A"),
                    "excerpt": doc[:200] + "..." if len(doc) > 200 else doc,
                    "relevance_score": round(1 - distance, 3) if distance else None
                })
        
        if not contexts:
            return {
                "answer": "I couldn't find relevant information in the uploaded documents to answer your question. Please try rephrasing or upload more documents.",
                "citations": [],
                "sources_count": 0
            }
        
        # Create prompt with context
        context_text = "\n\n".join([f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(contexts)])
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert AI assistant specializing in cybersecurity compliance and insider risk evaluation for cooperatives in Nepal. 
You analyze regulations and cybersecurity frameworks to provide accurate, explainable guidance.

Use the provided context documents to answer questions. Always be specific and cite information from the context.
If the context doesn't contain enough information, say so clearly. Be precise and professional."""),
            ("human", """Context from uploaded documents:
{context}

User Question: {question}

Provide a comprehensive answer based on the context above. Be specific and reference the relevant information.""")
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
