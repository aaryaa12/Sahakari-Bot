from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api import auth, chat, documents
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load existing documents on startup."""
    logger.info("Starting up Sahakari Bot...")
    try:
        from app.services.startup import load_existing_documents
        load_existing_documents()
    except Exception as e:
        logger.warning(f"Could not load existing documents during startup: {e}")
        logger.info("You can still upload documents via the web interface.")
    logger.info("Startup complete!")
    yield
    # Cleanup code can go here if needed
    logger.info("Shutting down Sahakari Bot...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI chatbot for cybersecurity compliance and insider risk evaluation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware - Allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["Chat"])
app.include_router(documents.router, prefix=settings.API_V1_STR, tags=["Documents"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to Sahakari Bot API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Sahakari Bot"}
