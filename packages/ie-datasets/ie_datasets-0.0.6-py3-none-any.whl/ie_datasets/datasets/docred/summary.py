from ie_datasets.datasets.docred.load import (
    DocREDSplit,
    load_docred_schema,
    load_docred_units,
)


def get_docred_summary() -> str:
    lines: list[str] = []

    schema = load_docred_schema()
    lines.append("=" * 80)
    lines.append("RELATION TYPES")
    L = max(len(relation_type.id) for relation_type in schema.relation_types)
    for relation_type in schema.relation_types:
        lines.append(f"  {relation_type.id.rjust(L)}: {relation_type.description}")

    for split in DocREDSplit:
        units = list(load_docred_units(split))

        lines.append("=" * 80)
        lines.append(f"{split}: {len(units)} units")

        L = max(len(str(unit.title)) for unit in units)

        if split != "train_distant":
            for unit in units:
                if unit.is_labelled:
                    lines.append(f"  {str(unit.title).rjust(L)}: {unit.num_tokens:3d} tokens, {unit.num_sentences:2d} sentences, {unit.num_entities:2d} entities, {unit.num_relations:2d} relations")
                else:
                    lines.append(f"  {str(unit.title).rjust(L)}: {unit.num_tokens:3d} tokens, {unit.num_sentences:2d} sentences, {unit.num_entities:2d} entities")

    return "\n".join(lines)


__all__ = [
    "get_docred_summary"
]
