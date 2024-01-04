from __future__ import annotations

import logging
import os
from collections import defaultdict
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from fastapi import Request
from zonis import RequestFailed

from garven.dependencies import get_auth_header
from garven.schema import Statistic, CachedItemsStatistic

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


@aggregate_router.get(
    "/cached/count",
    description="Fetch the counts of cached items in each cluster.",
    responses={200: {"model": CachedItemsStatistic}},
)
async def cached_item_counter(request: Request):
    z: Server = request.app.zonis
    partial_response = False
    raw_data: dict[str, dict[str, int]] = await z.request_all("cached_item_count")
    totals: dict[str, int] = defaultdict(lambda: 0)
    data: dict[str, dict[str, int]] = {}

    for cluster, item in raw_data.items():
        if isinstance(item, RequestFailed):
            partial_response = True
            log.error("/cached/count WS threw '%s'", item.response_data)
            continue

        data[cluster] = item

        for key, value in item.items():
            totals[key] += value

    statistic = CachedItemsStatistic(
        per_cluster=data, partial_response=partial_response, total_counts=totals
    )

    cluster_count = int(os.environ["CLUSTER_COUNT"])
    if len(data.keys()) != cluster_count:
        statistic.partial_response = True
        log.error(
            "/cached/count did not get a response from all %s clusters", cluster_count
        )

    return statistic
