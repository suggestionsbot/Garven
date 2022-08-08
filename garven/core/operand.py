from __future__ import annotations

import orjson

from garven.core import Codes


class Operand:
    def __init__(self, code: Codes, text: str):
        self.code: Codes = code
        self.text: str = text

    def serialize(self) -> str:
        data: bytes = orjson.dumps({"code": self.code.value, "text": self.text})
        return data.decode("UTF-8")

    def __repr__(self):
        return self.serialize()

    @classmethod
    def deserialize(cls, data: str) -> Operand:
        data: dict = orjson.loads(data)
        return Operand(Codes.from_str(data["code"]), data["text"])

    @classmethod
    def duplicate_connection(cls, cluster_id: int) -> Operand:
        return Operand(
            Codes.DUPLICATE_CONNECTION,
            f"Closing as new connection for cluster {cluster_id} is being established",
        )

    @classmethod
    def send_message(cls, message: str) -> Operand:
        return Operand(Codes.MESSAGE, message)

    @classmethod
    def request_guild_count(cls) -> Operand:
        return Operand(Codes.GUILD_COUNT, "")
