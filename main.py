from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logger import logger
from app.utils.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler
)

# Initialize FastAPI app
app = FastAPI(
    title="TripMate AI - Travel Planning API",
    description="Intelligent train travel planning.",
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 70)
    logger.info("TripMate AI Backend Starting...")
    logger.info("=" * 70)
    logger.info(f"Framework: LangChain + LangGraph + Google Gemini")
    logger.info(f"API Version: {settings.API_V1_STR}")
    logger.info(f"Environment: {'Production' if not settings.API_V1_STR else 'Development'}")
    logger.info("=" * 70)
    logger.info("Features:")
    logger.info("   LangGraph workflow engine")
    logger.info("   Google Gemini AI integration")
    logger.info("   LangChain tools for IRCTC API")
    logger.info("   Intelligent intent extraction")
    logger.info("   Multi-step agent reasoning")
    logger.info("   Real-time train data")
    logger.info("=" * 70)
    logger.info("Server ready! Visit http://localhost:8000/docs for API documentation")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=" * 70)
    logger.info("Backend shutting down...")
    logger.info("=" * 70)

@app.get("/")
async def root():
    return {
        "message": "Welcome to TripMate AI Backend",
        "version": "2.0.0",
        "powered_by": "Google Gemini",
        "documentation": "/docs",
        "api_base": settings.API_V1_STR,
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )