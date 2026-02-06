from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from typing import List, Dict, Optional, Any, AsyncGenerator
from app.core.database import get_collection
from app.services.embeddings import embedding_service
from app.services.documents import document_service
from app.services.intent_router import detect_intent
from app.services.hybrid_retrieval import hybrid_retrieve
from app.services.constrained_retrieval import constrained_retrieve
from app.services.numeric_validator import sanitize_penalty_response, validate_amounts
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
        # Handle both objects and dictionaries
        def get_msg_parts(m):
            if hasattr(m, 'role') and hasattr(m, 'content'):
                return f"{m.role}:{str(m.content)[:50]}"
            elif isinstance(m, dict):
                return f"{m.get('role', '')}:{m.get('content', '')[:50]}"
            return ""
        history_str = str([get_msg_parts(m) for m in history[-4:]])
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
        """Process and ingest document into vector database with section-aware metadata."""
        logger.info(f"🔍 START ingest_document: {file_path}")
        
        # Extract text from document
        logger.info(f"   Extracting document chunks...")
        document_chunks = document_service.process_document(file_path)
        logger.info(f"✅ Got {len(document_chunks)} chunks from document service")
        
        # Import legal classifier
        from app.services.legal_classifier import legal_classifier
        
        all_texts = []
        all_metadatas = []
        all_ids = []
        
        for idx, chunk in enumerate(document_chunks):
            # Check if this is a section-aware chunk (has metadata)
            has_section_metadata = "metadata" in chunk and chunk["metadata"].get("has_section_structure", False)
            
            if has_section_metadata:
                # Section chunks from legal parser - already sub-chunked
                chunk_id = str(uuid.uuid4())
                all_texts.append(chunk["text"])
                
                # LEGAL CLASSIFICATION (new step)
                if (idx + 1) % 10 == 0:
                    logger.info(f"   Classifying chunk {idx+1}/{len(document_chunks)}...")
                
                try:
                    classification = legal_classifier.classify_section(
                        section_text=chunk["text"],
                        section_number=chunk["metadata"]["section_number"],
                        section_title=chunk["metadata"].get("section_title", ""),
                        act_name=chunk["metadata"]["act_name"]
                    )
                    legal_type = classification["legal_type"]
                    legal_scope = classification["legal_scope"]
                except Exception as e:
                    logger.warning(f"Classification failed for Section {chunk['metadata']['section_number']}: {e}")
                    legal_type = "procedure"  # Default fallback
                    legal_scope = "general"
                
                # Preserve all metadata from legal parser + add classification
                metadata = {
                    "source": chunk["source"],
                    "page": str(chunk["page"]),
                    "type": chunk["type"],
                    "act_name": chunk["metadata"]["act_name"],
                    "section_number": chunk["metadata"]["section_number"],
                    "section_title": chunk["metadata"].get("section_title", ""),
                    "page_range": chunk["metadata"].get("page_range", ""),
                    "chunk_index": chunk["metadata"].get("chunk_index", 0),
                    "has_section_structure": True,
                    # NEW: Legal classification metadata
                    "legal_type": legal_type,
                    "legal_scope": legal_scope
                }
                
                # Include chapter if present
                if chunk["metadata"].get("chapter_number"):
                    metadata["chapter_number"] = chunk["metadata"]["chapter_number"]
                
                if file_hash:
                    metadata["file_hash"] = file_hash
                
                all_metadatas.append(metadata)
                all_ids.append(chunk_id)
            else:
                # Legacy: split into smaller chunks for non-legal documents
                texts = self.text_splitter.split_text(chunk["text"])
                
                for i, text in enumerate(texts):
                    if text.strip():
                        chunk_id = str(uuid.uuid4())
                        all_texts.append(text)
                        metadata = {
                            "source": chunk["source"],
                            "page": str(chunk["page"]),
                            "type": chunk["type"],
                            "chunk_index": str(i),
                            "has_section_structure": False
                        }
                        if file_hash:
                            metadata["file_hash"] = file_hash
                        all_metadatas.append(metadata)
                        all_ids.append(chunk_id)
        
        if not all_texts:
            raise ValueError("No text extracted from document")
        
        logger.info(f"🔍 START embedding generation for {len(all_texts)} chunks")
        
        # Generate embeddings in batches to show progress
        batch_size = 10
        embeddings = []
        
        for i in range(0, len(all_texts), batch_size):
            batch_end = min(i + batch_size, len(all_texts))
            batch_texts = all_texts[i:batch_end]
            
            logger.info(f"   Embedding batch {i//batch_size + 1}/{(len(all_texts) + batch_size - 1)//batch_size} ({i+1}-{batch_end}/{len(all_texts)})...")
            batch_embeddings = embedding_service.embed_documents(batch_texts)
            embeddings.extend(batch_embeddings)
        
        logger.info(f"✅ DONE embedding generation: {len(embeddings)} embeddings")
        
        # Add to ChromaDB
        logger.info(f"🔍 START chroma add ({len(all_texts)} documents)")
        self.collection.add(
            embeddings=embeddings,
            documents=all_texts,
            metadatas=all_metadatas,
            ids=all_ids
        )
        logger.info(f"✅ DONE chroma add")
        
        logger.info(f"✅ DONE ingest_document: {len(all_texts)} chunks ingested")
        
        return {
            "status": "success",
            "chunks_ingested": len(all_texts),
            "source": document_chunks[0]["source"] if document_chunks else "unknown"
        }
    
    def _add_legal_header(self, answer: str, citations: list, user_query: str) -> str:
        """Add Act + Section/Chapter label at the top of legal answers."""
        if not citations:
            return answer
        
        # Extract section or chapter number from query
        from app.services.hybrid_retrieval import extract_section_number, extract_chapter_number
        section_num = extract_section_number(user_query)
        chapter_num = extract_chapter_number(user_query)
        
        # Get act name from first citation
        act_name = citations[0].get("source", "Legal Document")
        
        # Build header
        header = ""
        if section_num:
            header = f"**{act_name} — Section {section_num}**\n\n"
        elif chapter_num:
            header = f"**{act_name} — Chapter {chapter_num}**\n\n"
        else:
            # For concept questions, just add act name
            header = f"**Source: {act_name}**\n\n"
        
        return header + answer
    
    def _identify_target_law(self, user_query: str) -> str:
        """Identify which specific law the question is about."""
        query_lower = user_query.lower()
        
        # Direct law mentions
        if 'electronic transaction' in query_lower or 'eta' in query_lower:
            return "Electronic Transaction Act 2063"
        if 'cooperative act' in query_lower or 'cooperatives act' in query_lower:
            return "Cooperatives Act 2074"
        if 'banking offence' in query_lower or 'bopa' in query_lower:
            return "Banking Offences and Punishment Act"
        
        # Topic-based law routing
        legal_topics = {
            "Cooperatives Act 2074": [
                "register cooperative", "cooperative formation", "cooperative board",
                "cooperative member", "cooperative audit", "cooperative merger",
                "cooperative dissolution", "unauthorized loan", "cooperative fund",
                "cooperative management", "cooperative share", "cooperative election"
            ],
            "Electronic Transaction Act 2063": [
                "digital signature", "electronic document", "electronic record",
                "cyber crime", "hacking", "data breach", "unauthorized access",
                "electronic authentication", "certification authority"
            ]
        }
        
        for law, keywords in legal_topics.items():
            if any(keyword in query_lower for keyword in keywords):
                return law
        
        return ""  # No specific law identified
    
    
    def query(self, user_query: str, top_k: Optional[int] = None, history: Optional[List[Dict[str, Any]]] = None) -> Dict:
        """Query RAG system and generate response."""
        # Check cache first for repeated queries
        cache_key = _generate_cache_key(user_query, history)
        cached = _get_cached_response(cache_key)
        if cached:
            logger.debug(f"Cache hit for query: {user_query[:50]}...")
            return cached
        
        # STEP 1: Classify intent BEFORE retrieval (simple keyword-based)
        intent = detect_intent(user_query)
        logger.info(f"Intent detected: {intent} for query: {user_query[:50]}...")
        
        # ============================================================================
        # ROUTING LAYER: Call appropriate module based on intent
        # ============================================================================
        
        # Route to Security Advisory Module (no RAG, no legal pipeline)
        if intent == 'SECURITY':
            from app.services.security_advisor import security_advisor
            result = security_advisor.get_security_advice(user_query, history)
            _set_cached_response(cache_key, result)
            return result
        
        # ============================================================================
        # LEGAL MODE PIPELINE STARTS HERE (unchanged - do not modify below)
        # ============================================================================
        
        # STEP 2: Route based on intent
        if intent == 'GENERAL':  # General conversation
            result = self._general_chat_response(user_query, history)
            _set_cached_response(cache_key, result)
            return result
        
        if intent == 'COOP':  # Cooperative operational guidance
            result = self._advisory_response(user_query, history, intent)
            _set_cached_response(cache_key, result)
            return result
        
        # STEP 3: For legal questions (intent LEGAL), use constrained retrieval
        # Check if collection has documents
        collection_count = self.collection.count()
        
        if collection_count == 0:
            result = {"answer": "I need the relevant legal documents to answer this accurately. Please add the law/regulation to the document library.", "citations": [], "sources_count": 0}
            _set_cached_response(cache_key, result)
            return result
        
        # STEP 4: Constrained retrieval (structure-first filtering + semantic search)
        default_top_k = getattr(settings, 'RAG_TOP_K', 4)  # Reduced to 4 for more focused results
        top_k = top_k or default_top_k
        
        # Use new constrained retrieval system
        retrieval_result = constrained_retrieve(user_query, top_k=top_k)
        contexts = retrieval_result["contexts"]
        citations = retrieval_result["citations"]
        retrieval_method = retrieval_result["retrieval_method"]
        filters_applied = retrieval_result.get("filters_applied", {})
        
        logger.info(f"Retrieved {len(contexts)} contexts using {retrieval_method}")
        logger.info(f"Filters applied: {filters_applied}")
        
        # Check query type FIRST (chapter or section)
        from app.services.hybrid_retrieval import extract_section_number, extract_chapter_number
        section_num = extract_section_number(user_query)
        chapter_num = extract_chapter_number(user_query)
        
        # Handle chapter query (returns all sections in chapter)
        if chapter_num and not section_num:
            if not contexts:
                from app.services.hybrid_retrieval import identify_target_act
                target_act = identify_target_act(user_query)
                act_display = target_act if target_act else "the provided legal documents"
                
                result = {
                    "answer": f"I cannot find Chapter {chapter_num} in {act_display}.",
                    "citations": [],
                    "sources_count": 0
                }
                _set_cached_response(cache_key, result)
                return result
            
            # Generate chapter summary from all retrieved sections
            law_name = citations[0]["source"] if citations else "Legal Documents"
            
            chapter_summary_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a legal compliance assistant for Sahakari Bot. Summarize the chapter using ONLY the provided text.

