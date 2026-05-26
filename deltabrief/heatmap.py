"""Per-author contribution heat map builder."""
from __future__ import annotations
from collections import Counter, defaultdict
from typing import TypedDict

from .parser import CommitRecord


class AuthorStats(TypedDict):
    count: int
    insertions: int
    deletions: int
    types: dict[str, int]


def compute_heatmap(commits: list[CommitRecord]) -> dict[str, AuthorStats]:
    """Return per-author statistics grouped by commit type."""
    result: dict[str, AuthorStats] = defaultdict(
        lambda: {"count": 0, "insertions": 0, "deletions": 0, "types": Counter()}
    )
    for commit in commits:
        stats = result[commit.author]
        stats["count"] += 1
        stats["insertions"] += commit.insertions
        stats["deletions"] += commit.deletions
        stats["types"][commit.commit_type] += 1
    # Convert Counters to plain dicts
    return {k: {**v, "types": dict(v["types"])} for k, v in result.items()}
