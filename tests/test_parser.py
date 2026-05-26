"""Tests for conventional commit classifier."""
import pytest
from deltabrief.parser import classify_commit


def test_feat():
    t, scope, breaking, desc = classify_commit("feat(auth): add OAuth2 support")
    assert t == "feat"
    assert scope == "auth"
    assert not breaking
    assert desc == "add OAuth2 support"


def test_fix_breaking():
    t, scope, breaking, desc = classify_commit("fix!: remove deprecated endpoint")
    assert t == "fix"
    assert breaking
    assert desc == "remove deprecated endpoint"


def test_other():
    t, scope, breaking, desc = classify_commit("Update README with examples")
    assert t == "other"
    assert not breaking


def test_chore():
    t, scope, breaking, desc = classify_commit("chore(deps): bump requests to 2.31")
    assert t == "chore"
    assert scope == "deps"
