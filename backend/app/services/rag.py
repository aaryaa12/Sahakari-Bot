from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from typing import List, Dict, Optional, Any, AsyncGenerator
from app.core.database import get_collection
from app.services.embeddings import embedding_service
from app.services.documents import document_service
from app.core.config import settings
import uuid
import logging
import requests
import hashlib
from functools import lru_cache
import asyncio

logger = logging.getLogger(__name__)

# Simple in-memory cache for query responses (max 100 cached responses)
_response_cache: Dict[str, Dict] = {}
_cache_max_size = 100


def _generate_cache_key(query: str, history: Optional[List[Dict[str, Any]]] = None) -> str:
    """Generate cache key from query and history."""
    history_str = ""
    if history:
        history_str = str([f"{m.get('role', '')}:{m.get('content', '')[:50]}" for m in history[-4:]])
    cache_input = f"{query.lower().strip()}|{history_str}"
    return hashlib.md5(cache_input.encode()).hexdigest()


def _get_cached_response(cache_key: str) -> Optional[Dict]:
    """Get cached response if available."""
    return _response_cache.get(cache_key)


def _set_cached_response(cache_key: str, response: Dict):
    """Cache response with size limit."""
    global _response_cache
    if len(_response_cache) >= _cache_max_size:
        # Remove oldest entry (simple FIFO)
        _response_cache.pop(next(iter(_response_cache)))
    _response_cache[cache_key] = response


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
        
        # Auto-select best model (prefer faster models first for better UX)
        # llama3.2:1b is fastest, phi3:mini is balanced, llama3 is most accurate
        preferred_order = ['llama3.2:1b', 'phi3:mini', 'phi3', 'llama3.2', 'llama3', 'mistral', 'llama2']
        for preferred in preferred_order:
            # Check exact match or partial match (e.g., llama3.2:1b matches llama3.2)
            for model in available_models:
                if model == preferred or model.startswith(preferred.split(':')[0]):
                    logger.info(f"Auto-selected model: {model} (optimized for speed)")
                    return model
        
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
    
    def query(self, user_query: str, top_k: Optional[int] = None, history: Optional[List[Dict[str, Any]]] = None) -> Dict:
        """Query RAG system and generate response."""
        # Check cache first for repeated queries
        cache_key = _generate_cache_key(user_query, history)
        cached = _get_cached_response(cache_key)
        if cached:
            logger.debug(f"Cache hit for query: {user_query[:50]}...")
            return cached
        
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
        max_similarity = 0.0
        
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
                    max_similarity = max(max_similarity, similarity_score)
                    
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
            history_text = self._history_text(history)
            combined_text = f"{history_text}\n{user_query}".strip()
            # If no relevant context, allow in-domain general response
            if self._is_in_domain(combined_text) or self._is_greeting(user_query):
                if self._is_legal_penalty_question(combined_text):
                    result = {
                        "answer": (
                            "I could not find legal penalty details in the current documents. "
                            "Please add the relevant act/regulation PDFs, then ask again."
                        ),
                        "citations": [],
                        "sources_count": 0
                    }
                    _set_cached_response(cache_key, result)
                    return result
                if self._is_risk_assessment_request(combined_text) and not self._has_risk_details(combined_text):
                    result = self._risk_assessment_prompt(history=history)
                    _set_cached_response(cache_key, result)
                    return result
                result = self._basic_chat(user_query, history=history)
                _set_cached_response(cache_key, result)
                return result
            result = {
                "answer": settings.RAG_OUT_OF_DOMAIN_MESSAGE,
                "citations": [],
                "sources_count": 0
            }
            _set_cached_response(cache_key, result)
            return result
        
        # If legal penalty question but context is weak, avoid unreliable answers
        if self._is_legal_penalty_question(user_query):
            legal_min_similarity = 0.4  # Reduced from 0.6 to allow more legal content
            if max_similarity < legal_min_similarity:
                result = {
                    "answer": (
                        "I could not find high-confidence legal penalty details in the current documents. "
                        "Please upload the specific act/regulation PDFs and try again."
                    ),
                    "citations": [],
                    "sources_count": 0
                }
                _set_cached_response(cache_key, result)
                return result

        # Create prompt with context - improved for accuracy
        # Build context with source information
        context_parts = []
        for i, ctx in enumerate(contexts):
            source_name = citations[i]['source'] if i < len(citations) else "Unknown"
            context_parts.append(f"[Context {i+1} from {source_name}]:\n{ctx}")
        context_text = "\n\n".join(context_parts)
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert AI assistant for cybersecurity compliance, cooperative regulation in Nepal, and legal frameworks (ETA, Cooperative Act, ISO 27001, NIST).

