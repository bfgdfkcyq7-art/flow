"""
外网/局域网启动脚本。

用法:
  python run_public.py

环境变量（可选）:
  FLOW_HOST=0.0.0.0          监听地址（默认 0.0.0.0，允许外网访问）
  FLOW_PORT=8000             端口
  FLOW_SECRET_KEY=随机字符串  Session 密钥（外网必设）
  FLOW_HTTPS_ONLY=1          仅 HTTPS Cookie（配好 SSL 后开启）
  FLOW_BEHIND_PROXY=1        在 nginx/frp 反代后开启
"""

import socket
import uvicorn

from app.config import HOST, PORT, warn_if_insecure

if __name__ == "__main__":
    warn_if_insecure()

    # 打印本机局域网 IP，方便手机/外网设备访问
    lan_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except OSError:
        pass

    print("Flow 外网模式启动")
    print(f"  本机:   http://127.0.0.1:{PORT}")
    print(f"  局域网: http://{lan_ip}:{PORT}")
    print("  公网访问: 需在路由器做端口映射，或使用 ngrok / frp 等隧道")
    print("  安全: 外网部署请设置 FLOW_SECRET_KEY 环境变量")

    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=False,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
