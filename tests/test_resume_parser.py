"""
Unit Tests for Skill Gap AI - Resume Parser and Workflow Validation
Covers PDF parsing, DOCX parsing, error handling, validation, and session constraints.
"""

import io
try:
    import pymupdf as fitz  # PyMuPDF modern import
except ImportError:
    import fitz
import docx
import pytest

from backend.resume_parser import (
    parse_resume,
    validate_file_metadata,
    clean_extracted_text,
    extract_text_from_pdf,
    extract_text_from_docx,
    MAX_FILE_SIZE_BYTES,
)


def create_sample_pdf_bytes(text_content: str = "Alex Morgan\nSenior Software Engineer\nPython, React, AWS") -> bytes:
    """Helper to create a valid PDF file in-memory using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    if text_content:
        page.insert_text((50, 72), text_content, fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_sample_docx_bytes(paragraphs: list = None, table_data: list = None) -> bytes:
    """Helper to create a valid DOCX file in-memory using python-docx."""
    doc = docx.Document()
    if paragraphs is None:
        paragraphs = [
            "Taylor Swift",
            "Full Stack Developer with 4 years experience",
            "Skills: Python, TypeScript, Docker, Kubernetes, PostgreSQL",
        ]
    for p in paragraphs:
        doc.add_paragraph(p)

    if table_data:
        table = doc.add_table(rows=len(table_data), cols=len(table_data[0]))
        for r_idx, row in enumerate(table_data):
            for c_idx, val in enumerate(row):
                table.cell(r_idx, c_idx).text = val

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()


class TestFileValidation:
    """Test file metadata and extension validation."""

    def test_valid_pdf_metadata(self):
        valid, err = validate_file_metadata("resume.pdf", 1024)
        assert valid is True
        assert err == ""

    def test_valid_docx_metadata(self):
        valid, err = validate_file_metadata("candidate_cv.docx", 2048)
        assert valid is True
        assert err == ""

    def test_case_insensitive_extension(self):
        valid, err = validate_file_metadata("Resume.PDF", 1024)
        assert valid is True
        assert err == ""

    def test_invalid_extension(self):
        for bad_name in ["resume.txt", "resume.png", "resume.exe", "resume"]:
            valid, err = validate_file_metadata(bad_name, 1024)
            assert valid is False
            assert "Unsupported file format" in err

    def test_empty_file_size(self):
        valid, err = validate_file_metadata("resume.pdf", 0)
        assert valid is False
        assert "empty (0 bytes)" in err

    def test_exceeds_max_size(self):
        oversized = MAX_FILE_SIZE_BYTES + 1
        valid, err = validate_file_metadata("large_resume.pdf", oversized)
        assert valid is False
        assert "exceeds the maximum allowed limit" in err


class TestPDFExtraction:
    """Test extraction of text from PDF files using PyMuPDF."""

    def test_extract_valid_pdf(self):
        sample_text = "John Doe\nCloud Architect\nExtensive experience in GCP, Terraform, Python."
        pdf_bytes = create_sample_pdf_bytes(sample_text)
        result = parse_resume(pdf_bytes, "john_doe_resume.pdf")

        assert result["success"] is True
        assert result["file_type"] == "PDF"
        assert "John Doe" in result["text"]
        assert "Cloud Architect" in result["text"]
        assert result["word_count"] > 5
        assert result["char_count"] > 20
        assert result["error"] is None

    def test_blank_pdf_fails_gracefully(self):
        blank_pdf_bytes = create_sample_pdf_bytes(text_content="")
        result = parse_resume(blank_pdf_bytes, "blank.pdf")

        assert result["success"] is False
        assert result["text"] == ""
        assert "No readable text could be extracted" in result["error"]

    def test_corrupted_pdf_handled(self):
        corrupted_bytes = b"%PDF-1.4\ncorrupted content that is not a valid pdf..."
        result = parse_resume(corrupted_bytes, "corrupt.pdf")

        assert result["success"] is False
        assert result["error"] is not None


class TestDOCXExtraction:
    """Test extraction of text from DOCX files using python-docx."""

    def test_extract_valid_docx(self):
        docx_bytes = create_sample_docx_bytes(
            paragraphs=["Sarah Connor", "DevOps Engineer", "Kubernetes, Helm, CI/CD pipelines"],
            table_data=[["Company", "Role", "Years"], ["TechCorp", "Lead SRE", "2021-2025"]],
        )
        result = parse_resume(docx_bytes, "sarah_resume.docx")

        assert result["success"] is True
        assert result["file_type"] == "DOCX"
        assert "Sarah Connor" in result["text"]
        assert "TechCorp" in result["text"]
        assert "Kubernetes" in result["text"]
        assert result["word_count"] > 5
        assert result["error"] is None

    def test_blank_docx_fails_gracefully(self):
        doc = docx.Document()
        bio = io.BytesIO()
        doc.save(bio)
        blank_docx_bytes = bio.getvalue()

        result = parse_resume(blank_docx_bytes, "blank.docx")
        assert result["success"] is False
        assert "No readable text could be extracted" in result["error"]

    def test_corrupted_docx_handled(self):
        corrupted_bytes = b"PK\x03\x04not a valid zip or docx file"
        result = parse_resume(corrupted_bytes, "corrupt.docx")

        assert result["success"] is False
        assert result["error"] is not None


class TestTextCleaning:
    """Test text cleanup and normalization."""

    def test_clean_text_normalizes_whitespace(self):
        raw = "Alex   Morgan \t\t Engineer \n\n\n\n\n Python \r\n\r\n React"
        cleaned = clean_extracted_text(raw)
        assert "   " not in cleaned
        assert "\r" not in cleaned
        assert "\n\n\n" not in cleaned
        assert "Alex Morgan Engineer" in cleaned
