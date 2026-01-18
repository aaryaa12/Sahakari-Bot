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
            max_rows = getattr(settings, "CSV_MAX_ROWS", 5000)
            chunk_rows = getattr(settings, "CSV_CHUNK_ROWS", 1000)

            # Try reading with pandas first (handles encoding better)
            def read_csv_chunks(encoding: str):
                nonlocal chunks
                processed_rows = 0
                for df_chunk in pd.read_csv(
                    file_path,
                    encoding=encoding,
                    on_bad_lines="skip",
                    low_memory=False,
                    chunksize=chunk_rows,
                ):
                    if processed_rows >= max_rows:
                        break
                    # Trim chunk if it exceeds max rows
                    remaining = max_rows - processed_rows
                    if remaining <= 0:
                        break
                    if len(df_chunk) > remaining:
                        df_chunk = df_chunk.head(remaining)
                    text = df_chunk.to_string(index=False)
                    if text and text.strip():
                        chunks.append({
                            "text": text,
                            "page": (processed_rows // chunk_rows) + 1,
                            "source": Path(file_path).name,
                            "type": "csv"
                        })
                    processed_rows += len(df_chunk)

            try:
                read_csv_chunks("utf-8")
            except UnicodeDecodeError:
                try:
                    read_csv_chunks("latin-1")
                except Exception as e:
                    logger.warning(f"Pandas CSV read failed, trying plain text: {e}")
                    # Last resort: read as plain text (limited)
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = "".join([next(f) for _ in range(max_rows)]).strip()
                        if text:
                            chunks.append({
                                "text": text,
                                "page": 1,
                                "source": Path(file_path).name,
                                "type": "csv"
                            })
            except Exception as e:
                logger.warning(f"CSV read error, trying plain text: {e}")
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = "".join([next(f) for _ in range(max_rows)]).strip()
                    if text:
                        chunks.append({
                            "text": text,
                            "page": 1,
                            "source": Path(file_path).name,
                            "type": "csv"
                        })
            
            if not chunks:
                raise ValueError("No readable content found in CSV")
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
    


document_service = DocumentService()
