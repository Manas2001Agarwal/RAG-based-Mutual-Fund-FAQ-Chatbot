"""
Query Classifier Node - Determines if query is factual or opinion-based
"""
from typing import Literal
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from pydantic import SecretStr

class QueryClassifier:
    """Classifies user queries as factual or opinion-based"""
    
    def __init__(self):
        """Initialize the LLM for classification"""
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL_NAME,
            api_key=SecretStr(settings.GROQ_API_KEY),
            temperature=0.0,  # Deterministic classification
            max_tokens=50
        )
    
    def classify(self, query: str) -> Literal["factual", "opinion"]:
        """
        Classify query as factual or opinion-based
        
        Args:
            query: User's question
            
        Returns:
            "factual" or "opinion"
        """
        
        # Check for obvious opinion/advice keywords first
        query_lower = query.lower()
        
        # Strong opinion indicators
        opinion_keywords = [
            "should i", "which is best", "which is better", "recommend", 
            "according to you", "your opinion", "what do you think",
            "which fund", "which scheme", "best fund", "best scheme",
            "top fund", "top scheme", "good fund", "good scheme",
            "invest in", "buy", "sell", "hold", "portfolio",
            "worth investing", "better investment", "safer", "risky",
            "suggest", "advice", "advise", "recommendation"
        ]
        
        # Check if any opinion keyword is present
        for keyword in opinion_keywords:
            if keyword in query_lower:
                print(f"[Classifier] Detected opinion keyword: '{keyword}' → opinion")
                return "opinion"
        
        # Use LLM for borderline cases
        messages = [
            SystemMessage(content="""You are a query classifier for a mutual fund FAQ system.

Your ONLY job is to classify queries as either "factual" or "opinion".

FACTUAL queries:
- Ask for definitions, explanations, processes, rules
- Ask "what is", "how does", "what are the requirements"
- Ask about regulations, procedures, documentation
- General information questions

OPINION queries (investment advice):
- Ask "should I buy/sell/invest"
- Ask "which fund/scheme is best/better"
- Ask for recommendations, suggestions, or advice
- Ask "according to you" or "what do you think"
- Ask about specific investment decisions
- Ask "is X good" or "is X worth it"
- Compare specific funds/schemes for selection

Respond with ONLY ONE WORD: "factual" or "opinion"
No explanations, just the classification."""),
            
            HumanMessage(content=f'Classify this query: "{query}"')
        ]
        
        try:
            response = self.llm.invoke(messages)
            classification = response.content.strip().lower()
            
            print(f"[Classifier] LLM response: '{classification}'")
            
            # Validate response
            if "opinion" in classification:
                return "opinion"
            elif "factual" in classification:
                return "factual"
            else:
                # If unclear, check for question words that usually indicate factual queries
                factual_starters = ["what", "how", "when", "where", "who", "define", "explain"]
                if any(query_lower.startswith(word) for word in factual_starters):
                    print(f"[Classifier] Defaulting to factual based on question word")
                    return "factual"
                else:
                    # Default to opinion if uncertain (safer to refuse than give bad advice)
                    print(f"[Classifier] Unclear, defaulting to opinion for safety")
                    return "opinion"
                
        except Exception as e:
            print(f"[Classifier] Error: {e}")
            # Default to opinion to be safe (better to refuse than give wrong advice)
            return "opinion"