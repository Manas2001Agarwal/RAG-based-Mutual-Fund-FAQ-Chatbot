"""
Generator Node - Generates grounded answers using LLM
"""
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings


class Generator:
    """Generates answers grounded in retrieved documents"""
    
    def __init__(self):
        """Initialize the LLM for generation"""
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL_NAME,
            api_key=settings.GROQ_API_KEY,
            temperature=0.2,  # Slightly higher for better generation
            max_tokens=500    # Increased significantly
        )
    
    def generate_answer(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate answer from retrieved documents
        
        Args:
            query: User's question
            retrieved_docs: List of relevant documents from retriever
            
        Returns:
            Dictionary with answer and citation
        """
        
        if not retrieved_docs:
            return {
                "answer": "I couldn't find relevant information in the available documents to answer your question.",
                "citation": None
            }
        
        # Use the most relevant document (first one)
        context = retrieved_docs[0]["text"]
        source_url = retrieved_docs[0]["source"]
        
        # Use chat messages format for better results
        messages = [
            SystemMessage(content="""You are a helpful mutual fund expert assistant. 
Your job is to answer questions accurately based on the provided context.
Always provide clear, direct answers in 2-3 sentences.
Use simple language that anyone can understand."""),
            
            HumanMessage(content=f"""Context from official SEBI documents:
{context}

User Question: {query}

Please answer the question based on the context above. Provide a clear, direct answer in 2-3 sentences. If the context doesn't contain enough information, say so briefly.""")
        ]
        
        try:
            # Get response from LLM
            response = self.llm.invoke(messages)
            answer = response.content.strip()
            
            # Validate answer quality
            if not answer:
                answer = "I couldn't generate an answer from the available information."
            elif len(answer) < 20:
                # Answer too short, try to provide at least basic info
                answer = f"Based on the documents: {answer}. Please ask for more specific details if needed."
            
            # Ensure answer doesn't exceed 3 sentences approximately
            sentences = answer.split('.')
            if len(sentences) > 3:
                answer = '. '.join(sentences[:3]) + '.'
            
            return {
                "answer": answer,
                "citation": source_url
            }
            
        except Exception as e:
            print(f"Generation error: {e}")
            # Fallback: try to extract key info from context
            try:
                # Simple extraction as fallback
                context_preview = context[:300] + "..." if len(context) > 300 else context
                return {
                    "answer": f"Based on the document, here's relevant information: {context_preview}",
                    "citation": source_url
                }
            except:
                return {
                    "answer": "I encountered an error generating the answer. The information exists in the documents but I couldn't process it properly.",
                    "citation": source_url
                }
    
    def generate_refusal(self, query: str) -> Dict[str, Any]:
        """
        Generate polite refusal for opinion-based queries
        
        Args:
            query: User's question
            
        Returns:
            Dictionary with refusal message and educational link
        """
        
        refusal_message = (
            "I can only provide factual information about mutual funds. "
            "I cannot offer investment advice, portfolio recommendations, or predictions. "
            "For personalized investment guidance, please consult a SEBI-registered investment advisor."
        )
        
        educational_link = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=4&ssid=18&smid=0"
        
        return {
            "answer": refusal_message,
            "citation": educational_link
        }