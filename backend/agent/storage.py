import json
import sqlite3
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_DB_PATH = Path("data") / "analyses.db"


class AnalysisRepository:
    """Persistencia SQLite de los análisis realizados por la API."""

    def __init__(self, database_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    risk_level TEXT,
                    indicators_json TEXT NOT NULL,
                    alerts_json TEXT NOT NULL,
                    response_json TEXT NOT NULL
                )
                """
            )

    def save_analysis(self, file_name: str, result: Mapping[str, Any]) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO analyses
                    (created_at, file_name, risk_level, indicators_json, alerts_json, response_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(UTC).isoformat(),
                    file_name,
                    result.get("nivel_riesgo"),
                    json.dumps(result.get("indicadores", {}), ensure_ascii=False),
                    json.dumps(result.get("alertas", []), ensure_ascii=False),
                    json.dumps(dict(result), ensure_ascii=False),
                ),
            )
            return int(cursor.lastrowid)

    def count(self) -> int:
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM analyses").fetchone()[0])

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM analyses ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]
