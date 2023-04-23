from __future__ import annotations

import datetime
import logging
from enum import Enum
from typing import TYPE_CHECKING, Literal, Union, Optional, cast

import disnake
from alaric import AQ
from alaric.comparison import EQ
from alaric.logical import AND
from disnake import Embed

log = logging.getLogger(__name__)
"""Class copied from the base suggestions bot repos"""


class SuggestionState(Enum):
    pending = 0
    approved = 1
    rejected = 2
    cleared = 3

    @staticmethod
    def from_str(value: str) -> SuggestionState:
        mappings = {
            "pending": SuggestionState.pending,
            "approved": SuggestionState.approved,
            "rejected": SuggestionState.rejected,
            "cleared": SuggestionState.cleared,
        }
        return mappings[value.lower()]

    def as_str(self) -> str:
        if self is SuggestionState.rejected:
            return "rejected"

        elif self is SuggestionState.approved:
            return "approved"

        elif self is SuggestionState.cleared:
            return "cleared"

        return "pending"


class Colors:
    """A class to keep colors in a single place."""

    error = disnake.Color.from_rgb(214, 48, 49)
    embed_color = disnake.Color.from_rgb(255, 214, 99)
    beta_required = disnake.Color.from_rgb(7, 0, 77)
    pending_suggestion = disnake.Color.from_rgb(255, 214, 99)
    approved_suggestion = disnake.Color.from_rgb(0, 230, 64)
    rejected_suggestion = disnake.Color.from_rgb(207, 0, 15)


