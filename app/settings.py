from __future__ import annotations
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def database_path() -> Path:
    return Path(os.getenv("KUDU_DATABASE_PATH", str(BASE_DIR / "kudu.sqlite3"))).expanduser().resolve()

def workspace_root() -> Path:
    return Path(os.getenv("KUDU_WORKSPACE_ROOT", str(BASE_DIR / "workspaces"))).expanduser().resolve()

def model_name() -> str:
    return os.getenv("KUDU_MODEL", "").strip()

VERSION = "0.3.0"
