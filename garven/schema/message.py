from pydantic import BaseModel


class Message(BaseModel):
    message: str

    class Config:
        schema_extra = {
            "example": {
                "message": "Invalid API key.",
            }
        }
