"""
用户认证：密码哈希、Session 读取、路由依赖。
"""

from typing import Optional

from fastapi import HTTPException, Request
from passlib.context import CryptContext

from app.config import HTTPS_ONLY, SESSION_MAX_AGE, SESSION_SECRET_KEY

# bcrypt 哈希（禁止明文存储密码）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Session Cookie 参数（外网/HTTPS 部署见 config.py）
SESSION_COOKIE_KWARGS = {
    "max_age": SESSION_MAX_AGE,
    "https_only": HTTPS_ONLY,
    "same_site": "lax",
}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_session_user_id(request: Request) -> Optional[int]:
    """从 session 读取 user_id；无效则返回 None。"""
    raw = request.session.get("user_id")
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def login_user(request: Request, user_id: int, username: str) -> None:
    """登录：写入 session。"""
    request.session["user_id"] = user_id
    request.session["username"] = username


def logout_user(request: Request) -> None:
    """退出：清空 session。"""
    request.session.clear()


def require_api_user(request: Request) -> dict:
    """
    API 依赖：必须已登录。
    未登录或 session 失效 → 401。
    """
    from app.user_crud import get_user_by_id

    user_id = get_session_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="请先登录")

    user = get_user_by_id(user_id)
    if not user:
        logout_user(request)
        raise HTTPException(status_code=401, detail="登录已失效，请重新登录")

    return user


def get_optional_user(request: Request) -> Optional[dict]:
    """可选用户：已登录返回用户 dict，否则 None。"""
    from app.user_crud import get_user_by_id

    user_id = get_session_user_id(request)
    if not user_id:
        return None
    return get_user_by_id(user_id)
