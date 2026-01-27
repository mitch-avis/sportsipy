#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

import requests


def _load_map(path: Path):
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _save_map(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture a fixture from a live URL and update the fixture map."
    )
    parser.add_argument("--url", required=True, help="URL to fetch")
    parser.add_argument(
        "--path",
        required=True,
        help="Relative fixture path (inside the fixtures directory)",
    )
    parser.add_argument(
        "--fixtures-dir",
        default="tests/fixtures",
        help="Root fixtures directory (default: tests/fixtures)",
    )
    parser.add_argument(
        "--map",
        dest="map_path",
        default=None,
        help="Fixture map JSON (default: <fixtures-dir>/url_map.json)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing fixture file if it exists",
    )
    parser.add_argument(
        "--allow-non-200",
        action="store_true",
        help="Save fixtures even if the response is not 200",
    )
    args = parser.parse_args()

    if not os.environ.get("SPORTSIPY_CAPTURE_FIXTURES"):
        print("Set SPORTSIPY_CAPTURE_FIXTURES=1 to enable fixture capture.")
        return 2

    fixtures_dir = Path(args.fixtures_dir)
    map_path = Path(args.map_path) if args.map_path else fixtures_dir / "url_map.json"

    response = requests.get(args.url, timeout=30)
    if response.status_code >= 400 and not args.allow_non_200:
        print(f"Request failed ({response.status_code}); use --allow-non-200 to save anyway.")
        return 3

    rel_path = Path(args.path)
    if rel_path.is_absolute():
        print("--path must be relative to the fixtures directory.")
        return 4

    output_path = fixtures_dir / rel_path
    if output_path.exists() and not args.overwrite:
        print(f"Fixture already exists: {output_path}")
        return 5
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(response.text, encoding="utf-8")

    mapping = _load_map(map_path)
    entry = {"url": args.url, "path": rel_path.as_posix()}
    if isinstance(mapping, list):
        mapping.append(entry)
    elif isinstance(mapping, dict):
        mapping[args.url] = rel_path.as_posix()
    else:
        mapping = [entry]
    _save_map(map_path, mapping)

    print(f"Saved fixture to {output_path}")
    print(f"Updated map at {map_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
