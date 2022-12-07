import asyncio
import json
import logging
from json import JSONDecodeError
from typing import Literal

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_204_NO_CONTENT
from starlette.templating import Jinja2Templates
from zonis import BaseZonisException, Packet
from zonis.server import Server

from garven import tags
from garven.schema import Message, ws
from garven import routers

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s | %(asctime)s | %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S %p",
)

nav_links: list[dict[Literal["name", "url"], str]] = [
    {"name": "Home", "url": "/"},
    {"name": "Docs", "url": "/docs"},
    {"name": "Redoc", "url": "/redoc"},
]

app = FastAPI(
    title="Garven",
    version="0.2.0",
    terms_of_service="https://suggestions.gg/terms",
    contact={
        "name": "Suggestions Bot",
        "url": "https://suggestions.gg/contact",
    },
    responses={403: {"model": Message}},
    openapi_tags=tags.tags_metadata,
    description="Messages are sorted in order based on ID, "
    "that is a message with an ID of 5 is newer then a message with an ID of 4.\n\n"
    "Message ID's are generated globally and not per conversation.\n\n"
    "**Global Rate-limit**\n\nAll requests are rate-limited globally by client IP and "
    "are throttled to 25 requests every 10 seconds.\n\n\n",
)
log = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.zonis = Server(using_fastapi_websockets=True)


app.include_router(routers.aggregate_router)
# Get real IP
# request.headers.get("X-Forwarded-For", 1)


@app.get("/", response_class=HTMLResponse, tags=["General"])
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "nav_links": nav_links}
    )


@app.get(
    "/ws",
    name="Entrypoint",
    description="Establish a websocket connection to this URL."
    "\n\n*This route describes data that can be returned via the websocket and is not an existing API route.*\n\n"
    "**WS Error Codes**\n\nThese can be served as the disconnect code or WS payload response.\n"
    """
| Code | Location    | Description | 
|------|-------------|-------------|
| 4001 | WS Response | Your WS payload was not valid JSON | 
| 4100 | Close Code  | Invalid secret key |
| 4101 | Close Code  | You failed to identify correctly |
| 4102 | Close Code  | You attempted to override an existing connection without valid override authorization |
""",
    tags=["Websocket"],
    status_code=101,
)
async def websocket_documentation(data: ws.IdentifyPacket):
    return Response(status_code=HTTP_204_NO_CONTENT)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    d: str = await websocket.receive_text()
    try:
        data: Packet = json.loads(d)
        identifier = await app.zonis.parse_identify(data, websocket)
    except (BaseZonisException, JSONDecodeError):
        await websocket.close(code=4101, reason="Identify failed")
        return

    try:
        await asyncio.Future()
    except WebSocketDisconnect:
        app.zonis.disconnect(identifier)
