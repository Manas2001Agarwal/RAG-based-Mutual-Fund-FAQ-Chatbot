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
    layout="wide",
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
        max-width: 1000px;
        padding-top: 2rem;
        padding-bottom: 8rem;
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
    
    /* Input area fixed at bottom */
    .stTextInput {
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%);
        width: calc(100% - 4rem);
        max-width: 960px;
        z-index: 999;
    }
    
    .stTextInput > div {
        background: white;
        border-radius: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
    }
    
    .stTextInput input {
        border: none !important;
        padding: 1rem 1.5rem !important;
        font-size: 0.95rem;
        border-radius: 24px;
    }
    
    .stTextInput input:focus {
        box-shadow: none !important;
    }
    
    /* Send button */
    div[data-testid="column"]:last-child .stButton {
        position: fixed;
        bottom: 2.5rem;
        right: calc(50% - 450px);
        z-index: 1000;
    }
    
    div[data-testid="column"]:last-child .stButton button {
        background: #0066cc;
        color: white;
        border: none;
        border-radius: 50%;
        width: 44px;
        height: 44px;
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(0,102,204,0.3);
    }
    
    div[data-testid="column"]:last-child .stButton button:hover {
        background: #0052a3;
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
    except:
        return None


def main():
    """Main application"""
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Header with INDMoney logo
    try:
        # Try to load the INDMoney logo
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
        # Fallback if logo not found
        st.markdown("""
        <div class="header-box">
            <div class="logo-box">IND</div>
            <div class="header-text">
                <h1>Mutual Fund FAQ Bot</h1>
                <p>Get answers to your mutual fund questions</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.warning("⚠️ Logo not found at assets/indmoney_logo.png - using fallback")
    
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
    
    # Example questions - left aligned
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
    
    # Spacer for chat area
    st.markdown("<br><br>", unsafe_allow_html=True)
    
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
    
    # Spacer for fixed input at bottom
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    
    # Input area (fixed at bottom via CSS)
    col1, col2 = st.columns([20, 1])
    
    with col1:
        user_input = st.text_input(
            "message",
            placeholder="Type your message",
            label_visibility="collapsed",
            key="user_input"
        )
    
    with col2:
        send = st.button("🚀", key="send_btn")
    
    # Handle send
    if send and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        result = send_query(user_input)
        if result:
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "citation": result.get("citation"),
                "classification": result.get("classification")
            })
        st.rerun()


if __name__ == "__main__":
    main()