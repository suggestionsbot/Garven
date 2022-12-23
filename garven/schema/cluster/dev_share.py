from pydantic import BaseModel


class DevShare(BaseModel):
    title: str
    description: str
