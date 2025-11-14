"""
Google Gemini embeddings utility using langchain
"""
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings


class EmbeddingGenerator:
    """Generates embeddings using Google Gemini"""
    
    def __init__(self):
        """Initialize Google Gemini embeddings"""
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            task_type="retrieval_document"  # Optimized for document retrieval
        )
        
        print(f"✓ Initialized Google Gemini Embeddings: {settings.EMBEDDING_MODEL}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents
        
        Args:
            texts: List of text documents
            
        Returns:
            List of embedding vectors
        """
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query
        
        Args:
            text: Query text
            
        Returns:
            Embedding vector
        """
        try:
            # Use retrieval_query task type for queries
            query_embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                task_type="retrieval_query"  # Optimized for query retrieval
            )
            return query_embeddings.embed_query(text)
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            raise