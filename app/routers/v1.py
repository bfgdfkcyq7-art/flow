"""
API v1 预留路由（Token 认证，尚未实现）。

未来迁移路径：/api/v1/records、/api/v1/dashboard
认证方式：Bearer Token（替代 Session Cookie）
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["v1-stub"])


@router.get("/status")
def v1_status():
    return {
        "version": "v1",
        "status": "not_implemented",
        "message": "Token 认证 API 尚未开放，请使用 Session 登录",
    }
