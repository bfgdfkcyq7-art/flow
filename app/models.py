"""
领域模型：将 sqlite3.Row 转为普通 dict，便于 JSON 序列化。
"""

import json
from typing import Any, Optional


def _safe_float(value) -> Optional[float]:
    """安全转为 float；无效值返回 None，避免图表/前端收到脏数据。"""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value) -> Optional[int]:
    """安全转为 int；无效值返回 None。"""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def row_to_user(row) -> Optional[dict[str, Any]]:
    """User 行 -> 字典（不含 password_hash）。"""
    if row is None:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "created_at": row["created_at"] or "",
    }


def row_to_user_with_hash(row) -> Optional[dict[str, Any]]:
    """User 行 -> 字典（含 password_hash，仅内部认证使用）。"""
    if row is None:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "password_hash": row["password_hash"],
        "created_at": row["created_at"] or "",
    }


def row_to_record(row) -> Optional[dict[str, Any]]:
    """数据库行 -> API/前端可用字典。"""
    if row is None:
        return None

    life_areas_raw = row["life_areas"] or "[]"
    try:
        life_areas = json.loads(life_areas_raw)
        if not isinstance(life_areas, list):
            life_areas = []
    except json.JSONDecodeError:
        life_areas = []

    keywords_raw = row["keywords"] or ""
    keywords = [k.strip() for k in str(keywords_raw).split(",") if k.strip()]

    return {
        "id": row["id"],
        "date": row["date"] or "",
        "weight": _safe_float(row["weight"]),
        "mood": _safe_int(row["mood"]),
        "sleep_hours": _safe_float(row["sleep_hours"]),
        "exercise_minutes": _safe_int(row["exercise_minutes"]),
        "keywords": keywords,
        "diary": (row["diary"] or "").strip(),
        "life_areas": [a for a in life_areas if isinstance(a, str) and a],
        "created_at": row["created_at"] or "",
    }
