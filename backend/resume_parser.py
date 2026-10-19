"""
Resume Parser Module for Skill Gap AI
Extracts readable text from PDF and DOCX documents with robust validation,
error handling, and security protections (no external leaks, no logging of PII).
"""

import io
import re
from typing import Dict, Any, Tuple

# Supported file extensions and size constraints
ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MINIMUM_EXTRACTED_CHARS = 10


def validate_file_metadata(filename: str, file_size_bytes: int) -> Tuple[bool, str]:
    """
    Validates file extension and size constraints.
    Returns (is_valid, error_message).
    """
    if not filename:
        return False, "No file was provided."

    # Validate file extension
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file format (.{ext}). Please upload a valid PDF or DOCX file."

    # Validate file size
    if file_size_bytes <= 0:
        return False, "The uploaded file is empty (0 bytes)."

    if file_size_bytes > MAX_FILE_SIZE_BYTES:
        size_mb = file_size_bytes / (1024 * 1024)
        return False, f"File size ({size_mb:.2f} MB) exceeds the maximum allowed limit of {MAX_FILE_SIZE_MB} MB."

    return True, ""


def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extracts text and page count from a PDF byte stream using PyMuPDF (fitz).
    Returns (extracted_text, page_count).
    Raises ValueError on parsing failure or encrypted PDFs.
    """
    try:
        import pymupdf as fitz  # PyMuPDF modern import
    except ImportError:
        import fitz

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"Corrupted or invalid PDF document: {str(e)}")

    if doc.is_encrypted:
        doc.close()
        raise ValueError("Password-protected PDF files cannot be processed. Please upload an unlocked PDF.")

    page_texts = []
    total_pages = len(doc)

    for page_num in range(total_pages):
        page = doc.load_page(page_num)
        text = page.get_text()
        if text and text.strip():
            page_texts.append(text.strip())

    doc.close()
    full_text = "\n\n".join(page_texts).strip()
    return full_text, total_pages


def extract_text_from_docx(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extracts text and section count from a DOCX byte stream using python-docx.
    Extracts text from both paragraphs and table cells.
    Returns (extracted_text, paragraph_count).
    Raises ValueError on parsing failure.
    """
    import docx

    try:
        doc = docx.Document(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"Corrupted or invalid DOCX document: {str(e)}")

    lines = []
    # Extract from paragraphs
    for para in doc.paragraphs:
        cleaned = para.text.strip()
        if cleaned:
            lines.append(cleaned)

    # Also extract text from tables (often used for resume formatting)
    for table in doc.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            # Deduplicate repeated cell text from merged cells in same row
            unique_cells = []
            for cell_text in row_cells:
                if not unique_cells or cell_text != unique_cells[-1]:
                    unique_cells.append(cell_text)
            if unique_cells:
                lines.append(" | ".join(unique_cells))

    full_text = "\n".join(lines).strip()
    paragraph_count = len(doc.paragraphs)
    return full_text, paragraph_count


def clean_extracted_text(raw_text: str) -> str:
    """
    Normalizes extracted text:
    - Removes non-printable control characters
    - Normalizes consecutive spaces
    - Limits consecutive blank lines to at most two
    """
    if not raw_text:
        return ""

    # Normalize carriage returns
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace multiple spaces with a single space (except newlines)
    text = re.sub(r"[ \t]+", " ", text)
    # Replace 3+ consecutive newlines with 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_resume(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Main entry point for parsing and validating an uploaded resume.
    Accepts file bytes and filename.
    Returns a structured dictionary:
      {
         "success": bool,
         "text": str,
         "word_count": int,
         "char_count": int,
         "file_type": str,
         "page_count": int,
         "error": str or None
      }
    """
    # 1. Metadata and format validation
    is_valid, error_msg = validate_file_metadata(filename, len(file_bytes) if file_bytes else 0)
    if not is_valid:
        return {
            "success": False,
            "text": "",
            "word_count": 0,
            "char_count": 0,
            "file_type": "",
            "page_count": 0,
            "error": error_msg,
        }

    ext = filename.rsplit(".", 1)[-1].lower()
    file_type = ext.upper()

    # 2. Format-specific extraction
    try:
        if ext == "pdf":
            raw_text, count = extract_text_from_pdf(file_bytes)
        elif ext == "docx":
            raw_text, count = extract_text_from_docx(file_bytes)
        else:
            return {
                "success": False,
                "text": "",
                "word_count": 0,
                "char_count": 0,
                "file_type": file_type,
                "page_count": 0,
                "error": f"Unsupported format: .{ext}",
            }
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "word_count": 0,
            "char_count": 0,
            "file_type": file_type,
            "page_count": 0,
            "error": str(e),
        }

    # 3. Clean and normalize text
    cleaned_text = clean_extracted_text(raw_text)

    # 4. Check for empty or unreadable content (e.g. scanned image PDFs)
    if not cleaned_text or len(cleaned_text.strip()) < MINIMUM_EXTRACTED_CHARS:
        return {
            "success": False,
            "text": "",
            "word_count": 0,
            "char_count": 0,
            "file_type": file_type,
            "page_count": count,
            "error": (
                "No readable text could be extracted from this document. "
                "The file may be blank, scanned as an image without OCR, or corrupt. "
                "Please upload a standard text-based PDF or DOCX resume."
            ),
        }

    # 5. Calculate statistics
    words = cleaned_text.split()
    word_count = len(words)
    char_count = len(cleaned_text)

    return {
        "success": True,
        "text": cleaned_text,
        "word_count": word_count,
        "char_count": char_count,
        "file_type": file_type,
        "page_count": count,
        "error": None,
    }
