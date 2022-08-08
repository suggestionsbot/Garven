from __future__ import annotations

from enum import IntEnum


class Codes(IntEnum):
    DUPLICATE_CONNECTION = 1
    MESSAGE = 2
    RESPONSE = 3
    GUILD_COUNT = 4

    @classmethod
    def from_str(cls, string: str) -> Codes:
        return Codes(int(string))
