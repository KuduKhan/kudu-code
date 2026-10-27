"""Provide explicit local-only developer access to every isolated API test."""
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

@pytest.fixture(autouse=True)
def local_dev_mode(monkeypatch):
    monkeypatch.setenv('KUDU_DEV_MODE','1')
