"""Best-effort OCR pipeline for PDF submissions.

Text PDFs use pypdf when available; image/handwriting OCR uses optional
pytesseract + pdf2image dependencies. Missing optional tooling is reported
as a useful processing error rather than crashing the API.
"""
from io import BytesIO


def extract_pdf_text(blob: bytes) -> str:
    try:
        from pypdf import PdfReader
        text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(blob)).pages).strip()
        if text:
            return text
    except Exception:
        pass
    try:
        from pdf2image import convert_from_bytes
        import pytesseract
        pages = convert_from_bytes(blob, dpi=220)
        return "\n".join(pytesseract.image_to_string(page) for page in pages).strip()
    except ImportError as exc:
        raise RuntimeError("OCR dependencies are not installed; install pypdf, pdf2image and pytesseract") from exc
    except Exception as exc:
        raise RuntimeError(f"OCR could not read this PDF: {exc}") from exc
