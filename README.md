# d3-knowledge-graph

Turn your notes into an interactive knowledge graph.

## How it works

1. Scans a folder for markdown, text, PDF, and image files
2. Sends content to Claude to extract entities and relationships
3. Caches results — only re-processes new or changed files
4. Serves an interactive D3.js force-directed graph on localhost
5. Explore your notes, ideas, and research as a visual network

## Installation

**Preferred (pipx):**

```
pipx install git+https://github.com/august-andersen/d3-knowledge-graph.git
```

**Alternative (pip + venv):**

```
python -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/august-andersen/d3-knowledge-graph.git
```

**From cloned repo:**

```
git clone https://github.com/august-andersen/d3-knowledge-graph.git
cd d3-knowledge-graph
pipx install .
```

## API Key Setup

Set the `ANTHROPIC_API_KEY` environment variable, or run `kgraph` and enter your key when prompted. The key is stored in `~/.d3kg/config.json`.

## Usage

```bash
# Scan current directory
kgraph

# Scan a specific directory
kgraph ./my-notes/

# Recurse into subdirectories
kgraph ./my-notes/ --recursive

# Show edge labels on graph
kgraph --labels

# Clear the cache and re-extract everything
kgraph --clear-cache

# Combine flags
kgraph ./research/ --recursive --labels

# Custom port
kgraph --port 9090
```

## Supported File Types

- `.md` — Markdown
- `.txt` — Plain text
- `.pdf` — PDF (text extraction, with vision fallback for scanned documents)
- `.jpg`, `.jpeg`, `.png` — Images (via Claude vision)

## License

MIT
