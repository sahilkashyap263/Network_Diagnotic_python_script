"""Small SQLite history store for diagnostic runs."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from network_checks import CheckResult

DB_PATH = Path(__file__).with_name("diagnostics.db")


def initialize_db() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS check_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checked_at TEXT NOT NULL,
                check_name TEXT NOT NULL,
                status TEXT NOT NULL,
                summary TEXT NOT NULL,
                details TEXT NOT NULL,
                latency_ms REAL
            )
            """
        )
        connection.commit()


def save_results(results: Iterable[CheckResult]) -> None:
    rows = [
        (
            result.checked_at,
            result.name,
            result.status,
            result.summary,
            result.details,
            result.latency_ms,
        )
        for result in results
    ]
    if not rows:
        return
    with sqlite3.connect(DB_PATH) as connection:
        connection.executemany(
            "INSERT INTO check_history (checked_at, check_name, status, summary, details, latency_ms) VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
        connection.commit()


def read_history(limit: int = 30) -> list[dict]:
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT checked_at, check_name, status, summary, details, latency_ms FROM check_history ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def clear_history() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("DELETE FROM check_history")
        connection.commit()
