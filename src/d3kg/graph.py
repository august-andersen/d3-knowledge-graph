"""Entity/relationship merging and deduplication."""


def merge_all_extractions(cache: dict) -> dict:
    """Merge entities and relationships from all cached files into the 'merged' field."""
    all_entities = []
    all_relationships = []

    for filepath, entry in cache.get("files", {}).items():
        filename = filepath.rsplit("/", 1)[-1]
        for entity in entry.get("entities", []):
            entity_copy = dict(entity)
            entity_copy.setdefault("source_files", [])
            if filename not in entity_copy["source_files"]:
                entity_copy["source_files"].append(filename)
            all_entities.append(entity_copy)

        for rel in entry.get("relationships", []):
            all_relationships.append(dict(rel))

    merged_entities = _deduplicate_entities(all_entities)
    merged_relationships = _deduplicate_relationships(all_relationships)

    cache["merged"] = {
        "entities": merged_entities,
        "relationships": merged_relationships,
    }
    return cache["merged"]


def _deduplicate_entities(entities: list[dict]) -> list[dict]:
    """Merge entities by case-insensitive name."""
    by_name: dict[str, dict] = {}

    for entity in entities:
        name = entity.get("name", "").strip()
        if not name:
            continue
        key = name.lower()

        if key in by_name:
            existing = by_name[key]
            # Keep the longer/more informative description
            new_desc = entity.get("description", "")
            if len(new_desc) > len(existing.get("description", "")):
                existing["description"] = new_desc
            # Merge source files
            for sf in entity.get("source_files", []):
                if sf not in existing.get("source_files", []):
                    existing.setdefault("source_files", []).append(sf)
            # Keep most common category (just keep first seen for simplicity)
        else:
            by_name[key] = {
                "name": name,
                "category": entity.get("category", "unknown"),
                "description": entity.get("description", ""),
                "source_files": list(entity.get("source_files", [])),
            }

    return list(by_name.values())


def _deduplicate_relationships(relationships: list[dict]) -> list[dict]:
    """Merge relationships by source-target pair."""
    by_pair: dict[tuple[str, str], dict] = {}

    for rel in relationships:
        source = rel.get("source", "").strip().lower()
        target = rel.get("target", "").strip().lower()
        if not source or not target:
            continue

        key = (source, target)
        if key in by_pair:
            existing = by_pair[key]
            # Keep highest weight
            existing["weight"] = max(existing.get("weight", 1), rel.get("weight", 1))
            # Merge labels
            new_label = rel.get("label", "")
            if new_label and new_label != existing.get("label", ""):
                existing["label"] = new_label
        else:
            by_pair[key] = {
                "source": rel.get("source", "").strip(),
                "target": rel.get("target", "").strip(),
                "label": rel.get("label", "relates to"),
                "weight": rel.get("weight", 1),
            }

    return list(by_pair.values())
