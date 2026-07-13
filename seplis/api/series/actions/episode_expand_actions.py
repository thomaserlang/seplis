import asyncio

import sqlalchemy as sa

from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.user import UserAuthenticated

from ..models.episode_model import MEpisodeWatched, episode_watched_mapper
from ..schemas.episode_schemas import Episode, EpisodeWatched, UserCanWatch


async def expand_episodes(
    expand: list[str] | None,
    user: UserAuthenticated | None,
    series_id: int,
    episodes: list[Episode],
) -> None:
    if not expand:
        return
    if not user:
        raise exceptions.NotSignedInException()
    expand_tasks = []
    if 'user_watched' in expand:
        expand_tasks.append(
            expand_user_watched(
                series_id=series_id,
                user_id=user.id,
                episodes=episodes,
            )
        )
    if 'user_can_watch' in expand:
        expand_tasks.append(
            expand_user_can_watch(
                series_id=series_id,
                user_id=user.id,
                episodes=episodes,
            )
        )
    if expand_tasks:
        await asyncio.gather(*expand_tasks)


async def expand_user_watched(
    series_id: int,
    user_id: int,
    episodes: list[Episode],
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        episodes_by_number: dict[int, Episode] = {}
        for episode in episodes:
            episode.user_watched = EpisodeWatched(episode_number=episode.number)
            episodes_by_number[episode.number] = episode
        result = await session.scalars(
            sa.select(
                MEpisodeWatched,
            ).where(
                MEpisodeWatched.user_id == user_id,
                MEpisodeWatched.series_id == series_id,
                MEpisodeWatched.episode_number.in_(set(episodes_by_number.keys())),
            )
        )
        for episode_watched in result:
            episodes_by_number[
                episode_watched.episode_number
            ].user_watched = episode_watched_mapper(episode_watched)


async def expand_user_can_watch(
    series_id: int,
    user_id: int,
    episodes: list[Episode],
    session: AsyncSession | None = None,
) -> None:
    from seplis.api.play_server.models.play_server_model import (
        MPlayServerAccess,
        MPlayServerEpisode,
    )

    async with get_session(session) as session:
        episodes_by_number: dict[int, Episode] = {}
        for episode in episodes:
            episode.user_can_watch = UserCanWatch()
            episodes_by_number[episode.number] = episode
        result = await session.scalars(
            sa.select(
                MPlayServerEpisode,
            )
            .where(
                MPlayServerAccess.user_id == user_id,
                MPlayServerEpisode.play_server_id == MPlayServerAccess.play_server_id,
                MPlayServerEpisode.series_id == series_id,
                MPlayServerEpisode.episode_number.in_(set(episodes_by_number.keys())),
            )
            .group_by(MPlayServerEpisode.episode_number)
        )
        for episode_play_server in result:
            episodes_by_number[
                episode_play_server.episode_number
            ].user_can_watch = UserCanWatch(on_play_server=True)
