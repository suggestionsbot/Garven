from pydantic import BaseModel, Field


class ShardInfo(BaseModel):
    latency: float
    is_currently_up: bool


class ClusterInfo(BaseModel):
    cluster_is_up: bool = Field(
        description="Ignoring individual shards, is the cluster as a whole functional"
    )
    shards: dict[str, ShardInfo] = Field(
        description="A mapping of shard id's in this cluster to ShardInfo's"
    )


class ClusterHealth(BaseModel):
    clusters: dict[str, ClusterInfo] = Field(
        description="A mapping of cluster id's to ClusterInfo"
    )
    partial_response: bool = Field(
        False,
        description="This will be true when the returned statistic "
        "does not accurately represent the entire expected dataset.",
    )

    class Config:
        schema_extra = {
            "example": {
                "1": {
                    "cluster_is_up": True,
                    "1": {"latency": 3.67, "is_currently_up": True},
                    "2": {"latency": 4.23, "is_currently_up": True},
                },
                "2": {
                    "cluster_is_up": True,
                    "3": {"latency": 12.6, "is_currently_up": True},
                    "4": {"latency": 7.32, "is_currently_up": False},
                },
                "partial_response": False,
            }
        }
