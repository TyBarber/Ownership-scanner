#!/usr/bin/env python3
"""Verify Lambda ZIP contents, platform compatibility, safety, and importability."""

from __future__ import annotations

import argparse
import json
import os
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = ROOT / "dist" / "ownership-scanner-lambda.zip"
REQUIRED_CSVS = {
    "data/brands.csv",
    "data/companies.csv",
    "data/ownership_groups.csv",
    "data/ownership_relationships.csv",
    "data/products.csv",
    "data/relationship_sources.csv",
    "data/research_gap_sources.csv",
    "data/research_gaps.csv",
    "data/sources.csv",
}
REQUIRED_PATHS = REQUIRED_CSVS | {
    "ownership_scanner/api.py",
    "ownership_scanner/config.py",
    "ownership_scanner/lambda_handler.py",
    "mangum/__init__.py",
    "fastapi/__init__.py",
    "starlette/__init__.py",
    "pydantic/__init__.py",
}
PROHIBITED_PARTS = {".git", ".venv", "venv", "tests", "docs", "__pycache__"}
PROHIBITED_TOP_LEVEL = {"pytest", "httpx", "uvicorn", "certifi", "click"}
PROHIBITED_SUFFIXES = {".jpg", ".jpeg", ".png", ".heic", ".pem", ".key"}
PROHIBITED_FILENAMES = {".env", ".env.local", "credentials", "credentials.json"}
ABSOLUTE_PATH_MARKERS = (b"/Users/", b"file:///Users/")


def human_size(size: int) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return "{:.1f} {}".format(value, unit)
        value /= 1024
    raise AssertionError("unreachable")


def verify_elf_x86_64(name: str, content: bytes) -> None:
    if not content.startswith(b"\x7fELF"):
        raise SystemExit("Binary extension is not Linux ELF: {}".format(name))
    if len(content) < 20 or content[5] != 1:
        raise SystemExit("Unsupported ELF format: {}".format(name))
    machine = struct.unpack("<H", content[18:20])[0]
    if machine != 62:
        raise SystemExit("Binary extension is not x86_64: {}".format(name))


def verify_import(archive: zipfile.ZipFile, names: set[str], python: str) -> None:
    with tempfile.TemporaryDirectory(prefix="ownership-lambda-verify-") as temporary:
        root = Path(temporary)
        selected = [
            name
            for name in names
            if name.startswith("ownership_scanner/") or name.startswith("data/")
        ]
        for name in selected:
            archive.extract(name, root)
        code = (
            "import json,sys;"
            "sys.path.insert(0,sys.argv[1]);"
            "from ownership_scanner.lambda_handler import handler;"
            "print(json.dumps({'callable': callable(handler), 'module': handler.__module__}))"
        )
        environment = os.environ.copy()
        environment.pop("OWNERSHIP_DATA_DIR", None)
        result = subprocess.run(
            [python, "-c", code, str(root)],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        imported = json.loads(result.stdout)
        if not imported["callable"]:
            raise SystemExit("Packaged Lambda handler is not callable")


def verify(path: Path, python: str) -> None:
    if not path.is_file():
        raise SystemExit("Lambda artifact does not exist: {}".format(path))
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        missing = sorted(REQUIRED_PATHS - names)
        if missing:
            raise SystemExit("Artifact is missing required files: {}".format(", ".join(missing)))

        for name in sorted(names):
            item = PurePosixPath(name)
            lower_parts = {part.casefold() for part in item.parts}
            if lower_parts & PROHIBITED_PARTS:
                raise SystemExit("Prohibited directory in artifact: {}".format(name))
            if item.parts and item.parts[0].casefold() in PROHIBITED_TOP_LEVEL:
                raise SystemExit("Local-only dependency in artifact: {}".format(name))
            if item.name.casefold() in PROHIBITED_FILENAMES:
                raise SystemExit("Potential secret file in artifact: {}".format(name))
            if item.suffix.casefold() in PROHIBITED_SUFFIXES:
                raise SystemExit("Prohibited file type in artifact: {}".format(name))
            content = archive.read(name)
            if any(marker in content for marker in ABSOLUTE_PATH_MARKERS):
                raise SystemExit("Absolute Mac path found in artifact: {}".format(name))
            if item.suffix == ".so":
                verify_elf_x86_64(name, content)

        verify_import(archive, names, python)
        uncompressed = sum(item.file_size for item in archive.infolist())

    print("Verified {} files".format(len(names)))
    for name in sorted(names):
        print(name)
    print("Handler: ownership_scanner.lambda_handler.handler")
    print("Compressed size: {}".format(human_size(path.stat().st_size)))
    print("Uncompressed size: {}".format(human_size(uncompressed)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    verify(args.artifact.resolve(), args.python)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
