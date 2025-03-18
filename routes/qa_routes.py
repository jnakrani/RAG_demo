from controler.chromadb_controler import ChromaDBController
from utils.llm_setup import setup_qa_system, process_qa_response
from utils.logging_utils import setup_logging
from database import get_db
from authorization.auth import require_permission, get_current_active_user
from user_model import User

from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

logger = setup_logging()

router = APIRouter(prefix="/qa", tags=["qa"])

def get_document_permission(action: str):
    return require_permission(action, "Document")

@router.post("/ask")
@get_document_permission("read")
async def question_answer(
    query: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Process a question and generate an answer based on stored documents.

    Args:
        query (str): The question to be answered

    Returns:
        dict: Contains the answer and relevant source information

    Raises:
        HTTPException: If search or answer generation fails
    """
    chroma_controller = ChromaDBController()
    try:
        try:
            results = chroma_controller.query(query=query)
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")
        
        context = [doc.page_content for doc in results]
        context = "\n".join(context)
        qa_system = setup_qa_system()
        
        try:
            qa_response = qa_system.invoke({"context": context, "question": query})
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")
        
        return process_qa_response(qa_response, results)
    
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")
