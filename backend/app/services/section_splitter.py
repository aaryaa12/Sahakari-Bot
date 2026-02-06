"""
Section-Aware Document Splitter for Nepali Legal Acts
Splits by section headings, preserves structure
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class SectionChunk:
    """Represents a single legal section."""
    section_number: str
    section_title: str
    content: str
    act_name: str
    metadata: Dict


def extract_act_name(filename: str, text: str) -> str:
    """Extract act name from filename or content."""
    filename_lower = filename.lower()
    
    # From filename
    if 'cooperative' in filename_lower:
        # Extract year from content if possible
        year_match = re.search(r'207[0-9]|201[0-9]', text[:500])
        if year_match:
            return f"Cooperatives Act {year_match.group()}"
        return "Cooperatives Act 2074"
    
    if 'electronic' in filename_lower or 'eta' in filename_lower:
        year_match = re.search(r'206[0-9]', text[:500])
        if year_match:
            return f"Electronic Transaction Act {year_match.group()}"
        return "Electronic Transaction Act 2063"
    
    if 'banking' in filename_lower or 'bopa' in filename_lower:
        return "Banking Offences and Punishment Act 2064"
    
    # Try from content
    if 'cooperative' in text[:1000].lower():
        return "Cooperatives Act 2074"
    if 'electronic transaction' in text[:1000].lower():
        return "Electronic Transaction Act 2063"
    
    return "Unknown Act"


def split_into_sections(text: str, filename: str = "document.pdf") -> List[SectionChunk]:
    """
    Split legal document into section-level chunks.
    
    Supports both:
    - English: "Section 43", "43.", "Chapter 3"
    - Nepali: "दफा ४३", "परिच्छेद ३"
    """
    import logging
    logger = logging.getLogger(__name__)
    
    act_name = extract_act_name(filename, text)
    logger.info(f"Extracting sections from {filename}, identified as: {act_name}")
    
    # Regex patterns for section headings (English + Nepali)
    # Matches: "Section 43", "43.", "Section 43:", "दफा ४३"
    section_pattern = re.compile(
        r'(?:^|\n)(?:'
        r'(?:Section|SECTION)\s*(\d+)|'  # Section 43
        r'(?:Chapter|CHAPTER)\s*(\d+)|'  # Chapter 3
        r'(?:Article|ARTICLE)\s*(\d+)|'  # Article 12
        r'(\d+)\.\s+[A-Z]|'  # 43. Definition
        r'दफा\s*([०-९\d]+)|'  # Nepali: दफा ४३
        r'परिच्छेद\s*([०-९\d]+)'  # Nepali: परिच्छेद ३ (Chapter)
        r')[:\.\s]',
        re.MULTILINE
    )
    
    # Find all section positions
    sections = []
    for match in section_pattern.finditer(text):
        # Extract section number from any captured group
        section_num = None
        for group in match.groups():
            if group:
                # Convert Nepali digits to English if needed
                section_num = convert_nepali_to_english(group)
                break
        
        if section_num:
            sections.append({
                'number': section_num,
                'start': match.start(),
                'heading': match.group(0).strip()
            })
    
    # If no sections found, return empty to trigger page-based fallback
    if not sections:
        logger.warning(f"No sections found in {filename}, returning empty list for fallback")
        return []
    
    logger.info(f"Found {len(sections)} section matches in {filename}")
    
    # Create chunks from sections
    # Strategy: Keep ALL sections but deduplicate by keeping the LONGEST version
    section_map = {}  # section_num -> {first: chunk, longest: chunk}
    
    for i, section in enumerate(sections):
        start_pos = section['start']
        
        # End position is start of next section (or end of document)
        end_pos = sections[i + 1]['start'] if i + 1 < len(sections) else len(text)
        
        # Extract section content
        section_content = text[start_pos:end_pos].strip()
        content_length = len(section_content)
        
        section_num = section['number']
        
        # Track both first occurrence and longest version
        if section_num not in section_map:
            section_map[section_num] = {
                'number': section_num,
                'content': section_content,
                'heading': section['heading'],
                'length': content_length,
                'is_first': True
            }
        elif content_length > section_map[section_num]['length']:
            # Found longer version - likely the real content (TOC was shorter)
            section_map[section_num] = {
                'number': section_num,
                'content': section_content,
                'heading': section['heading'],
                'length': content_length,
                'is_first': False
            }
    
    # Now create SectionChunk objects from the best versions
    chunks = []
    for section_num in sorted(section_map.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        section_data = section_map[section_num]
        section_content = section_data['content']
        content_length = section_data['length']
        
        # Filter out TOC entries: very short OR mostly dots/page numbers
        if content_length < 100:  # TOC entries are typically < 100 chars
            logger.debug(f"Skipping short section {section_num} ({content_length} chars) - likely TOC")
            continue
        
        # Check if it's a TOC line (lots of dots)
        dot_ratio = section_content.count('.') / max(len(section_content), 1)
        if dot_ratio > 0.3:  # More than 30% dots = TOC
            logger.debug(f"Skipping section {section_num} - high dot ratio ({dot_ratio:.1%}) - likely TOC")
            continue
        
        # Build section keys (for exact matching)
        section_keys = [
            f"Section {section_num}",
            f"section {section_num}",
            f"SECTION {section_num}",
            f"दफा {section_num}",  # Add Nepali version
        ]
        
        # Extract title (first line after heading)
        lines = section_content.split('\n')
        title_line = lines[1] if len(lines) > 1 else section_data['heading']
        
        chunk = SectionChunk(
            section_number=section_num,
            section_title=title_line[:100].strip(),  # First 100 chars of title
            content=section_content,
            act_name=act_name,
            metadata={
                'act_name': act_name,
                'section_number': section_num,
                'section_keys': section_keys,
                'has_section_structure': True,
                'source_file': filename
            }
        )
        chunks.append(chunk)
    
    logger.info(f"Returning {len(chunks)} unique sections after deduplication")
    return chunks


def convert_nepali_to_english(nepali_num: str) -> str:
    """Convert Nepali numerals to English."""
    nepali_to_english = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    
    result = nepali_num
    for nep, eng in nepali_to_english.items():
        result = result.replace(nep, eng)
    
    return result


def extract_section_number_from_query(query: str) -> Optional[str]:
    """
    Extract section number from user query.
    Supports: "section 43", "Section 43 of ETA", "दफा ४३"
    """
    query_lower = query.lower()
    
    # English patterns
    patterns = [
        r'(?:section|chapter|article)\s*(\d+)',
        r'sec\.\s*(\d+)',
        r'art\.\s*(\d+)',
        r'दफा\s*([०-९\d]+)',
        r'परिच्छेद\s*([०-९\d]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            section_num = match.group(1)
            return convert_nepali_to_english(section_num)
    
    return None


# Example usage and testing
if __name__ == "__main__":
    # Mock text simulating a legal PDF
    mock_text = """
