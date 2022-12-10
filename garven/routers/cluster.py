from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from fastapi import Request

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
    z: Server = request.app.zonis
    d = await z.request_all("cluster_status")

    if len(d.values()) != int(os.environ.get("CLUSTER_COUNT", 6)):
        d["partial_response"] = True
    else:
        d["partial_response"] = False

    return d
