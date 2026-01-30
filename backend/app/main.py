from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.config import get_settings
from app.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 Starting ShopBot AI Backend...")
    print(f"Environment: {settings.environment}")
    print(f"Debug Mode: {settings.debug}")
    
    # Initialize database
    init_db()
    
    yield
    print("👋 Shutting down ShopBot AI Backend...")


# Initialize FastAPI app
app = FastAPI(
    title="ShopBot AI API",
    description="AI-powered customer support for e-commerce",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "ok",
        "message": "ShopBot AI API is running",
        "version": "0.1.0",
        "environment": settings.environment
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api": "operational",
        "database": "not connected yet",  # We'll update this when we add DB
        "ai_service": "ready"
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# Import and include routers
from app.routes import chat, payment
# from app.routes import auth  # We'll add this later
# app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(payment.router, prefix="/api/payment", tags=["payment"])


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
