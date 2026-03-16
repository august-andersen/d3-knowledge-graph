"""File discovery, hashing, and cache comparison."""

import hashlib
from pathlib import Path

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf", ".jpg", ".jpeg", ".png"}


def scan_directory(directory: str, recursive: bool = False) -> list[Path]:
    """Discover supported files in the given directory."""
    root = Path(directory).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Directory not found: {directory}")

    files = []
    if recursive:
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(path)
    else:
        for path in sorted(root.iterdir()):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(path)

    return files


def compute_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def categorize_files(files: list[Path]) -> dict[str, int]:
    """Count files by extension for display."""
    counts: dict[str, int] = {}
    for f in files:
        ext = f.suffix.lower()
        counts[ext] = counts.get(ext, 0) + 1
    return counts
