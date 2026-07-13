from dataclasses import asdict

import jwt
import sqlalchemy as sa

from seplis.api.contexts import AsyncSession, get_session
from seplis.api.play_server import PlayIdInfoEpisode, PlayRequest
from seplis.api.play_server.models.play_server_model import (
    MPlayServer,
    MPlayServerAccess,
    MPlayServerEpisode,
)


async def get_episode_play_servers(
    series_id: int,
    episode_number: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> list[PlayRequest]:
    async with get_session(session) as session:
        rows = await session.scalars(
            sa.select(MPlayServer).where(
                MPlayServerAccess.user_id == user_id,
                MPlayServer.id == MPlayServerAccess.play_server_id,
                MPlayServerEpisode.play_server_id == MPlayServer.id,
                MPlayServerEpisode.series_id == series_id,
                MPlayServerEpisode.episode_number == episode_number,
            )
        )
        return [
            PlayRequest(
                play_id=jwt.encode(
                    asdict(PlayIdInfoEpisode(series_id=series_id, number=episode_number)),
                    row.secret,
                    algorithm='HS256',
                ),
                play_url=row.url or '',
            )
            for row in rows
        ]
