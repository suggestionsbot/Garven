from fastapi import APIRouter, Depends

from garven.dependencies import get_auth_header
from garven.schema import Statistic
from main import manager
from garven.core import Operand, Codes

aggregate_router = APIRouter(
    prefix="/aggregate",
    dependencies=[Depends(get_auth_header)],
    tags=["Aggregate"],
    responses={200: {"model": Statistic}},
)


@aggregate_router.get("/guilds/count", description="Fetch an up to date guild count.")
async def guild_count():
    total_guilds: int = 0
    data: list[Operand] = await manager.broadcast(
        Operand.request_guild_count(), expect_response=True
    )
    for cluster in data:
        assert cluster.code == Codes.RESPONSE
        total_guilds += int(cluster.text)

    return Statistic(statistic=total_guilds)
