import pdfplumber
import pandas as pd
from pathlib import Path
from typing import List, Dict
from app.core.config import settings
import csv
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for processing PDF, Excel, CSV, and TXT documents."""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text_from_pdf(self, file_path: str) -> List[Dict]:
        """Extract text from PDF with page numbers."""
        chunks = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text and text.strip():
                        chunks.append({
                            "text": text,
                            "page": page_num,
                            "source": Path(file_path).name,
                            "type": "pdf"
                        })
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")
        
        return chunks
    
    def extract_text_from_excel(self, file_path: str) -> List[Dict]:
        """Extract text from Excel file."""
        chunks = []
        try:
            excel_file = pd.ExcelFile(file_path)
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Convert dataframe to text
                text = f"Sheet: {sheet_name}\n\n"
                text += df.to_string(index=False)
                
                if text.strip():
                    chunks.append({
                        "text": text,
                        "page": sheet_name,
                        "source": Path(file_path).name,
                        "type": "excel"
                    })
        except Exception as e:
            raise Exception(f"Error extracting Excel: {str(e)}")
        
        return chunks
    
    def extract_text_from_csv(self, file_path: str) -> List[Dict]:
        """Extract text from CSV file."""
        chunks = []
        try:
            # Try reading with pandas first (handles encoding better)
            try:
                # Read CSV with error handling
                df = pd.read_csv(
                    file_path, 
                    encoding='utf-8', 
                    on_bad_lines='skip',
                    low_memory=False
                )
                text = df.to_string(index=False)
            except UnicodeDecodeError:
                # Fallback to different encodings
                try:
                    df = pd.read_csv(
                        file_path, 
                        encoding='latin-1', 
                        on_bad_lines='skip',
                        low_memory=False
                    )
                    text = df.to_string(index=False)
                except Exception as e:
                    logger.warning(f"Pandas CSV read failed, trying plain text: {e}")
                    # Last resort: read as plain text
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
            except Exception as e:
                logger.warning(f"CSV read error, trying plain text: {e}")
                # Last resort: read as plain text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            
            if text and text.strip():
                # For very large CSV files, split into chunks
                chunk_size = 10000  # Characters per chunk
                if len(text) > chunk_size:
                    lines = text.split('\n')
                    current_chunk = ""
                    chunk_num = 1
                    
                    for line in lines:
                        if len(current_chunk) + len(line) > chunk_size and current_chunk:
                            chunks.append({
                                "text": current_chunk.strip(),
                                "page": chunk_num,
                                "source": Path(file_path).name,
                                "type": "csv"
                            })
                            current_chunk = line + "\n"
                            chunk_num += 1
                        else:
                            current_chunk += line + "\n"
                    
                    # Add remaining chunk
                    if current_chunk.strip():
                        chunks.append({
                            "text": current_chunk.strip(),
                            "page": chunk_num,
                            "source": Path(file_path).name,
                            "type": "csv"
                        })
                else:
                    chunks.append({
                        "text": text,
                        "page": 1,
                        "source": Path(file_path).name,
                        "type": "csv"
                    })
        except Exception as e:
            raise Exception(f"Error extracting CSV: {str(e)}")
        
        return chunks
    
    def extract_text_from_txt(self, file_path: str) -> List[Dict]:
        """Extract text from TXT file."""
        chunks = []
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            text = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if text is None:
                # Last resort: read with error handling
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            
            if text and text.strip():
                # Split large text files into chunks by paragraphs or lines
                lines = text.split('\n')
                chunk_size = 5000  # Characters per chunk
                current_chunk = ""
                chunk_num = 1
                
                for line in lines:
                    if len(current_chunk) + len(line) > chunk_size and current_chunk:
                        chunks.append({
                            "text": current_chunk.strip(),
                            "page": chunk_num,
                            "source": Path(file_path).name,
                            "type": "txt"
                        })
                        current_chunk = line + "\n"
                        chunk_num += 1
                    else:
                        current_chunk += line + "\n"
                
                # Add remaining chunk
                if current_chunk.strip():
                    chunks.append({
                        "text": current_chunk.strip(),
                        "page": chunk_num,
                        "source": Path(file_path).name,
                        "type": "txt"
                    })
        except Exception as e:
            raise Exception(f"Error extracting TXT: {str(e)}")
        
        return chunks
    
    def process_document(self, file_path: str) -> List[Dict]:
        """Process document based on file type."""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif file_ext in [".xlsx", ".xls"]:
            return self.extract_text_from_excel(file_path)
        elif file_ext == ".csv":
            return self.extract_text_from_csv(file_path)
        elif file_ext == ".txt":
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def save_file(self, content: bytes, filename: str) -> str:
        """Save uploaded file and return path."""
        # Sanitize filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
        file_path = self.upload_dir / safe_filename
        
        # Handle duplicate filenames
        counter = 1
        original_path = file_path
        while file_path.exists():
            stem = original_path.stem
            suffix = original_path.suffix
            file_path = self.upload_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return str(file_path)


document_service = DocumentService()
