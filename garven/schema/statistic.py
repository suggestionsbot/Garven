from pydantic import BaseModel


class Statistic(BaseModel):
    statistic: int

    class Config:
        schema_extra = {
            "example": {
                "statistic": 500,
            }
        }