BEHAVIORAL CONTRACT:
- Use ONLY the retrieved text
- Never add external knowledge
- Never say "consult a lawyer" or disclaimers
- Be structured and deterministic

OUTPUT FORMAT (for chapter summaries):

**Chapter Overview:**
[2-3 sentences on what this chapter addresses]

**Key Sections:**
- Section X: [Brief description]
- Section Y: [Brief description]

**Main Legal Requirements:**
[Bullet list of key obligations and provisions from the chapter]

**What is NOT specified:**
[What the chapter does not address]

**Citation:**
{law_name}, Chapter {chapter_num}

Use ONLY the provided text. Be precise."""),
                ("human", """Chapter {chapter_num} content from {law_name}:

{context}

Question: {question}

Provide a structured chapter summary.""")
            ])
            
            context_parts = []
            for i, ctx in enumerate(contexts):
                source_name = citations[i]['source'] if i < len(citations) else "Unknown"
                section_info = citations[i].get('page', 'Unknown')
                context_parts.append(f"[{section_info}]:\n{ctx}")
            context_text = "\n\n".join(context_parts)
            
            try:
                messages = chapter_summary_prompt.format_messages(
                    context=context_text,
                    question=user_query,
                    law_name=law_name,
                    chapter_num=chapter_num
                )
                
                llm = self._get_llm()
                response = llm.invoke(messages)
                answer = response.content if hasattr(response, 'content') else str(response)
                
                result = {
                    "answer": answer,
                    "citations": citations,
                    "sources_count": len(citations)
                }
                _set_cached_response(cache_key, result)
                return result
            except Exception as e:
                logger.error(f"Error generating chapter summary: {e}")
                answer = f"Error generating chapter summary: {str(e)}"
                result = {
                    "answer": answer,
                    "citations": citations,
                    "sources_count": len(citations)
                }
                _set_cached_response(cache_key, result)
                return result
        
        # Handle section query
        if section_num:
            # This is a section query - must be deterministic
            if not contexts:
                # No results for section query - deterministic refusal
                from app.services.hybrid_retrieval import identify_target_act
                target_act = identify_target_act(user_query)
                act_display = target_act if target_act else "the provided legal documents"
                
                result = {
                    "answer": f"I cannot find Section {section_num} in {act_display}.",
                    "citations": [],
                    "sources_count": 0
                }
                _set_cached_response(cache_key, result)
                return result
            
            # Section query with results - verify it's the right section
            correct_section_found = False
            for citation in citations:
                if citation.get("page") == f"Section {section_num}":
                    correct_section_found = True
                    break
            
            if not correct_section_found:
                # Retrieved something but not the requested section
                from app.services.hybrid_retrieval import identify_target_act
                target_act = identify_target_act(user_query)
                act_display = target_act if target_act else "the provided legal documents"
                
                result = {
                    "answer": f"I cannot find Section {section_num} in {act_display}.",
                    "citations": [],
                    "sources_count": 0
                }
                _set_cached_response(cache_key, result)
                return result
        elif not contexts:
            # FALLBACK RULE: No matching sections found
            # Check if this was a legal question that failed retrieval
            if intent == 'LEGAL':
                # For legal questions, give specific message about document coverage
                result = {
                    "answer": "The provided legal documents do not contain a provision addressing this specific matter.",
                    "citations": [],
                    "sources_count": 0
                }
                _set_cached_response(cache_key, result)
                return result
            
            # Non-legal queries with no contexts
            history_text = self._history_text(history)
            combined_text = f"{history_text}\n{user_query}".strip()
            
            if self._is_in_domain(combined_text) or self._is_greeting(user_query):
                if self._is_legal_penalty_question(combined_text):
                    result = {
                        "answer": "The provided legal documents do not contain a provision addressing this specific matter.",
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
            # Calculate max similarity from citations
            max_similarity = max([c.get("relevance_score", 0) for c in citations]) if citations else 0
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
        
        # Identify law name from citations for better prompting
        law_name = citations[0]["source"] if citations else "Legal Documents"
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You analyze legal documents for cooperatives. Answer using the text provided below.

FORMAT (include all 5 sections):

**1) Legal meaning (plain language)**
[2-4 sentences explaining the provision]

**2) Legal effect / obligations**
- [Bullet list of obligations]

**3) Practical implications for a cooperative (Kathmandu Valley context)**
- [3-6 implementation steps]

**4) What the Act does NOT specify**
- [List what is not defined]

**5) Evidence (from provided documents)**
Quote: "[short quote]"
Source: {law_name}, Section [number from text]

EXAMPLE:

**1) Legal meaning (plain language)**
This requires cooperatives to maintain financial records and conduct annual audits.

**2) Legal effect / obligations**
- MUST maintain complete financial records
- MUST conduct annual audit by licensed auditor

**3) Practical implications for a cooperative (Kathmandu Valley context)**
- Appoint auditor before fiscal year end
- Maintain accounting ledgers
- Submit audit report by deadline

**4) What the Act does NOT specify**
- Specific record format
- Late submission penalties

**5) Evidence (from provided documents)**
Quote: "Every cooperative shall maintain proper books and conduct annual audit"
Source: Cooperatives Act 2074, Section 45

Answer based only on the text."""),
            ("human", """Legal text:

{context}

Question: {question}

Answer in 5-section format.""")
        ])
        
        # Generate response using Ollama
        try:
            messages = prompt_template.format_messages(
                context=context_text,
                question=user_query,
                history=self._history_text(history),
                law_name=law_name
            )
            
            llm = self._get_llm()  # Lazy initialization
            response = llm.invoke(messages)
            answer = response.content if hasattr(response, 'content') else str(response)
            
            # Add legal header (Act + Section/Chapter label) for legal answers
            if intent == 'LEGAL' and citations:
                answer = self._add_legal_header(answer, citations, user_query)
            
            # Apply numeric sanity check for penalty responses
            if any(keyword in user_query.lower() for keyword in ["penalty", "fine", "punishment", "imprisonment"]):
                validation = validate_amounts(answer)
                if not validation["valid"]:
                    logger.warning(f"Numeric mismatch detected: {validation['reason']}")
                    answer = sanitize_penalty_response(answer)
                    logger.info("Applied numeric sanitization to response")
            
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
        # Check cache first
        cache_key = _generate_cache_key(user_query, history)
        cached = _get_cached_response(cache_key)
        if cached:
            logger.debug(f"Cache hit (stream mode) for query: {user_query[:50]}...")
            yield {"type": "content", "content": cached["answer"]}
            yield {"type": "done", "citations": cached["citations"], "sources_count": cached["sources_count"]}
            return
        
        # Intent routing
        intent = detect_intent(user_query)
        logger.info(f"Intent detected (stream): {intent}")
        
        # ============================================================================
        # ROUTING LAYER: Call appropriate module based on intent
        # ============================================================================
        
        # Route to Security Advisory Module (no RAG, no legal pipeline)
        if intent == 'SECURITY':
            from app.services.security_advisor import security_advisor
            result = security_advisor.get_security_advice(user_query, history)
            yield {"type": "content", "content": result["answer"]}
            yield {"type": "done", "citations": result["citations"], "sources_count": result["sources_count"]}
            return
        
        # ============================================================================
        # LEGAL MODE PIPELINE STARTS HERE (unchanged - do not modify below)
        # ============================================================================
        
        if intent == 'GENERAL':
            result = self._general_chat_response(user_query, history)
            yield {"type": "content", "content": result["answer"]}
            yield {"type": "done", "citations": result["citations"], "sources_count": result["sources_count"]}
            return
        
        if intent == 'COOP':
            result = self._advisory_response(user_query, history, intent)
            yield {"type": "content", "content": result["answer"]}
            yield {"type": "done", "citations": result["citations"], "sources_count": result["sources_count"]}
            return
        
        # For LEGAL intent, use constrained retrieval
        collection_count = self.collection.count()
        if collection_count == 0:
            result = self._basic_chat(user_query, history)
            yield {"type": "content", "content": result["answer"]}
            yield {"type": "done", "citations": result["citations"], "sources_count": result["sources_count"]}
            return
        
        # Constrained retrieval (streaming)
        default_top_k = getattr(settings, 'RAG_TOP_K', 4)
        top_k = top_k or default_top_k
        
        retrieval_result = constrained_retrieve(user_query, top_k=top_k)
        contexts = retrieval_result["contexts"]
        citations = retrieval_result["citations"]
        
        # Check if this is a section query FIRST
        from app.services.section_splitter import extract_section_number_from_query
        section_num = extract_section_number_from_query(user_query)
        
        if section_num:
            # This is a section query - must be deterministic
            if not contexts:
                # No results - deterministic refusal
                from app.services.hybrid_retrieval import identify_target_act
                target_act = identify_target_act(user_query)
                act_display = target_act if target_act else "the provided legal documents"
                
                answer = f"I cannot find Section {section_num} in {act_display}."
                yield {"type": "content", "content": answer}
                yield {"type": "done", "citations": [], "sources_count": 0}
                return
            
            # Verify it's the right section
            correct_section_found = False
            for citation in citations:
                if citation.get("page") == f"Section {section_num}":
                    correct_section_found = True
                    break
            
            if not correct_section_found:
                from app.services.hybrid_retrieval import identify_target_act
                target_act = identify_target_act(user_query)
                act_display = target_act if target_act else "the provided legal documents"
                
                answer = f"I cannot find Section {section_num} in {act_display}."
                yield {"type": "content", "content": answer}
                yield {"type": "done", "citations": [], "sources_count": 0}
                return
        elif not contexts:
            # Non-section query with no contexts - fall back
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
        
        law_name = citations[0]["source"] if citations else "Legal Documents"
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You analyze legal documents for cooperatives. Answer using the text provided below.

