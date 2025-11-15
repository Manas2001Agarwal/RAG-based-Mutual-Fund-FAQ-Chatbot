"""
Streamlit Frontend for INDMoney Mutual Fund FAQ Bot
Clean chat interface with INDMoney branding
"""
import streamlit as st
import requests
import base64
from typing import Optional

# MUST BE FIRST
st.set_page_config(
    page_title="INDMoney - Mutual Fund FAQ Bot",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Configuration
API_URL = "http://localhost:8000/api/chat"
HEALTH_URL = "http://localhost:8000/health"

# Custom CSS
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main {
        background-color: #f8f9fa;
    }
    
    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Header card */
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
        flex-shrink: 0;
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .header-text h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a;
    }
    
    .header-text p {
        margin: 0;
        font-size: 0.95rem;
        color: #666;
    }
    
    /* Disclaimer */
    .disclaimer {
        background: #fff9e6;
        border: 1px solid #f5e6c3;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.5rem;
        display: flex;
        gap: 0.75rem;
    }
    
    .disclaimer-icon {
        font-size: 1.25rem;
        flex-shrink: 0;
    }
    
    .disclaimer-content {
        flex: 1;
    }
    
    .disclaimer-title {
        font-weight: 600;
        color: #855d00;
        margin: 0 0 0.25rem 0;
    }
    
    .disclaimer-text {
        color: #6b5100;
        margin: 0;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Try asking section */
    .try-asking {
        font-weight: 500;
        color: #666;
        margin: 1.5rem 0 0.75rem 0;
        font-size: 0.95rem;
        text-align: left;
    }
    
    /* Example buttons - left aligned */
    .stButton button {
        width: 100%;
        text-align: left;
        background: white;
        color: #1a1a1a;
        border: 1px solid #e0e0e0;
        padding: 0.875rem 1.25rem;
        border-radius: 8px;
        font-weight: 400;
        margin-bottom: 0.5rem;
        justify-content: flex-start;
    }
    
    .stButton button:hover {
        background: #f8f9fa;
        border-color: #0066cc;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        background: transparent !important;
        border: none !important;
    }
    
    .stChatInput {
        background: white !important;
        border-radius: 24px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        border: 1px solid #e0e0e0 !important;
        padding: 0.5rem 1rem !important;
    }
    
    .stChatInput textarea {
        background: white !important;
        border: none !important;
    }
    
    .stChatInput textarea:focus {
        box-shadow: none !important;
        border: none !important;
    }
    
    /* Ensure proper width */
    [data-testid="stChatInput"] {
        max-width: 100%;
    }
    
    /* Remove extra padding/margin */
    [data-testid="stChatInputContainer"] {
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)


def check_backend_health() -> bool:
    """Check if backend API is running"""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        return response.status_code == 200
    except:
        return False


def send_query(query: str) -> Optional[dict]:
    """Send query to backend API"""
    try:
        response = requests.post(API_URL, json={"query": query}, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def main():
    """Main application"""
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Header with INDMoney logo
    try:
        with open("assets/indmoney_logo.png", "rb") as image_file:
            encoded_logo = base64.b64encode(image_file.read()).decode()
        
        st.markdown(f"""
        <div class="header-box">
            <img src="data:image/png;base64,{encoded_logo}" class="logo-img" />
            <div class="header-text">
                <h1>Mutual Fund FAQ Bot</h1>
                <p>Get answers to your mutual fund questions</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("""
        <div class="header-box">
            <div class="logo-box">IND</div>
            <div class="header-text">
                <h1>Mutual Fund FAQ Bot</h1>
                <p>Get answers to your mutual fund questions</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Check backend
    if not check_backend_health():
        st.error("⚠️ Backend is offline. Please start the server.")
        st.code("cd backend && uvicorn app.main:app --reload", language="bash")
        st.stop()
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
        <div class="disclaimer-icon">ℹ️</div>
        <div class="disclaimer-content">
            <div class="disclaimer-title">Disclaimer:</div>
            <div class="disclaimer-text">
                This assistant provides <strong>facts only</strong>. 
                No investment advice is offered. For personalized guidance, consult a SEBI-registered advisor.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Try asking section
    st.markdown('<div class="try-asking">Try asking:</div>', unsafe_allow_html=True)
    
    # Example questions
    examples = [
        "What is a Mutual Fund?",
        "What is the difference between SIP and lump sum investment?",
        "What is NAV and how is it calculated?"
    ]
    
    for example in examples:
        if st.button(example, key=f"ex_{example}"):
            st.session_state.messages.append({"role": "user", "content": example})
            result = send_query(example)
            if result:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "citation": result.get("citation"),
                    "classification": result.get("classification")
                })
            st.rerun()
    
    st.divider()
    
    # Display chat messages
    if st.session_state.messages:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg["content"])
                    if msg.get("citation"):
                        st.caption(f"📎 [View Source]({msg['citation']})")
                    if msg.get("classification") == "opinion":
                        st.warning("🚫 No investment advice provided")
        
        # Clear chat button
        if st.button("Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
    else:
        st.info("💬 Ask a question to get started")
        st.divider()
    
    # Chat input - properly aligned
    user_input = st.chat_input("Type your message", key="chat_input")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get response
        with st.spinner("🔍 Getting answer..."):
            result = send_query(user_input)
            
            if result:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "citation": result.get("citation"),
                    "classification": result.get("classification")
                })
            else:
                st.error("Failed to get response from backend. Please try again.")
        
        st.rerun()


if __name__ == "__main__":
    main()