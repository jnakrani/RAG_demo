import os
import uuid

from utils.utils import split_pdf
from controler.chromadb_controler import ChromaDBController
from utils.logging_utils import setup_logging

from fastapi import UploadFile, File, HTTPException, APIRouter

logger = setup_logging()

router = APIRouter(tags=["ChromaDB"])

@router.get("/list_documents")
async def list_documents():
    """
    Retrieve a list of all documents stored in the database.

    Returns:
        dict: Contains message, total documents count, and list of documents

    Raises:
        HTTPException: If there's an error retrieving documents
    """
    try:
        chroma_controller = ChromaDBController()
        documents = chroma_controller.list_documents()

        logger.info(f"Successfully retrieved {len(documents)} documents")
        return {
            "message": "Documents retrieved successfully",
            "total_documents": len(documents),
            "documents": documents
        }
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")
    
@router.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF file into ChromaDB.

    The function:
    1. Validates the file type
    2. Saves the file temporarily
    3. Splits the PDF into chunks
    4. Stores chunks in ChromaDB with metadata
    5. Cleans up temporary files

    Args:
        file (UploadFile): The PDF file to be uploaded

    Returns:
        dict: Contains success message, document ID, and chunk information

    Raises:
        HTTPException: If file is not PDF or processing fails
    """
    chroma_controller = ChromaDBController()
    
    if not file.filename.endswith('.pdf'):
        logger.error("Invalid file type uploaded")
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        doc_uuid = str(uuid.uuid4())

        file_path = file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        chunks = split_pdf(file_path)
        
        chunk_ids = []
        for i, chunk in enumerate(chunks):
            chunk_uuid = str(uuid.uuid4())
            chunk_ids.append(chunk_uuid)
            chunk.metadata = {
                "file_name": file.filename,
                "file_type": "pdf",
                "document_id": doc_uuid,
                "chunk_id": chunk_uuid,
            }

        stored_ids = chroma_controller.add_documents(documents=chunks, ids=chunk_ids)
        
        os.remove(file_path)
        logger.info(f"PDF processed successfully, {len(stored_ids)} chunks stored")
        return {
                "message": "PDF processed successfully",
                "document_id": doc_uuid,
                "chunks_stored": len(stored_ids),
                "chunk_ids": stored_ids
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.delete("/delete_documents")
async def delete_documents(file_name: str):
    """
    Delete documents from the database by file name.

    Args:
        file_name (str): Name of the file to delete

    Returns:
        dict: Success message

    Raises:
        HTTPException: If deletion fails
    """
    chroma_controller = ChromaDBController()
    try:
        chroma_controller.delete_documents(file_name)
        logger.info(f"Documents deleted successfully: {file_name}")
        return {"message": "Documents deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting documents: {str(e)}")

@router.delete("/clear_collection")
async def clear_collection():
    """
    Clear all documents from the collection.

    Returns:
        dict: Success message

    Raises:
        HTTPException: If clearing collection fails
    """
    chroma_controller = ChromaDBController()
    try:
        chroma_controller.clear_collection()
        logger.info("Collection cleared successfully")
        return {"message": "Collection cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing collection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing collection: {str(e)}")
