from pydantic import BaseModel, Field


class Statistic(BaseModel):
    statistic: int
    partial_response: bool = Field(
        False,
        description="This will be true when the returned statistic "
        "does not accurately represent the entire expected dataset.",
    )

    class Config:
        schema_extra = {"example": {"statistic": 500, "partial_response": False}}


class CachedItemsStatistic(BaseModel):
    total_counts: dict[str, int]
    per_cluster: dict[str, dict[str, int]]
    partial_response: bool = Field(
        False,
        description="This will be true when the returned statistic "
        "does not accurately represent the entire expected dataset.",
    )
