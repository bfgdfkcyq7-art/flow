"""
OAuth 第三方登录预留接口（尚未实现）。

未来可接入：
- Google Login
- GitHub Login
"""

from typing import Any


class OAuthService:
    """占位：第三方 OAuth 登录。"""

    def google_login_url(self) -> dict[str, Any]:
        return {"status": "not_implemented", "provider": "google"}

    def github_login_url(self) -> dict[str, Any]:
        return {"status": "not_implemented", "provider": "github"}

    def handle_callback(self, provider: str, code: str) -> dict[str, Any]:
        return {
            "status": "not_implemented",
            "provider": provider,
            "message": "OAuth 回调尚未接入",
        }


oauth_service = OAuthService()
