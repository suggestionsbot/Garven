from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Query
from fastapi import Request
from starlette import status
from starlette.responses import Response, JSONResponse
from zonis import RequestFailed

from garven.dependencies import get_auth_header
from garven.schema import Message
from garven.schema.premium import SharedGuildsRequest, SharedGuildsResponse

if TYPE_CHECKING:
    from zonis.server import Server

log = logging.getLogger(__name__)

premium_router = APIRouter(
    prefix="/premium",
    dependencies=[Depends(get_auth_header)],
    tags=["Premium"],
)


@premium_router.post(
    "/{user_id}/refresh",
    description="Refresh premium data for the given user.",
    status_code=204,
    responses={503: {"model": Message}},
)
async def refresh_premium(request: Request, user_id: int):
    z: Server = request.app.zonis
    data: dict = await z.request_all("refresh_premium", user_id=user_id)
    for item in data.values():
        if isinstance(item, RequestFailed):
            log.error("/{user_id}/refresh WS threw '%s'", item.response_data)
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"message": "Some bot clusters failed to refresh correctly."},
            )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@premium_router.get(
    "/{user_id}/guilds/shared",
    description="Fetch guilds that the user shares with the bot.",
    response_model=SharedGuildsResponse,
    responses={400: {"model": Message}},
)
async def fetch_shared_guilds(
    request: Request,
    user_id: int,
    guild_ids: str = Query(description="Comma seperated list of guild ids."),
):
    try:
        guild_ids = guild_ids.split(",")
        guild_ids = list(map(int, guild_ids))
    except:
        return Response(Message(message="Invalid guild_ids param"), status_code=400)

    z: Server = request.app.zonis
    d: dict[str, list[int]] = await z.request_all("shared_guilds", guild_ids=guild_ids)
    data = SharedGuildsResponse(shared_guilds=[])
    for k, item in d.items():
        if isinstance(item, RequestFailed):
            data.partial_response = True
            log.error("/{user_id}/guilds/shared WS threw '%s'", item.response_data)
            d.pop(k)
            continue

        if item:
            data.shared_guilds.extend(item)

    return data
