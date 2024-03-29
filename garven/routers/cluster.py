from __future__ import annotations

import logging
import os
from copy import deepcopy
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from fastapi import Request
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_204_NO_CONTENT
from zonis import RequestFailed, UnknownClient

from garven.calculate_dev_cluster import get_dev_cluster
from garven.dependencies import get_auth_header
from garven.schema import Message
from garven.schema.cluster import ClusterHealth, DevShare, ClusterWSInfo

if TYPE_CHECKING:
    from zonis.server import Server

log = logging.getLogger(__name__)

cluster_router = APIRouter(
    prefix="/cluster",
    dependencies=[Depends(get_auth_header)],
    tags=["Clusters"],
)


@cluster_router.get("/status", response_model=ClusterHealth)
async def cluster_status(request: Request):
    partial_response = False
    z: Server = request.app.zonis
    d = await z.request_all("cluster_status")
    for k, item in deepcopy(d).items():
        if isinstance(item, RequestFailed):
            partial_response = True
            log.error("/cluster/status WS threw '%s'", item.response_data)
            d.pop(k)
            continue

    if len(d.values()) != int(os.environ.get("CLUSTER_COUNT", 11)):
        partial_response = True

    return ClusterHealth(clusters=d, partial_response=partial_response)


@cluster_router.get("/latency/ws", response_model=ClusterWSInfo)
async def cluster_status(request: Request):
    partial_response = False
    z: Server = request.app.zonis
    d: dict[str, dict[str, str]] = await z.request_all("cluster_ws_status")
    shard_data = {}
    for c, item in deepcopy(d).items():
        if isinstance(item, RequestFailed):
            partial_response = True
            log.error("/cluster/latency/ws WS threw '%s'", item.response_data)
            continue

        if item is None:
            partial_response = True
            log.error("/cluster/latency/ws had a null value from %s", c)
            continue

        for shard_id, value in item.items():
            shard_data[shard_id] = value

    if len(shard_data.values()) != int(os.environ.get("TOTAL_SHARDS")):
        partial_response = True

    return ClusterWSInfo(shards=shard_data, partial_response=partial_response)  # noqa


@cluster_router.post(
    "/notify_devs", status_code=204, responses={503: {"model": Message}}
)
async def notify_devs(request: Request, data: DevShare):
    try:
        z: Server = request.app.zonis
        await z.request(
            "share_with_devs",
            client_identifier=get_dev_cluster(),
            title=data.title,
            description=data.description,
            sender=data.sender,
        )
    except UnknownClient:
        return JSONResponse(
            status_code=503,
            content={"message": "The required cluster is not currently connected."},
        )

    return Response(status_code=HTTP_204_NO_CONTENT)
