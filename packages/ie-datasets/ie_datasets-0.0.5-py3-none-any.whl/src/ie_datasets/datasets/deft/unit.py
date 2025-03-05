from functools import cached_property
from typing import get_args, Literal, Mapping, Sequence, TypeAlias

from pydantic import model_validator

from ie_datasets.util.interfaces import ImmutableModel


DEFTEntityType: TypeAlias = Literal[
    "Term",
    "Alias-Term",
    "Ordered-Term",
    "Referential-Term",
    "Definition",
    "Secondary-Definition",
    "Ordered-Definition",
    "Referential-Definition",
    "Qualifier",
    "Definition-frag",
]
all_deft_entity_types: set[DEFTEntityType] = set(get_args(DEFTEntityType))

DEFTRelationType: TypeAlias = Literal[
    "Direct-Defines",
    "Indirect-Defines",
    "Refers-To",
    "AKA",
    "Supplements",
    "fragment",
]
all_deft_relation_types: set[DEFTRelationType] = set(get_args(DEFTRelationType))


class DEFTEntity(ImmutableModel):
    id: str
    entity_type: DEFTEntityType
    text: str
    start_char: int
    end_char: int


class DEFTRelation(ImmutableModel):
    root_id: str
    child_id: str
    relation_type: DEFTRelationType


class DEFTUnit(ImmutableModel):
    source: str
    id: int
    text: str
    entities: Sequence[DEFTEntity]
    relations: Sequence[DEFTRelation]

    @property
    def num_chars(self) -> int:
        return len(self.text)

    @property
    def num_entities(self) -> int:
        return len(self.entities)

    @property
    def num_relations(self) -> int:
        return len(self.relations)

    @cached_property
    def entities_by_id(self) -> Mapping[str, DEFTEntity]:
        entities_by_id = {entity.id: entity for entity in self.entities}
        assert len(entities_by_id) == len(self.entities), self
        return entities_by_id

    @model_validator(mode="after")
    def sort_and_deduplicate_sequences(self):
        with self._unfreeze():
            self.entities = sorted(
                set(self.entities),
                key=lambda e: e.id,
            )
            self.relations = sorted(
                set(self.relations),
                key=(lambda r: (r.root_id, r.child_id)),
            )
        return self

    @model_validator(mode="after")
    def validate_relations(self):
        for relation in self.relations:
            assert relation.root_id in self.entities_by_id, self
            assert relation.child_id in self.entities_by_id, self
        return self

    @model_validator(mode="after")
    def validate_spans(self):
        for entity in self.entities:
            s = entity.start_char
            e = entity.end_char
            assert 0 <= s < e <= len(self.text)
            assert self.text[s:e] == entity.text
        return self


__all__ = [
    "all_deft_entity_types",
    "all_deft_relation_types",
    "DEFTEntity",
    "DEFTEntityType",
    "DEFTRelation",
    "DEFTRelationType",
    "DEFTUnit",
]
