# Sahakari Bot - Setup Guide

## Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn
- OpenAI API key (for embeddings and LLM)

## Quick Start

### 1. Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the `backend` directory:
```bash
cp .env.example .env
```

6. Edit `.env` and add your configuration:
```env
SECRET_KEY=your-secret-key-min-32-characters-long
OPENAI_API_KEY=your-openai-api-key-here
```

7. Run the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 2. Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

### 3. Using the Application

1. Open `http://localhost:3000` in your browser
2. Register a new account or login
3. Upload compliance documents (PDF or Excel files)
4. Start asking questions about cybersecurity compliance or insider risk

## Docker Setup (Alternative)

If you prefer using Docker:

1. Make sure Docker and Docker Compose are installed
2. Create `.env` file in the `backend` directory with your configuration
3. Run:
```bash
docker-compose up --build
```

This will start both frontend and backend services.

## Project Structure

```
sahakari-bot/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Core configuration
│   │   ├── models/      # Pydantic models
│   │   └── services/    # Business logic
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API client
│   │   └── context/     # React context
│   └── package.json
└── data/                # Document storage
    └── documents/
```

## Troubleshooting

### Backend Issues

- **Import errors**: Make sure you're in the virtual environment and all dependencies are installed
- **ChromaDB errors**: The `chroma_db` directory will be created automatically
- **OpenAI API errors**: Verify your API key is correct in `.env`

### Frontend Issues

- **Tailwind CSS not working**: Run `npm install` again to ensure all dev dependencies are installed
- **API connection errors**: Make sure the backend is running on port 8000
- **CORS errors**: Check that `BACKEND_CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`

## Next Steps

1. Add your compliance documents (PDF/Excel) to the `data/documents/` directory or upload them through the UI
2. The system will automatically process and index them
3. Start asking questions!

## Notes

- User data is stored in `users.json` (simple file-based storage for demo purposes)
- ChromaDB data is stored in `chroma_db/` directory
- Uploaded documents are stored in `data/documents/` directory
