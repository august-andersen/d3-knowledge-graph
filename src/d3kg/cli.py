"""Entry point — arg parsing, orchestration, terminal output."""

import argparse
import sys
import webbrowser
from pathlib import Path

from .cache import (
    clear_cache,
    is_cached,
    load_cache,
    remove_stale_files,
    save_cache,
    update_file_cache,
)
from .extractor import (
    extract_image_base64,
    extract_text,
    get_image_media_type,
    get_pdf_page_images,
    is_image_file,
)
from .graph import merge_all_extractions
from .llm import extract_from_image, extract_from_pdf_images, extract_from_text, get_client
from .scanner import categorize_files, compute_hash, scan_directory


def main():
    parser = argparse.ArgumentParser(
        prog="kgraph",
        description="Turn your notes into an interactive knowledge graph.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan (default: current directory)",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recurse into subdirectories",
    )
    parser.add_argument(
        "-l", "--labels",
        action="store_true",
        help="Show relationship labels on edges",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the cache and re-extract everything",
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=8080,
        help="Port for the local server (default: 8080)",
    )

    args = parser.parse_args()

    if args.clear_cache:
        clear_cache()
        print("🗑️  Cache cleared.")

    # Scan
    directory = args.directory
    mode = "recursive" if args.recursive else "flat"
    print(f"\n📂 Scanning {directory}/ ({mode})...")

    try:
        files = scan_directory(directory, recursive=args.recursive)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)

    if not files:
        print("No supported files found.")
        sys.exit(0)

    counts = categorize_files(files)
    parts = []
    for ext, count in sorted(counts.items()):
        parts.append(f"{count} {ext}")
    print(f"Found {len(files)} files ({', '.join(parts)})\n")

    # Load cache and prepare client
    cache = load_cache()
    valid_paths = set()
    needs_extraction = False

    # Check which files need extraction
    for filepath in files:
        fp_str = str(filepath)
        valid_paths.add(fp_str)
        file_hash = compute_hash(filepath)
        if not is_cached(cache, fp_str, file_hash):
            needs_extraction = True

    # Only initialize API client if we need to extract
    client = None
    if needs_extraction:
        print("⏳ Extracting entities...")
        client = get_client()

    # Process files
    for filepath in files:
        fp_str = str(filepath)
        file_hash = compute_hash(filepath)

        if is_cached(cache, fp_str, file_hash):
            cached_entry = cache["files"][fp_str]
            n_ent = len(cached_entry.get("entities", []))
            n_rel = len(cached_entry.get("relationships", []))
            print(f"  ✓ {filepath.name} (cached — {n_ent} entities, {n_rel} relationships)")
            continue

        # Extract based on file type
        result = {"entities": [], "relationships": []}

        if is_image_file(filepath):
            print(f"  ⏳ {filepath.name} (extracting via vision...)", end="", flush=True)
            b64 = extract_image_base64(filepath)
            media_type = get_image_media_type(filepath)
            if b64:
                result = extract_from_image(client, b64, media_type, filepath.name)
        else:
            text = extract_text(filepath)
            if text:
                print(f"  ⏳ {filepath.name} (extracting...)", end="", flush=True)
                result = extract_from_text(client, text, filepath.name)
            elif filepath.suffix.lower() == ".pdf":
                # Scanned PDF — use vision
                print(f"  ⏳ {filepath.name} (extracting via vision...)", end="", flush=True)
                images = get_pdf_page_images(filepath)
                if images:
                    result = extract_from_pdf_images(client, images, filepath.name)
            else:
                print(f"  ⚠ {filepath.name} (no content extracted)")
                continue

        n_ent = len(result.get("entities", []))
        n_rel = len(result.get("relationships", []))
        print(f"\r  ✓ {filepath.name} ({n_ent} entities, {n_rel} relationships)          ")

        update_file_cache(cache, fp_str, file_hash, result.get("entities", []), result.get("relationships", []))

    # Clean stale entries
    remove_stale_files(cache, valid_paths)

    # Merge and save
    merged = merge_all_extractions(cache)
    save_cache(cache)

    n_entities = len(merged["entities"])
    n_relationships = len(merged["relationships"])
    print(f"\n🔗 Merged graph: {n_entities} entities, {n_relationships} relationships across {len(files)} files.\n")

    if n_entities == 0:
        print("No entities found. Nothing to visualize.")
        sys.exit(0)

    # Start server
    from .server import create_app

    app = create_app(merged, show_labels=args.labels)
    url = f"http://localhost:{args.port}"
    print(f"🌐 Knowledge graph running at {url} — press Ctrl+C to stop.\n")

    webbrowser.open(url)

    try:
        app.run(host="127.0.0.1", port=args.port, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Stopped.")


if __name__ == "__main__":
    main()
