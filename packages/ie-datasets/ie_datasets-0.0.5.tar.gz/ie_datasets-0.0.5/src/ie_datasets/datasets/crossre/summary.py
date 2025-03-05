from collections import defaultdict
from ie_datasets.datasets.crossre.load import (
    all_domains,
    all_splits,
    load_units,
)


def get_summary() -> str:
    schema_lines: list[str] = []
    units_lines: list[str] = []

    entity_types: dict[str, int] = defaultdict(int)
    explanations_by_relation_type: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for split in all_splits:
        for domain in all_domains:
            units = list(load_units(split, domain=domain))

            units_lines.append("=" * 80)
            units_lines.append(f"{split}/{domain}: {len(units)} units")

            L = max(len(str(unit.doc_key)) for unit in units)

            for unit in units:
                units_lines.append(f"  {str(unit.doc_key).rjust(L)}: {unit.num_tokens:2d} tokens, {unit.num_entities:2d} entities, {unit.num_relations:2d} relations")
                for e in unit.entity_objects:
                    entity_types[e.entity_type] += 1
                for r in unit.relation_objects:
                    key = r.relation_type if r.explanation == "" else r.explanation
                    explanations_by_relation_type[r.relation_type][key] += 1

    schema_lines.append("=" * 80)
    schema_lines.append("SCHEMA")

    schema_lines.append("-" * 80)
    schema_lines.append(f"{len(entity_types)} entity types")
    L = max(len(entity_type) for entity_type in entity_types.keys())
    for entity_type in sorted(entity_types):
        count = entity_types[entity_type]
        schema_lines.append(f"  {entity_type.rjust(L)}: {count}")

    schema_lines.append("-" * 80)
    relation_types = sorted(explanations_by_relation_type.keys())
    schema_lines.append(f"{len(relation_types)} relation types")
    for relation_type in relation_types:
        schema_lines.append(f"  {relation_type}")
        explanations = sorted(explanations_by_relation_type[relation_type].keys())
        L = max(len(explanation) for explanation in explanations)
        for explanation in explanations:
            count = explanations_by_relation_type[relation_type][explanation]
            schema_lines.append(f"    {explanation.rjust(L)}: {count}")

    return "\n".join(schema_lines + units_lines)
