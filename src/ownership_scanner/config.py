"""Application configuration for local and packaged deployments."""

import os
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Optional

from .errors import DataConfigurationError


REQUIRED_CSV_FILES = (
    "brands.csv",
    "companies.csv",
    "ownership_groups.csv",
    "ownership_relationships.csv",
    "products.csv",
    "relationship_sources.csv",
    "research_gap_sources.csv",
    "research_gaps.csv",
    "sources.csv",
)
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
LOCAL_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _validate_data_dir(path: Path, source: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        raise DataConfigurationError(
            "Configured ownership dataset directory is unavailable ({})".format(source)
        )
    missing = [name for name in REQUIRED_CSV_FILES if not (resolved / name).is_file()]
    if missing:
        raise DataConfigurationError(
            "Ownership dataset is incomplete ({}); missing {} required CSV file(s)".format(
                source, len(missing)
            )
        )
    return resolved


def resolve_data_dir(
    packaged_root: Optional[Path] = None,
    local_root: Optional[Path] = None,
) -> Path:
    override = os.environ.get("OWNERSHIP_DATA_DIR")
    if override is not None:
        if not override.strip():
            raise DataConfigurationError("OWNERSHIP_DATA_DIR must not be empty")
        return _validate_data_dir(Path(override), "OWNERSHIP_DATA_DIR")

    packaged_data = (packaged_root or PACKAGE_ROOT) / "data"
    if packaged_data.is_dir():
        return _validate_data_dir(packaged_data, "packaged deployment")

    local_data = (local_root or LOCAL_PROJECT_ROOT) / "data"
    return _validate_data_dir(local_data, "local repository")


@dataclass(frozen=True)
class Settings:
    data_dir: Path = field(default_factory=resolve_data_dir)
