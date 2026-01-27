import pytest
import requests


@pytest.fixture(autouse=True)
def _offline_fixtures(offline_mode):
    # Ensure integration tests run with offline fixtures by default.
    yield


@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    def _blocked(*args, **kwargs):
        raise AssertionError(
            "Network access is disabled in integration tests. "
            "Add a fixture entry in tests/fixtures/url_map.json."
        )

    monkeypatch.setattr(requests, "get", _blocked)
    monkeypatch.setattr(requests, "head", _blocked)
