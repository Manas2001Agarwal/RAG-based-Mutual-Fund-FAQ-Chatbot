# 💰 Mutual Fund FAQ Assistant

An **Agentic RAG-based chatbot** that answers mutual fund questions using official SEBI FAQ documents. Built with LangGraph, ChromaDB, FastAPI, and Streamlit.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🎯 Features

- ✅ **Factual Answers Only** - Refuses investment advice and opinion-based queries
- ✅ **Grounded Responses** - Every answer includes citation to source document
- ✅ **Semantic Search** - Uses ChromaDB vector database for intelligent retrieval
- ✅ **Agentic RAG Pipeline** - LangGraph-based workflow with query classification
- ✅ **Modern UI** - Clean, intuitive Streamlit interface
- ✅ **Free API Usage** - Google Gemini embeddings (free) + GROQ LLM

---

## 🏗️ Architecture
```
User Query
    ↓
[Query Classifier] → Factual or Opinion?
    ↓                      ↓
Factual                Opinion
    ↓                      ↓
[Semantic Search]    [Polite Refusal]
    ↓                      ↓
[Answer Generator]       END
    ↓
Answer + Citation
```

### **Tech Stack**

**Backend:**
- FastAPI - REST API framework
- LangChain/LangGraph - Agentic RAG orchestration
- ChromaDB - Vector database
- Google Gemini - Text embeddings (free)
- GROQ - LLM inference (openai/gpt-oss-20b)

**Frontend:**
- Streamlit - Web UI

**Data Sources:**
- 5 official SEBI FAQ PDFs on mutual funds

---

## 📁 Project Structure
```
mutual-fund-faq-assistant/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── classifier.py      # Query classification
│   │   │   ├── retriever.py       # Vector DB retrieval
│   │   │   ├── generator.py       # Answer generation
│   │   │   └── orchestrator.py    # LangGraph workflow
│   │   ├── routes/
│   │   │   └── chat.py            # API endpoints
│   │   ├── utils/
│   │   │   ├── pdf_loader.py      # PDF processing
│   │   │   ├── embeddings.py      # Embedding generation
│   │   │   └── vector_store.py    # ChromaDB operations
│   │   ├── config.py              # Configuration
│   │   ├── models.py              # Pydantic models
│   │   └── main.py                # FastAPI app
│   ├── data/
│   │   ├── pdfs/                  # Downloaded PDFs (gitignored)
│   │   └── chroma_db/             # Vector DB (gitignored)
│   ├── .env.example               # Example environment file
│   └── requirements.txt
├── frontend/
│   ├── app.py                     # Streamlit UI
│   └── requirements.txt
├── scripts/
│   └── setup_vectordb.py          # One-time setup script
├── .gitignore
├── README.md
└── DEPLOYMENT.md
```

---

## 🚀 Quick Start

### **Prerequisites**

- Python 3.9+
- pip
- Virtual environment tool
- Git

### **1. Clone the Repository**
```bash
git clone https://github.com/YOUR_USERNAME/mutual-fund-faq-assistant.git
cd mutual-fund-faq-assistant
```

### **2. Get API Keys**

You'll need two **free** API keys:

1. **GROQ API Key** (for LLM):
   - Sign up at https://console.groq.com
   - Create an API key

2. **Google Gemini API Key** (for embeddings):
   - Get from https://ai.google.dev
   - Free tier available

### **3. Setup Backend**
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys
```

**Edit `backend/.env`:**
```env
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### **4. Setup Vector Database (One-time)**
```bash
# From project root
python scripts/setup_vectordb.py
```

This will:
- ✅ Download 5 SEBI FAQ PDFs
- ✅ Extract and chunk text
- ✅ Generate embeddings using Google Gemini
- ✅ Populate ChromaDB vector database

**Expected time:** 2-5 minutes

### **5. Start Backend API**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend available at: http://localhost:8000

API docs: http://localhost:8000/docs

### **6. Start Frontend (New Terminal)**
```bash
# Navigate to frontend
cd frontend

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit
streamlit run app.py
```

Frontend opens automatically at: http://localhost:8501

---

## 📖 Usage

### **Example Factual Questions (Answered):**
- "What is KYC in mutual funds?"
- "How does Aadhaar-based e-KYC work?"
- "What are derivatives?"
- "What is a mutual fund?"

### **Example Opinion Questions (Refused):**
- "Should I invest in mutual funds?"
- "Which is the best ELSS scheme?"
- "What fund should I buy?"
- "Is this a good investment?"

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Health check with stats |
| POST | `/api/chat` | Process user query |

### **Example API Request**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is KYC?"}'
```

### **Example Response**
```json
{
  "query": "What is KYC?",
  "answer": "KYC stands for Know Your Customer. It is a verification process required by SEBI for investors to establish their identity and address. This process helps prevent fraud and money laundering in financial transactions.",
  "citation": "https://www.sebi.gov.in/sebi_data/faqfiles/jan-2017/1485861159393.pdf",
  "classification": "factual"
}
```

---

## 🧪 Testing

### **Test Backend API**
```bash
# Health check
curl http://localhost:8000/health

# Test query
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is KYC?"}'
```

### **Test Vector Database**
```bash
cd backend
python -c "from app.utils.vector_store import VectorStore; vs = VectorStore(); print(vs.get_collection_stats())"
```

---

## 🔧 Configuration

All configuration is in `backend/.env`:
```env
# API Keys
GROQ_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# LLM Settings
GROQ_MODEL_NAME=openai/gpt-oss-20b
TEMPERATURE=0.2
MAX_TOKENS=500

# Embedding Settings
EMBEDDING_MODEL=models/text-embedding-004

# Vector DB Settings
CHROMA_PERSIST_DIR=./data/chroma_db
COLLECTION_NAME=mutual_fund_faqs
TOP_K_RESULTS=3
```

---

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:
- Render.com (Backend)
- Streamlit Community Cloud (Frontend)
- Railway.app
- Docker deployment

---

## 🐛 Troubleshooting

### **Backend won't start**
- Verify `.env` file exists with valid API keys
- Check if port 8000 is available
- Ensure virtual environment is activated

### **Frontend can't connect**
- Make sure backend is running on port 8000
- Check firewall settings
- Verify `API_URL` in `frontend/app.py`

### **No documents in vector store**
- Run `python scripts/setup_vectordb.py`
- Check internet connection (PDFs download from SEBI)
- Verify Google API key is valid

### **Poor answers or empty responses**
- Check backend logs for errors
- Verify GROQ API key and quota
- Try increasing `MAX_TOKENS` in `.env`

---

## 📊 Data Sources

This chatbot uses **5 official SEBI FAQ documents**:

1. KYC Requirements - Aadhaar e-KYC
2. Equity and Currency Derivatives
3. Mutual Funds - General FAQs
4. Investment Advisory Services
5. Portfolio Management Services

All documents are automatically downloaded from [SEBI's official website](https://www.sebi.gov.in).

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

**Important:** This chatbot provides factual information only and does NOT offer investment advice. Always consult a SEBI-registered investment advisor for personalized financial guidance.

---

## 🙏 Acknowledgments

- **SEBI** - For providing comprehensive FAQ documents
- **Google Gemini** - For free embedding API
- **GROQ** - For fast LLM inference
- **LangChain/LangGraph** - For agentic workflow framework

---

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using LangGraph, ChromaDB, FastAPI, and Streamlit**