class Suggestion:
    """An abstract wrapper encapsulating all suggestion functionality."""

    def __init__(
        self,
        _id: str,
        guild_id: int,
        suggestion: str,
        suggestion_author_id: int,
        created_at: datetime.datetime,
        state: Union[
            Literal["open", "approved", "rejected", "cleared"],
            SuggestionState,
        ],
        *,
        total_up_votes: Optional[int] = None,
        total_down_votes: Optional[int] = None,
        up_voted_by: Optional[list[int]] = None,
        down_voted_by: Optional[list[int]] = None,
        channel_id: Optional[int] = None,
        message_id: Optional[int] = None,
        resolved_by: Optional[int] = None,
        resolution_note: Optional[str] = None,
        resolved_at: Optional[datetime.datetime] = None,
        image_url: Optional[str] = None,
        uses_views_for_votes: bool = False,
        is_anonymous: bool = False,
        **kwargs,
    ):
        """
        Parameters
        ----------
        guild_id: int
            The guild this suggestion is in
        suggestion: str
            The suggestion content itself
        _id: str
            The id of the suggestion
        suggestion_author_id: int
            The id of the person who created the suggestion
        created_at: datetime.datetime
            When this suggestion was created
        state: Union[Literal["open", "approved", "rejected"], SuggestionState]
            The current state of the suggestion itself
        Other Parameters
        ----------------
        resolved_by: Optional[int]
            Who changed the final state of this suggestion
        resolution_note: Optional[str]
            A note to add to the suggestion on resolve
        resolved_at: Optional[datetime.datetime]
            When this suggestion was resolved
        channel_id: Optional[int]
            The channel this suggestion is currently in
        message_id: Optional[int]
            The current message ID. This could be the suggestion
            or the log channel message.
        total_up_votes: Optional[int]
            How many up votes this had when closed
            This is based off the old reaction system.
        total_down_votes: Optional[int]
            How many down votes this had when closed
            This is based off the old reaction system.
        up_voted_by: Optional[list[int]]
            A list of people who up voted this suggestion
            This is based off the new button system
        up_voted_by: Optional[list[int]]
            A list of people who up voted this suggestion
            This is based off the new button system
        down_voted_by: Optional[list[int]]
            A list of people who down voted this suggestion
            This is based off the new button system
        image_url: Optional[str]
            An optional url for an image attached to the suggestion
        uses_views_for_votes: bool
            A simple flag to make backwards compatibility easier.
            Defaults to `False` as all old suggestions will use this
            value since they don't have the field in the database
        is_anonymous: bool
            Whether or not this suggestion
            should be displayed anonymous
        """
        self._id: str = _id
        self.guild_id: int = guild_id
        self.suggestion: str = suggestion
        self.suggestion_author_id: int = suggestion_author_id
        self.created_at: datetime.datetime = created_at
        self.state: SuggestionState = (
            SuggestionState.from_str(state)
            if not isinstance(state, SuggestionState)
            else state
        )
        self.uses_views_for_votes: bool = uses_views_for_votes

        self.channel_id: Optional[int] = channel_id
        self.message_id: Optional[int] = message_id
        self.resolved_by: Optional[int] = resolved_by
        self.resolved_at: Optional[datetime.datetime] = resolved_at
        self.resolution_note: Optional[str] = resolution_note
        self._total_up_votes: Optional[int] = total_up_votes
        self._total_down_votes: Optional[int] = total_down_votes
        self.up_voted_by: set[int] = set(up_voted_by) if up_voted_by else set()
        self.down_voted_by: set[int] = set(down_voted_by) if down_voted_by else set()
        self.image_url: Optional[str] = image_url
        self.is_anonymous: bool = is_anonymous

    @property
    def total_up_votes(self) -> Optional[int]:
        if self._total_up_votes:
            return self._total_up_votes

        if not self.uses_views_for_votes:
            return None

        return len(self.up_voted_by)

    @property
    def total_down_votes(self) -> Optional[int]:
        if self._total_down_votes:
            return self._total_down_votes

        if not self.uses_views_for_votes:
            return None

        return len(self.down_voted_by)

    @property
    def color(self) -> disnake.Color:
        if self.state is SuggestionState.rejected:
            return Colors.rejected_suggestion

        elif self.state is SuggestionState.approved:
            return Colors.approved_suggestion

        return Colors.pending_suggestion

    @property
    def suggestion_id(self) -> str:
        return self._id

    def as_filter(self) -> dict:
        return {"_id": self.suggestion_id}

    def as_dict(self) -> dict:
        data = {
            "guild_id": self.guild_id,
            "state": self.state.as_str(),
            "suggestion": self.suggestion,
            "_id": self.suggestion_id,
            "suggestion_author_id": self.suggestion_author_id,
            "created_at": self.created_at,
            "uses_views_for_votes": self.uses_views_for_votes,
            "is_anonymous": self.is_anonymous,
        }

        if self.resolved_by:
            data["resolved_by"] = self.resolved_by
            data["resolution_note"] = self.resolution_note

        if self.resolved_at:
            data["resolved_at"] = self.resolved_at

        if self.message_id:
            data["message_id"] = self.message_id
            data["channel_id"] = self.channel_id

        if self.uses_views_for_votes:
            data["up_voted_by"] = list(self.up_voted_by)
            data["down_voted_by"] = list(self.down_voted_by)

        else:
            data["total_up_votes"] = self._total_up_votes
            data["total_down_votes"] = self._total_down_votes

        if self.image_url is not None:
            data["image_url"] = self.image_url

        return data

    async def as_embed(
        self,
        *,
        display_name: str,
        display_avatar: str,
        guild_name: str,
        guild_icon_url: str,
    ) -> Embed:
        if self.resolved_by:
            return await self._as_resolved_embed(
                display_name=display_name,
                guild_name=guild_name,
                guild_icon_url=guild_icon_url,
            )

        embed: Embed = Embed(
            description=f"**Submitter**\n{display_name}\n\n"
            f"**Suggestion**\n{self.suggestion}",
            colour=self.color,
            timestamp=bot.state.now,
        )
        if not self.is_anonymous:
            embed.set_thumbnail(display_avatar)
            embed.set_footer(
                text=f"User ID: {self.suggestion_author_id} | sID: {self.suggestion_id}"
            )
        else:
            embed.set_footer(text=f"sID: {self.suggestion_id}")

        if self.image_url:
            embed.set_image(self.image_url)

        if self.uses_views_for_votes:
            results = (
                f"**Results so far**\n{await bot.suggestion_emojis.default_up_vote()}: **{self.total_up_votes}**\n"
                f"{await bot.suggestion_emojis.default_down_vote()}: **{self.total_down_votes}**"
            )
            embed.description += f"\n\n{results}"

        return embed

    async def _as_resolved_embed(
        self,
        *,
        display_name: str,
        guild_icon_url: str,
        guild_name: str,
    ) -> Embed:
        results = (
            f"**Results**\n{await bot.suggestion_emojis.default_up_vote()}: **{self.total_up_votes}**\n"
            f"{await bot.suggestion_emojis.default_down_vote()}: **{self.total_down_votes}**"
        )

        text = "Approved" if self.state == SuggestionState.approved else "Rejected"
        embed = Embed(
            description=f"{results}\n\n**Suggestion**\n{self.suggestion}\n\n"
            f"**Submitter**\n{display_name}\n\n"
            f"**{text} By**\n<@{self.resolved_by}>\n\n",
            colour=self.color,
            timestamp=bot.state.now,
        ).set_footer(text=f"sID: {self.suggestion_id}")

        embed.set_author(name=guild_name, icon_url=guild_icon_url)

        if self.resolution_note:
            embed.description += f"**Response**\n{self.resolution_note}"

        if self.image_url:
            embed.set_image(self.image_url)

        return embed
