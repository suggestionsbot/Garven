from pydantic import BaseModel


class ShardInfo(BaseModel):
    latency: float
    is_currently_up: bool


class ClusterInfo(BaseModel):
    shards: dict[int, ShardInfo]


class ClusterHealth(BaseModel):
    clusters: dict[int, ClusterInfo]
