from datetime import UTC, date, datetime
from typing import cast

import sqlalchemy as sa
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.engine import RowMapping

from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.page_cursor import PageCursor, PageCursorQuery, page_cursor
from seplis.api.user import UserAuthenticated

from ..models.episode_model import (
    MEpisode,
    MEpisodeLastWatched,
    MEpisodeWatched,
    MEpisodeWatchedHistory,
)
from ..schemas.episode_schemas import Episode, EpisodeWatched, EpisodeWatchedIncrement
from .episode_expand_actions import expand_episodes, expand_user_can_watch
from .series_mapping import episode_row_mapper, episode_watched_row_mapper


def episode_page_mapper(row: RowMapping) -> Episode:
    return episode_row_mapper(row)


async def get_episode(
    series_id: int,
    number: int,
    expand: list[str] | None,
    user: UserAuthenticated | None,
    session: AsyncSession | None = None,
) -> Episode:
    async with get_session(session) as session:
        episode = (
            (
                await session.execute(
                    sa.select(MEpisode.__table__).where(
                        MEpisode.series_id == series_id,
                        MEpisode.number == number,
                    )
                )
            )
            .mappings()
            .first()
        )
        if not episode:
            raise exceptions.NotFound('Unknown episode')
        result = episode_row_mapper(episode)
        await expand_episodes(
            episodes=[result], series_id=series_id, user=user, expand=expand
        )
        return result


async def delete_episode(
    series_id: int, number: int, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.delete(cast(sa.Table, MEpisode.__table__)).where(
                MEpisode.series_id == series_id,
                MEpisode.number == number,
            )
        )


async def get_episodes(
    series_id: int,
    season: int | None,
    episode: int | None,
    number: int | None,
    air_date: date | None,
    air_date_ge: date | None,
    air_date_le: date | None,
    expand: list[str] | None,
    user: UserAuthenticated | None,
    page_query: PageCursorQuery,
    session: AsyncSession | None = None,
) -> PageCursor[Episode]:
    query = (
        sa.select(MEpisode.__table__)
        .where(MEpisode.series_id == series_id)
        .order_by(MEpisode.number)
    )
    if season:
        query = query.where(MEpisode.season == season)
    if episode:
        query = query.where(MEpisode.episode == episode)
    if number:
        query = query.where(MEpisode.number == number)
    if air_date:
        query = query.where(MEpisode.air_date == air_date)
    if air_date_ge:
        query = query.where(MEpisode.air_date >= air_date_ge)
    if air_date_le:
        query = query.where(MEpisode.air_date <= air_date_le)

    page = await page_cursor(
        session=session,
        query=query,
        page_query=page_query,
        count_total=False,
        record_mapper=episode_page_mapper,
    )
    await expand_episodes(
        episodes=page.records, series_id=series_id, user=user, expand=expand
    )
    return page


