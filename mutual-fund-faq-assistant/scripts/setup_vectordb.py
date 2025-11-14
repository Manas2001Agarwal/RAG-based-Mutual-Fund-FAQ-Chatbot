"""
One-time script to download PDFs and populate ChromaDB
Run this script to set up the vector database
"""
import sys
import os

# Add backend directory to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

# Change working directory to backend (so .env is found)
os.chdir(backend_path)

from app.config import settings
from app.utils.pdf_loader import PDFLoader, prepare_documents_for_vectordb
from app.utils.vector_store import VectorStore


def main():
    """Main function to set up vector database"""
    
    print("=" * 60)
    print("🚀 MUTUAL FUND FAQ - VECTOR DATABASE SETUP")
    print("=" * 60)
    print(f"\nWorking Directory: {os.getcwd()}")
    print(f"Backend Path: {backend_path}")
    
    # Verify .env is loaded
    print(f"\n🔑 Verifying Configuration...")
    print(f"  GROQ API Key: {settings.GROQ_API_KEY[:20]}..." if settings.GROQ_API_KEY else "  ❌ GROQ API Key missing!")
    print(f"  Google API Key: {settings.GOOGLE_API_KEY[:20]}..." if settings.GOOGLE_API_KEY else "  ❌ Google API Key missing!")
    print(f"  PDF URLs: {len(settings.pdf_urls_list)} sources")
    
    # Step 1: Load PDFs
    print("\n📚 STEP 1: Loading PDF Documents")
    print("-" * 60)
    loader = PDFLoader(settings.pdf_urls_list)
    documents = loader.load_all_pdfs()
    
    if not documents:
        print("❌ No documents loaded. Exiting.")
        return
    
    # Step 2: Prepare documents (chunking)
    print("\n✂️  STEP 2: Chunking Documents")
    print("-" * 60)
    prepared_docs = prepare_documents_for_vectordb(
        documents,
        chunk_size=1000,
        overlap=200
    )
    
    # Step 3: Initialize vector store and add documents
    print("\n💾 STEP 3: Initializing Vector Store")
    print("-" * 60)
    vector_store = VectorStore()
    
    # Check if collection already has documents
    stats = vector_store.get_collection_stats()
    if stats['total_documents'] > 0:
        print(f"\n⚠️  Collection already contains {stats['total_documents']} documents.")
        response = input("Do you want to reset and re-populate? (yes/no): ").lower()
        if response == 'yes':
            vector_store.reset_collection()
        else:
            print("Keeping existing collection. Exiting.")
            return
    
    # Step 4: Add documents to vector store
    print("\n📥 STEP 4: Adding Documents to Vector Store")
    print("-" * 60)
    vector_store.add_documents(prepared_docs)
    
    # Step 5: Verify
    print("\n✅ STEP 5: Verification")
    print("-" * 60)
    final_stats = vector_store.get_collection_stats()
    print(f"Collection Name: {final_stats['collection_name']}")
    print(f"Total Documents: {final_stats['total_documents']}")
    print(f"Storage Location: {final_stats['persist_directory']}")
    
    # Test query
    print("\n🔍 Testing with sample query...")
    test_query = "What is KYC?"
    results = vector_store.query(test_query, top_k=2)
    
    if results:
        print(f"\nQuery: '{test_query}'")
        print(f"Found {len(results)} results:")
        for idx, result in enumerate(results, 1):
            print(f"\n  Result {idx}:")
            print(f"    Source: {result['source']}")
            print(f"    Page: {result['metadata'].get('page', 'N/A')}")
            print(f"    Score: {result['score']:.4f}")
            print(f"    Text preview: {result['text'][:150]}...")
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\nYou can now start the FastAPI server and use the chatbot.")
    print("\nTo start backend:")
    print("  cd backend")
    print("  uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()