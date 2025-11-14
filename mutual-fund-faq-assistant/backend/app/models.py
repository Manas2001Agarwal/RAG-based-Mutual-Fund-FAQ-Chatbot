"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    query: str = Field(..., min_length=1, max_length=500, description="User's question")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is KYC in mutual funds?"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    query: str = Field(..., description="Original user query")
    answer: str = Field(..., description="Generated answer")
    citation: Optional[str] = Field(None, description="Source URL for citation")
    classification: str = Field(..., description="Query classification (factual/opinion)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is KYC in mutual funds?",
                "answer": "KYC stands for Know Your Customer. It is a verification process required by SEBI for investors.",
                "citation": "https://www.sebi.gov.in/sebi_data/faqfiles/jan-2017/1485861159393.pdf",
                "classification": "factual"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str
    message: str
    vector_store_documents: int