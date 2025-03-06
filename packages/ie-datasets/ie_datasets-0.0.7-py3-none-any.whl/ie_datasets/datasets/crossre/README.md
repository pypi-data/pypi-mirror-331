# CrossRE

**EMNLP 2022**: [CrossRE: A Cross-Domain Dataset for Relation Extraction](https://aclanthology.org/2022.findings-emnlp.263/)

**GitHub**: [`mainlp/CrossRE`](https://github.com/mainlp/CrossRE)

[**Annotation Guidelines**](https://github.com/mainlp/CrossRE/blob/main/crossre_annotation/CrossRE-annotation-guidelines.pdf)


## Schema

### Entity Types

The `ai`, `literature`, `music`, `politics`, and `science` domains of CrossRE are derived from CrossNER, and inherits the same entity types.
The entity types of CrossRE are defined in the appendix of the paper [CrossNER: Evaluating Cross-Domain Named Entity Recognition](https://arxiv.org/abs/2012.04373).

Meanwhile, the `news` domain of CrossRE is derived from [CoNLL-2003](https://aclanthology.org/W03-0419/), which contains only 3 non-miscellaneous entity types, all of which are self-explanatory:
- `person`
- `organization`
- `location`

### Relation Types

The [annotation guidelines](https://github.com/mainlp/CrossRE/blob/main/crossre_annotation/CrossRE-annotation-guidelines.pdf) outline the relation types of CrossRE.
Besides the main relation types which apply across domains, the `explanation` field can include a more specific relation type for the given domain and entity types.
