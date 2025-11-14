"""
Chat API routes
"""
from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse
from app.agents.orchestrator import RAGOrchestrator

router = APIRouter(prefix="/api", tags=["chat"])

# Initialize orchestrator (singleton)
orchestrator = RAGOrchestrator()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a user query and return an answer
    
    Args:
        request: ChatRequest with user query
        
    Returns:
        ChatResponse with answer and citation
    """
    try:
        # Process query through RAG pipeline
        result = orchestrator.process_query(request.query)
        
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