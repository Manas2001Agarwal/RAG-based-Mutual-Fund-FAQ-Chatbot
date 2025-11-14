"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.models import HealthResponse
from app.utils.vector_store import VectorStore
from app.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Mutual Fund FAQ Assistant API",
    description="Agentic RAG-based chatbot for mutual fund FAQs",
    version="1.0.0"
)

# Add CORS middleware (for Streamlit frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        vector_store = VectorStore()
        stats = vector_store.get_collection_stats()
        
        return HealthResponse(
            status="healthy",
            message="Mutual Fund FAQ Assistant API is running",
            vector_store_documents=stats["total_documents"]
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


# Run with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )