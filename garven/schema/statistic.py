from pydantic import BaseModel, Field


class Statistic(BaseModel):
    statistic: int
    partial_response: bool = Field(
        False,
        description="This will be true when the returned statistic does not accurately represent the entire dataset.",
    )

    class Config:
        schema_extra = {"example": {"statistic": 500, "partial_response": False}}
