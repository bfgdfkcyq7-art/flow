"""Dashboard 数据 API（须登录，按 user_id 隔离）。"""

from fastapi import APIRouter, Depends

from app import crud
from app.auth import require_api_user
from app.services.ai_summary import ai_summary_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/charts")
def api_chart_data(user: dict = Depends(require_api_user)):
    return crud.get_chart_data(user["id"])


@router.get("/life-timeline")
def api_life_timeline(user: dict = Depends(require_api_user)):
    uid = user["id"]
    return {
        "stats": crud.get_life_timeline_stats(uid),
        "records": crud.list_records(uid),
    }


@router.get("/ai-preview")
def api_ai_preview(user: dict = Depends(require_api_user)):
    records = crud.list_records(user["id"])
    return {
        "weekly": ai_summary_service.weekly_summary(records),
        "monthly": ai_summary_service.monthly_summary(records),
        "mood": ai_summary_service.mood_analysis(records),
        "weight": ai_summary_service.weight_trend_analysis(records),
    }
