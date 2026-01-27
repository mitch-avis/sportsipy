import os

import pytest
import requests


def _live_mode_enabled() -> bool:
    value = os.environ.get("SPORTSIPY_LIVE", "")
    return value.lower() in {"1", "true", "yes", "on"}


@pytest.fixture(autouse=True)
def _offline_fixtures(request):
    # Ensure integration tests run with offline fixtures by default.
    if _live_mode_enabled():
        yield
        return
    request.getfixturevalue("offline_mode")
    yield


@pytest.fixture(autouse=True)
def _live_mode_rate_limit(monkeypatch):
    if not _live_mode_enabled():
        return
    monkeypatch.delenv("SPORTSIPY_OFFLINE", raising=False)
    monkeypatch.delenv("SPORTSIPY_DISABLE_RATE_LIMIT", raising=False)
    monkeypatch.setenv("SPORTSIPY_FORCE_RATE_LIMIT", "1")
    # 20 requests per minute.
    monkeypatch.setenv("SPORTSIPY_RATE_LIMIT_SECONDS", "3.0")


@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    if _live_mode_enabled():
        return

    def _blocked(*args, **kwargs):
        raise AssertionError(
            "Network access is disabled in integration tests. "
            "Add a fixture entry in tests/integration/url_map.json, "
            "or set SPORTSIPY_LIVE=1 to run against the live site."
        )

    monkeypatch.setattr(requests, "get", _blocked)
    monkeypatch.setattr(requests, "head", _blocked)
