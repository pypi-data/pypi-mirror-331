import os
from typing import get_args, FrozenSet, Iterable, Literal, TypeAlias

from ie_datasets.datasets.crossre.unit import CrossREUnit
from ie_datasets.util.env import get_cache_dir
from ie_datasets.util.wget import open_or_wget


CrossREDomain: TypeAlias = Literal[
    "ai",
    "literature",
    "music",
    "news",
    "politics",
    "science",
]
all_domains: FrozenSet[CrossREDomain] = frozenset(get_args(CrossREDomain))

CrossRESplit: TypeAlias = Literal[
    "train",
    "dev",
    "test",
]
all_splits: FrozenSet[CrossRESplit] = frozenset(get_args(CrossRESplit))

BASE_CROSSRE_PATH = get_cache_dir(subpath="crossre")
BASE_DATA_URL = "https://raw.githubusercontent.com/mainlp/CrossRE/refs/heads/main/crossre_data"


def load_units(
        split: CrossRESplit,
        *,
        domain: CrossREDomain,
) -> Iterable[CrossREUnit]:
    split_path = os.path.join(BASE_CROSSRE_PATH, f"{domain}-{split}.jsonl")
    data_url = f"{BASE_DATA_URL}/{domain}-{split}.json"
    with open_or_wget(split_path, data_url) as f:
        for line in f:
            unit = CrossREUnit.model_validate_json(line)
            yield unit


__all__ = [
    "all_domains",
    "all_splits",
    "CrossREDomain",
    "CrossRESplit",
    "load_units",
]
