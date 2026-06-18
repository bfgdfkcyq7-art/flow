"""
User 表增删改查。
"""

from typing import Optional

from app.database import get_connection
from app.models import row_to_user, row_to_user_with_hash


def create_user(username: str, password_hash: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO User (username, password_hash)
            VALUES (?, ?)
            """,
            (username.strip(), password_hash),
        )
        conn.commit()
        return get_user_by_id(cur.lastrowid)
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM User WHERE id = ?", (user_id,)
        ).fetchone()
        return row_to_user(row)
    finally:
        conn.close()


def get_user_with_hash_by_username(username: str) -> Optional[dict]:
    """登录校验用，返回含 password_hash 的用户。"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM User WHERE username = ?", (username.strip(),)
        ).fetchone()
        return row_to_user_with_hash(row)
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM User WHERE username = ?", (username.strip(),)
        ).fetchone()
        return row_to_user(row)
    finally:
        conn.close()


def username_exists(username: str) -> bool:
    return get_user_by_username(username) is not None
