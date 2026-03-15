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
|---------|---------|
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
|----------|--------|
| `SPORTSIPY_ENABLE_PLAYWRIGHT=1` | Enable Playwright for *every* request (full-browser mode; slower but most compatible) |
| `SPORTSIPY_DISABLE_PLAYWRIGHT=1` | Suppress Playwright even when a Cloudflare JS-challenge is detected (useful in CI or restricted environments) |

With neither env var set, Playwright is used *automatically* only when
`curl_cffi` still receives a bot-challenge HTTP response.

## Credits

This fork builds on the original
[roclark/sportsipy](https://github.com/roclark/sportsipy) project and the
[davidjkrause/sportsipy](https://github.com/davidjkrause/sportsipy) fork which
incorporated key fixes.