FORMAT (include all 5 sections):

**1) Legal meaning (plain language)**
[2-4 sentences explaining the provision]

**2) Legal effect / obligations**
- [Bullet list of obligations]

**3) Practical implications for a cooperative (Kathmandu Valley context)**
- [3-6 implementation steps]

**4) What the Act does NOT specify**
- [List what is not defined]

**5) Evidence (from provided documents)**
Quote: "[short quote]"
Source: {law_name}, Section [number from text]

EXAMPLE:

**1) Legal meaning (plain language)**
This requires cooperatives to maintain financial records and conduct annual audits.

**2) Legal effect / obligations**
- MUST maintain complete financial records
- MUST conduct annual audit by licensed auditor

**3) Practical implications for a cooperative (Kathmandu Valley context)**
- Appoint auditor before fiscal year end
- Maintain accounting ledgers
- Submit audit report by deadline

**4) What the Act does NOT specify**
- Specific record format
- Late submission penalties

**5) Evidence (from provided documents)**
Quote: "Every cooperative shall maintain proper books and conduct annual audit"
Source: Cooperatives Act 2074, Section 45

Answer based only on the text."""),
            ("human", """Legal text:

{context}

Question: {question}

Answer in 5-section format.""")
        ])
        
        try:
            messages = prompt_template.format_messages(
                context=context_text,
                question=user_query,
                history=self._history_text(history),
                law_name=law_name
            )
            
            llm = self._get_llm()
            
            # Collect full response for numeric validation
            full_response = ""
            
            # Add legal header first (for streaming)
            if intent == 'LEGAL' and citations:
                header = self._add_legal_header("", citations, user_query)
                if header:
                    yield {"type": "content", "content": header}
            
            # Stream response chunks
            for chunk in llm.stream(messages):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if content:
                    full_response += content
                    yield {"type": "content", "content": content}
                    await asyncio.sleep(0)  # Allow other tasks to run
            
            # Apply numeric sanity check after streaming completes
            if any(keyword in user_query.lower() for keyword in ["penalty", "fine", "punishment", "imprisonment"]):
                validation = validate_amounts(full_response)
                if not validation["valid"]:
                    logger.warning(f"Numeric mismatch detected in streaming response")
            
            # Send citations at the end
            yield {"type": "done", "citations": citations, "sources_count": len(citations)}
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield {"type": "error", "content": f"Error: {str(e)}"}
    
    def _general_chat_response(self, user_query: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict:
        """Handle general conversation (greetings, unrelated topics)."""
        try:
            llm = self._get_llm()
            prompt = ChatPromptTemplate.from_messages([
                ("system", """GENERAL MODE - Normal conversational assistant.

