import datetime

from pydantic import BaseModel, Field


class RateLimited(BaseModel):
    retry_after: float = Field(
        description="How many seconds before you can retry this route."
    )
    resets_at: datetime.datetime = Field(
        description="The exact datetime this ratelimit expires."
    )
