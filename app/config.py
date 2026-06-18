"""
Flow 运行配置（支持环境变量，便于内网/外网部署）。
"""

import os
import warnings

# 服务监听
HOST = os.environ.get("FLOW_HOST", "0.0.0.0")
PORT = int(os.environ.get("FLOW_PORT", "8000"))

# Session 安全（外网部署务必设置 FLOW_SECRET_KEY）
SESSION_SECRET_KEY = os.environ.get(
    "FLOW_SECRET_KEY", "flow-dev-secret-change-in-production"
)
SESSION_MAX_AGE = int(os.environ.get("FLOW_SESSION_MAX_AGE", str(14 * 24 * 3600)))

# 外网 HTTPS 部署时设为 1，Cookie 仅通过 HTTPS 传输
HTTPS_ONLY = os.environ.get("FLOW_HTTPS_ONLY", "0").lower() in ("1", "true", "yes")

# 反向代理（nginx / frp）后可设 1，信任 X-Forwarded-* 头
BEHIND_PROXY = os.environ.get("FLOW_BEHIND_PROXY", "0").lower() in ("1", "true", "yes")


def warn_if_insecure() -> None:
    """外网暴露时使用默认密钥则警告。"""
    if SESSION_SECRET_KEY == "flow-dev-secret-change-in-production":
        warnings.warn(
            "FLOW_SECRET_KEY 使用默认值，外网部署前请设置随机密钥",
            stacklevel=2,
        )
