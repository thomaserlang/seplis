from dataclasses import asdict

import jwt
import sqlalchemy as sa

from seplis.api.contexts import AsyncSession, get_session
from seplis.api.play_server import PlayIdInfoMovie, PlayRequest
from seplis.api.play_server.models.play_server_model import (
    MPlayServer,
    MPlayServerAccess,
    MPlayServerMovie,
)


async def get_movie_play_servers(
    *, movie_id: int, user_id: int, session: AsyncSession | None = None
) -> list[PlayRequest]:
    async with get_session(session) as session:
        query = await session.scalars(
            sa.select(MPlayServer).where(
                MPlayServerAccess.user_id == user_id,
                MPlayServer.id == MPlayServerAccess.play_server_id,
                MPlayServerMovie.play_server_id == MPlayServer.id,
                MPlayServerMovie.movie_id == movie_id,
            )
        )
        return [
            PlayRequest(
                play_id=jwt.encode(
                    asdict(PlayIdInfoMovie(movie_id=movie_id)),
                    row.secret,
                    algorithm='HS256',
                ),
                play_url=row.url or '',
            )
            for row in query
        ]
