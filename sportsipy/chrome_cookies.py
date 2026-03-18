"""Extract Cloudflare cookies from Google Chrome's local cookie store.

This module reads Chrome's encrypted SQLite cookie database on Linux and
decrypts ``cf_clearance`` and ``__cf_bm`` cookies for sports-reference
family domains.  This enables automated cookie injection without manual
copy-paste from the browser's developer tools.

Requirements
------------
- ``cryptography`` — for AES-128-CBC decryption of Chrome's encrypted cookie
  values.  Install via ``pip install cryptography``.
- (Optional) ``secretstorage`` — for reading the encryption password from
  GNOME Keyring instead of the hardcoded fallback.  Install via
  ``pip install secretstorage``.

Platform Support
----------------
Currently supports **Linux only**.  Chrome on Linux stores cookies in an
SQLite database at ``~/.config/google-chrome/<Profile>/Cookies``.  Cookie
values are encrypted with AES-128-CBC using a key derived via PBKDF2 from
either the GNOME Keyring password or the fallback password ``"peanuts"``.

On systems without GNOME Keyring (containers, WSL, headless servers), Chrome
falls back to the ``"peanuts"`` password automatically.
"""

from __future__ import annotations

import contextlib
import hashlib
import logging
import re
import shutil
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cloudflare-protected sports-reference domains and relevant cookie names
# ---------------------------------------------------------------------------
CLOUDFLARE_DOMAINS: tuple[str, ...] = (
    ".pro-football-reference.com",
    ".sports-reference.com",
    ".fbref.com",
)

_CF_COOKIE_NAMES: tuple[str, ...] = ("cf_clearance", "__cf_bm")

# ---------------------------------------------------------------------------
# AES decryption constants for Chrome on Linux
# ---------------------------------------------------------------------------
_V10_PREFIX = b"v10"
_V11_PREFIX = b"v11"
_PBKDF2_SALT = b"saltysalt"
_PBKDF2_ITERATIONS = 1
_PBKDF2_KEY_LENGTH = 16  # AES-128
_CBC_IV = b" " * 16  # 16 space characters

# Chrome prepends a 32-byte binary header (integrity HMAC) to the plaintext
# cookie value before encrypting.  After decryption and PKCS7 unpadding, we
# skip this prefix to extract the actual cookie value.
_PLAINTEXT_HEADER_SIZE = 32

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Optional dependency availability flags
# ---------------------------------------------------------------------------
try:
    import cryptography  # noqa: F401

    _CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    _CRYPTOGRAPHY_AVAILABLE = False

try:
    import secretstorage  # noqa: F401

    _SECRETSTORAGE_AVAILABLE = True
except ImportError:
    _SECRETSTORAGE_AVAILABLE = False


def _chrome_cookie_db_path(profile: str = "Default") -> Path:
    """Return the path to Chrome's Cookies SQLite database.

    Parameters
    ----------
    profile : str
        Chrome profile directory name (default ``"Default"``).

    Returns
    -------
    Path
        Absolute path to the Cookies database file.

    """
    return Path.home() / ".config" / "google-chrome" / profile / "Cookies"


def _derive_key_from_keyring() -> bytes | None:
    """Derive the AES key from Chrome's GNOME Keyring entry.

    Returns
    -------
    bytes or None
        The 16-byte AES key, or ``None`` if the keyring is unavailable.

    """
    if not _SECRETSTORAGE_AVAILABLE:
        return None
    try:
        import secretstorage

        connection = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(connection)
        if collection.is_locked():
            collection.unlock()
        for item in collection.get_all_items():
            label = item.get_label()
            if label in ("Chrome Safe Storage", "Chromium Safe Storage"):
                password = item.get_secret()
                return hashlib.pbkdf2_hmac(
                    "sha1",
                    password,
                    _PBKDF2_SALT,
                    _PBKDF2_ITERATIONS,
                    dklen=_PBKDF2_KEY_LENGTH,
                )
    except Exception:
        _LOGGER.debug("GNOME Keyring unavailable, will use fallback password", exc_info=True)
    return None


def _derive_key_fallback() -> bytes:
    """Derive the AES key using Chrome's hardcoded fallback password.

    Returns
    -------
    bytes
        The 16-byte AES key derived from ``"peanuts"``.

    """
    return hashlib.pbkdf2_hmac(
        "sha1",
        b"peanuts",
        _PBKDF2_SALT,
        _PBKDF2_ITERATIONS,
        dklen=_PBKDF2_KEY_LENGTH,
    )