RESPONSE STYLE:
- Be direct, specific, and authoritative
- Use structured formatting (bullet points, sections) for clarity
- Cite specific laws, sections, penalties, and amounts when available
- Provide actionable, concrete information

CRITICAL RULES:
1. LEGAL QUESTIONS: Extract and cite exact sections, penalties, fines, imprisonment terms from documents
2. TECHNICAL QUESTIONS: Provide specific controls, frameworks, and implementation steps
3. If documents contain specific details (amounts, timeframes, sections), ALWAYS include them
4. If no specific details exist, state clearly what is NOT in the documents
5. Never give generic answers when specific details are available in context
6. Structure complex answers with clear headings and bullet points"""),
            ("human", """Context Documents:
{context}

User Question: {question}

Conversation History:
{history}

Provide a specific, well-structured answer. If the context contains laws, penalties, or specific details, include them. Format your response clearly.""")
        ])
        
        # Generate response using Ollama
        # ChatOllama works with ChatPromptTemplate directly
        try:
            messages = prompt_template.format_messages(
                context=context_text,
                question=user_query,
                history=self._history_text(history)
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
        
        result = {
            "answer": answer,
            "citations": citations,
            "sources_count": len(citations)
        }
        
        # Cache successful responses
        _set_cached_response(cache_key, result)
        return result
    
    async def query_stream(self, user_query: str, top_k: Optional[int] = None, history: Optional[List[Dict[str, Any]]] = None) -> AsyncGenerator[Dict, None]:
        """Stream query response in chunks for better UX."""
        collection_count = self.collection.count()
        
        # Get configuration values
        default_top_k = getattr(settings, 'RAG_TOP_K', 5)
        similarity_threshold = getattr(settings, 'RAG_SIMILARITY_THRESHOLD', 0.3)
        max_context_length = getattr(settings, 'RAG_MAX_CONTEXT_LENGTH', 4000)
        top_k = top_k or default_top_k
        
        # If no documents, fall back to basic non-streaming
        if collection_count == 0:
            result = self._basic_chat(user_query, history)
            yield {"type": "content", "content": result["answer"]}
            yield {"type": "done", "citations": result["citations"], "sources_count": result["sources_count"]}
            return
        
        # Retrieve context (same as non-streaming)
        query_embedding = embedding_service.embed_text(user_query)
        search_k = min(top_k * 2, collection_count)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=search_k
        )
        
        contexts = []
        citations = []
        total_context_length = 0
        
        if results["documents"] and len(results["documents"][0]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if "distances" in results else None
                
                if distance is not None:
                    similarity_score = 1 - (distance / 2.0)
                    if similarity_score < similarity_threshold:
                        continue
                else:
                    similarity_score = None
                
                doc_length = len(doc)
                if total_context_length + doc_length > max_context_length and contexts:
                    break
                
                contexts.append(doc)
                total_context_length += doc_length
                citations.append({
                    "source": metadata.get("source", "Unknown"),
                    "page": metadata.get("page", "N/A"),
                    "excerpt": doc[:200] + "..." if len(doc) > 200 else doc,
                    "relevance_score": round(similarity_score, 3) if similarity_score is not None else None
                })
                
                if len(contexts) >= top_k:
                    break
        
        # If no context, fall back
        if not contexts:
            result = self._basic_chat(user_query, history)
            yield {"type": "content", "content": result["answer"]}
            yield {"type": "done", "citations": result["citations"], "sources_count": result["sources_count"]}
            return
        
        # Build context and prompt
        context_parts = []
        for i, ctx in enumerate(contexts):
            source_name = citations[i]['source'] if i < len(citations) else "Unknown"
            context_parts.append(f"[Context {i+1} from {source_name}]:\n{ctx}")
        context_text = "\n\n".join(context_parts)
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert AI assistant for cybersecurity compliance, cooperative regulation in Nepal, and legal frameworks (ETA, Cooperative Act, ISO 27001, NIST).

RESPONSE STYLE:
- Be direct, specific, and authoritative
- Use structured formatting (bullet points, sections) for clarity
- Cite specific laws, sections, penalties, and amounts when available
- Provide actionable, concrete information

CRITICAL RULES:
1. LEGAL QUESTIONS: Extract and cite exact sections, penalties, fines, imprisonment terms from documents
2. TECHNICAL QUESTIONS: Provide specific controls, frameworks, and implementation steps
3. If documents contain specific details (amounts, timeframes, sections), ALWAYS include them
4. If no specific details exist, state clearly what is NOT in the documents
5. Never give generic answers when specific details are available in context
6. Structure complex answers with clear headings and bullet points"""),
            ("human", """Context Documents:
{context}

User Question: {question}

Conversation History:
{history}

Provide a specific, well-structured answer. If the context contains laws, penalties, or specific details, include them. Format your response clearly.""")
        ])
        
        try:
            messages = prompt_template.format_messages(
                context=context_text,
                question=user_query,
                history=self._history_text(history)
            )
            
            llm = self._get_llm()
            
            # Stream response chunks
            for chunk in llm.stream(messages):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if content:
                    yield {"type": "content", "content": content}
                    await asyncio.sleep(0)  # Allow other tasks to run
            
            # Send citations at the end
            yield {"type": "done", "citations": citations, "sources_count": len(citations)}
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield {"type": "error", "content": f"Error: {str(e)}"}
    
    def _basic_chat(self, user_query: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict:
        """General chat mode for in-domain queries when no relevant documents are found."""
        try:
            llm = self._get_llm()  # Lazy initialization
            
            # Create a simple prompt for general chat
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are Sahakari Bot, an expert AI assistant specializing in cybersecurity compliance, cooperative regulation in Nepal, and risk management.

EXPERTISE AREAS:
- Nepal legal frameworks (Cooperative Act, ETA, Nepal Rastra Bank regulations)
- International standards (ISO 27001, NIST CSF)
- Cybersecurity controls and best practices
- Insider risk and governance

RESPONSE GUIDELINES:
1. Be specific and actionable - provide concrete steps, not generic advice
2. Structure answers clearly with bullet points and sections
3. For legal questions: Cite specific acts, sections, and penalties when you know them
4. For technical questions: Provide specific controls, tools, and implementation guidance
5. For risk questions: Use clear risk levels (Low/Medium/High/Critical) with justification

If the question is outside cybersecurity/compliance scope, respond with:
\""" + settings.RAG_OUT_OF_DOMAIN_MESSAGE + "\""""),
                ("human", """User Question: {question}

Conversation History:
{history}

Provide a clear, specific, well-structured answer.""")
            ])
            
            messages = prompt_template.format_messages(
                question=user_query,
                history=self._history_text(history)
            )
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

    def _history_text(self, history: Optional[List[Dict[str, Any]]]) -> str:
        """Flatten recent conversation into a single text block."""
        if not history:
            return ""
        parts = []
        for msg in history[-8:]:
            if hasattr(msg, "role") and hasattr(msg, "content"):
                role = msg.role
                content = msg.content
            else:
                role = msg.get("role", "user")
                content = msg.get("content", "")
            if not content:
                continue
            parts.append(f"{role}: {content}")
        return "\n".join(parts)

    def _is_risk_assessment_request(self, user_query: str) -> bool:
        """Detect if user wants a cooperative cyber risk assessment."""
        query = user_query.lower()
        triggers = [
            "risk assessment", "risk evaluation", "assess risk", "evaluate risk",
            "risk rating", "risk level", "how vulnerable", "vulnerability",
            "cyber risk", "security risk", "risk score"
        ]
        return any(t in query for t in triggers)

    def _is_legal_penalty_question(self, user_query: str) -> bool:
        """Detect legal penalty or punishment questions to keep responses grounded."""
        query = user_query.lower()
        keywords = [
            "penalty", "fine", "imprisonment", "punishment", "jail",
            "legal consequence", "sentence", "offense", "offence"
        ]
        return any(keyword in query for keyword in keywords)

    def _has_risk_details(self, user_query: str) -> bool:
        """Heuristic: check if user provided enough details to rate risk."""
        query = user_query.lower()
        details = [
            "employees", "staff", "users", "branches", "core banking",
            "server", "cloud", "on-prem", "on premise", "network",
            "firewall", "antivirus", "edr", "mfa", "2fa",
            "backup", "disaster recovery", "incident", "breach",
            "training", "policy", "access control", "privilege",
            "data types", "pii", "personal data", "financial data"
        ]
        return any(d in query for d in details)

    def _risk_assessment_prompt(self, history: Optional[List[Dict[str, Any]]] = None) -> Dict:
        """Return a structured questionnaire for cooperative risk assessment."""
        try:
            llm = self._get_llm()
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are Sahakari Bot. The user wants a cybersecurity risk evaluation for their cooperative.
Ask a concise set of questions (8–10) to gather the minimum necessary details before rating risk.
Keep the questions short, clear, and practical. Use bullet points. No extra explanation."""),
                ("human", """Conversation so far:
{history}

