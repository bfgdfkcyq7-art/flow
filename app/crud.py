"""
DailyRecord 增删改查。
所有查询必须绑定 user_id，确保多用户数据隔离。
"""

import json
from typing import Optional

from app.database import get_connection
from app.models import row_to_record


def _keywords_to_db(keywords: list[str]) -> str:
    return ",".join(keywords)


def create_record(user_id: int, data: dict) -> dict:
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO DailyRecord
            (user_id, date, weight, mood, sleep_hours, exercise_minutes,
             keywords, diary, life_areas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                data["date"],
                data.get("weight"),
                data.get("mood"),
                data.get("sleep_hours"),
                data.get("exercise_minutes"),
                _keywords_to_db(data.get("keywords", [])),
                data.get("diary", ""),
                json.dumps(data.get("life_areas", []), ensure_ascii=False),
            ),
        )
        conn.commit()
        return get_record_by_id(user_id, cur.lastrowid)
    finally:
        conn.close()


def update_record(user_id: int, record_id: int, data: dict) -> Optional[dict]:
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            UPDATE DailyRecord SET
                date = ?,
                weight = ?,
                mood = ?,
                sleep_hours = ?,
                exercise_minutes = ?,
                keywords = ?,
                diary = ?,
                life_areas = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                data["date"],
                data.get("weight"),
                data.get("mood"),
                data.get("sleep_hours"),
                data.get("exercise_minutes"),
                _keywords_to_db(data.get("keywords", [])),
                data.get("diary", ""),
                json.dumps(data.get("life_areas", []), ensure_ascii=False),
                record_id,
                user_id,
            ),
        )
        conn.commit()
        if cur.rowcount == 0:
            return None
        return get_record_by_id(user_id, record_id)
    finally:
        conn.close()


def delete_record(user_id: int, record_id: int) -> bool:
    conn = get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM DailyRecord WHERE id = ? AND user_id = ?",
            (record_id, user_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_record_by_id(user_id: int, record_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM DailyRecord WHERE id = ? AND user_id = ?",
            (record_id, user_id),
        ).fetchone()
        return row_to_record(row)
    finally:
        conn.close()


def get_record_by_date(user_id: int, date_str: str) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM DailyRecord WHERE user_id = ? AND date = ?",
            (user_id, date_str),
        ).fetchone()
        return row_to_record(row)
    finally:
        conn.close()


def list_records(user_id: int) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT * FROM DailyRecord
            WHERE user_id = ?
            ORDER BY date DESC, id DESC
            """,
            (user_id,),
        ).fetchall()
        return [row_to_record(r) for r in rows]
    finally:
        conn.close()


def get_chart_data(user_id: int) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT * FROM DailyRecord
            WHERE user_id = ?
            ORDER BY date ASC, id ASC
            """,
            (user_id,),
        ).fetchall()
        return [row_to_record(r) for r in rows]
    finally:
        conn.close()


def get_life_timeline_stats(user_id: int) -> dict:
    records = list_records(user_id)
    stats = {area: 0 for area in ["学业", "健身", "感情", "旅行", "摄影", "生活"]}
    for r in records:
        for area in r.get("life_areas", []):
            if area in stats:
                stats[area] += 1
    return stats
