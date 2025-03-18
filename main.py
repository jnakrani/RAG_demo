"""
PDF Question Answering API

This module provides a FastAPI application for managing PDF documents and performing
question-answering operations using ChromaDB and LangChain.

The API supports:
- PDF document upload and chunking
- Document storage and retrieval
- Question answering based on stored documents
- Document management operations
- Role-based access control
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from utils.logging_utils import setup_logging
from routes.chroma_routes import router as chroma_router
from routes.qa_routes import router as qa_router
from routes.genral import router as general_router
from routes.user_routes import router as user_router
from routes.role_routes import router as role_router
from database import Base, engine
from authorization.auth import initialize_oso
import traceback

# Initialize logging
logger = setup_logging()

# Create FastAPI app with debug mode
app = FastAPI(
    title="PDF Question Answering API",
    description="API for document management and question answering with RBAC",
    version="1.0.0",
    debug=True  # Enable debug mode
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

try:
    # Initialize Oso
    initialize_oso()
    logger.info("Oso initialization successful")
except Exception as e:
    logger.error(f"Failed to initialize Oso: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions and provide detailed error information in debug mode"""
    error_detail = str(exc)
    if app.debug:
        error_detail = {
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "path": request.url.path,
            "method": request.method,
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
        }
        logger.error(f"Detailed error: {error_detail}")
    else:
        logger.error(f"Error: {error_detail}")
    
    return JSONResponse(
        status_code=500,
        content={"detail": error_detail if app.debug else "Internal Server Error"}
    )

# Include routers
app.include_router(general_router)
app.include_router(chroma_router)
app.include_router(qa_router)
app.include_router(user_router)
app.include_router(role_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
