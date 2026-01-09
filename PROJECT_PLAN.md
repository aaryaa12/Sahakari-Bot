# Sahakari Bot - Project Planning Document

## 1. PROJECT OVERVIEW

**Name**: Sahakari Bot  
**Purpose**: AI chatbot for cybersecurity compliance and insider risk evaluation for cooperatives in Nepal  
**Approach**: RAG (Retrieval-Augmented Generation) - no custom model training  
**Target Users**: Single user type (compliance officers, cooperative managers)  
**Language**: English (expandable to Nepali later)

---

## 2. CORE REQUIREMENTS

### Functional Requirements

1. **User Authentication**

   - Simple login/registration system
   - JWT-based authentication
   - Session management

2. **Document Management**

   - Upload PDF documents (Nepalese regulations, compliance docs)
   - Upload Excel files (policies, risk assessments)
   - List uploaded documents
   - Store documents securely

3. **RAG Chat System**

   - Ask questions in natural language
   - Get AI-generated answers based on uploaded documents
   - Show source citations (which document, which page)
   - Context-aware responses

4. **Citation & Explainability**
   - Display source documents for every answer
   - Show relevant excerpts
   - Page/section references
   - Confidence/relevance scores

### Non-Functional Requirements

- Fast response time (<5 seconds)
- Handle documents up to 10MB
- Secure data storage
- Clean, modern UI
- Mobile-responsive

---

## 3. PROPOSED TECH STACK

### Backend

```
FastAPI (Python)
├── Pros: Fast, modern, auto API docs, async support
├── Alternatives considered: Flask (too basic), Django (too heavy)
└── Decision: ✅ FastAPI - best for AI/ML projects
```

### RAG Framework

```
LangChain
├── Pros: Industry standard, good abstractions, active community
├── Alternatives: LlamaIndex, Direct OpenAI API
└── Decision: ✅ LangChain - most mature for RAG
```

### Vector Database

```
ChromaDB
├── Pros: Lightweight, embedded, easy setup, free
├── Alternatives: Pinecone (paid), Weaviate (complex), FAISS (lower-level)
└── Decision: ✅ ChromaDB - perfect for final year project
```

### LLM & Embeddings

```
OpenAI API
├── gpt-3.5-turbo: Chat responses (fast, cheap)
├── text-embedding-ada-002: Document embeddings
├── Alternatives: Local models (Ollama, LLaMA) - slower, needs GPU
└── Decision: ✅ OpenAI - reliable, good quality
```

### Frontend

```
React.js + Tailwind CSS
├── Pros: Popular, component-based, good for chat UIs
├── Alternatives: Vue (smaller community), Angular (too complex)
└── Decision: ✅ React - best ecosystem
```

### Authentication

```
JWT (JSON Web Tokens)
├── Storage: Simple file-based for demo
├── Alternative: SQLite, PostgreSQL
└── Decision: ✅ JWT + File storage - simple for demo
```

---

## 4. SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────┐
│                   USER                          │
│              (Web Browser)                      │
└────────────────┬────────────────────────────────┘
                 │
                 │ HTTP/REST
                 │
┌────────────────▼────────────────────────────────┐
│           REACT FRONTEND                        │
│  ┌──────────────────────────────────────┐      │
│  │  • Login/Register Pages              │      │
│  │  • Chat Interface                    │      │
│  │  • Document Upload                   │      │
│  │  • Citation Display                  │      │
│  └──────────────────────────────────────┘      │
└────────────────┬────────────────────────────────┘
                 │
                 │ Axios HTTP Calls
                 │
┌────────────────▼────────────────────────────────┐
│         FASTAPI BACKEND                         │
│  ┌──────────────────────────────────────┐      │
│  │  API Routes:                         │      │
│  │  • POST /auth/register               │      │
│  │  • POST /auth/login                  │      │
│  │  • POST /chat/query                  │      │
│  │  • POST /documents/upload            │      │
│  │  • GET  /documents/list              │      │
│  └──────────────────────────────────────┘      │
│                                                  │
│  ┌──────────────────────────────────────┐      │
│  │  Services:                           │      │
│  │  • RAG Service (main logic)          │      │
│  │  • Document Processing               │      │
│  │  • Embedding Generation              │      │
│  └──────────────────────────────────────┘      │
└─────┬──────────────────┬─────────────────┬─────┘
      │                  │                 │
      │                  │                 │
      ▼                  ▼                 ▼
┌──────────┐      ┌──────────┐      ┌──────────┐
│ ChromaDB │      │ OpenAI   │      │  File    │
│ (Vector  │      │   API    │      │ Storage  │
│  Store)  │      │          │      │          │
│          │      │ • GPT-3.5│      │ • PDFs   │
│ • Docs   │      │ • Embed  │      │ • Excel  │
│ • Embeds │      │          │      │ • users  │
└──────────┘      └──────────┘      └──────────┘
```

---

## 5. DATA FLOW

### Document Upload Flow

```
1. User uploads PDF/Excel
2. Frontend sends file to /documents/upload
3. Backend:
   a. Save file to disk
   b. Extract text (PDF: pdfplumber, Excel: pandas)
   c. Split text into chunks (1000 chars, 200 overlap)
   d. Generate embeddings via OpenAI
   e. Store in ChromaDB with metadata
4. Return success to user
```

### Chat Query Flow

```
1. User asks question
2. Frontend sends to /chat/query
3. Backend:
   a. Generate embedding for question
   b. Search ChromaDB for similar chunks (top 5)
   c. Build prompt with context
   d. Call GPT-3.5 for answer
   e. Extract citations
4. Return answer + citations to frontend
5. Display answer with expandable sources
```

---

## 6. DATABASE SCHEMA

### User Storage (users.json)

```json
{
  "1": {
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "password_hash": "bcrypt_hash",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### ChromaDB Collections

```
Collection: "documents"
- IDs: UUID for each chunk
- Documents: Text chunks
- Embeddings: Vector embeddings (1536 dimensions)
- Metadata: {
    source: "filename.pdf",
    page: "5",
    chunk_index: 0,
    upload_date: "2024-01-01"
  }
```

---

## 7. SECURITY CONSIDERATIONS

1. **Authentication**: JWT tokens, HTTP-only cookies
2. **Password Storage**: Bcrypt hashing
3. **File Upload**:
   - Size limits (10MB)
   - Type validation (.pdf, .xlsx, .xls only)
   - Sanitize filenames
4. **API Protection**: All chat/document routes require auth
5. **CORS**: Only allow localhost:3000 (dev) or production domain
6. **Environment Variables**: Store API keys in .env (never commit)

---

## 8. FILE STRUCTURE

```
sahakari-bot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── core/
│   │   │   ├── config.py           # Settings
│   │   │   ├── security.py         # JWT, passwords
│   │   │   └── database.py         # ChromaDB setup
│   │   ├── api/
│   │   │   ├── auth.py             # Login/register
│   │   │   ├── chat.py             # RAG queries
│   │   │   └── documents.py        # Upload/list
│   │   ├── services/
│   │   │   ├── rag.py              # Main RAG logic
│   │   │   ├── documents.py        # PDF/Excel processing
│   │   │   └── embeddings.py       # OpenAI embeddings
│   │   └── models/
│   │       └── schemas.py          # Pydantic models
│   ├── requirements.txt
│   ├── .env                        # OPENAI_API_KEY
│   └── .env.example
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   └── Chat.js
│   │   ├── components/
│   │   │   ├── ChatMessage.js
│   │   │   ├── Citation.js
│   │   │   └── FileUpload.js
│   │   ├── services/
│   │   │   └── api.js              # Axios client
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
│
├── data/
│   ├── uploads/                    # PDF/Excel files
│   ├── chroma_db/                  # Vector database
│   └── users.json                  # User data
│
└── README.md
```

---

## 9. IMPLEMENTATION PHASES

### Phase 1: Backend Foundation (Day 1-2)

- [ ] Setup FastAPI project structure
- [ ] Create configuration system (.env)
- [ ] Implement authentication (JWT)
- [ ] Create user registration/login endpoints
- [ ] Test with Postman/curl

### Phase 2: Document Management (Day 2-3)

- [ ] File upload endpoint
- [ ] PDF text extraction (pdfplumber)
- [ ] Excel text extraction (pandas)
- [ ] Save files to disk
- [ ] List documents endpoint

### Phase 3: RAG System (Day 3-5)

- [ ] Setup ChromaDB
- [ ] Implement text chunking
- [ ] OpenAI embedding generation
- [ ] Store documents in ChromaDB
- [ ] Implement similarity search
- [ ] Build prompt engineering
- [ ] Generate responses with GPT-3.5
- [ ] Extract and format citations

### Phase 4: Frontend (Day 5-7)

- [ ] Setup React project
- [ ] Create login/register pages
- [ ] Implement authentication flow
- [ ] Build chat interface
- [ ] File upload component
- [ ] Citation display component
- [ ] Connect to backend APIs

### Phase 5: Testing & Polish (Day 7-8)

- [ ] End-to-end testing
- [ ] Error handling
- [ ] Loading states
- [ ] UI improvements
- [ ] Documentation
- [ ] Demo preparation

---

## 10. DEPENDENCIES

### Backend (requirements.txt)

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic-settings==2.1.0
langchain==0.1.0
langchain-openai==0.0.2
chromadb==0.4.22
pdfplumber==0.10.3
pandas==2.1.4
openpyxl==3.1.2
python-multipart==0.0.6
```

### Frontend (package.json)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "tailwindcss": "^3.3.6"
  }
}
```

---

## 11. POTENTIAL CHALLENGES & SOLUTIONS

| Challenge                  | Solution                                     |
| -------------------------- | -------------------------------------------- |
| Large PDFs slow to process | Async processing, progress indicators        |
| OpenAI API rate limits     | Implement retry logic, caching               |
| Poor answer quality        | Better prompt engineering, adjust chunk size |
| Irrelevant citations       | Tune similarity threshold, increase top_k    |
| File upload failures       | Validate before upload, clear error messages |

---

## 12. SUCCESS CRITERIA

✅ **Must Have:**

- User can register and login
- User can upload PDF and Excel files
- User can ask questions and get AI responses
- Responses show source citations
- System is secure (auth, file validation)

🎯 **Nice to Have:**

- Chat history persistence
- Multiple documents in one query
- Export answers as PDF
- Admin panel
- Usage analytics

---

## 13. NEXT STEPS

Before we start coding, please confirm:

1. **Is this architecture acceptable?**
2. **Any features to add/remove?**
3. **Do you have an OpenAI API key?** (Required for embeddings + GPT)
4. **Any specific Nepalese regulations you want to include as test data?**
5. **Preferred deployment target?** (Local only, Cloud, Docker)

Once confirmed, we'll build this step-by-step, testing each phase before moving to the next.

---

**Questions or changes needed?** Let me know and we'll adjust the plan!
