"""
FastAPI application entry point - Production Ready
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.models import HealthResponse, ChatRequest, ChatResponse
from app.utils.vector_store import VectorStore
from app.config import settings
import os
import asyncio

# Initialize FastAPI app
app = FastAPI(
    title="Mutual Fund FAQ Assistant API",
    description="Agentic RAG-based chatbot for mutual fund FAQs",
    version="1.0.0"
)

# CORS - Allow all for now, restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global flag to track vector DB readiness
vector_db_ready = False
vector_store_instance = None


async def populate_vector_db_background():
    """Populate vector DB in background without blocking startup"""
    global vector_db_ready, vector_store_instance
    
    try:
        from app.utils.pdf_loader import PDFLoader, prepare_documents_for_vectordb
        
        print("📥 Starting vector DB population in background...")
        vector_store_instance = VectorStore()
        
        current_count = vector_store_instance.collection.count()
        print(f"📊 Current document count: {current_count}")
        
        if current_count == 0:
            print("⏳ Downloading and processing PDFs...")
            print("⏳ This will take 1-2 minutes...")
            
            loader = PDFLoader(settings.pdf_urls_list)
            documents = loader.load_all_pdfs()
            
            if documents:
                print(f"✓ Loaded {len(documents)} pages from PDFs")
                print("🔄 Preparing documents (chunking)...")
                prepared_docs = prepare_documents_for_vectordb(documents)
                
                print(f"💾 Adding {len(prepared_docs)} chunks to vector store...")
                vector_store_instance.add_documents(prepared_docs)
                
                final_count = vector_store_instance.collection.count()
                print(f"✅ Vector DB ready with {final_count} documents")
                vector_db_ready = True
            else:
                print("⚠️ No documents loaded from PDFs")
        else:
            print(f"✅ Vector DB already has {current_count} documents")
            vector_db_ready = True
            
    except Exception as e:
        print(f"❌ Vector DB population failed: {e}")
        import traceback
        traceback.print_exc()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("=" * 60)
    print("🚀 Starting Mutual Fund FAQ Assistant API")
    print("=" * 60)
    print(f"📊 Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
    print(f"🔧 API Host: {settings.API_HOST}")
    print(f"🔧 API Port: {settings.API_PORT}")
    print(f"📁 ChromaDB Path: {settings.chroma_persist_path}")
    print("=" * 60)
    print("✅ Server is ready to accept requests")
    print("⏳ Vector DB is populating in background...")
    print("   (This may take 1-2 minutes on first startup)")
    print("=" * 60)
    
    # Start background task
    asyncio.create_task(populate_vector_db_background())


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    global vector_db_ready, vector_store_instance
    
    try:
        if vector_store_instance:
            doc_count = vector_store_instance.collection.count()
        else:
            doc_count = 0
        
        return HealthResponse(
            status="healthy" if vector_db_ready else "initializing",
            message="Mutual Fund FAQ Assistant API is running" if vector_db_ready else "Vector database is still loading...",
            vector_store_documents=doc_count
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            message=f"Error: {str(e)}",
            vector_store_documents=0
        )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Alternative health check endpoint"""
    return await health_check()


@app.post("/admin/setup")
async def setup_database(secret_key: str):
    """
    One-time setup endpoint to populate vector database
    Useful for manual triggering if background population fails
    """
    if secret_key != os.getenv("SETUP_SECRET", "change-me-in-production"):
        return {"error": "Unauthorized"}
    
    global vector_db_ready
    
    try:
        from app.utils.pdf_loader import PDFLoader, prepare_documents_for_vectordb
        
        print("🔄 Manual setup triggered...")
        vector_store = VectorStore()
        
        # Reset if exists
        if vector_store.collection.count() > 0:
            print("⚠️ Resetting existing collection...")
            vector_store.reset_collection()
        
        # Load PDFs
        loader = PDFLoader(settings.pdf_urls_list)
        documents = loader.load_all_pdfs()
        
        if not documents:
            return {"error": "No documents loaded"}
        
        # Prepare documents
        prepared_docs = prepare_documents_for_vectordb(documents)
        
        # Add to vector store
        vector_store.add_documents(prepared_docs)
        
        vector_db_ready = True
        
        return {
            "status": "success",
            "documents_added": len(prepared_docs),
            "message": "Vector database populated successfully"
        }
    except Exception as e:
        return {"error": str(e)}


# Include chat router
app.include_router(chat_router)


# For local development with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )