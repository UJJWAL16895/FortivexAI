"""Single-instance demo perimeter for HTTP and WebSocket application work."""

import hashlib
import hmac
import time
from collections import deque

from starlette.requests import HTTPConnection, Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class PublicGuard:
    def __init__(self, app: ASGIApp, access_code: str, rpm: int, daily: int) -> None:
        self.app = app
        self.key = access_code.encode()
        self.rpm, self.daily = rpm, daily
        self.clients: dict[str, deque[float]] = {}
        self.requests: deque[float] = deque()

    def token(self, day: int) -> str:
        return hmac.new(self.key, f"shelfpilot-demo:{day}".encode(), hashlib.sha256).hexdigest()

    def reserve(self, peer: str) -> bool:
        now = time.monotonic()
        while self.requests and self.requests[0] <= now - 86400:
            self.requests.popleft()
        if len(self.requests) >= self.daily:
            return False
        times = self.clients.get(peer)
        if times is None:
            if len(self.clients) >= 2048:
                self.clients = {
                    key: recent
                    for key, recent in self.clients.items()
                    if recent and recent[-1] > now - 60
                }
                if len(self.clients) >= 2048:
                    return False
            times = self.clients.setdefault(peer, deque())
        while times and times[0] <= now - 60:
            times.popleft()
        if len(times) >= self.rpm:
            return False
        times.append(now)
        self.requests.append(now)
        return True

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return
        path = scope["path"]
        connection = HTTPConnection(scope)
        peer = connection.client.host if connection.client else "unknown"
        day = int(time.time() // 86400)
        if path == "/api/unlock" and scope["type"] == "http":
            response = await self.unlock(Request(scope, receive), peer, day)
            await response(scope, receive, send)
            return
        protected = scope["type"] == "websocket" or (
            path.startswith("/api/") and path != "/api/public-status"
        )
        if not protected:
            await self.app(scope, receive, send)
            return
        if self.key and not hmac.compare_digest(
            connection.cookies.get("shelf_access", "").encode(), self.token(day).encode()
        ):
            if scope["type"] == "websocket":
                await send({"type": "websocket.close", "code": 1008})
            else:
                await JSONResponse({"detail": "Enter the evaluator access code."}, status_code=401)(
                    scope, receive, send
                )
            return
        if scope["type"] == "http":
            if not self.reserve(peer):
                await JSONResponse({"detail": "Demo request limit reached."}, status_code=429)(
                    scope, receive, send
                )
                return
            await self.app(scope, receive, send)
            return

        async def limited_receive() -> Message:
            message = await receive()
            if message["type"] == "websocket.receive" and not self.reserve(peer):
                await send(
                    {
                        "type": "websocket.close",
                        "code": 1008,
                        "reason": "Demo request limit reached",
                    }
                )
                return {"type": "websocket.disconnect", "code": 1008}
            return message

        await self.app(scope, limited_receive, send)

    async def unlock(self, request: Request, peer: str, day: int) -> Response:
        if request.method != "POST":
            return Response(status_code=405)
        if not self.reserve(peer):
            return PlainTextResponse("Demo request limit reached", status_code=429)
        if request.headers.get("origin") != f"{request.url.scheme}://{request.headers.get('host')}":
            return Response(status_code=403)
        value = bytearray()
        async for chunk in request.stream():
            if len(value) + len(chunk) > 256:
                return Response(status_code=413)
            value.extend(chunk)
        if not self.key or not hmac.compare_digest(bytes(value), self.key):
            return PlainTextResponse("Invalid access code", status_code=401)
        response = Response(status_code=204)
        response.set_cookie(
            "shelf_access",
            self.token(day),
            secure=True,
            httponly=True,
            samesite="strict",
            max_age=86400,
        )
        return response
