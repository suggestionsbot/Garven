from typing import Optional

from pydantic import BaseModel, Field


class ShardInfo(BaseModel):
    is_currently_up: bool
    latency: Optional[float] = Field(
        description="The shard latency, or None if the latency is currently undefined."
    )


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
                "clusters": {
                    "1": {
                        "cluster_is_up": True,
                        "shards": {
                            "1": {"latency": 3.67, "is_currently_up": True},
                            "2": {"latency": 4.23, "is_currently_up": True},
                        },
                    },
                    "2": {
                        "cluster_is_up": True,
                        "shards": {
                            "3": {"latency": 12.6, "is_currently_up": True},
                            "4": {"latency": 7.32, "is_currently_up": False},
                        },
                    },
                },
                "partial_response": False,
            }
        }
