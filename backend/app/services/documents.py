import pdfplumber
import pandas as pd
from pathlib import Path
from typing import List, Dict
from app.core.config import settings
from app.services.section_splitter import split_into_sections
import csv
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for processing PDF, Excel, CSV, and TXT documents."""
    
    def extract_text_from_pdf(self, file_path: str) -> List[Dict]:
        """Extract text from PDF using robust legal parser."""
        chunks = []
        try:
            filename = Path(file_path).name
            
            # Check if this is a legal document
            is_legal = any(keyword in filename.lower() for keyword in 
                          ['act', 'law', 'regulation', 'cooperative', 'eta', 'transaction'])
            
            if is_legal:
                logger.info(f"🔍 START extract_text for {filename}")
                
                # Import legal parser
                from app.services.legal_parser import legal_parser
                
                # Extract text per page using pdfplumber (preserves line breaks)
                page_texts = []
                full_text = ""
                
                with pdfplumber.open(file_path) as pdf:
                    total_pages = len(pdf.pages)
                    logger.info(f"   PDF has {total_pages} pages")
                    
                    for i, page in enumerate(pdf.pages, 1):
                        page_text = page.extract_text()
                        if page_text:
                            page_texts.append(page_text)
                            full_text += page_text + "\n"
                        
                        if i % 10 == 0:
                            logger.info(f"   Extracted {i}/{total_pages} pages...")
                
                if not full_text.strip():
                    raise Exception("No text extracted from PDF")
                
                logger.info(f"✅ DONE extract_text: {len(full_text):,} chars, {len(full_text.splitlines()):,} lines, {len(page_texts)} pages")
                
                # Parse document into sections
                logger.info(f"🔍 START section_split for {filename}")
                sections = legal_parser.parse_document(full_text, filename, page_texts)
                logger.info(f"✅ DONE section_split: {len(sections)} sections detected")
                
                if sections:
                    logger.info(f"🔍 START chunking {len(sections)} sections")
                    
                    # Chunk each section
                    for idx, section in enumerate(sections, 1):
                        logger.info(f"   Chunking section {idx}/{len(sections)}: Section {section.section_number} ({len(section.full_text)} chars)...")
                        
                        section_chunks = legal_parser.chunk_section(section)
                        logger.info(f"   Created {len(section_chunks)} chunks for Section {section.section_number}")
                        
                        for chunk in section_chunks:
                            chunks.append({
                                "text": chunk.text,
                                "page": chunk.page_range,
                                "source": filename,
                                "type": "pdf",
                                "metadata": {
                                    "act_name": chunk.act_name,
                                    "chapter_number": chunk.chapter_number,
                                    "section_number": chunk.section_number,
                                    "section_title": chunk.section_title,
                                    "page_range": chunk.page_range,
                                    "chunk_index": chunk.chunk_index,
                                    "total_chunks": chunk.total_chunks,
                                    "has_section_structure": True
                                }
                            })
                    
                    logger.info(f"✅ DONE chunking: Created {len(chunks)} total chunks from {len(sections)} sections")
                else:
                    # Fallback to page-based
                    logger.warning(f"No sections detected in {filename}, using page-based fallback")
                    for page_num, page_text in enumerate(page_texts, start=1):
                        if page_text.strip():
                            chunks.append({
                                "text": page_text,
                                "page": page_num,
                                "source": filename,
                                "type": "pdf"
                            })
            else:
                # Non-legal documents: page-based chunking
                logger.info(f"Using page-based chunking for {filename}")
                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages, start=1):
                        text = page.extract_text()
                        if text and text.strip():
                            chunks.append({
                                "text": text,
                                "page": page_num,
                                "source": filename,
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
