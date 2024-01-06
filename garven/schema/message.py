from pydantic import BaseModel


class Message(BaseModel):
    message: str

    class Config:
        schema_extra = {
            "example": {
                "message": "Invalid API key.",
            }
        }


class ShardInfo(BaseModel):
    shard_id: str
    cluster_id: str

    class Config:
        schema_extra = {"example": {"shard_id": "9", "cluster_id": "1"}}
