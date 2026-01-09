from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from typing import List, Dict, Tuple
from app.core.database import get_collection
from app.services.embedding_service import EmbeddingService
from app.services.document_service import DocumentService
from app.core.config import settings
import uuid
import os


class RAGService:
    """Service for RAG (Retrieval-Augmented Generation) operations."""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.document_service = DocumentService()
        self.collection = get_collection()
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def ingest_document(self, file_path: str) -> Dict:
        """Process and ingest a document into the vector database."""
        # Extract text from document
        document_chunks = self.document_service.process_document(file_path)
        
        all_texts = []
        all_metadatas = []
        all_ids = []
        
        for chunk in document_chunks:
            # Split into smaller chunks if needed
            texts = self.text_splitter.split_text(chunk["text"])
            
            for i, text in enumerate(texts):
                chunk_id = str(uuid.uuid4())
                all_texts.append(text)
                all_metadatas.append({
                    "source": chunk["source"],
                    "page": str(chunk["page"]),
                    "type": chunk["type"],
                    "chunk_index": i
                })
                all_ids.append(chunk_id)
        
        # Generate embeddings
        embeddings = self.embedding_service.embed_documents(all_texts)
        
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
            "source": os.path.basename(file_path)
        }
    
    def query(self, user_query: str, top_k: int = 5) -> Dict:
        """Query the RAG system and generate a response."""
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(user_query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
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
                    "type": metadata.get("type", "Unknown"),
                    "excerpt": doc[:200] + "..." if len(doc) > 200 else doc,
                    "relevance_score": round(1 - distance, 3) if distance else None
                })
        
        # Create prompt with context
        context_text = "\n\n".join([f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(contexts)])
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert AI assistant specializing in cybersecurity compliance and insider risk evaluation for cooperatives in Nepal. 
            You analyze Nepalese regulations and international cybersecurity frameworks to provide accurate, explainable guidance.
            
            Use the provided context documents to answer questions. Always cite your sources. If the context doesn't contain enough information, 
            say so clearly. Be precise and professional in your responses."""),
            ("human", """Context from documents:
{context}

User Question: {question}

Please provide a comprehensive answer based on the context above. Include specific references to the source documents when possible.""")
        ])
        
        # Generate response
        messages = prompt_template.format_messages(
            context=context_text,
            question=user_query
        )
        
        response = self.llm.invoke(messages)
        answer = response.content
        
        return {
            "answer": answer,
            "citations": citations,
            "context_used": len(contexts)
        }
