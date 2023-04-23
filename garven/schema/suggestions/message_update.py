from pydantic import BaseModel


class MessageUpdate(BaseModel):
    time_after: float
    guild_icon_url: str
    user_display_name: str
    user_display_avatar: str
    guild_name: str
