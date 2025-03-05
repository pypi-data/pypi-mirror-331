from functools import cached_property
from typing import get_args, FrozenSet, Literal, Sequence, TypeAlias

from pydantic import model_validator

from ie_datasets.util.interfaces import ImmutableModel


CrossREEntityTypeName: TypeAlias = Literal[
    "academicjournal",
    "album",
    "algorithm",
    "astronomicalobject",
    "award",
    "band",
    "book",
    "chemicalcompound",
    "chemicalelement",
    "conference",
    "country",
    "discipline",
    "election",
    "enzyme",
    "event",
    "field",
    "literarygenre",
    "location",
    "magazine",
    "metrics",
    "misc",
    "musicalartist",
    "musicalinstrument",
    "musicgenre",
    "organisation",
    "person",
    "poem",
    "politicalparty",
    "politician",
    "product",
    "programlang",
    "protein",
    "researcher",
    "scientist",
    "song",
    "task",
    "theory",
    "university",
    "writer",
]
all_entity_type_names: FrozenSet[CrossREEntityTypeName] = frozenset(
    get_args(CrossREEntityTypeName)
)

CrossRERelationTypeName: TypeAlias = Literal[
    "artifact",
    "cause-effect",
    "compare",
    "general-affiliation",
    "named",
    "opposite",
    "origin",
    "part-of",
    "physical",
    "related-to",
    "role",
    "social",
    "temporal",
    "topic",
    "type-of",
    "usage",
    "win-defeat",
]
all_relation_type_names: FrozenSet[CrossRERelationTypeName] = frozenset(
    get_args(CrossRERelationTypeName)
)


class CrossREEntity(ImmutableModel):
    start: int
    end: int
    entity_type: CrossREEntityTypeName


class CrossRERelation(ImmutableModel):
    head_start: int
    head_end: int
    tail_start: int
    tail_end: int
    relation_type: CrossRERelationTypeName
    explanation: str
    uncertain: bool
    syntax_ambiguity: bool


class CrossREUnit(ImmutableModel):
    doc_key: str
    sentence: Sequence[str]
    ner: Sequence[tuple[int, int, CrossREEntityTypeName]]
    relations: Sequence[tuple[int, int, int, int, CrossRERelationTypeName, str, bool, bool]]

    @cached_property
    def text(self) -> str:
        return " ".join(self.sentence)

    @property
    def num_chars(self) -> int:
        return len(self.text)

    @property
    def num_tokens(self) -> int:
        return len(self.sentence)

    @property
    def num_entities(self) -> int:
        return len(self.entity_objects)

    @property
    def num_relations(self) -> int:
        return len(self.relation_objects)

    @model_validator(mode="after")
    def sort_sequences(self):
        with self._unfreeze():
            self.ner = sorted(self.ner)
            self.relations = sorted(self.relations)
        return self

    @cached_property
    def _token_spans(self) -> Sequence[tuple[int, int]]:
        spans: list[tuple[int, int]] = []
        offset = 0
        for token in self.sentence:
            start = offset
            end = start + len(token)
            spans.append((start, end))
            offset = end + 1
        return spans

    def token_span_to_char_span(self, start: int, end: int) -> tuple[int, int]:
        assert 0 <= start <= end < self.num_tokens
        return self._token_spans[start][0], self._token_spans[end][1]

    @cached_property
    def entity_objects(self) -> Sequence[CrossREEntity]:
        entities: list[CrossREEntity] = []
        for start, end, entity_type in self.ner:
            start, end = self.token_span_to_char_span(start, end)
            entity = CrossREEntity(
                start=start,
                end=end,
                entity_type=entity_type,
            )
            entities.append(entity)
        return entities

    @cached_property
    def entities_by_span(self) -> dict[tuple[int, int], CrossREEntity]:
        entities_by_span = {
            (entity.start, entity.end): entity
            for entity in self.entity_objects
        }
        assert len(entities_by_span) == self.num_entities
        return entities_by_span

    @cached_property
    def relation_objects(self) -> Sequence[CrossRERelation]:
        relations: list[CrossRERelation] = []
        for (
            head_start,
            head_end,
            tail_start,
            tail_end,
            relation_type,
            explanation,
            uncertain,
            syntax_ambiguity,
        ) in self.relations:
            head_start, head_end = self.token_span_to_char_span(head_start, head_end)
            tail_start, tail_end = self.token_span_to_char_span(tail_start, tail_end)
            relation = CrossRERelation(
                head_start=head_start,
                head_end=head_end,
                tail_start=tail_start,
                tail_end=tail_end,
                relation_type=relation_type,
                explanation=explanation,
                uncertain=uncertain,
                syntax_ambiguity=syntax_ambiguity,
            )
            relations.append(relation)
        return relations

    @model_validator(mode="after")
    def validate_relations(self):
        for relation in self.relation_objects:
            assert (relation.head_start, relation.head_end) in self.entities_by_span
            assert (relation.tail_start, relation.tail_end) in self.entities_by_span
        return self


__all__ = [
    "all_entity_type_names",
    "all_relation_type_names",
    "CrossREEntity",
    "CrossREEntityTypeName",
    "CrossRERelation",
    "CrossRERelationTypeName",
    "CrossREUnit",
]
