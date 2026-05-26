"""File change frequency analyzer."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass

from .parser import CommitRecord


@dataclass
class Hotspot:
    path: str
    change_count: int
    commit_types: dict[str, int]


def compute_hotspots(commits: list[CommitRecord], top: int = 10) -> list[Hotspot]:
    """Return the top N most frequently changed files."""
    file_counts: Counter[str] = Counter()
    file_types: dict[str, Counter] = {}

    for commit in commits:
        for f in commit.files_changed:
            file_counts[f] += 1
            if f not in file_types:
                file_types[f] = Counter()
            file_types[f][commit.commit_type] += 1

    hotspots = []
    for path, count in file_counts.most_common(top):
        hotspots.append(Hotspot(
            path=path,
            change_count=count,
            commit_types=dict(file_types[path]),
        ))
    return hotspots
