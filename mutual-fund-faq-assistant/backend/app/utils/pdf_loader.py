"""
PDF downloading and text extraction utility
"""
import os
import requests
from typing import List, Dict
from pypdf import PdfReader
import io


class PDFLoader:
    """Handles PDF downloading and text extraction"""
    
    def __init__(self, pdf_urls: List[str], download_dir: str = "./data/pdfs"):
        """
        Initialize PDF Loader
        
        Args:
            pdf_urls: List of PDF URLs to download
            download_dir: Directory to save downloaded PDFs
        """
        self.pdf_urls = pdf_urls
        self.download_dir = download_dir
        
        # Create download directory if it doesn't exist
        os.makedirs(self.download_dir, exist_ok=True)
    
    def download_pdf(self, url: str) -> bytes:
        """
        Download PDF from URL
        
        Args:
            url: PDF URL
            
        Returns:
            PDF content as bytes
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading PDF from {url}: {e}")
            raise
    
    def extract_text_from_pdf(self, pdf_content: bytes, source_url: str) -> List[Dict[str, str]]:
        """
        Extract text from PDF content
        
        Args:
            pdf_content: PDF file content as bytes
            source_url: Source URL of the PDF (for citation)
            
        Returns:
            List of dictionaries with page text and metadata
        """
        documents = []
        
        try:
            # Read PDF from bytes
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PdfReader(pdf_file)
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                text = page.extract_text()
                
                # Only add pages with meaningful content
                if text and len(text.strip()) > 50:
                    documents.append({
                        "text": text.strip(),
                        "source": source_url,
                        "page": page_num,
                        "metadata": {
                            "source": source_url,
                            "page": page_num,
                            "total_pages": len(pdf_reader.pages)
                        }
                    })
            
            print(f"✓ Extracted {len(documents)} pages from {source_url}")
            
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            raise
        
        return documents
    
    def load_all_pdfs(self) -> List[Dict[str, str]]:
        """
        Download and extract text from all PDFs
        
        Returns:
            List of all documents with text and metadata
        """
        all_documents = []
        
        print(f"\n📥 Downloading and processing {len(self.pdf_urls)} PDFs...\n")
        
        for idx, url in enumerate(self.pdf_urls, start=1):
            try:
                print(f"[{idx}/{len(self.pdf_urls)}] Processing: {url}")
                
                # Download PDF
                pdf_content = self.download_pdf(url)
                
                # Extract text
                documents = self.extract_text_from_pdf(pdf_content, url)
                all_documents.extend(documents)
                
            except Exception as e:
                print(f"✗ Failed to process {url}: {e}")
                continue
        
        print(f"\n✅ Total documents extracted: {len(all_documents)}\n")
        
        return all_documents


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Input text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Overlap between chunks in characters
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        # Only add non-empty chunks
        if chunk.strip():
            chunks.append(chunk.strip())
        
        start += (chunk_size - overlap)
    
    return chunks


def prepare_documents_for_vectordb(documents: List[Dict[str, str]], 
                                   chunk_size: int = 1000, 
                                   overlap: int = 200) -> List[Dict[str, any]]:
    """
    Prepare documents for vector database by chunking
    
    Args:
        documents: List of documents with text and metadata
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of chunked documents ready for embedding
    """
    prepared_docs = []
    
    for doc in documents:
        text = doc["text"]
        chunks = chunk_text(text, chunk_size, overlap)
        
        for chunk_idx, chunk in enumerate(chunks):
            prepared_docs.append({
                "text": chunk,
                "source": doc["source"],
                "page": doc["page"],
                "chunk_id": chunk_idx,
                "metadata": {
                    **doc["metadata"],
                    "chunk_id": chunk_idx,
                    "total_chunks": len(chunks)
                }
            })
    
    print(f"✓ Created {len(prepared_docs)} chunks from {len(documents)} documents")
    
    return prepared_docs