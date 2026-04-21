import asyncio

import sqlalchemy as sa

from .. import exceptions, models, schemas
from ..database import auto_session
from ..dependencies import AsyncSession


async def expand_episodes(
    expand: list[str], user: schemas.User, series_id: int, episodes: list[schemas.Episode]
) -> None:
    if not expand:
        return
    if not user:
        raise exceptions.Not_signed_in_exception()
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


@auto_session
async def expand_user_watched(
    series_id: int, user_id: int, episodes: list[schemas.Episode], session: AsyncSession
) -> None:
    _episodes: dict[int, schemas.Episode] = {}
    for episode in episodes:
        episode.user_watched = schemas.Episode_watched(episode_number=episode.number)
        _episodes[episode.number] = episode
    result: list[models.MEpisodeWatched] = await session.scalars(
        sa.select(
            models.MEpisodeWatched,
        ).where(
            models.MEpisodeWatched.user_id == user_id,
            models.MEpisodeWatched.series_id == series_id,
            models.MEpisodeWatched.episode_number.in_(set(_episodes.keys())),
        )
    )
    for episode_watched in result:
        _episodes[
            episode_watched.episode_number
        ].user_watched = schemas.Episode_watched.model_validate(episode_watched)


@auto_session
async def expand_user_can_watch(
    series_id: int, user_id: int, episodes: list[schemas.Episode], session: AsyncSession
) -> None:
    _episodes: dict[int, schemas.Episode] = {}
    for episode in episodes:
        episode.user_can_watch = schemas.User_can_watch()
        _episodes[episode.number] = episode
    result: list[models.MPlayServerEpisode] = await session.scalars(
        sa.select(
            models.MPlayServerEpisode,
        )
        .where(
            models.MPlayServerAccess.user_id == user_id,
            models.MPlayServerEpisode.play_server_id
            == models.MPlayServerAccess.play_server_id,
            models.MPlayServerEpisode.series_id == series_id,
            models.MPlayServerEpisode.episode_number.in_(set(_episodes.keys())),
        )
        .group_by(models.MPlayServerEpisode.episode_number)
    )
    for episode_watched in result:
        _episodes[episode_watched.episode_number].user_can_watch.on_play_server = True
