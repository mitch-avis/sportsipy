"""Unit-test configuration and fixtures."""

from __future__ import annotations

import pytest

from sportsipy import utils


@pytest.fixture(autouse=True)
def disable_curl_cffi(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable curl_cffi for all unit tests.

    Many unit tests mock ``requests.get`` via ``@patch("requests.get", ...)``.
    When ``curl_cffi`` is installed, ``_http_get()`` calls
    ``_cffi_requests.get()`` before falling back to ``requests.get()``,
    bypassing those mocks.

    This autouse fixture ensures that ``_CURL_CFFI_AVAILABLE`` is ``False``
    for every unit test so the ``requests`` mock path is always exercised.
    Tests that specifically need curl_cffi behaviour can override this by
    calling ``monkeypatch.setattr(utils, "_CURL_CFFI_AVAILABLE", True)``
    inside their own body.
    """
    monkeypatch.setattr(utils, "_CURL_CFFI_AVAILABLE", False)


@pytest.fixture(autouse=True)
def disable_playwright(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable Playwright fallback for unit tests.

    Unit tests primarily exercise parser and control-flow logic with mocked
    HTTP calls. If Playwright fallback is enabled, a mocked empty/invalid
    response can trigger a real browser navigation, introducing network
    nondeterminism and flaky failures.

    Tests that explicitly validate Playwright behavior can opt back in by
    monkeypatching ``_PLAYWRIGHT_AVAILABLE`` and ``sync_playwright``.
    """
    monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", False)
    monkeypatch.setattr(utils, "sync_playwright", None)