BEHAVIORAL CONTRACT:
1. Respond naturally and friendly to greetings
2. Answer general questions conversationally
3. Be helpful and professional
4. If topic is unrelated to your expertise, gently suggest cybersecurity/compliance topics

RESTRICTIONS:
- DO NOT refuse to answer greetings or small talk
- DO NOT cite laws for non-legal questions
- DO NOT say "I cannot help with that" for greetings

Be a normal, friendly assistant."""),
                ("human", "{question}")
            ])
            messages = prompt.format_messages(question=user_query)
            response = llm.invoke(messages)
            answer = response.content if hasattr(response, 'content') else str(response)
            return {"answer": answer, "citations": [], "sources_count": 0}
        except Exception as e:
            logger.error(f"General chat error: {e}")
            return {"answer": "Hello! I'm here to help with cybersecurity, compliance, and cooperative management questions. How can I assist you today?", "citations": [], "sources_count": 0}
    
    def _advisory_response(self, user_query: str, history: Optional[List[Dict[str, Any]]] = None, intent: str = 'SECURITY') -> Dict:
        """Provide cybersecurity or operational advice without forcing document retrieval."""
        try:
            llm = self._get_llm()
            
            if intent == 'SECURITY':  # Cybersecurity advice
                system_msg = """SECURITY MODE - You provide practical cybersecurity and risk management guidance for cooperatives.

