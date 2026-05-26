"""GitPython-based commit loader and conventional commit classifier."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import re

import git

CONVENTIONAL_PATTERN = re.compile(
    r"^(?P<type>feat|fix|refactor|chore|docs|test|perf|ci|build|style|revert)"
    r"(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?"
    r":\s+(?P<description>.+)$",
    re.IGNORECASE,
)

COMMIT_TYPES = {
    "feat": "\u2728 Feature",
    "fix": "\U0001f41b Fix",
    "refactor": "\u267b\ufe0f Refactor",
    "chore": "\U0001f527 Chore",
    "docs": "\U0001f4dd Docs",
    "test": "\U0001f9ea Test",
    "perf": "\u26a1 Perf",
    "ci": "\U0001f501 CI",
    "build": "\U0001f3d7\ufe0f Build",
    "style": "\U0001f3a8 Style",
    "revert": "\u23ea Revert",
    "other": "\U0001f4e6 Other",
}


@dataclass
class CommitRecord:
    sha: str
    short_sha: str
    author: str
    author_email: str
    timestamp: datetime
    message: str
    commit_type: str
    scope: Optional[str]
    breaking: bool
    description: str
    files_changed: list[str] = field(default_factory=list)
    insertions: int = 0
    deletions: int = 0


def classify_commit(message: str) -> tuple[str, Optional[str], bool, str]:
    """Returns (type, scope, is_breaking, description)."""
    first_line = message.strip().splitlines()[0]
    m = CONVENTIONAL_PATTERN.match(first_line)
    if m:
        return (
            m.group("type").lower(),
            m.group("scope"),
            bool(m.group("breaking")),
            m.group("description"),
        )
    return "other", None, False, first_line


def load_commits(
    repo_path: str,
    since: datetime,
    branch: Optional[str] = None,
    author: Optional[str] = None,
) -> list[CommitRecord]:
    """Load and classify commits from a git repo since a given datetime."""
    repo = git.Repo(repo_path, search_parent_directories=True)
    rev = branch or repo.active_branch.name

    records: list[CommitRecord] = []
    for commit in repo.iter_commits(rev):
        committed_dt = datetime.fromtimestamp(commit.committed_date, tz=timezone.utc)
        if committed_dt < since:
            break

        if author and author.lower() not in commit.author.name.lower():
            continue

        commit_type, scope, breaking, description = classify_commit(commit.message)

        files_changed: list[str] = []
        insertions = 0
        deletions = 0
        try:
            if commit.parents:
                diff = commit.parents[0].diff(commit)
                for d in diff:
                    if d.b_path:
                        files_changed.append(d.b_path)
                stats = commit.stats.total
                insertions = stats.get("insertions", 0)
                deletions = stats.get("deletions", 0)
        except Exception:
            pass

        records.append(CommitRecord(
            sha=commit.hexsha,
            short_sha=commit.hexsha[:7],
            author=commit.author.name,
            author_email=commit.author.email,
            timestamp=committed_dt,
            message=commit.message.strip(),
            commit_type=commit_type,
            scope=scope,
            breaking=breaking,
            description=description,
            files_changed=files_changed,
            insertions=insertions,
            deletions=deletions,
        ))

    return records
