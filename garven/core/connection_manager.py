import logging
from typing import Dict, Union, Optional

import orjson
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK

from garven.core import Operand

log = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def register(self, cluster_id: int, websocket: WebSocket):
        log.info("Registered a connection for cluster %s", cluster_id)
        if cluster_id in self.active_connections:
            await self.active_connections[cluster_id].close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=Operand.duplicate_connection(cluster_id).serialize(),
            )

        self.active_connections[cluster_id] = websocket

    def disconnect(self, cluster_id: int):
        log.info("Disconnect a connection for cluster %s", cluster_id)
        self.active_connections.pop(cluster_id, None)

    async def send_to_cluster(
        self, cluster_id: int, message: Union[str, Dict, Operand]
    ):
        if isinstance(message, Operand):
            message = message.serialize()
        websocket: WebSocket = self.active_connections.get(cluster_id)
        if not websocket:
            raise ValueError(f"{cluster_id} does not have an active connection")

        await websocket.send_bytes(self.convert_to_bytes(message))

    async def broadcast(
        self, message: Union[str, Dict, Operand], *, expect_response: bool = False
    ) -> Optional[list[Operand]]:
        if isinstance(message, Operand):
            message = message.serialize()

        to_pop: list[int] = []
        for cluster_id, connection in self.active_connections.items():
            try:
                await connection.send_bytes(self.convert_to_bytes(message))
            except ConnectionClosedOK:
                to_pop.append(cluster_id)

        if not expect_response:
            for entry in to_pop:
                self.disconnect(entry)
            return

        resp: list[Operand] = []
        for cluster_id, connection in self.active_connections.items():
            try:
                value = await connection.receive_text()
            except WebSocketDisconnect:
                to_pop.append(cluster_id)
            else:
                resp.append(Operand(**self.dict_from_str(value)))

        for entry in to_pop:
            self.disconnect(entry)

        return resp

    @staticmethod
    def convert_to_bytes(message: Union[str, Dict]) -> bytes:
        if isinstance(message, dict):
            return orjson.dumps(message)

        return bytes(message, "UTF-8")

    @staticmethod
    def convert_from_bytes(data: bytes) -> dict:
        return orjson.loads(data)

    @staticmethod
    def dict_from_str(data: str) -> dict:
        return orjson.loads(data)
