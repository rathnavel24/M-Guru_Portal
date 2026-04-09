import asyncio

from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder


class ChatConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, dict[WebSocket, int]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, conversation_id: int, user_id: int, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.setdefault(conversation_id, {})[websocket] = user_id

    async def disconnect(self, conversation_id: int, websocket: WebSocket):
        async with self._lock:
            connections = self.active_connections.get(conversation_id)
            if not connections:
                return

            connections.pop(websocket, None)
            if not connections:
                self.active_connections.pop(conversation_id, None)

    async def send_personal_message(self, websocket: WebSocket, payload: dict):
        await websocket.send_json(jsonable_encoder(payload))

    async def broadcast(self, conversation_id: int, payload: dict):
        async with self._lock:
            connections = list(
                self.active_connections.get(conversation_id, {}).keys()
            )

        stale_connections = []
        encoded_payload = jsonable_encoder(payload)

        for connection in connections:
            try:
                await connection.send_json(encoded_payload)
            except Exception:
                stale_connections.append(connection)

        for connection in stale_connections:
            await self.disconnect(conversation_id, connection)

    async def close_user_connections(
        self,
        conversation_id: int,
        user_id: int,
        payload: dict | None = None,
        close_code: int = 1008,
    ):
        async with self._lock:
            targets = [
                connection
                for connection, connection_user_id in self.active_connections.get(
                    conversation_id, {}
                ).items()
                if connection_user_id == user_id
            ]

        encoded_payload = jsonable_encoder(payload) if payload is not None else None

        for connection in targets:
            try:
                if encoded_payload is not None:
                    await connection.send_json(encoded_payload)
                await connection.close(code=close_code)
            except Exception:
                pass
            finally:
                await self.disconnect(conversation_id, connection)

    async def close_conversation(
        self,
        conversation_id: int,
        payload: dict | None = None,
        close_code: int = 1008,
    ):
        async with self._lock:
            targets = list(self.active_connections.get(conversation_id, {}).keys())

        encoded_payload = jsonable_encoder(payload) if payload is not None else None

        for connection in targets:
            try:
                if encoded_payload is not None:
                    await connection.send_json(encoded_payload)
                await connection.close(code=close_code)
            except Exception:
                pass
            finally:
                await self.disconnect(conversation_id, connection)

    async def connection_count(self, conversation_id: int) -> int:
        async with self._lock:
            return len(self.active_connections.get(conversation_id, {}))


chat_connection_manager = ChatConnectionManager()
