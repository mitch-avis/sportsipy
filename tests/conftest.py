from pathlib import Path

import pytest


@pytest.fixture
def offline_mode(monkeypatch):
    """
    Enable offline fixture mode for tests that opt in.
    """
    fixtures_dir = Path(__file__).parent / "fixtures"
    monkeypatch.setenv("SPORTSIPY_OFFLINE", "1")
    monkeypatch.setenv("SPORTSIPY_FIXTURE_DIR", str(fixtures_dir))
    monkeypatch.setenv("SPORTSIPY_FIXTURE_MAP", str(fixtures_dir / "url_map.json"))
