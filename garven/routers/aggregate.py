from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from fastapi import Request
from zonis import RequestFailed

from garven.dependencies import get_auth_header
from garven.schema import Statistic

if TYPE_CHECKING:
    from zonis.server import Server

log = logging.getLogger(__name__)

aggregate_router = APIRouter(
    prefix="/aggregate",
    dependencies=[Depends(get_auth_header)],
    tags=["Aggregate"],
    responses={200: {"model": Statistic}},
)


@aggregate_router.get("/guilds/count", description="Fetch an up to date guild count.")
async def guild_count(request: Request):
    z: Server = request.app.zonis
    statistic = Statistic(statistic=0)
    data: dict[str, int] = await z.request_all("guild_count")
    for item in data.values():
        if isinstance(item, RequestFailed):
            statistic.partial_response = True
            log.error("/guilds/count WS threw '%s'", item.response_data)
            continue

        statistic.statistic += item

    cluster_count = int(os.environ.get("CLUSTER_COUNT", 11))
    if len(data.keys()) != cluster_count:
        statistic.partial_response = True
        log.error(
            "/guilds/count did not get a response from all %s clusters", cluster_count
        )

    return statistic