async def get_watched(
    series_id: int,
    episode_number: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> EpisodeWatched:
    async with get_session(session) as session:
        watched = (
            (
                await session.execute(
                    sa.select(MEpisodeWatched.__table__).where(
                        MEpisodeWatched.user_id == user_id,
                        MEpisodeWatched.series_id == series_id,
                        MEpisodeWatched.episode_number == episode_number,
                    )
                )
            )
            .mappings()
            .first()
        )
        if watched:
            return episode_watched_row_mapper(watched)
        return EpisodeWatched(episode_number=episode_number)


async def increment_watched(
    series_id: int,
    episode_number: int,
    user_id: int,
    data: EpisodeWatchedIncrement | None,
    session: AsyncSession | None = None,
) -> EpisodeWatched:
    async with get_session(session) as session:
        await increment_episode_watched(
            session=session,
            user_id=user_id,
            series_id=series_id,
            episode_number=episode_number,
            data=data or {},
        )
        watched = (
            (
                await session.execute(
                    sa.select(MEpisodeWatched.__table__).where(
                        MEpisodeWatched.user_id == user_id,
                        MEpisodeWatched.series_id == series_id,
                        MEpisodeWatched.episode_number == episode_number,
                    )
                )
            )
            .mappings()
            .first()
        )
        await session.commit()
        if not watched:
            return EpisodeWatched(episode_number=episode_number)
        return episode_watched_row_mapper(watched)


async def decrement_watched(
    series_id: int,
    episode_number: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> EpisodeWatched:
    async with get_session(session) as session:
        await decrement_episode_watched(
            session=session,
            user_id=user_id,
            series_id=series_id,
            episode_number=episode_number,
        )
        watched = (
            (
                await session.execute(
                    sa.select(MEpisodeWatched.__table__).where(
                        MEpisodeWatched.user_id == user_id,
                        MEpisodeWatched.series_id == series_id,
                        MEpisodeWatched.episode_number == episode_number,
                    )
                )
            )
            .mappings()
            .first()
        )
        await session.commit()
        if watched:
            return episode_watched_row_mapper(watched)
        return EpisodeWatched(episode_number=episode_number)


async def increment_watched_range(
    series_id: int,
    from_episode_number: int,
    to_episode_number: int,
    user_id: int,
    data: EpisodeWatchedIncrement | None,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        if to_episode_number < from_episode_number:
            raise exceptions.APIException(
                400, 0, 'to_episode_number must be bigger than from_episode_number'
            )
        for number in range(from_episode_number, to_episode_number + 1):
            await increment_episode_watched(
                session=session,
                user_id=user_id,
                series_id=series_id,
                episode_number=number,
                data=data or {},
            )
        await session.commit()


async def get_watched_position(
    series_id: int,
    episode_number: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> EpisodeWatched | None:
    async with get_session(session) as session:
        watched = (
            (
                await session.execute(
                    sa.select(MEpisodeWatched.__table__).where(
                        MEpisodeWatched.series_id == series_id,
                        MEpisodeWatched.episode_number == episode_number,
                        MEpisodeWatched.user_id == user_id,
                    )
                )
            )
            .mappings()
            .first()
        )
        if not watched:
            return None
        return episode_watched_row_mapper(watched)


async def set_watched_position(
    series_id: int,
    episode_number: int,
    position: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        await set_episode_watched_position(
            session=session,
            user_id=user_id,
            series_id=series_id,
            episode_number=episode_number,
            position=position,
        )
        await session.commit()


async def delete_watched_position(
    series_id: int,
    episode_number: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        await reset_episode_watched_position(
            session=session,
            user_id=user_id,
            series_id=series_id,
            episode_number=episode_number,
        )
        await session.commit()


async def increment_episode_watched(
    user_id: int,
    series_id: int,
    episode_number: int,
    data: EpisodeWatchedIncrement,
    session: AsyncSession,
) -> None:
    watched_at = data.get('watched_at') or datetime.now(tz=UTC)
    episode_watched = mysql_insert(cast(sa.Table, MEpisodeWatched.__table__)).values(
        series_id=series_id,
        episode_number=episode_number,
        user_id=user_id,
        watched_at=watched_at,
        times=1,
    )
    episode_watched = episode_watched.on_duplicate_key_update(
        watched_at=episode_watched.inserted.watched_at,
        times=MEpisodeWatched.times + 1,
        position=0,
    )

    watched_history = sa.insert(cast(sa.Table, MEpisodeWatchedHistory.__table__)).values(
        series_id=series_id,
        episode_number=episode_number,
        user_id=user_id,
        watched_at=watched_at,
    )

    episode_last_watched = (
        mysql_insert(cast(sa.Table, MEpisodeLastWatched.__table__))
        .values(
            series_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
        )
        .on_duplicate_key_update(
            episode_number=episode_number,
        )
    )

    await session.execute(episode_watched)
    await session.execute(watched_history)
    await session.execute(episode_last_watched)


async def decrement_episode_watched(
    user_id: int,
    series_id: int,
    episode_number: int,
    session: AsyncSession,
) -> None:
    watched = (
        (
            await session.execute(
                sa.select(MEpisodeWatched.__table__).where(
                    MEpisodeWatched.series_id == series_id,
                    MEpisodeWatched.episode_number == episode_number,
                    MEpisodeWatched.user_id == user_id,
                )
            )
        )
        .mappings()
        .first()
    )
    if not watched:
        return
    if watched['times'] == 0 or (watched['times'] == 1 and watched['position'] == 0):
        await session.execute(
            sa.delete(cast(sa.Table, MEpisodeWatched.__table__)).where(
                MEpisodeWatched.series_id == series_id,
                MEpisodeWatched.episode_number == episode_number,
                MEpisodeWatched.user_id == user_id,
            )
        )
        await session.execute(
            sa.delete(cast(sa.Table, MEpisodeWatchedHistory.__table__)).where(
                MEpisodeWatchedHistory.series_id == series_id,
                MEpisodeWatchedHistory.episode_number == episode_number,
                MEpisodeWatchedHistory.user_id == user_id,
            )
        )
    elif watched['position'] > 0:
        watched_at = await session.scalar(
            sa.select(MEpisodeWatchedHistory.watched_at)
            .where(
                MEpisodeWatchedHistory.series_id == series_id,
                MEpisodeWatchedHistory.episode_number == episode_number,
                MEpisodeWatchedHistory.user_id == user_id,
            )
            .order_by(MEpisodeWatchedHistory.watched_at.desc())
            .limit(1)
        )
        await session.execute(
            sa.update(cast(sa.Table, MEpisodeWatched.__table__))
            .where(
                MEpisodeWatched.series_id == series_id,
                MEpisodeWatched.episode_number == episode_number,
                MEpisodeWatched.user_id == user_id,
            )
            .values(
                position=0,
                watched_at=watched_at,
            )
        )
    else:
        history_rows = (
            await session.execute(
                sa.select(MEpisodeWatchedHistory.id, MEpisodeWatchedHistory.watched_at)
                .where(
                    MEpisodeWatchedHistory.series_id == series_id,
                    MEpisodeWatchedHistory.episode_number == episode_number,
                    MEpisodeWatchedHistory.user_id == user_id,
                )
                .order_by(MEpisodeWatchedHistory.watched_at.desc())
                .limit(2)
            )
        ).all()
        await session.execute(
            sa.delete(cast(sa.Table, MEpisodeWatchedHistory.__table__)).where(
                MEpisodeWatchedHistory.id == history_rows[0].id,
            )
        )
        await session.execute(
            sa.update(cast(sa.Table, MEpisodeWatched.__table__))
            .where(
                MEpisodeWatched.series_id == series_id,
                MEpisodeWatched.episode_number == episode_number,
                MEpisodeWatched.user_id == user_id,
            )
            .values(
                times=MEpisodeWatched.times - 1,
                position=0,
                watched_at=history_rows[1].watched_at,
            )
        )
    await set_previous_watched_episode(
        session=session,
        user_id=user_id,
        series_id=series_id,
        episode_number=episode_number,
    )


async def set_episode_watched_position(
    user_id: int,
    series_id: int,
    episode_number: int,
    position: int,
    session: AsyncSession,
) -> None:
    if position == 0:
        await reset_episode_watched_position(
            session=session,
            user_id=user_id,
            series_id=series_id,
            episode_number=episode_number,
        )
        return
    stmt = mysql_insert(cast(sa.Table, MEpisodeWatched.__table__)).values(
        series_id=series_id,
        episode_number=episode_number,
        user_id=user_id,
        watched_at=datetime.now(tz=UTC),
        position=position,
    )
    stmt = stmt.on_duplicate_key_update(
        watched_at=stmt.inserted.watched_at,
        position=stmt.inserted.position,
    )
    await session.execute(stmt)

    last_watched_stmt = (
        mysql_insert(cast(sa.Table, MEpisodeLastWatched.__table__))
        .values(
            series_id=series_id,
            episode_number=episode_number,
            user_id=user_id,
        )
        .on_duplicate_key_update(
            episode_number=episode_number,
        )
    )
    await session.execute(last_watched_stmt)


async def reset_episode_watched_position(
    user_id: int,
    series_id: int,
    episode_number: int,
    session: AsyncSession,
) -> None:
    watched = (
        (
            await session.execute(
                sa.select(MEpisodeWatched.__table__).where(
                    MEpisodeWatched.series_id == series_id,
                    MEpisodeWatched.episode_number == episode_number,
                    MEpisodeWatched.user_id == user_id,
                )
            )
        )
        .mappings()
        .first()
    )
    if not watched:
        return
    if watched['times'] < 1:
        await session.execute(
            sa.delete(cast(sa.Table, MEpisodeWatched.__table__)).where(
                MEpisodeWatched.series_id == series_id,
                MEpisodeWatched.episode_number == episode_number,
                MEpisodeWatched.user_id == user_id,
            )
        )
        await session.execute(
            sa.delete(cast(sa.Table, MEpisodeWatchedHistory.__table__)).where(
                MEpisodeWatchedHistory.series_id == series_id,
                MEpisodeWatchedHistory.episode_number == episode_number,
                MEpisodeWatchedHistory.user_id == user_id,
            )
        )
    elif watched['position'] > 0:
        watched_at = await session.scalar(
            sa.select(MEpisodeWatchedHistory.watched_at)
            .where(
                MEpisodeWatchedHistory.series_id == series_id,
                MEpisodeWatchedHistory.episode_number == episode_number,
                MEpisodeWatchedHistory.user_id == user_id,
            )
            .order_by(MEpisodeWatchedHistory.watched_at.desc())
            .limit(1)
        )
        await session.execute(
            sa.update(cast(sa.Table, MEpisodeWatched.__table__))
            .where(
                MEpisodeWatched.series_id == series_id,
                MEpisodeWatched.episode_number == episode_number,
                MEpisodeWatched.user_id == user_id,
            )
            .values(
                position=0,
                watched_at=watched_at,
            )
        )
    else:
        return
    await set_previous_watched_episode(
        session=session,
        user_id=user_id,
        series_id=series_id,
        episode_number=episode_number,
    )


async def set_previous_watched_episode(
    user_id: int,
    series_id: int,
    episode_number: int,
    session: AsyncSession,
) -> None:
    last_episode_watched = (
        (
            await session.execute(
                sa.select(MEpisodeLastWatched.__table__).where(
                    MEpisodeLastWatched.series_id == series_id,
                    MEpisodeLastWatched.user_id == user_id,
                )
            )
        )
        .mappings()
        .first()
    )
    if last_episode_watched and last_episode_watched['episode_number'] == episode_number:
        previous_episode = (
            (
                await session.execute(
                    sa.select(MEpisodeWatchedHistory.__table__)
                    .where(
                        MEpisodeWatchedHistory.user_id == user_id,
                        MEpisodeWatchedHistory.series_id == series_id,
                    )
                    .order_by(
                        sa.desc(MEpisodeWatchedHistory.watched_at),
                        sa.desc(MEpisodeWatchedHistory.episode_number),
                    )
                    .limit(1)
                )
            )
            .mappings()
            .first()
        )
        if not previous_episode:
            await session.execute(
                sa.delete(cast(sa.Table, MEpisodeLastWatched.__table__)).where(
                    MEpisodeLastWatched.user_id == user_id,
                    MEpisodeLastWatched.series_id == series_id,
                )
            )
        else:
            await session.execute(
                sa.update(cast(sa.Table, MEpisodeLastWatched.__table__))
                .values(
                    episode_number=previous_episode['episode_number'],
                )
                .where(
                    MEpisodeLastWatched.series_id == series_id,
                    MEpisodeLastWatched.user_id == user_id,
                )
            )


async def get_episode_to_watch(
    series_id: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> Episode | None:
    async with get_session(session) as session:
        watched = (
            (
                await session.execute(
                    sa.select(
                        MEpisodeWatched.episode_number,
                        MEpisodeWatched.position,
                    ).where(
                        MEpisodeLastWatched.user_id == user_id,
                        MEpisodeLastWatched.series_id == series_id,
                        MEpisodeWatched.series_id == MEpisodeLastWatched.series_id,
                        MEpisodeWatched.user_id == MEpisodeLastWatched.user_id,
                        MEpisodeWatched.episode_number
                        == MEpisodeLastWatched.episode_number,
                    )
                )
            )
            .mappings()
            .first()
        )

        episode_number = 1
        if watched:
            episode_number = watched['episode_number']
            if watched['position'] == 0:
                episode_number += 1

        result = await session.execute(
            sa.select(
                MEpisode.__table__,
                MEpisodeWatched.__table__,
            )
            .where(
                MEpisode.series_id == series_id,
                MEpisode.number == episode_number,
            )
            .join(
                MEpisodeWatched.__table__,
                sa.and_(
                    MEpisodeWatched.user_id == user_id,
                    MEpisodeWatched.series_id == MEpisode.series_id,
                    MEpisodeWatched.episode_number == MEpisode.number,
                ),
                isouter=True,
            )
        )
        row = result.mappings().first()
        if not row:
            return None

        episode = episode_row_mapper(row)
        episode.user_watched = (
            episode_watched_row_mapper(row)
            if row['episode_number'] is not None
            else EpisodeWatched(episode_number=row['number'])
        )
        await expand_user_can_watch(
            series_id=series_id, user_id=user_id, episodes=[episode], session=session
        )
        return episode


async def get_last_watched_episode(
    series_id: int,
    user_id: int,
    session: AsyncSession | None = None,
) -> Episode | None:
    async with get_session(session) as session:
        result = await session.execute(
            sa.select(
                MEpisode.__table__,
                MEpisodeWatched.__table__,
            )
            .where(
                MEpisodeWatched.user_id == user_id,
                MEpisodeWatched.series_id == series_id,
                MEpisode.series_id == MEpisodeWatched.series_id,
                MEpisode.number == MEpisodeWatched.episode_number,
            )
            .order_by(
                sa.desc(MEpisodeWatched.watched_at),
                sa.desc(MEpisodeWatched.episode_number),
            )
            .limit(2)
        )
        rows = result.mappings().all()

        if not rows:
            return None

        row = rows[0]
        if len(rows) == 1:
            if rows[0]['position'] > 0:
                return None
        elif rows[0]['position'] > 0:
            row = rows[1]

        episode = episode_row_mapper(row)
        episode.user_watched = episode_watched_row_mapper(row)
        await expand_user_can_watch(
            series_id=series_id, user_id=user_id, episodes=[episode], session=session
        )
        return episode
