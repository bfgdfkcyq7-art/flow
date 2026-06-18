"""
SQLite 数据库连接、初始化与迁移。
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "flow.db"

MOOD_MAP = {
    5: "😀",
    4: "🙂",
    3: "😐",
    2: "😔",
    1: "😭",
}

LIFE_AREAS = ["学业", "健身", "感情", "旅行", "摄影", "生活"]


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [r["name"] for r in rows]


def _migrate_daily_record(conn: sqlite3.Connection) -> None:
    """将旧版 DailyRecord（无 user_id）迁移为多用户结构。"""
    if "DailyRecord" not in [
        r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    ]:
        return

    cols = _table_columns(conn, "DailyRecord")
    if "user_id" in cols:
        return

    # 旧数据无法安全归属用户，重建表结构（多用户隔离优先）
    conn.executescript(
        """
        DROP TABLE IF EXISTS DailyRecord;

        CREATE TABLE DailyRecord (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            weight REAL,
            mood INTEGER CHECK(mood BETWEEN 1 AND 5),
            sleep_hours REAL,
            exercise_minutes INTEGER,
            keywords TEXT DEFAULT '',
            diary TEXT DEFAULT '',
            life_areas TEXT DEFAULT '[]',
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            UNIQUE(user_id, date),
            FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_daily_record_user_date
        ON DailyRecord(user_id, date DESC);
        """
    )


def init_db() -> None:
    """创建 User / DailyRecord 表，并执行必要迁移。"""
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS User (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE INDEX IF NOT EXISTS idx_user_username ON User(username);
            """
        )

        _migrate_daily_record(conn)

        # 新版 DailyRecord（首次安装或迁移后已存在则跳过）
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS DailyRecord (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                weight REAL,
                mood INTEGER CHECK(mood BETWEEN 1 AND 5),
                sleep_hours REAL,
                exercise_minutes INTEGER,
                keywords TEXT DEFAULT '',
                diary TEXT DEFAULT '',
                life_areas TEXT DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                UNIQUE(user_id, date),
                FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_daily_record_user_date
            ON DailyRecord(user_id, date DESC);
            """
        )
        conn.commit()
    finally:
        conn.close()
