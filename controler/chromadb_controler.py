"""
ChromaDB Controller Module

This module provides a controller class for managing document operations with ChromaDB,
including adding, querying, and managing documents with vector embeddings.
"""

import os
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

class ChromaDBController:
    """
    A controller class for managing ChromaDB operations.

    This class provides methods for document management, including adding documents,
    querying the database, and managing document lifecycle in ChromaDB with vector embeddings.

    Attributes:
        embeddings: OpenAIEmbeddings instance for text embedding generation
        chroma_db: ChromaDB instance for document storage and retrieval
    """

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    def __init__(self):
        """
        Initialize ChromaDBController with a new ChromaDB instance.
        """
        self.chroma_db = Chroma(
            collection_name="test",
            embedding_function=self.embeddings,
            persist_directory="chroma_db",
        )

    def add_documents(self, documents: List[Document], ids: Optional[List[str]] = None) -> List[str]:
        """
        Add documents to the ChromaDB collection.
        
        Args:
            documents: List of Document objects to add to the database
            ids: Optional list of unique identifiers for the documents
            
        Returns:
            List[str]: List of IDs for the added documents
            
        Raises:
            Exception: If there's an error adding documents to the database
        """
        return self.chroma_db.add_documents(documents=documents, ids=ids)

    def query(self, query: str, n_results: int = 5) -> List[Document]:
        """
        Query the ChromaDB collection using similarity search.
        
        Args:
            query: Search query string to find relevant documents
            n_results: Number of results to return (default: 5)
            
        Returns:
            List[Document]: List of relevant Document objects matching the query
            
        Raises:
            Exception: If there's an error performing the search
        """
        results = self.chroma_db.similarity_search(
            query=query,
            k=n_results
        )
        return results
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists in the ChromaDB collection.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if file exists, False otherwise
            
        Raises:
            Exception: If there's an error checking file existence
        """
        return self.chroma_db.get(file_path)
    
    def delete_documents(self, file_name: str) -> dict:
        """
        Delete documents from the ChromaDB collection by file name.
        
        Args:
            file_name: Name of the file to delete
            
        Returns:
            dict: Message indicating successful deletion
            
        Raises:
            Exception: If no documents are found or if there's an error during deletion
        """
        try:
            matching_docs = self.chroma_db.get(
                where={"file_name": file_name}
            )
            if not matching_docs or not matching_docs['ids']:
                raise Exception(f"No documents found with file name: {file_name}")
            
            self.chroma_db.delete(
                ids=matching_docs['ids']
            )
            
            return {"message": f"Successfully deleted all chunks for file: {file_name}"}
            
        except Exception as e:
            raise Exception(f"Error deleting documents: {str(e)}")
    
    def list_documents(self) -> List[dict]:
        """
        Get a list of unique documents in the collection.
        
        Returns:
            List[dict]: List of dictionaries containing document information
                Each dictionary contains:
                - document_id: Unique identifier for the document
                - file_name: Name of the file
                - file_type: Type of the document
                
        Raises:
            Exception: If there's an error retrieving the document list
        """
        try:
            results = self.chroma_db.get()
            
            if not results or not results['metadatas']:
                return []
            
            unique_docs = {}
            
            for metadata in results['metadatas']:
                if metadata and 'file_name' in metadata:
                    doc_id = metadata.get('document_id', '')
                    if doc_id not in unique_docs:
                        unique_docs[doc_id] = {
                            'document_id': doc_id,
                            'file_name': metadata['file_name'],
                            'file_type': metadata.get('file_type', ''),
                        }
            
            return list(unique_docs.values())
        
        except Exception as e:
            raise Exception(f"Error listing documents: {str(e)}")

    def clear_collection(self) -> None:
        """
        Clear all documents from the ChromaDB collection.
        
        Raises:
            Exception: If there's an error clearing the collection
        """
        self.chroma_db.delete_collection()
    