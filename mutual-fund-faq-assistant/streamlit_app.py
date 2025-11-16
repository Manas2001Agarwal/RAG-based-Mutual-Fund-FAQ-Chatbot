"""
Combined Streamlit App - Frontend + Backend in One
INDMoney Mutual Fund FAQ Bot
"""
import streamlit as st
import base64
from typing import Optional, Dict, List
import os

# Page config MUST be first
st.set_page_config(
    page_title="INDMoney - Mutual Fund FAQ Bot",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main {background-color: #f8f9fa;}
    
    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .header-box {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo-img {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        object-fit: cover;
    }
    
    .logo-box {
        width: 56px;
        height: 56px;
        background: #2c3e50;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .disclaimer {
        background: #fff9e6;
        border: 1px solid #f5e6c3;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.5rem;
        display: flex;
        gap: 0.75rem;
    }
    
    .disclaimer-title {
        font-weight: 600;
        color: #855d00;
    }
    
    .disclaimer-text {
        color: #6b5100;
        font-size: 0.9rem;
    }
    
    .stButton button {
        width: 100%;
        text-align: left;
        background: white;
        color: #1a1a1a;
        border: 1px solid #e0e0e0;
        padding: 0.875rem 1.25rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    .stButton button:hover {
        background: #f8f9fa;
        border-color: #0066cc;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# BACKEND LOGIC (Embedded)
# ============================================================================

@st.cache_resource
def initialize_backend():
    """Initialize vector store and LLM (cached)"""
    from langchain_community.vectorstores import Chroma
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_groq import ChatGroq
    from langchain.schema import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    import pypdf
    
    # Get API keys from Streamlit secrets
    groq_api_key = st.secrets["GROQ_API_KEY"]
    google_api_key = st.secrets["GOOGLE_API_KEY"]
    
    # Initialize embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=google_api_key
    )
    
    # Initialize LLM
    llm = ChatGroq(
        api_key=groq_api_key,
        model="mixtral-8x7b-32768",
        temperature=0.2
    )
    
    # Load PDFs
    pdf_dir = "backend/data/pdfs"
    documents = []
    
    if os.path.exists(pdf_dir):
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            filepath = os.path.join(pdf_dir, pdf_file)
            
            with open(filepath, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    text = pdf_reader.pages[page_num].extract_text()
                    
                    if text.strip():
                        documents.append(
                            Document(
                                page_content=text,
                                metadata={
                                    "source": pdf_file,
                                    "page": page_num + 1
                                }
                            )
                        )
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)
    
    # Create vector store
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=None  # In-memory
    )
    
    return vectorstore, llm


def classify_query(query: str, llm) -> str:
    """Classify if query is factual or opinion-seeking"""
    from langchain.prompts import ChatPromptTemplate
    
    classification_prompt = ChatPromptTemplate.from_template("""
    Classify the following query as either 'factual' or 'opinion'.
    
    Factual queries ask for facts, definitions, or explanations.
    Opinion queries ask for recommendations, advice, or subjective judgments.
    
    Query: {query}
    
    Respond with only one word: factual or opinion
    """)
    
    response = llm.invoke(classification_prompt.format(query=query))
    classification = response.content.strip().lower()
    
    return "factual" if "factual" in classification else "opinion"


def get_answer(query: str, vectorstore, llm) -> Dict:
    """Get answer for user query"""
    from langchain.prompts import ChatPromptTemplate
    
    # Classify query
    classification = classify_query(query, llm)
    
    # If opinion, refuse
    if classification == "opinion":
        return {
            "query": query,
            "answer": "I can only provide factual information about mutual funds. I cannot offer investment advice or recommendations. Please consult a SEBI-registered financial advisor for personalized guidance.",
            "citation": None,
            "classification": "opinion"
        }
    
    # Retrieve relevant documents
    docs = vectorstore.similarity_search(query, k=3)
    
    if not docs:
        return {
            "query": query,
            "answer": "I couldn't find relevant information in the knowledge base. Please rephrase your question.",
            "citation": None,
            "classification": "factual"
        }
    
    # Create context from retrieved docs
    context = "\n\n".join([doc.page_content for doc in docs])
    source = docs[0].metadata.get("source", "Unknown")
    
    # Generate answer
    qa_prompt = ChatPromptTemplate.from_template("""
    You are a helpful assistant that answers questions about mutual funds based on SEBI guidelines.
    
    Use the following context to answer the question. Be concise and accurate.
    If the answer is not in the context, say so.
    
    Context:
    {context}
    
    Question: {query}
    
    Answer:
    """)
    
    response = llm.invoke(qa_prompt.format(context=context, query=query))
    
    return {
        "query": query,
        "answer": response.content,
        "citation": source,
        "classification": "factual"
    }


# ============================================================================
# FRONTEND
# ============================================================================

def main():
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'backend_ready' not in st.session_state:
        with st.spinner("🔄 Initializing AI system..."):
            try:
                vectorstore, llm = initialize_backend()
                st.session_state.vectorstore = vectorstore
                st.session_state.llm = llm
                st.session_state.backend_ready = True
            except Exception as e:
                st.error(f"❌ Initialization failed: {e}")
                st.stop()
    
    # Header
    try:
        with open("frontend/assets/indmoney_logo.png", "rb") as f:
            logo = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div class="header-box">
            <img src="data:image/png;base64,{logo}" class="logo-img" />
            <div>
                <h1 style="margin:0;font-size:1.5rem;">Mutual Fund FAQ Bot</h1>
                <p style="margin:0;color:#666;">Get answers to your mutual fund questions</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except:
        st.markdown("""
        <div class="header-box">
            <div class="logo-box">IND</div>
            <div>
                <h1 style="margin:0;font-size:1.5rem;">Mutual Fund FAQ Bot</h1>
                <p style="margin:0;color:#666;">Get answers to your mutual fund questions</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Status
    if st.session_state.backend_ready:
        st.success("🟢 AI System Ready")
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
        <div style="font-size:1.25rem;">ℹ️</div>
        <div>
            <div class="disclaimer-title">Disclaimer:</div>
            <div class="disclaimer-text">
                This assistant provides <strong>facts only</strong>. 
                No investment advice is offered. For personalized guidance, consult a SEBI-registered advisor.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Example questions
    st.markdown("**Try asking:**")
    
    examples = [
        "What is a Mutual Fund?",
        "What is the difference between SIP and lump sum investment?",
        "What is NAV and how is it calculated?"
    ]
    
    for example in examples:
        if st.button(example, key=f"ex_{example}"):
            st.session_state.messages.append({"role": "user", "content": example})
            
            with st.spinner("🤔 Thinking..."):
                result = get_answer(
                    example,
                    st.session_state.vectorstore,
                    st.session_state.llm
                )
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "citation": result.get("citation"),
                "classification": result.get("classification")
            })
            st.rerun()
    
    st.divider()
    
    # Display chat
    if st.session_state.messages:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg["content"])
                    if msg.get("citation"):
                        st.caption(f"📎 Source: {msg['citation']}")
                    if msg.get("classification") == "opinion":
                        st.warning("🚫 No investment advice provided")
        
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
    
    # Chat input
    user_input = st.chat_input("Type your question here")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("🤔 Thinking..."):
            result = get_answer(
                user_input,
                st.session_state.vectorstore,
                st.session_state.llm
            )
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "citation": result.get("citation"),
            "classification": result.get("classification")
        })
        st.rerun()


if __name__ == "__main__":
    main()