from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ownership_scanner.api import create_app
from ownership_scanner.repository import CsvRepository


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def repository():
    return CsvRepository(ROOT / "data")


@pytest.fixture
def client(repository):
    return TestClient(create_app(repository))
