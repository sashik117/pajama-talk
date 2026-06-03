import asyncio
from collections import defaultdict

from fastapi import WebSocket

from app.core.config import settings

WS_POLICY_LIMIT_CODE = 4408


class WebSocketConnectionLimiter:
    def __init__(self) -> None:
        self._active_by_ip: dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()

    def client_ip(self, websocket: WebSocket) -> str:
        if websocket.client and websocket.client.host:
            return websocket.client.host
        return "unknown"

    async def acquire(self, websocket: WebSocket) -> str | None:
        ip_address = self.client_ip(websocket)
        async with self._lock:
            active_count = self._active_by_ip[ip_address]
            if active_count >= settings.websocket_max_connections_per_ip:
                return None
            self._active_by_ip[ip_address] = active_count + 1
            return ip_address

    async def release(self, ip_address: str) -> None:
        async with self._lock:
            active_count = self._active_by_ip.get(ip_address, 0)
            if active_count <= 1:
                self._active_by_ip.pop(ip_address, None)
                return
            self._active_by_ip[ip_address] = active_count - 1


websocket_connection_limiter = WebSocketConnectionLimiter()
