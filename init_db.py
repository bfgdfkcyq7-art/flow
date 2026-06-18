"""独立运行：python init_db.py — 初始化 User + DailyRecord 表"""

from app.database import init_db

# SQL 建表语句（与 database.py 保持一致，供参考）
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

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
"""

if __name__ == "__main__":
    init_db()
    print("Flow V2 数据库初始化完成：data/flow.db")
    print("表：User（用户）、DailyRecord（每日记录，含 user_id 隔离）")
