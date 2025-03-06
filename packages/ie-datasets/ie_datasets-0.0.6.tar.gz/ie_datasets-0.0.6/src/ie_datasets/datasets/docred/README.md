# DocRED

**ACL 2019**: [DocRED: A Large-Scale Document-Level Relation Extraction Dataset](https://aclanthology.org/P19-1074/)

**GitHub**: [`thunlp/DocRED`](https://github.com/thunlp/DocRED)

[**Google Drive**](https://drive.google.com/drive/folders/1c5-0YwnoJx8NS6CV2f-NoTHR__BdkNqw?usp=drive_link)


## Schema

DocRED uses spaCy entity types.


## Quirks

- We convert all field names to standard Python snake case.
  We replace the reserved keyword `type` with `entity_type` instead.
