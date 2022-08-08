import asyncio
import logging
import os
from typing import Literal

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from garven import tags
from garven.core import ConnectionManager, Operand
from garven.schema import Message

nav_links: list[dict[Literal["name", "url"], str]] = [
    {"name": "Home", "url": "/"},
]

app = FastAPI(
    title="Garven",
    description="A websocket MITM for suggestions bot cluster IPC.",
    version="0.1.0",
    terms_of_service="https://suggestions.gg/terms",
    contact={
        "name": "Suggestions Bot",
        "url": "https://suggestions.gg/contact",
    },
    responses={403: {"model": Message}},
    openapi_tags=tags.tags_metadata,
)
log = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
manager = ConnectionManager()

# Delayed import for manager exporting to work
from garven import routers

app.include_router(routers.aggregate_router)


@app.get("/", response_class=HTMLResponse, tags=["General"])
async def get(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "nav_links": nav_links}
    )


@app.websocket("/ws/cluster/{cluster_id}")
async def websocket_endpoint(websocket: WebSocket, cluster_id: int):
    try:
        await websocket.accept()

        try:
            connection_state: bytes = await websocket.receive_bytes()
        except KeyError:
            # Invalid connection
            return
        connection_state: dict = manager.convert_from_bytes(connection_state)
        api_key = connection_state.get("X-API-KEY")
        if not api_key or api_key != os.environ["X-API-KEY"]:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # if cluster_id in manager.active_connections:
        #     await websocket.close(
        #         code=status.WS_1008_POLICY_VIOLATION,
        #         reason=Operand.duplicate_connection(cluster_id).serialize(),
        #     )
        #     log.info("Rejected duplicate connection for cluster %s", cluster_id)
        #     return

        await manager.register(cluster_id, websocket)
        await manager.broadcast(
            Operand.send_message(f"Cluster {cluster_id} has joined").serialize()
        )
        try:
            while True:
                await asyncio.sleep(0.5)
        except WebSocketDisconnect as e:
            manager.disconnect(cluster_id)
            await manager.broadcast(
                Operand.send_message(f"Cluster {cluster_id} left the chat").serialize()
            )
            raise e
    except Exception as e:
        manager.disconnect(cluster_id)
        raise e
