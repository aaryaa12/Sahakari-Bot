from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, chat, documents

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI chatbot for cybersecurity compliance and insider risk evaluation",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["authentication"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(documents.router, prefix=settings.API_V1_STR, tags=["documents"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to Sahakari Bot API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
