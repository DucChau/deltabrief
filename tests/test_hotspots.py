"""Tests for hotspot file analyzer."""
from datetime import datetime, timezone
from deltabrief.parser import CommitRecord
from deltabrief.hotspots import compute_hotspots


def _make_commit(files, ctype="feat"):
    return CommitRecord(
        sha="abc1234", short_sha="abc1234", author="Test", author_email="t@t.com",
        timestamp=datetime.now(tz=timezone.utc), message="feat: test",
        commit_type=ctype, scope=None, breaking=False, description="test",
        files_changed=files,
    )


def test_hotspot_ordering():
    commits = [
        _make_commit(["a.py", "b.py"]),
        _make_commit(["a.py"]),
        _make_commit(["b.py", "c.py"]),
        _make_commit(["a.py"]),
    ]
    hotspots = compute_hotspots(commits, top=3)
    assert hotspots[0].path == "a.py"
    assert hotspots[0].change_count == 3


def test_empty_commits():
    assert compute_hotspots([], top=5) == []
