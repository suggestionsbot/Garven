from __future__ import annotations

import logging
import os
from copy import deepcopy
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from fastapi import Request
from zonis import RequestFailed

from garven.dependencies import get_auth_header
from garven.schema.cluster import ClusterHealth

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
    for k, item in deepcopy(d.items()):
        if isinstance(item, RequestFailed):
            partial_response = True
            log.error("/cluster/status WS threw '%s'", item.response_data)
            d.pop(k)
            continue

    if len(d.values()) != int(os.environ.get("CLUSTER_COUNT", 6)):
        partial_response = True

    return ClusterHealth(clusters=d, partial_response=partial_response)
