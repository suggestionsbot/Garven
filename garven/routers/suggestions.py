from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import httpx
from alaric import Document, AQ
from alaric.comparison import EQ
from fastapi import APIRouter, Depends
from fastapi import Request
from starlette import status
from starlette.responses import Response

from garven.dependencies import get_auth_header
from garven.schema import Message
from garven.schema.suggestions import MessageUpdate

if TYPE_CHECKING:
    from garven.objects import Suggestion

log = logging.getLogger(__name__)

suggestion_router = APIRouter(
    prefix="/suggestions",
    dependencies=[Depends(get_auth_header)],
    tags=["Suggestions"],
)
pending_edits: set[str] = set()


async def message_update(
    *,
    document: Document,
    suggestion_id: str,
    data: MessageUpdate,
    ac: httpx.AsyncClient,
):
    await asyncio.sleep(data.time_after)
    suggestion: Suggestion = await document.find(AQ(EQ("_id", suggestion_id)))
    channel_id: int = suggestion.channel_id
    message_id: int = suggestion.message_id
    embed = await suggestion.as_embed(
        display_name=data.user_display_name,
        display_avatar=data.user_display_avatar,
        guild_name=data.guild_name,
        guild_icon_url=data.guild_icon_url,
    )
    embed = embed.to_dict()

    for _ in range(5):
        resp = await ac.patch(
            f"https://discord.com/api/v10/channels/{channel_id}/messages/{message_id}",
            json=embed,
        )
        if resp.status_code != 200:
            await asyncio.sleep(2.5)
            continue

        break

    else:
        # TODO Fire off something to the cluster saying as such maybe?
        log.error(
            "Failed to update message for suggestion %s", suggestion.suggestion_id
        )

    pending_edits.discard(suggestion_id)


@suggestion_router.post(
    "/{suggestion_id}/message/update",
    description="Schedules a suggestion for delayed message editing.",
    status_code=204,
    responses={503: {"model": Message}},
)
async def update_message(request: Request, suggestion_id: str, data: MessageUpdate):
    if suggestion_id not in pending_edits:
        pending_edits.add(suggestion_id)
        asyncio.create_task(
            message_update(
                data=data,
                document=request.app.suggestions_document,
                suggestion_id=suggestion_id,
                ac=request.app.ac,
            )
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
