import os

from fastapi import Header, HTTPException


async def get_auth_header(
    x_api_key: str = Header(
        title="API key for interaction",
        description="Required authorization key.",
        example='headers={"X-API-KEY": "TEST"}',
    )
):
    if x_api_key != os.environ["X-API-KEY"]:
        raise HTTPException(status_code=403, detail="X-Token header invalid")