def _decrypt_v10(encrypted_value: bytes, key: bytes) -> str | None:
    """Decrypt a v10-encrypted Chrome cookie value.

    Parameters
    ----------
    encrypted_value : bytes
        The raw ``encrypted_value`` blob from Chrome's cookie DB (including
        the ``v10`` prefix).
    key : bytes
        The 16-byte AES key.

    Returns
    -------
    str or None
        The decrypted cookie value, or ``None`` on failure.

    """
    if not _CRYPTOGRAPHY_AVAILABLE:
        return None

    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.padding import PKCS7

    data = encrypted_value[3:]  # strip v10/v11 prefix
    if len(data) < _PLAINTEXT_HEADER_SIZE + 16:
        _LOGGER.debug("Encrypted value too short to contain a cookie: %d bytes", len(data))
        return None

    cipher = Cipher(algorithms.AES(key), modes.CBC(_CBC_IV))
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(data) + decryptor.finalize()

    unpadder = PKCS7(128).unpadder()
    try:
        decrypted = unpadder.update(decrypted) + unpadder.finalize()
    except ValueError:
        _LOGGER.debug("PKCS7 unpadding failed; cookie may use a different encryption scheme")
        return None

    # Skip the 32-byte binary header Chrome prepends to the plaintext.
    cookie_bytes = decrypted[_PLAINTEXT_HEADER_SIZE:]
    try:
        value = cookie_bytes.decode("utf-8")
    except UnicodeDecodeError:
        # Fallback: scan for the longest printable ASCII run.
        full_text = decrypted.decode("latin-1")
        match = re.search(r"[\x20-\x7e]{8,}", full_text)
        if match:
            value = match.group(0)
        else:
            _LOGGER.debug("Could not extract printable cookie value from decrypted data")
            return None

    if not value.isprintable():
        _LOGGER.debug("Decrypted value contains non-printable characters")
        return None

    return value


def chrome_cookies_for_domain(
    domain: str,
    profile: str = "Default",
    cookie_names: tuple[str, ...] = _CF_COOKIE_NAMES,
) -> dict[str, str]:
    """Extract specific cookies for a domain from Chrome's cookie store.

    Parameters
    ----------
    domain : str
        The cookie domain to query (e.g. ``".pro-football-reference.com"``).
        Must include the leading dot for domain-scoped cookies.
    profile : str
        Chrome profile directory name (default ``"Default"``).
    cookie_names : tuple of str
        Cookie names to extract (default: ``cf_clearance`` and ``__cf_bm``).

    Returns
    -------
    dict of str to str
        Mapping of cookie name to decrypted value.  Only cookies that exist
        and decrypt successfully are included.

    """
    if sys.platform != "linux":
        _LOGGER.debug("Chrome cookie extraction is only supported on Linux")
        return {}

    if not _CRYPTOGRAPHY_AVAILABLE:
        _LOGGER.warning(
            "Install 'cryptography' to auto-extract Chrome cookies: pip install cryptography"
        )
        return {}

    db_path = _chrome_cookie_db_path(profile)
    if not db_path.exists():
        _LOGGER.warning(
            "Chrome cookie DB not found at %s — is Chrome installed and has the "
            "'%s' profile been used? Try --chrome-profile to specify a different profile.",
            db_path,
            profile,
        )
        return {}

    # Chrome holds a lock on the Cookies file while running.  Copy to a
    # temp file to avoid SQLite locking issues.
    key = _derive_key_from_keyring() or _derive_key_fallback()
    cookies: dict[str, str] = {}
    tmp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        shutil.copy2(db_path, tmp_path)

        conn = sqlite3.connect(str(tmp_path))
        try:
            placeholders = ",".join("?" for _ in cookie_names)
            # Chrome stores expires_utc as microseconds since 1601-01-01.
            # Filter out expired cookies (expires_utc=0 means session cookie).
            now_chrome = int(time.time() * 1_000_000) + 11_644_473_600_000_000
            query = (
                f"SELECT name, encrypted_value, value FROM cookies "  # noqa: S608
                f"WHERE host_key = ? AND name IN ({placeholders}) "
                f"AND (expires_utc = 0 OR expires_utc > ?)"
            )
            cursor = conn.execute(query, (domain, *cookie_names, now_chrome))
            for name, encrypted_value, plain_value in cursor.fetchall():
                # Prefer the plaintext value column if populated.
                if plain_value:
                    cookies[name] = plain_value
                    continue

                if not encrypted_value:
                    continue

                prefix = encrypted_value[:3]
                if prefix in (_V10_PREFIX, _V11_PREFIX):
                    decrypted = _decrypt_v10(encrypted_value, key)
                    if decrypted:
                        cookies[name] = decrypted
                    else:
                        _LOGGER.debug("Failed to decrypt %s cookie for %s", name, domain)
                else:
                    _LOGGER.debug("Unknown encryption prefix for %s cookie: %r", name, prefix[:3])
        finally:
            conn.close()
    except (sqlite3.Error, OSError) as exc:
        _LOGGER.warning("Error reading Chrome cookie DB: %s", exc)
    finally:
        if tmp_path is not None:
            with contextlib.suppress(OSError):
                tmp_path.unlink(missing_ok=True)

    return cookies


