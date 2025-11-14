"""
Retriever Node - Performs semantic search in vector database
"""
from typing import List, Dict, Any
from app.utils.vector_store import VectorStore
from app.config import settings


class Retriever:
    """Retrieves relevant documents from vector store"""
    
    def __init__(self):
        """Initialize vector store"""
        self.vector_store = VectorStore()
    
    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for query
        
        Args:
            query: User's question
            top_k: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        try:
            results = self.vector_store.query(query, top_k=top_k)
            return results
        except Exception as e:
            print(f"Retrieval error: {e}")
            return []