# Installation

## From PyPI

The easiest way to install the published `sportsipy` package is via PyPI:

```bash
pip install sportsipy
```

This installs the latest official release from the original project. The active
fork for this repository is not published to PyPI.

## From Source (this fork)

If the bleeding-edge version of this fork is desired, clone this repository
using git and install it from source:

```bash
git clone https://github.com/mitch-avis/sportsipy
cd sportsipy
pip install -e .
```

This repository targets **Python 3.12+**.

Using [uv](https://github.com/astral-sh/uv) (recommended for development):

```bash
git clone https://github.com/mitch-avis/sportsipy
cd sportsipy
uv venv
uv pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
```

## Building a Wheel

To build a wheel locally, install the build frontend and run:

```bash
pip install build
python -m build
```

This creates a `.whl` file in the `dist/` directory which can then be installed:

```bash
pip install dist/*.whl
```

## Optional: Bot-Evasion Extras

`sportsipy` includes an optional bot-detection and evasion layer for live
scraping against Cloudflare-protected sites (e.g. NFL, FBref). Two packages
unlock extra capabilities:

| Package | Purpose |
| ------- | ------- |
| `curl_cffi` | Chrome TLS fingerprint impersonation via `libcurl-impersonate`; defeats most TLS-fingerprint-based blocks without a browser |
| `playwright` | Headless browser fallback; used automatically whenever `curl_cffi` still gets a Cloudflare JS-challenge response |

Install both at once:

```bash
pip install "sportsipy[bot-evasion]"
```

Or install them individually:

```bash
pip install curl_cffi playwright
```

If `playwright` is installed, also download the browser binary:

```bash
playwright install chromium
```

### Environment Variables

| Variable | Effect |
| -------- | ------ |
| `SPORTSIPY_ENABLE_PLAYWRIGHT=1` | Enable Playwright for *every* request (full-browser mode; slower but most compatible) |
| `SPORTSIPY_DISABLE_PLAYWRIGHT=1` | Suppress Playwright even when a Cloudflare JS-challenge is detected (useful in CI or restricted environments) |
| `SPORTSIPY_PLAYWRIGHT_HEADLESS=0` | Run Playwright in headed mode for manual challenge solving and visual debugging |
| `SPORTSIPY_PLAYWRIGHT_WAIT_UNTIL=networkidle` | Navigation wait mode (`load`, `domcontentloaded`, `networkidle`, or `commit`) |
| `SPORTSIPY_PLAYWRIGHT_SETTLE_MS=2500` | Additional wait after navigation before reading HTML |
| `SPORTSIPY_PLAYWRIGHT_TIMEOUT_MS=90000` | Per-navigation timeout in milliseconds |
| `SPORTSIPY_PLAYWRIGHT_STORAGE_STATE=/path/state.json` | Reuse a previously saved Playwright storage-state file (cookies/local storage) |
| `SPORTSIPY_PLAYWRIGHT_USER_DATA_DIR=/path/profile` | Launch a persistent Chromium profile directory and reuse browser session state |
| `SPORTSIPY_BOT_DEBUG_HTML_DIR=/path/debug-html` | Save fetched Playwright HTML pages for challenge diagnostics |
| `SPORTSIPY_BOT_DEBUG_SCREENSHOT_DIR=/path/debug-shots` | Save Playwright screenshots for challenge diagnostics |

With neither env var set, Playwright is used *automatically* only when
`curl_cffi` still receives a bot-challenge HTTP response.

Recommended troubleshooting flow for Cloudflare-gated pages:

1. Start in headed mode (`SPORTSIPY_PLAYWRIGHT_HEADLESS=0`) and verify whether a manual challenge appears.
2. If a challenge can be solved manually, persist and reuse session state via
 `SPORTSIPY_PLAYWRIGHT_USER_DATA_DIR` or `SPORTSIPY_PLAYWRIGHT_STORAGE_STATE`.
3. Enable debug dumps (`SPORTSIPY_BOT_DEBUG_HTML_DIR`,
 `SPORTSIPY_BOT_DEBUG_SCREENSHOT_DIR`) to inspect what content is actually
 returned when parsing fails.

## Credits

This fork builds on the original
[roclark/sportsipy](https://github.com/roclark/sportsipy) project and the
[davidjkrause/sportsipy](https://github.com/davidjkrause/sportsipy) fork which
incorporated key fixes.
