from ie_datasets.datasets.deft.load import load_units


def get_summary() -> str:
    lines: list[str] = []

    for split in ("train", "dev", "test"):
        for category in (
            "biology",
            "history",
            "physics",
            "psychology",
            "economic",
            "sociology",
            "government",
        ):
            units = list(load_units(split=split, category=category))

            lines.append("=" * 80)
            lines.append(f"{split.upper()} {category.upper()}: {len(units)} units")

            L = max(len(str(unit.id)) for unit in units)

            for unit in units:
                lines.append(f"  {str(unit.id).rjust(L)}: {unit.num_chars:4d} chars, {unit.num_entities:2d} entities, {unit.num_relations:1d} relations")

    return "\n".join(lines)


__all__ = [
    "get_summary"
]
