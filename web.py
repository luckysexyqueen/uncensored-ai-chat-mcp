import hmac
import os

from starlette.requests import Request
from starlette.responses import JSONResponse
from server import mcp

token = os.environ["MCP_ACCESS_TOKEN"].encode()
if not token or not os.environ.get("UNCENSORED_API_KEY"):
    raise RuntimeError("두 인증 환경변수를 모두 설정해 주세요.")

transport = mcp.streamable_http_app()


async def app(scope, receive, send):
    if scope["type"] == "http":
        request = Request(scope)
        if request.url.path == "/healthz" and request.method in {"GET", "HEAD"}:
            await JSONResponse({"status": "ok"})(scope, receive, send)
            return
        supplied = request.headers.get("authorization", "").encode()
        if not hmac.compare_digest(supplied, b"Bearer " + token):
            await JSONResponse({"error": "unauthorized"}, status_code=401,
                               headers={"WWW-Authenticate": "Bearer"})(scope, receive, send)
            return
    await transport(scope, receive, send)
