"""记录相关 REST API（须登录，按 user_id 隔离）。"""

from fastapi import APIRouter, Depends, HTTPException

from app import crud
from app.auth import require_api_user
from app.schemas import RecordCreate, RecordUpdate

router = APIRouter(prefix="/api/records", tags=["records"])


@router.get("")
def api_list_records(user: dict = Depends(require_api_user)):
    return crud.list_records(user["id"])


@router.get("/today/{date_str}")
def api_get_by_date(date_str: str, user: dict = Depends(require_api_user)):
    record = crud.get_record_by_date(user["id"], date_str)
    return record or {}


@router.post("")
def api_create_record(payload: RecordCreate, user: dict = Depends(require_api_user)):
    existing = crud.get_record_by_date(user["id"], payload.date)
    if existing:
        raise HTTPException(status_code=400, detail="该日期已有记录，请使用编辑功能")
    return crud.create_record(user["id"], payload.model_dump())


@router.put("/{record_id}")
def api_update_record(
    record_id: int,
    payload: RecordUpdate,
    user: dict = Depends(require_api_user),
):
    updated = crud.update_record(user["id"], record_id, payload.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="记录不存在")
    return updated


@router.delete("/{record_id}")
def api_delete_record(record_id: int, user: dict = Depends(require_api_user)):
    ok = crud.delete_record(user["id"], record_id)
    if not ok:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"message": "删除成功"}
