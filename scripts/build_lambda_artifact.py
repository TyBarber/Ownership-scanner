#!/usr/bin/env python3
"""Build a deterministic Python 3.12 Linux x86_64 Lambda ZIP."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist" / "ownership-scanner-lambda.zip"
LOCK_FILE = ROOT / "requirements-lambda.lock"
SOURCE_PACKAGE = ROOT / "src" / "ownership_scanner"
DATA_DIR = ROOT / "data"
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def install_linux_dependencies(stage: Path, python: str) -> None:
    command = [
        python,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-compile",
        "--no-deps",
        "--only-binary=:all:",
        "--platform=manylinux2014_x86_64",
        "--implementation=cp",
        "--python-version=3.12",
        "--abi=cp312",
        "--target",
        str(stage),
        "--requirement",
        str(LOCK_FILE),
    ]
    subprocess.run(command, check=True)


def deterministic_zip(stage: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output.with_suffix(".zip.tmp")
    if temporary_output.exists():
        temporary_output.unlink()
    try:
        with zipfile.ZipFile(
            temporary_output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            for path in sorted(item for item in stage.rglob("*") if item.is_file()):
                relative = path.relative_to(stage).as_posix()
                info = zipfile.ZipInfo(relative, ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes(), compresslevel=9)
        os.replace(temporary_output, output)
    finally:
        if temporary_output.exists():
            temporary_output.unlink()


def build(output: Path, python: str) -> None:
    if not LOCK_FILE.is_file():
        raise SystemExit("Missing Lambda dependency lock: {}".format(LOCK_FILE))
    if not SOURCE_PACKAGE.is_dir() or not DATA_DIR.is_dir():
        raise SystemExit("Application package or canonical data directory is missing")

    with tempfile.TemporaryDirectory(prefix="ownership-lambda-build-") as temporary:
        stage = Path(temporary) / "stage"
        stage.mkdir()
        install_linux_dependencies(stage, python)
        generated_bin = stage / "bin"
        if generated_bin.exists():
            shutil.rmtree(generated_bin)
        shutil.copytree(SOURCE_PACKAGE, stage / "ownership_scanner")
        shutil.copytree(DATA_DIR, stage / "data")
        deterministic_zip(stage, output)
    print("Built {}".format(output))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    build(args.output.resolve(), args.python)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
