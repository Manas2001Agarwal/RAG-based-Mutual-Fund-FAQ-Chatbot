"""
Streamlit Frontend for Mutual Fund FAQ Assistant - Modern UI
"""
import streamlit as st
import requests
from typing import Optional
import time

# Configuration
API_URL = "http://localhost:8000/api/chat"
HEALTH_URL = "http://localhost:8000/health"

# Page configuration
st.set_page_config(
    page_title="Mutual Fund FAQ Assistant",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Modern Custom CSS
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    /* Chat container */
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem auto;
        max-width: 800px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    /* Header */
    .header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .header p {
        font-size: 1.1rem;
        color: #6b7280;
        margin-top: 0;
    }
    
    /* Disclaimer badge */
    .disclaimer-badge {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        font-size: 0.95rem;
        color: #92400e;
    }
    
    .disclaimer-badge strong {
        color: #78350f;
    }
    
    /* Example questions */
    .example-section {
        margin: 2rem 0;
    }
    
    .example-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Answer display */
    .answer-container {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        border-left: 4px solid #0ea5e9;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .question-text {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e40af;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
    }
    
    .answer-text {
        font-size: 1.05rem;
        line-height: 1.7;
        color: #1f2937;
        margin: 1rem 0;
    }
    
    .citation-box {
        background: white;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-top: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
        color: #6b7280;
        border: 1px solid #e5e7eb;
    }
    
    .citation-box a {
        color: #0ea5e9;
        text-decoration: none;
        font-weight: 500;
    }
    
    .citation-box a:hover {
        text-decoration: underline;
    }
    
    /* Opinion badge */
    .opinion-badge {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #991b1b;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        margin-top: 1rem;
        display: inline-block;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.5);
    }
    
    /* Text input */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #667eea;
    }
    
    /* Backend status */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-online {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-offline {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e7eb;
        color: #9ca3af;
        font-size: 0.85rem;
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
        response = requests.post(
            API_URL,
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ API Error: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend API. Please make sure the FastAPI server is running.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def main():
    """Main Streamlit application"""
    
    # Check backend status first
    backend_online = check_backend_health()
    
    # Header with status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
            <div class="header">
                <h1>💰 Mutual Fund FAQ</h1>
                <p>Get instant, factual answers about mutual funds</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if backend_online:
            st.markdown('<div class="status-badge status-online">🟢 Online</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge status-offline">🔴 Offline</div>', unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
        <div class="disclaimer-badge">
            <strong>⚠️ Important:</strong> This assistant provides facts only. 
            No investment advice is offered. Consult a SEBI-registered advisor for personalized guidance.
        </div>
    """, unsafe_allow_html=True)
    
    if not backend_online:
        st.error("⚠️ Backend API is not responding. Please start the FastAPI server.")
        st.code("cd backend && uvicorn app.main:app --reload", language="bash")
        return
    
    # Example questions
    st.markdown("""
        <div class="example-section">
            <div class="example-label">
                💡 Try these example questions
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    example_questions = [
        "What is KYC in mutual funds?",
        "How does Aadhaar-based e-KYC work?",
        "What are derivatives?"
    ]
    
    # Initialize session state
    if 'current_answer' not in st.session_state:
        st.session_state.current_answer = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Example question buttons
    cols = st.columns(len(example_questions))
    for idx, (col, question) in enumerate(zip(cols, example_questions)):
        with col:
            if st.button(f"📌 {question}", key=f"example_{idx}", use_container_width=True):
                st.session_state.processing = True
                with st.spinner("🔍 Finding answer..."):
                    result = send_query(question)
                    if result:
                        st.session_state.current_answer = result
                        st.session_state.processing = False
                        st.rerun()
    
    # Divider
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Query input
    st.markdown("""
        <div style="margin: 2rem 0 1rem 0;">
            <div style="font-size: 1.1rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem;">
                💬 Ask your question
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    query = st.text_input(
        "Query",
        placeholder="e.g., What is a mutual fund?",
        label_visibility="collapsed",
        key="user_query"
    )
    
    # Send button - centered
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        send_button = st.button("🚀 Get Answer", type="primary", use_container_width=True)
    
    # Process query
    if send_button and query and query.strip():
        st.session_state.processing = True
        with st.spinner("🔍 Finding answer..."):
            time.sleep(0.3)  # Small delay for UX
            result = send_query(query.strip())
            if result:
                st.session_state.current_answer = result
                st.session_state.processing = False
                st.rerun()
    elif send_button and (not query or not query.strip()):
        st.warning("⚠️ Please enter a question")
    
    # Display answer
    if st.session_state.current_answer:
        answer_data = st.session_state.current_answer
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Answer container
        st.markdown(f"""
            <div class="answer-container">
                <div class="question-text">
                    <span>💬</span>
                    <span>{answer_data['query']}</span>
                </div>
                <div class="answer-text">
                    {answer_data['answer']}
                </div>
        """, unsafe_allow_html=True)
        
        # Citation
        if answer_data.get("citation"):
            st.markdown(f"""
                <div class="citation-box">
                    <span>📎</span>
                    <span>Source: <a href="{answer_data['citation']}" target="_blank">View Document</a></span>
                </div>
            """, unsafe_allow_html=True)
        
        # Opinion badge
        if answer_data["classification"] == "opinion":
            st.markdown("""
                <div class="opinion-badge">
                    🚫 Opinion-based query - No investment advice provided
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Clear button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Ask Another Question", use_container_width=True):
                st.session_state.current_answer = None
                st.rerun()
    
    # Footer
    st.markdown("""
        <div class="footer">
            <p>Powered by SEBI FAQ Documents • Built with LangGraph & FastAPI</p>
            <p style="margin-top: 0.5rem; font-size: 0.8rem;">
                💡 This is a prototype. Always verify important information with official sources.
            </p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()