def get_cloudflare_cookies(
    profile: str = "Default",
) -> dict[str, dict[str, str]]:
    """Extract Cloudflare cookies for all sports-reference domains.

    Scans Chrome's cookie store for ``cf_clearance`` and ``__cf_bm`` cookies
    across all known Cloudflare-protected sports-reference domains.

    Parameters
    ----------
    profile : str
        Chrome profile directory name (default ``"Default"``).

    Returns
    -------
    dict of str to dict of str to str
        Outer key is the domain (e.g. ``".pro-football-reference.com"``),
        inner dict maps cookie name to decrypted value.  Only domains with
        at least one valid cookie are included.

    Examples
    --------
    >>> cookies = get_cloudflare_cookies()
    >>> cookies.get(".pro-football-reference.com", {}).get("cf_clearance")
    'jZJ_Noym...'

    """
    all_cookies: dict[str, dict[str, str]] = {}
    for domain in CLOUDFLARE_DOMAINS:
        domain_cookies = chrome_cookies_for_domain(domain, profile=profile)
        if domain_cookies:
            all_cookies[domain] = domain_cookies
    return all_cookies


def get_flat_cloudflare_cookies(
    profile: str = "Default",
) -> dict[str, str]:
    """Extract Cloudflare cookies as a flat name-to-value mapping.

    Convenience wrapper over :func:`get_cloudflare_cookies` that merges all
    domain cookies into a single dict.  If the same cookie name exists for
    multiple domains, the last one wins (though in practice ``cf_clearance``
    and ``__cf_bm`` are domain-specific and don't conflict).

    Parameters
    ----------
    profile : str
        Chrome profile directory name (default ``"Default"``).

    Returns
    -------
    dict of str to str
        Merged cookie name-to-value mapping suitable for passing to
        ``SPORTSIPY_EXTRA_COOKIES``.

    """
    flat: dict[str, str] = {}
    for domain_cookies in get_cloudflare_cookies(profile).values():
        flat.update(domain_cookies)
    return flat


def get_domain_for_url(url: str) -> str | None:
    """Map a sports-reference URL to its Cloudflare cookie domain.

    Parameters
    ----------
    url : str
        An absolute URL to a sports-reference site.

    Returns
    -------
    str or None
        The matching Cloudflare domain (e.g. ``".pro-football-reference.com"``),
        or ``None`` if the URL doesn't match a known Cloudflare-protected site.

    """
    from urllib.parse import urlparse

    hostname = urlparse(url).hostname
    if not hostname:
        return None
    for domain in CLOUDFLARE_DOMAINS:
        # domain starts with "." — match the bare domain or any subdomain.
        bare = domain.lstrip(".")
        if hostname == bare or hostname.endswith(domain):
            return domain
    return None


def detect_chrome_user_agent() -> str | None:
    """Detect the installed Google Chrome version and return a matching User-Agent.

    Reads the ``google-chrome --version`` output on Linux and constructs the
    standard Chrome User-Agent string.  This is critical for Cloudflare cookie
    validity — ``cf_clearance`` is bound to the exact User-Agent that was
    present when the challenge was solved.

    Returns
    -------
    str or None
        A User-Agent string like ``Mozilla/5.0 ... Chrome/146.0.7680.80
        Safari/537.36``, or ``None`` if Chrome's version cannot be determined.

    """
    if sys.platform != "linux":
        return None

    import subprocess

    try:
        result = subprocess.run(
            ["google-chrome", "--version"],  # noqa: S603, S607
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Output looks like: "Google Chrome 146.0.7680.80\n"
        match = re.search(r"(\d+(?:\.\d+){2,3})", result.stdout)
        if not match:
            _LOGGER.debug("Could not parse Chrome version from: %r", result.stdout.strip())
            return None
        version = match.group(1)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        _LOGGER.debug("Could not detect Chrome version: %s", exc)
        return None

    # Chrome 107+ uses a "reduced" User-Agent where the minor/build/patch
    # are frozen to 0.0.0.  Cloudflare binds cf_clearance to the exact UA
    # the browser sent, so we must replicate the reduced form.
    # See https://www.chromium.org/updates/ua-reduction/
    parts = version.split(".")
    major = parts[0]
    ua_version = f"{major}.0.0.0" if int(major) >= 107 else version

    ua = (
        f"Mozilla/5.0 (X11; Linux x86_64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{ua_version} Safari/537.36"
    )
    _LOGGER.debug("Detected Chrome UA: %s", ua)
    return ua
