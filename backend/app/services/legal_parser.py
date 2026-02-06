"""
Robust Legal Document Parser for Nepal Acts
Implements deterministic heading-aware parsing with chapter support
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


def roman_to_arabic(roman: str) -> int:
    """Convert Roman numerals to Arabic numbers."""
    roman_values = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000
    }
    
    roman = roman.upper().strip()
    result = 0
    prev_value = 0
    
    for char in reversed(roman):
        value = roman_values.get(char, 0)
        if value < prev_value:
            result -= value
        else:
            result += value
        prev_value = value
    
    return result


@dataclass
class Section:
    """Represents a legal section with metadata."""
    act_name: str
    chapter_number: Optional[int]
    chapter_title: Optional[str]
    section_number: str
    section_title: str
    full_text: str
    start_page: int
    end_page: int


@dataclass
class Chunk:
    """Represents a sub-chunk of a section."""
    act_name: str
    chapter_number: Optional[int]
    section_number: str
    section_title: str
    text: str
    page_range: str
    chunk_index: int
    total_chunks: int


class LegalDocumentParser:
    """Parser for Nepal legal acts with robust heading detection."""
    
    def __init__(self):
        # Primary pattern: "4. Title of Section" at line start
        self.section_pattern = re.compile(
            r'^\s*(\d{1,3})\.\s+(.+)$',
            re.MULTILINE
        )
        
        # Chapter pattern: "Chapter - 3" or "Chapter III" at line start
        self.chapter_pattern = re.compile(
            r'^\s*Chapter\s*[-–]?\s*([0-9IVXLC]+)\b(.*)$',
            re.MULTILINE | re.IGNORECASE
        )
        
        # Nepali section pattern: "दफा ४३"
        self.nepali_section_pattern = re.compile(
            r'^\s*दफा\s+([०-९\d]+)[\s\.\:]+(.*)$',
            re.MULTILINE
        )
    
    def extract_act_name(self, filename: str, text: str) -> str:
        """Extract act name from filename or content."""
        filename_lower = filename.lower()
        
        if 'cooperative' in filename_lower or 'coop' in filename_lower:
            # Try to extract year
            year_match = re.search(r'20\d{2}', filename)
            if year_match:
                return f"Cooperatives Act {year_match.group()}"
            return "Cooperatives Act 2017"
        
        if 'electronic' in filename_lower or 'eta' in filename_lower:
            year_match = re.search(r'20\d{2}', filename)
            if year_match:
                return f"Electronic Transaction Act {year_match.group()}"
            return "Electronic Transaction Act 2063"
        
        # Try from content
        if 'cooperative' in text[:2000].lower():
            return "Cooperatives Act 2017"
        if 'electronic transaction' in text[:2000].lower():
            return "Electronic Transaction Act 2063"
        
        return "Unknown Act"
    
    def convert_nepali_digits(self, nepali_num: str) -> str:
        """Convert Nepali numerals to English."""
        nepali_to_english = {
            '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
            '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
        }
        
        result = nepali_num
        for nep, eng in nepali_to_english.items():
            result = result.replace(nep, eng)
        
        return result
    
    def detect_headings(self, text: str, filename: str) -> List[Dict]:
        """
        Detect all section and chapter headings in document.
        Returns list of {type, number, title, position}.
        """
        headings = []
        
        # Detect chapters
        for match in self.chapter_pattern.finditer(text):
            chapter_num_str = match.group(1)
            chapter_title = match.group(2).strip() if len(match.groups()) > 1 else ""
            
            # Convert Roman to Arabic if needed
            if chapter_num_str.isdigit():
                chapter_num = int(chapter_num_str)
            else:
                chapter_num = roman_to_arabic(chapter_num_str)
            
            headings.append({
                'type': 'chapter',
                'number': chapter_num,
                'title': chapter_title,
                'position': match.start(),
                'raw': match.group(0).strip()
            })
        
        # Detect English sections
        for match in self.section_pattern.finditer(text):
            section_num = match.group(1)
            section_title = match.group(2).strip()
            
            # Filter out false positives (references to sections)
            # Check context: should not be preceded by "in Section" or "to Section"
            context_start = max(0, match.start() - 50)
            context = text[context_start:match.start()].lower()
            
            if any(phrase in context for phrase in ['in section', 'to section', 'under section', 'section ']):
                continue
            
            headings.append({
                'type': 'section',
                'number': section_num,
                'title': section_title,
                'position': match.start(),
                'raw': match.group(0).strip()
            })
        
        # Detect Nepali sections
        for match in self.nepali_section_pattern.finditer(text):
            section_num_nepali = match.group(1)
            section_title = match.group(2).strip()
            
            section_num = self.convert_nepali_digits(section_num_nepali)
            
            headings.append({
                'type': 'section',
                'number': section_num,
                'title': section_title,
                'position': match.start(),
                'raw': match.group(0).strip()
            })
        
        # Sort by position
        headings.sort(key=lambda x: x['position'])
        
        return headings
    
    def parse_document(self, text: str, filename: str, page_texts: List[str]) -> List[Section]:
        """
        Parse legal document into structured sections.
        
        Args:
            text: Full document text
            filename: PDF filename
            page_texts: List of text per page for page number tracking
        
        Returns:
            List of Section objects
        """
        logger.info(f"   Extracting act name...")
        act_name = self.extract_act_name(filename, text)
        logger.info(f"   Act name: {act_name}")
        
        logger.info(f"   Detecting headings (running regex on {len(text):,} chars)...")
        headings = self.detect_headings(text, filename)
        
        logger.info(f"   Detected {len(headings)} headings in {filename}")
        logger.info(f"     Chapters: {len([h for h in headings if h['type'] == 'chapter'])}")
        logger.info(f"     Sections: {len([h for h in headings if h['type'] == 'section'])}")
        
        if not headings:
            logger.warning(f"No headings found in {filename}")
            return []
        
        sections = []
        current_chapter_num = None
        current_chapter_title = None
        
        logger.info(f"   Building sections from headings...")
        
        for i, heading in enumerate(headings):
            if (i + 1) % 10 == 0:
                logger.info(f"     Processing heading {i+1}/{len(headings)}...")
            if heading['type'] == 'chapter':
                # Update current chapter context
                current_chapter_num = heading['number']
                current_chapter_title = heading['title']
                continue
            
            # This is a section
            section_num = heading['number']
            section_title = heading['title']
            start_pos = heading['position']
            
            # Determine end position
            if i + 1 < len(headings):
                # Find next section (skip chapters)
                next_section_idx = i + 1
                while next_section_idx < len(headings) and headings[next_section_idx]['type'] == 'chapter':
                    # Update chapter if we pass one
                    next_chapter = headings[next_section_idx]
                    if next_chapter['position'] < start_pos:
                        current_chapter_num = next_chapter['number']
                        current_chapter_title = next_chapter['title']
                    next_section_idx += 1
                
                if next_section_idx < len(headings):
                    end_pos = headings[next_section_idx]['position']
                else:
                    end_pos = len(text)
            else:
                end_pos = len(text)
            
            # Extract section text
            section_text = text[start_pos:end_pos].strip()
            
            # Determine page numbers
            start_page = self._find_page_number(start_pos, page_texts)
            end_page = self._find_page_number(end_pos, page_texts)
            
            section = Section(
                act_name=act_name,
                chapter_number=current_chapter_num,
                chapter_title=current_chapter_title,
                section_number=section_num,
                section_title=section_title,
                full_text=section_text,
                start_page=start_page,
                end_page=end_page
            )
            
            sections.append(section)
        
        logger.info(f"Parsed {len(sections)} sections from {filename}")
        return sections
    
    def _find_page_number(self, position: int, page_texts: List[str]) -> int:
        """Find which page a text position belongs to."""
        cumulative_length = 0
        
        for page_num, page_text in enumerate(page_texts, start=1):
            cumulative_length += len(page_text) + 1  # +1 for newline
            if position < cumulative_length:
                return page_num
        
        return len(page_texts)
    
    def chunk_section(self, section: Section, max_tokens: int = 1000, overlap: int = 150) -> List[Chunk]:
        """
        Split a section into sub-chunks with overlap.
        
        Args:
            section: Section to chunk
            max_tokens: Maximum tokens per chunk (approximated as words * 1.3)
            overlap: Overlap tokens between chunks
        
        Returns:
            List of Chunk objects
        """
        logger.debug(f"Chunking Section {section.section_number}: {len(section.full_text)} chars")
        
        # Approximate: 1 token ≈ 0.75 words, so 1000 tokens ≈ 750 words
        max_words = int(max_tokens * 0.75)
        overlap_words = int(overlap * 0.75)
        
        # Ensure overlap is less than max to prevent infinite loop
        if overlap_words >= max_words:
            overlap_words = max_words // 2
            logger.warning(f"Overlap ({overlap_words}) >= max_words ({max_words}), reduced overlap")
        
        words = section.full_text.split()
        logger.debug(f"Section has {len(words)} words, max_words={max_words}, overlap={overlap_words}")
        
        if len(words) <= max_words:
            # Single chunk
            logger.debug(f"Section {section.section_number} fits in single chunk")
            return [Chunk(
                act_name=section.act_name,
                chapter_number=section.chapter_number,
                section_number=section.section_number,
                section_title=section.section_title,
                text=section.full_text,
                page_range=f"{section.start_page}-{section.end_page}",
                chunk_index=0,
                total_chunks=1
            )]
        
        # Multiple chunks with overlap
        chunks = []
        start_idx = 0
        chunk_idx = 0
        max_iterations = 1000  # Safety limit
        iteration = 0
        
        while start_idx < len(words) and iteration < max_iterations:
            iteration += 1
            end_idx = min(start_idx + max_words, len(words))
            chunk_words = words[start_idx:end_idx]
            chunk_text = ' '.join(chunk_words)
            
            logger.debug(f"Creating chunk {chunk_idx}: words[{start_idx}:{end_idx}] = {len(chunk_words)} words")
            
            chunks.append(Chunk(
                act_name=section.act_name,
                chapter_number=section.chapter_number,
                section_number=section.section_number,
                section_title=section.section_title,
                text=chunk_text,
                page_range=f"{section.start_page}-{section.end_page}",
                chunk_index=chunk_idx,
                total_chunks=0  # Will update after loop
            ))
            
            # Move to next chunk start with overlap
            # CRITICAL: Ensure we always move forward
            next_start = end_idx - overlap_words
            
            if next_start <= start_idx:
                # Would move backwards or stay same - force forward
                next_start = start_idx + max(1, max_words // 2)
                logger.warning(f"Overlap too large, forcing forward: {start_idx} -> {next_start}")
            
            start_idx = next_start
            chunk_idx += 1
            
            # Additional safety: if we're at or past the end, stop
            if start_idx >= len(words):
                break
        
        if iteration >= max_iterations:
            logger.error(f"Hit max iterations ({max_iterations}) for Section {section.section_number}!")
            raise RuntimeError(f"Chunking infinite loop detected for Section {section.section_number}")
        
        # Update total_chunks for all
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
        
        logger.debug(f"Section {section.section_number} split into {len(chunks)} chunks")
        return chunks


# Global parser instance
legal_parser = LegalDocumentParser()
