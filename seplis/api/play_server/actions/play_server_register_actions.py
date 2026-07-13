from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session

from ..models.play_server_model import MPlayServer, MPlayServerEpisode, MPlayServerMovie
from ..schemas.play_server_schemas import (
    PlayServerEpisodeCreate,
    PlayServerMovieCreate,
)


async def register_play_server_movies(
    play_server_id: str,
    data: list[PlayServerMovieCreate],
    secret: str,
    patch: bool,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        play_server = await session.scalar(
            sa.select(MPlayServer.id).where(
                MPlayServer.id == play_server_id,
                MPlayServer.secret == secret,
            )
        )
        if not play_server:
            raise exceptions.PlayServerUnknown()

        if not patch:
            await session.execute(
                sa.delete(MPlayServerMovie.__table__).where(  # type: ignore
                    MPlayServerMovie.play_server_id == play_server_id,
                )
            )
        if data:
            now = datetime.now(tz=UTC)
            stmt = sa.dialects.mysql.insert(MPlayServerMovie.__table__).values(  # type: ignore
                [
                    {
                        'play_server_id': play_server_id,
                        'movie_id': row['movie_id'],
                        'created_at': row.get('created_at', now),
                        'updated_at': now,
                    }
                    for row in data
                ]
            )
            stmt = stmt.on_duplicate_key_update(
                created_at=stmt.inserted.created_at,
                updated_at=stmt.inserted.updated_at,
            )
            try:
                await session.execute(stmt)
            except IntegrityError as err:
                from seplis.api.movie.models.movie_model import MMovie

                for row in data:
                    movie = await session.scalar(
                        sa.select(MMovie.id).where(MMovie.id == row['movie_id'])
                    )
                    if not movie:
                        raise exceptions.MovieUnknown(row['movie_id']) from err
                raise


async def delete_movie_from_play_server(
    play_server_id: str,
    movie_id: int,
    secret: str,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        play_server = await session.scalar(
            sa.select(MPlayServer.id).where(
                MPlayServer.id == play_server_id,
                MPlayServer.secret == secret,
            )
        )
        if not play_server:
            raise exceptions.PlayServerUnknown()
        await session.execute(
            sa.delete(MPlayServerMovie.__table__).where(  # type: ignore
                MPlayServerMovie.play_server_id == play_server_id,
                MPlayServerMovie.movie_id == movie_id,
            )
        )


async def register_play_server_episodes(
    play_server_id: str,
    data: list[PlayServerEpisodeCreate],
    secret: str,
    patch: bool,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        play_server = await session.scalar(
            sa.select(MPlayServer.id).where(
                MPlayServer.id == play_server_id,
                MPlayServer.secret == secret,
            )
        )
        if not play_server:
            raise exceptions.PlayServerUnknown()

        if not patch:
            await session.execute(
                sa.delete(MPlayServerEpisode.__table__).where(  # type: ignore
                    MPlayServerEpisode.play_server_id == play_server_id,
                )
            )

        if data:
            now = datetime.now(tz=UTC)
            stmt = sa.dialects.mysql.insert(MPlayServerEpisode.__table__).values(  # type: ignore
                [
                    {
                        'play_server_id': play_server_id,
                        'series_id': row['series_id'],
                        'episode_number': row['episode_number'],
                        'created_at': row.get('created_at', now),
                        'updated_at': now,
                    }
                    for row in data
                ]
            )
            stmt = stmt.on_duplicate_key_update(
                created_at=stmt.inserted.created_at,
                updated_at=stmt.inserted.updated_at,
            )
            try:
                await session.execute(stmt)
            except IntegrityError as err:
                from seplis.api.series.models.series_model import MSeries

                series_ids = []
                for row in data:
                    if row['series_id'] in series_ids:
                        continue
                    series = await session.scalar(
                        sa.select(MSeries.id).where(MSeries.id == row['series_id'])
                    )
                    if not series:
                        raise exceptions.SeriesUnknown(row['series_id']) from err
                    series_ids.append(row['series_id'])
                raise


async def delete_episode_from_play_server(
    play_server_id: str,
    series_id: int,
    episode_number: int,
    secret: str,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        play_server = await session.scalar(
            sa.select(MPlayServer.id).where(
                MPlayServer.id == play_server_id,
                MPlayServer.secret == secret,
            )
        )
        if not play_server:
            raise exceptions.PlayServerUnknown()
        await session.execute(
            sa.delete(MPlayServerEpisode.__table__).where(  # type: ignore
                MPlayServerEpisode.play_server_id == play_server_id,
                MPlayServerEpisode.series_id == series_id,
                MPlayServerEpisode.episode_number == episode_number,
            )
        )
