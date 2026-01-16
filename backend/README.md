# Sahakari Bot - Backend

FastAPI backend for cybersecurity compliance RAG chatbot.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the server:

```bash
uvicorn app.main:app --reload
```

3. Open API docs:

```
http://localhost:8000/docs
```

## Document Management

### Adding Documents

Place your documents (PDF, CSV, TXT, Excel) in:

```
data/documents/
```

Documents are automatically processed on server startup.

### Reload Documents

To reload documents after adding new files:

```bash
POST /api/v1/documents/reload?force=false
```

- `force=false`: Only process new/modified files (default)
- `force=true`: Reprocess all files

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user

### Chat

- `POST /api/v1/chat/query` - Query the RAG system

### Documents

- `GET /api/v1/documents/list` - List documents
- `POST /api/v1/documents/reload` - Reload documents
- `GET /api/v1/documents/status` - Get vector DB status

### Health

- `GET /health` - Health check
- `GET /` - API info

## Test Authentication

1. Register a user:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"test","password":"password123"}'
```

2. Login:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

You'll receive a token to use for authenticated requests!
