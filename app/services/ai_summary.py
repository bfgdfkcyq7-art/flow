"""
AI Summary 模块预留接口。

未来可接入：
- 周报 / 月报生成
- 情绪分析
- 体重趋势分析
"""

from typing import Any


class AISummaryService:
    """占位实现，后续替换为真实 LLM 调用。"""

    def weekly_summary(self, records: list[dict]) -> dict[str, Any]:
        return {
            "status": "not_implemented",
            "message": "周报生成功能尚未接入 AI",
            "record_count": len(records),
        }

    def monthly_summary(self, records: list[dict]) -> dict[str, Any]:
        return {
            "status": "not_implemented",
            "message": "月报生成功能尚未接入 AI",
            "record_count": len(records),
        }

    def mood_analysis(self, records: list[dict]) -> dict[str, Any]:
        moods = [r["mood"] for r in records if r.get("mood") is not None]
        avg = sum(moods) / len(moods) if moods else None
        return {
            "status": "not_implemented",
            "average_mood": avg,
            "message": "情绪深度分析尚未接入 AI",
        }

    def weight_trend_analysis(self, records: list[dict]) -> dict[str, Any]:
        weights = [
            (r["date"], r["weight"])
            for r in records
            if r.get("weight") is not None
        ]
        return {
            "status": "not_implemented",
            "data_points": len(weights),
            "message": "体重趋势 AI 解读尚未接入",
        }


ai_summary_service = AISummaryService()
