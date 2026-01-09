# Sahakari Bot

A web-based AI chatbot application for cybersecurity compliance and insider risk evaluation for cooperatives in Nepal. The system uses Retrieval-Augmented Generation (RAG) to analyze Nepalese regulations and international cybersecurity frameworks, providing accurate, explainable guidance.

## Tech Stack

- **Frontend**: React.js with Tailwind CSS
- **Backend**: FastAPI (Python)
- **RAG Engine**: LangChain
- **Vector Database**: ChromaDB
- **Authentication**: JWT tokens
- **Document Processing**: PDF (pdfplumber) and Excel (pandas)

## Project Structure

```
sahakari-bot/
├── frontend/          # React frontend application
├── backend/           # FastAPI backend application
├── data/              # Document storage (PDFs, Excel files)
└── docker-compose.yml # Docker orchestration
```

## Features

- 🔐 User authentication (registration/login)
- 💬 AI-powered chat interface with RAG
- 📄 Document upload and processing (PDF, Excel)
- 📚 Source citations with document references
- 🔍 Compliance checking and risk assessment
- 📊 Explainable AI responses

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker and Docker Compose (optional)

### Backend Setup

1. Navigate to backend directory:

```bash
cd backend
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

5. Update `.env` with your configuration (API keys, etc.)

6. Run the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start development server:

```bash
npm start
```

The application will be available at `http://localhost:3000`

### Docker Setup (Optional)

```bash
docker-compose up --build
```

## API Documentation

Once the backend is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

### Backend (.env)

```
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your-openai-api-key
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

## Usage

1. Register a new account or login
2. Upload compliance documents (PDF/Excel) through the interface
3. Ask questions about cybersecurity compliance or insider risk
4. View source citations for each response

## License

This project is developed as a final year project.