ELECTRONIC TRANSACTION ACT, 2063 (2008)

Chapter 1: Preliminary

Section 1. Short title and commencement
(1) This Act may be called as the "Electronic Transaction Act, 2063 (2008)".
(2) This Act shall come into force immediately.

Section 2. Definitions
Unless the subject or context otherwise requires, in this Act:
(a) "Electronic" means technology relating to electrical, digital, magnetic, wireless, optical, electromagnetic or photonic or any other technology.
(b) "Electronic record" means a record generated in an electronic form.

Chapter 3: Digital Signature

Section 43. Penalty for breach of confidentiality
Whoever accesses confidential electronic records without authorization shall be punished with imprisonment up to two years or fine up to Two Hundred Thousand Rupees (NPR 200,000), or both.

Section 44. Unauthorized modification
Any person who modifies electronic records without authorization shall face penalties.
"""

    # Test section splitter
    chunks = split_into_sections(mock_text, "eta-2063.pdf")
    
    print(f"Total chunks: {len(chunks)}\n")
    
    for chunk in chunks[:3]:
        print(f"Section: {chunk.section_number}")
        print(f"Act: {chunk.act_name}")
        print(f"Title: {chunk.section_title}")
        print(f"Metadata: {chunk.metadata}")
        print(f"Content preview: {chunk.content[:150]}...")
        print("-" * 80)
    
    # Test section extraction from query
    queries = [
        "What is Section 43 of ETA?",
        "Tell me about section 2",
        "What does दफा ४३ say?",
        "How to register cooperative?"
    ]
    
    print("\nQuery Section Extraction Tests:")
    for q in queries:
        section = extract_section_number_from_query(q)
        print(f"Query: {q}")
        print(f"Extracted section: {section}\n")
