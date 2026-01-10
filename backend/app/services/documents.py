import pdfplumber
import pandas as pd
from pathlib import Path
from typing import List, Dict
from app.core.config import settings


class DocumentService:
    """Service for processing PDF and Excel documents."""
    
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
    
    def process_document(self, file_path: str) -> List[Dict]:
        """Process document based on file type."""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif file_ext in [".xlsx", ".xls"]:
            return self.extract_text_from_excel(file_path)
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
