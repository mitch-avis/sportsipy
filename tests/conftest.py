"""Provide utilities for conftest."""

from pathlib import Path

import pytest

from sportsipy import utils


@pytest.fixture
def offline_mode(monkeypatch):
    """Enable offline fixture mode for tests that opt in."""
    utils._FIXTURE_MAP = None
    fixtures_dir = Path(__file__).parent / "integration"
    monkeypatch.setenv("SPORTSIPY_OFFLINE", "1")
    monkeypatch.setenv("SPORTSIPY_FIXTURE_DIR", str(fixtures_dir))
    monkeypatch.setenv("SPORTSIPY_FIXTURE_MAP", str(fixtures_dir / "url_map.json"))
    yield
    utils._FIXTURE_MAP = None
