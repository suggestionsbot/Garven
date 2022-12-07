from typing import Optional, Literal

from pydantic import BaseModel, Field


class IdentifyDataPacket(BaseModel):
    secret_key: str = Field(
        description="The shared secret key for authentication purposes"
    )
    override_key: Optional[str] = Field(
        description="An optional override key to allow for replacing existing connections"
    )


class IdentifyPacket(BaseModel):
    identifier: str = Field(description="Your connections identifier.")
    type: Literal["IDENTIFY"]
    data: IdentifyDataPacket
