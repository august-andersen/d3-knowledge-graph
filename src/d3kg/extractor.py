"""File content extraction for different file types."""

import base64
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
TEXT_EXTENSIONS = {".md", ".txt"}


def extract_text(filepath: Path) -> str | None:
    """Extract text content from a text-based file. Returns None for non-text files."""
    ext = filepath.suffix.lower()

    if ext in TEXT_EXTENSIONS:
        return filepath.read_text(encoding="utf-8", errors="replace")

    if ext == ".pdf":
        return _extract_pdf_text(filepath)

    return None


def extract_image_base64(filepath: Path) -> str | None:
    """Encode an image file as base64. Returns None for non-image files."""
    ext = filepath.suffix.lower()
    if ext not in IMAGE_EXTENSIONS:
        return None

    with open(filepath, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("ascii")


def get_image_media_type(filepath: Path) -> str:
    """Get the media type for an image file."""
    ext = filepath.suffix.lower()
    if ext == ".png":
        return "image/png"
    return "image/jpeg"


def is_image_file(filepath: Path) -> bool:
    return filepath.suffix.lower() in IMAGE_EXTENSIONS


def _extract_pdf_text(filepath: Path) -> str | None:
    """Extract text from a PDF using PyMuPDF."""
    try:
        import fitz
    except ImportError:
        print("  ⚠ PyMuPDF not installed, skipping PDF: " + filepath.name)
        return None

    text_parts = []
    doc = fitz.open(filepath)
    for page in doc:
        text = page.get_text()
        if text.strip():
            text_parts.append(text)
    doc.close()

    full_text = "\n\n".join(text_parts)

    # If no text was extracted (scanned PDF), return None to trigger vision fallback
    if not full_text.strip():
        return None

    return full_text


def get_pdf_page_images(filepath: Path) -> list[tuple[str, str]]:
    """For scanned PDFs, render pages as images and return as (base64, media_type) tuples."""
    try:
        import fitz
    except ImportError:
        return []

    images = []
    doc = fitz.open(filepath)
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        b64 = base64.standard_b64encode(img_bytes).decode("ascii")
        images.append((b64, "image/png"))
    doc.close()
    return images
