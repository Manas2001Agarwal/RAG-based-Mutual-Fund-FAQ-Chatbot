"""
Configuration management using pydantic-settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    GROQ_API_KEY: str
    GOOGLE_API_KEY: str
    
    # LLM Configuration
    GROQ_MODEL_NAME: str = "openai/gpt-oss-20b"
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 500
    
    # Embedding Configuration (Free Google Gemini model)
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    
    # Vector DB Configuration
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    COLLECTION_NAME: str = "mutual_fund_faqs"
    
    # PDF Sources
    PDF_URLS: str
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Retrieval Configuration
    TOP_K_RESULTS: int = 3
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def pdf_urls_list(self) -> List[str]:
        """Convert comma-separated PDF URLs to list"""
        return [url.strip() for url in self.PDF_URLS.split(",")]
    
    @property
    def chroma_persist_path(self) -> str:
        """Get absolute path for ChromaDB persistence"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, self.CHROMA_PERSIST_DIR.lstrip("./"))


# Global settings instance
settings = Settings()