"""用户认证 API：注册、登录、退出。"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.auth import hash_password, login_user, logout_user, verify_password
from app.schemas_auth import LoginRequest, RegisterRequest
from app.user_crud import create_user, get_user_with_hash_by_username, username_exists

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def api_register(payload: RegisterRequest, request: Request):
    if username_exists(payload.username):
        raise HTTPException(status_code=400, detail="用户名已被注册")

    user = create_user(payload.username, hash_password(payload.password))
    login_user(request, user["id"], user["username"])
    return {"message": "注册成功", "username": user["username"]}


@router.post("/login")
def api_login(payload: LoginRequest, request: Request):
    user = get_user_with_hash_by_username(payload.username)
    if not user or not verify_password(payload.password, user["password_hash"]):
        # 统一提示，不泄露用户名是否存在
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    login_user(request, user["id"], user["username"])
    return {"message": "登录成功", "username": user["username"]}


@router.get("/logout")
def api_logout_get(request: Request):
    """GET /api/auth/logout → 清 session 并跳转登录页（供链接使用）。"""
    logout_user(request)
    return RedirectResponse(url="/login", status_code=303)


@router.post("/logout")
def api_logout_post(request: Request):
    logout_user(request)
    return {"message": "已退出登录"}
