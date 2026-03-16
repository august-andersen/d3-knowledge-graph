"""Anthropic API calls, prompt construction, JSON parsing."""

import json
import os

import anthropic

from .cache import load_api_key, save_api_key

MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """You are an entity and relationship extractor. Analyze the following document and extract:

1. ENTITIES: People, concepts, ideas, projects, tools, technologies, organizations, places, theories, or any other notable nouns/subjects. For each entity:
   - "name": a short canonical name (consistent casing, deduplicate variants like "ML" and "Machine Learning" into one)
   - "category": a short category you determine organically from the content (e.g., "person", "concept", "technology", "project", "organization", "theory"). Use consistent category names across extractions.
   - "description": a one-sentence description based on the document content.

2. RELATIONSHIPS: Connections between entities. For each relationship:
   - "source": entity name
   - "target": entity name
   - "label": a short verb/phrase describing the relationship (e.g., "uses", "created", "relates to", "part of", "influences", "depends on")
   - "weight": 1-3 (1 = weak/tangential, 2 = moderate, 3 = strong/core relationship)

Return ONLY valid JSON:
{
  "entities": [...],
  "relationships": [...]
}

Be thorough but not excessive. Extract the most meaningful entities and connections. Prefer fewer, higher-quality extractions over exhaustive low-quality ones."""


def get_api_key() -> str:
    """Get API key from env var, config file, or prompt user."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key

    key = load_api_key()
    if key:
        return key

    print()
    key = input("Enter your Anthropic API key: ").strip()
    if not key:
        raise SystemExit("No API key provided.")
    save_api_key(key)
    return key


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=get_api_key())


def extract_from_text(client: anthropic.Anthropic, text: str, filename: str) -> dict:
    """Extract entities and relationships from text content."""
    user_content = f"Document: {filename}\n\n{text}"

    # Chunk if very large (rough estimate: 4 chars per token)
    if len(text) > 400_000:
        return _extract_chunked(client, text, filename)

    return _call_api(client, [{"type": "text", "text": user_content}])


def extract_from_image(client: anthropic.Anthropic, image_b64: str, media_type: str, filename: str) -> dict:
    """Extract entities and relationships from an image."""
    content = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_b64,
            },
        },
        {
            "type": "text",
            "text": f"Document: {filename}\n\nExtract entities and relationships from this image.",
        },
    ]
    return _call_api(client, content)


def extract_from_pdf_images(client: anthropic.Anthropic, images: list[tuple[str, str]], filename: str) -> dict:
    """Extract from scanned PDF rendered as images."""
    all_entities = []
    all_relationships = []

    for i, (b64, media_type) in enumerate(images):
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": b64,
                },
            },
            {
                "type": "text",
                "text": f"Document: {filename} (page {i + 1})\n\nExtract entities and relationships from this page.",
            },
        ]
        result = _call_api(client, content)
        all_entities.extend(result.get("entities", []))
        all_relationships.extend(result.get("relationships", []))

    return {"entities": all_entities, "relationships": all_relationships}


def _call_api(client: anthropic.Anthropic, content: list) -> dict:
    """Make a single API call and parse the JSON response."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )

    text = response.content[0].text.strip()

    # Try to extract JSON from the response
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last ``` lines
        json_lines = []
        in_block = False
        for line in lines:
            if line.strip().startswith("```") and not in_block:
                in_block = True
                continue
            elif line.strip() == "```" and in_block:
                break
            elif in_block:
                json_lines.append(line)
        text = "\n".join(json_lines)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        return {"entities": [], "relationships": []}


def _extract_chunked(client: anthropic.Anthropic, text: str, filename: str) -> dict:
    """Split large text into chunks and extract from each."""
    chunk_size = 300_000  # chars, roughly 75k tokens
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    all_entities = []
    all_relationships = []

    for i, chunk in enumerate(chunks):
        user_content = f"Document: {filename} (part {i + 1}/{len(chunks)})\n\n{chunk}"
        result = _call_api(client, [{"type": "text", "text": user_content}])
        all_entities.extend(result.get("entities", []))
        all_relationships.extend(result.get("relationships", []))

    return {"entities": all_entities, "relationships": all_relationships}
