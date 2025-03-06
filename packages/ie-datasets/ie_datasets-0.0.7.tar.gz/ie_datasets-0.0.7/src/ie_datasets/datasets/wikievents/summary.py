from ie_datasets.datasets.wikievents.load import (
    load_wikievents_ontology,
    load_wikievents_units,
    WikiEventsSplit,
)


def get_wikievents_summary() -> str:
    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("ONTOLOGY")

    ontology = load_wikievents_ontology()
    lines.append("-" * 80)
    lines.append("ENTITY TYPES")
    L = max(len(entity_type.name) for entity_type in ontology.entity_types)
    for entity_type in ontology.entity_types:
        lines.append(f"  {entity_type.name.rjust(L)}: \"{entity_type.definition}\"")
    lines.append("-" * 80)
    lines.append("EVENT TYPES")
    L = max(len(event_type.name) for event_type in ontology.event_types)
    for event_type in ontology.event_types:
        lines.append(f"  {event_type.name.rjust(L)}: \"{event_type.template}\"")

    for split in WikiEventsSplit:
        units = list(load_wikievents_units(split))
        lines.append("=" * 80)
        lines.append(f"{split}: {len(units)} units")
        L = max(len(unit.doc_id) for unit in units)
        for unit in units:
            lines.append(f"  {unit.doc_id.rjust(L)}: {unit.num_chars:5d} chars, {unit.num_tokens:5d} tokens, {unit.num_sentences:3d} sentences, {unit.num_entity_mentions:4d} entity mentions, {unit.num_event_mentions:3d} event mentions")
            ontology.validate_unit(unit)

    return "\n".join(lines)


__all__ = [
    "get_wikievents_summary",
]
