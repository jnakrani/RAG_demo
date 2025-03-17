"""
PDF Processing Utilities

This module provides utility functions for processing PDF documents,
including loading and splitting PDFs into manageable chunks for
further processing.
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_pdf(pdf_path: str):
    """
    Load and split a PDF file into chunks for processing.

    This function performs the following operations:
    1. Initializes a text splitter with specified parameters
    2. Loads the PDF file
    3. Splits the PDF content into manageable chunks

    Args:
        pdf_path (str): Path to the PDF file to be processed

    Returns:
        List[Document]: List of document chunks, where each chunk contains:
            - page_content: The text content of the chunk
            - metadata: Original metadata plus chunk-specific information

    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If there's an error processing the PDF

    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    chunks = text_splitter.split_documents(pages)

    return chunks

