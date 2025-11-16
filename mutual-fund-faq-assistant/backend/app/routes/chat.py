"""
Chat API routes
"""
from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse
from app.agents.orchestrator import RAGOrchestrator
import app.main as main_app

router = APIRouter(prefix="/api", tags=["chat"])

# Initialize orchestrator (singleton)
orchestrator = None


def get_orchestrator():
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = RAGOrchestrator()
    return orchestrator


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a user query and return an answer
    
    Args:
        request: ChatRequest with user query
        
    Returns:
        ChatResponse with answer and citation
    """
    # Check if vector DB is ready
    if not main_app.vector_db_ready:
        raise HTTPException(
            status_code=503,
            detail="Service is initializing. Vector database is still loading. Please try again in 1-2 minutes."
        )
    
    try:
        # Process query through RAG pipeline
        orch = get_orchestrator()
        result = orch.process_query(request.query)
        
        return ChatResponse(
            query=result["query"],
            answer=result["answer"],
            citation=result["citation"],
            classification=result["classification"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )
        
        