from pydantic import BaseModel, Field


class SharedGuildsRequest(BaseModel):
    guild_ids: list[int] = Field(
        description="A list of guild ids to check if the bot is in."
    )


class SharedGuildsResponse(BaseModel):
    shared_guilds: list[int] = Field(
        description="A list of guild id's that the bot is also in."
    )
    partial_response: bool = Field(
        False,
        description="This will be true when the returned data "
        "does not accurately represent the entire expected dataset.",
    )
