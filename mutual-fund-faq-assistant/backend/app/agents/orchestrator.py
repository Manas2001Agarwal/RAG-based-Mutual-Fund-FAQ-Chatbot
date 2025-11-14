"""
LangGraph Orchestrator - Manages the agentic RAG workflow
"""
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from app.agents.classifier import QueryClassifier
from app.agents.retriever import Retriever
from app.agents.generator import Generator


# Define the state that flows through the graph
class AgentState(TypedDict):
    """State object that passes through the graph"""
    query: str
    classification: Literal["factual", "opinion"]
    retrieved_docs: list
    answer: str
    citation: str


class RAGOrchestrator:
    """Orchestrates the agentic RAG workflow using LangGraph"""
    
    def __init__(self):
        """Initialize all agent components"""
        self.classifier = QueryClassifier()
        self.retriever = Retriever()
        self.generator = Generator()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _classify_query(self, state: AgentState) -> AgentState:
        """Node: Classify the query"""
        classification = self.classifier.classify(state["query"])
        state["classification"] = classification
        return state
    
    def _retrieve_documents(self, state: AgentState) -> AgentState:
        """Node: Retrieve relevant documents"""
        retrieved_docs = self.retriever.retrieve(state["query"])
        state["retrieved_docs"] = retrieved_docs
        return state
    
    def _generate_answer(self, state: AgentState) -> AgentState:
        """Node: Generate grounded answer"""
        result = self.generator.generate_answer(
            state["query"],
            state["retrieved_docs"]
        )
        state["answer"] = result["answer"]
        state["citation"] = result["citation"]
        return state
    
    def _generate_refusal(self, state: AgentState) -> AgentState:
        """Node: Generate refusal for opinion queries"""
        result = self.generator.generate_refusal(state["query"])
        state["answer"] = result["answer"]
        state["citation"] = result["citation"]
        return state
    
    def _route_based_on_classification(self, state: AgentState) -> Literal["retrieve", "refuse"]:
        """Conditional edge: Route based on classification"""
        if state["classification"] == "factual":
            return "retrieve"
        else:
            return "refuse"
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Initialize graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify", self._classify_query)
        workflow.add_node("retrieve", self._retrieve_documents)
        workflow.add_node("generate", self._generate_answer)
        workflow.add_node("refuse", self._generate_refusal)
        
        # Set entry point
        workflow.set_entry_point("classify")
        
        # Add conditional edge after classification
        workflow.add_conditional_edges(
            "classify",
            self._route_based_on_classification,
            {
                "retrieve": "retrieve",
                "refuse": "refuse"
            }
        )
        
        # Add edges
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        workflow.add_edge("refuse", END)
        
        # Compile graph
        return workflow.compile()
    
    def process_query(self, query: str) -> dict:
        """
        Process a user query through the RAG pipeline
        
        Args:
            query: User's question
            
        Returns:
            Dictionary with answer and citation
        """
        
        # Initial state
        initial_state = {
            "query": query,
            "classification": None,
            "retrieved_docs": [],
            "answer": "",
            "citation": None
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Format response
        response = {
            "query": query,
            "answer": final_state["answer"],
            "citation": final_state["citation"],
            "classification": final_state["classification"]
        }
        
        return response