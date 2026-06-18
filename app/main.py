"""
Flow 主入口：
- Session 认证（支持外网部署配置）
- 页面路由（未登录跳转 /login）
- API 路由（未登录返回 401）
"""

from datetime import date
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.auth import SESSION_COOKIE_KWARGS, SESSION_SECRET_KEY, get_optional_user, logout_user
from app.config import BEHIND_PROXY, warn_if_insecure
from app.database import LIFE_AREAS, MOOD_MAP, init_db
from app.routers import auth, dashboard, records, v1

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Flow",
    description="记录人生状态的流动 — Everything Flows",
    version="2.1.0",
)

warn_if_insecure()

# 反向代理后正确识别客户端 IP / 协议（nginx、frp 等）
if BEHIND_PROXY:
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    **SESSION_COOKIE_KWARGS,
)

init_db()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    field_hints = {
        "weight": "数值须大于 0，且不超过 999999",
        "sleep_hours": "睡眠时长须在 0–24 小时之间",
        "exercise_minutes": "运动时间须 ≥ 0 分钟，且不超过 1440",
        "mood": "心情须在 1–5 之间",
        "diary": "日记不能超过 200 字",
        "password": "密码至少 6 位",
        "password_confirm": "两次输入的密码不一致",
    }
    messages = []
    for err in exc.errors():
        loc = err.get("loc", [])
        field = loc[-1] if loc else ""
        if field in field_hints:
            messages.append(field_hints[field])
        else:
            messages.append(err.get("msg", "输入数据无效"))
    return JSONResponse(status_code=422, content={"detail": "；".join(messages)})


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.include_router(auth.router)
app.include_router(records.router)
app.include_router(dashboard.router)
app.include_router(v1.router)


@app.get("/health")
def health_check():
    """健康检查（部署/监控用）。"""
    return {"status": "ok", "service": "flow"}


def _redirect_login():
    return RedirectResponse(url="/login", status_code=303)


def _require_page_user(request: Request) -> dict | RedirectResponse:
    user = get_optional_user(request)
    if not user:
        logout_user(request)
        return _redirect_login()
    return user


@app.get("/login", response_class=HTMLResponse)
def page_login(request: Request):
    user = get_optional_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
def page_register(request: Request):
    user = get_optional_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/logout")
def page_logout(request: Request):
    logout_user(request)
    return RedirectResponse(url="/login", status_code=303)


@app.get("/", response_class=HTMLResponse)
def page_index(request: Request):
    user = _require_page_user(request)
    if isinstance(user, RedirectResponse):
        return user

    today = date.today().isoformat()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "today": today,
            "mood_map": MOOD_MAP,
            "life_areas": LIFE_AREAS,
            "current_user": user,
        },
    )


@app.get("/history", response_class=HTMLResponse)
def page_history(request: Request):
    user = _require_page_user(request)
    if isinstance(user, RedirectResponse):
        return user

    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "mood_map": MOOD_MAP,
            "life_areas": LIFE_AREAS,
            "current_user": user,
        },
    )


@app.get("/dashboard", response_class=HTMLResponse)
def page_dashboard(request: Request):
    user = _require_page_user(request)
    if isinstance(user, RedirectResponse):
        return user

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "life_areas": LIFE_AREAS,
            "current_user": user,
        },
    )
