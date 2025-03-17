"""
LLM Setup and Response Processing Module

This module provides functionality for setting up and managing the Language Model (LLM)
question-answering system. It includes functions for initializing the QA system and
processing responses from the LLM.

The module handles:
- QA system initialization with custom prompts
- Response processing and formatting
- Token usage tracking
- Error handling and logging
"""
import json
from typing import Dict, Any, List

from utils.logging_utils import setup_logging

from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from fastapi import HTTPException

logger = setup_logging()

def setup_qa_system() -> object:
    """
    Initialize and configure the Question-Answering system.

    Sets up a QA chain with:
    - Custom prompt template for context-based answering
    - GPT-4 model configuration
    - JSON response formatting

    Returns:
        object: Configured QA chain ready for question processing

    Raises:
        Exception: If setup fails due to configuration or API issues
    """
    try:
        template = """You are a helpful assistant answering questions based on the documents provided. 
        Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        - Always give answer in json format, Do not add any other information in the response.
        Context: {context}
        
        Question: {question}

        answer: {{answer}}

        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        model = ChatOpenAI(
            model_name="gpt-4o-mini",
        )
        
        chain = prompt | model
        return chain
    except Exception as e:
        logger.error(f"Failed to setup QA system: {str(e)}", exc_info=True)
        raise

def process_qa_response(response, query_results):
    """
    Process and format the QA system response with metadata and token usage.

    This function:
    1. Extracts and formats the response content
    2. Processes token usage statistics
    3. Formats relevant document metadata
    4. Handles various error cases

    Args:
        response (LLMResult): Raw response from the QA system
        query_results (List[Document]): List of relevant documents used for the answer

    Returns:
        Dict[str, Any]: Formatted response containing:
            - response_content: Parsed JSON response
            - token_usage: Token consumption statistics
            - metadatas: Relevant document metadata

    Raises:
        HTTPException: If response parsing fails or format is invalid
    """
    metadata = [
            {
                "metadata": {
                    "file_name": doc.metadata.get("file_name"),
                    "file_type": doc.metadata.get("file_type"),
                    "total_pages": doc.metadata.get("total_pages")
                }
            }
            for doc in query_results
        ]
    try:
        response_dict = response.content.replace("```", "").replace("json", "").replace("Response:", "")
        response_dict = json.loads(response_dict)
    except json.JSONDecodeError as je:
        logger.error(f"Failed to parse response JSON: {str(je)}")
        return HTTPException(status_code=500, detail={"success": False, "message": "Invalid response format"})
    except AttributeError as ae:
        logger.error(f"Invalid response object: {str(ae)}")
        return HTTPException(status_code=500, detail={"success": False, "message": "Invalid response object"})
        
    try:
        input_tokens = response.response_metadata.get('token_usage', {}).get('prompt_tokens', 0)
        output_tokens = response.response_metadata.get('token_usage', {}).get('completion_tokens', 0)
        total_tokens = response.response_metadata.get('token_usage', {}).get('total_tokens', 0)
        
        logger.debug(f"Token usage - Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}")
    except AttributeError as ae:
        logger.warning(f"Could not retrieve token usage: {str(ae)}")
        input_tokens = output_tokens = total_tokens = 0

    return {
        "response_content": response_dict,
        "token_usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        },
        "metadatas": metadata
    }
