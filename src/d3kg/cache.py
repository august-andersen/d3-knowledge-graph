"""Cache read/write/clear logic."""

import json
from datetime import datetime, timezone
from pathlib import Path

CACHE_DIR = Path.home() / ".d3kg"
CACHE_FILE = CACHE_DIR / "cache.json"
CONFIG_FILE = CACHE_DIR / "config.json"


def ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_cache() -> dict:
    ensure_cache_dir()
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {"files": {}, "merged": {"entities": [], "relationships": []}}


def save_cache(cache: dict):
    ensure_cache_dir()
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def clear_cache():
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()


def is_cached(cache: dict, filepath: str, file_hash: str) -> bool:
    entry = cache.get("files", {}).get(filepath)
    if entry and entry.get("hash") == file_hash:
        return True
    return False


def update_file_cache(cache: dict, filepath: str, file_hash: str, entities: list, relationships: list):
    cache.setdefault("files", {})
    cache["files"][filepath] = {
        "hash": file_hash,
        "last_processed": datetime.now(timezone.utc).isoformat(),
        "entities": entities,
        "relationships": relationships,
    }


def remove_stale_files(cache: dict, valid_paths: set[str]):
    """Remove cached entries for files that no longer exist."""
    stale = [p for p in cache.get("files", {}) if p not in valid_paths]
    for p in stale:
        del cache["files"][p]


def load_api_key() -> str | None:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("api_key")
    return None


def save_api_key(api_key: str):
    ensure_cache_dir()
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    config["api_key"] = api_key
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
