"""
PDF Question Answering API

This module provides a FastAPI application for managing PDF documents and performing
question-answering operations using ChromaDB and LangChain.

The API supports:
- PDF document upload and chunking
- Document storage and retrieval
- Question answering based on stored documents
- Document management operations
"""

from utils.logging_utils import setup_logging
from routes.chroma_routes import router as chroma_router
from routes.qa_routes import router as qa_router
from routes.genral import router as general_router
from routes.user_routes import router as user_router

from database import Base, engine
from user_model import User


from fastapi import FastAPI

Base.metadata.create_all(bind=engine)

logger = setup_logging()

app = FastAPI()

app.include_router(general_router)
app.include_router(chroma_router)
app.include_router(qa_router)
app.include_router(user_router)