YOUR ROLE:
- Answer ALL security and risk management questions directly and helpfully
- Provide technical security advice and best practices
- Address insider threats, access control, data protection, and operational security
- Recommend specific controls: access control, monitoring, segregation of duties, audit trails
- Explain HOW to implement protections (step-by-step)
- Give practical recommendations for cooperative environments
- Reference technical standards (ISO 27001, NIST CSF, CIS Controls) when helpful

INSIDER RISK PROTECTION includes:
- Access control and least privilege
- Segregation of duties (no single person controls entire transaction)
- Regular audits and monitoring
- Background checks for key positions
- Dual authorization for critical transactions
- Activity logging and review
- Policy enforcement and training

IMPORTANT:
- "Insider risk" is a LEGITIMATE business concern, not illegal activity
- Protecting against insider threats is STANDARD governance practice
- Answer these questions with practical controls and procedures
- DO NOT refuse questions about risk management or security
- DO NOT cite laws unless specifically asked
- Be direct, helpful, and actionable

Provide PRACTICAL guidance. NEVER refuse legitimate security questions."""
            else:  # Cooperative operational guidance
                system_msg = """COOPERATIVE OPERATIONAL MODE - You provide management and governance guidance for cooperatives.

YOUR ROLE:
- Answer ALL cooperative management questions directly and helpfully
- Provide practical operational advice for running cooperatives
- Recommend best practices for governance, meetings, member services, audits
- Explain processes and management procedures
- Address risk management, internal controls, and operational security
- Be direct and actionable

GOVERNANCE & RISK MANAGEMENT includes:
- Board oversight and accountability
- Internal controls and checks & balances
- Segregation of duties
- Financial controls and audit
- Member communication and transparency
- Policy development and enforcement
- Training and capacity building

IMPORTANT:
- Questions about risk management, controls, and governance are LEGITIMATE
- These are STANDARD cooperative management topics
- Answer with best practices from cooperative management principles
- DO NOT refuse questions about governance, controls, or risk management
- DO NOT cite laws unless specifically asked
- Be practical and helpful

Provide PRACTICAL operational guidance. NEVER refuse legitimate management questions."""
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_msg),
                ("human", """Previous conversation:
{history}

Question: {question}

Provide clear, actionable guidance.""")
            ])
            
            messages = prompt.format_messages(
                question=user_query,
                history=self._history_text(history)
            )
            response = llm.invoke(messages)
            answer = response.content if hasattr(response, 'content') else str(response)
            return {"answer": answer, "citations": [], "sources_count": 0}
        except Exception as e:
            logger.error(f"Advisory response error: {e}")
            return {"answer": "I can help with cybersecurity and compliance guidance. Please ask a specific question.", "citations": [], "sources_count": 0}
    
    def _basic_chat(self, user_query: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict:
        """General chat mode for in-domain queries when no relevant documents are found."""
        try:
            llm = self._get_llm()  # Lazy initialization
            
            # Create a simple prompt for general chat
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are Sahakari Bot, an expert AI assistant for:
- Cybersecurity compliance
- Insider risk management
- Cooperative regulation in Nepal
- Governance and audit
- Data privacy
- Network security

You provide accurate, practical guidance using general knowledge in these areas.

If the user wants a cooperative cyber risk evaluation, do this:
1) Ask the minimum necessary questions to assess risk (size, systems, data types, controls, recent incidents, staff training, backups, access control).
2) Provide a clear risk rating (Low/Medium/High) ONLY after enough info is provided.
3) Provide prioritized recommendations.

If the question is outside this scope, respond with:
\""" + settings.RAG_OUT_OF_DOMAIN_MESSAGE + "\""""),
                ("human", """Conversation so far:
{history}

User Question: {question}""")
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
            # Handle both object types (with attributes) and dictionaries
            if hasattr(msg, "role") and hasattr(msg, "content"):
                # It's an object with attributes
                role = msg.role
                content = msg.content
            elif isinstance(msg, dict):
                # It's a dictionary
                role = msg.get("role", "user")
                content = msg.get("content", "")
            else:
                # Unknown type, skip
                continue
            
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