User Question: {question}""")
            ])
            messages = prompt_template.format_messages(
                question="Please start the cooperative cybersecurity risk evaluation.",
                history=self._history_text(history)
            )
            response = llm.invoke(messages)
            answer = response.content if hasattr(response, "content") else str(response)
            return {"answer": answer, "citations": [], "sources_count": 0}
        except Exception:
            questions = [
                "How many employees and branches does your cooperative have?",
                "What core systems do you use (core banking, accounting, mobile/online services)?",
                "Where is your data hosted (on‑premise, cloud, hybrid)?",
                "Do you use MFA/2FA for staff access and admin accounts?",
                "Do you have regular backups and a disaster recovery plan?",
                "Have you had any security incidents or data breaches in the last 12 months?",
                "Do staff receive cybersecurity awareness training? How often?",
                "Do you have documented policies (access control, incident response, data privacy)?",
                "What type of sensitive data do you store (PII, financial records, member data)?"
            ]
            formatted = "To evaluate your cooperative’s cybersecurity risk, please answer:\n\n"
            formatted += "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
            formatted += "\n\nOnce you answer, I will rate risk (Low/Medium/High) and provide prioritized recommendations."
            return {"answer": formatted, "citations": [], "sources_count": 0}

    def _is_in_domain(self, user_query: str) -> bool:
        """Check if query is within the project's domain."""
        query = user_query.lower().strip()
        keywords = getattr(settings, "RAG_DOMAIN_KEYWORDS", [])
        return any(keyword in query for keyword in keywords)

    def _is_greeting(self, user_query: str) -> bool:
        """Allow basic greetings to get a friendly response."""
        query = user_query.lower().strip()
        greetings = getattr(settings, "RAG_GREETING_KEYWORDS", [])
        return any(greet in query for greet in greetings)


rag_service = RAGService()
