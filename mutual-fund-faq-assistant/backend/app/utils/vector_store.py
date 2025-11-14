"""
ChromaDB vector store operations
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
from app.config import settings
from app.utils.embeddings import EmbeddingGenerator


class VectorStore:
    """Manages ChromaDB vector store operations"""
    
    def __init__(self):
        """Initialize ChromaDB client and collection"""
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding generator
        self.embedder = EmbeddingGenerator()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"description": "Mutual Fund FAQ documents from SEBI"}
        )
        
        print(f"✓ ChromaDB initialized at: {settings.chroma_persist_path}")
        print(f"✓ Collection: {settings.COLLECTION_NAME}")
        print(f"✓ Total documents in collection: {self.collection.count()}")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to vector store
        
        Args:
            documents: List of document dictionaries with 'text', 'source', and 'metadata'
        """
        if not documents:
            print("No documents to add")
            return
        
        print(f"\n💾 Adding {len(documents)} documents to vector store...")
        
        # Prepare data for ChromaDB
        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Generate embeddings
        print("🔄 Generating embeddings...")
        embeddings = self.embedder.embed_documents(texts)
        
        # Add to ChromaDB in batches (ChromaDB has limits)
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            
            self.collection.add(
                embeddings=embeddings[i:end_idx],
                documents=texts[i:end_idx],
                metadatas=metadatas[i:end_idx],
                ids=ids[i:end_idx]
            )
            
            print(f"✓ Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        
        print(f"✅ Successfully added {len(documents)} documents to vector store\n")
    
    def query(self, query_text: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Query the vector store
        
        Args:
            query_text: Query string
            top_k: Number of results to return (default from settings)
            
        Returns:
            List of relevant documents with metadata and scores
        """
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self.embedder.embed_query(query_text)
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results and results['documents'] and results['documents'][0]:
            for idx in range(len(results['documents'][0])):
                formatted_results.append({
                    "text": results['documents'][0][idx],
                    "metadata": results['metadatas'][0][idx],
                    "score": results['distances'][0][idx],
                    "source": results['metadatas'][0][idx].get('source', 'Unknown')
                })
        
        return formatted_results
    
    def reset_collection(self) -> None:
        """Delete and recreate the collection (for re-ingestion)"""
        print("⚠️  Resetting collection...")
        self.client.delete_collection(name=settings.COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"description": "Mutual Fund FAQ documents from SEBI"}
        )
        print("✓ Collection reset complete")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        return {
            "total_documents": self.collection.count(),
            "collection_name": settings.COLLECTION_NAME,
            "persist_directory": settings.chroma_persist_path
        }