"""SQLite store with per-operation connections and parameterized queries."""
from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4
from .settings import database_path

def stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def uid() -> str:
    return str(uuid4())

@contextmanager
def connect():
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=12)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA busy_timeout=12000")
    db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def initialize():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
          id TEXT PRIMARY KEY, name TEXT NOT NULL, repo_url TEXT NOT NULL DEFAULT '',
          workspace TEXT NOT NULL UNIQUE, stack TEXT NOT NULL DEFAULT 'Unknown',
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks (
          id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
          title TEXT NOT NULL, instruction TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'queued',
          plan TEXT NOT NULL DEFAULT '[]', proposal TEXT NOT NULL DEFAULT '',
          branch TEXT NOT NULL DEFAULT '', result TEXT NOT NULL DEFAULT '',
          pr_url TEXT NOT NULL DEFAULT '',
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
          id TEXT PRIMARY KEY, task_id TEXT, project_id TEXT,
          kind TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
        CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at DESC);
        """)
        existing = {r['name'] for r in db.execute('PRAGMA table_info(tasks)')}
        if 'pr_url' not in existing:
            db.execute("ALTER TABLE tasks ADD COLUMN pr_url TEXT NOT NULL DEFAULT ''")

def rows(query: str, values=()):
    with connect() as db:
        return [dict(x) for x in db.execute(query, values).fetchall()]

def one(query: str, values=()):
    with connect() as db:
        value = db.execute(query, values).fetchone()
        return dict(value) if value else None

def execute(query: str, values=()):
    with connect() as db:
        db.execute(query, values)

def log(kind: str, message: str, task_id=None, project_id=None):
    execute("INSERT INTO events VALUES (?,?,?,?,?,?)", (uid(), task_id, project_id, kind, message[:2000], stamp()))
