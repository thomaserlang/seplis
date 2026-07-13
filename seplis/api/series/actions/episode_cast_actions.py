import sqlalchemy as sa
from sqlalchemy.engine import RowMapping

from seplis.api.contexts import AsyncSession, get_session
from seplis.api.page_cursor import PageCursor, PageCursorQuery, page_cursor
from seplis.api.person import person_mapper

from ..models.episode_cast_model import MEpisodeCast
from ..schemas.episode_cast_schemas import EpisodeCastPerson, EpisodeCastPersonCreate


def episode_cast_person_mapper(row: RowMapping) -> EpisodeCastPerson:
    cast: MEpisodeCast = row['MEpisodeCast']
    return EpisodeCastPerson(
        person=person_mapper(cast.person),
        character=cast.character or '',
        series_id=cast.series_id,
        episode_number=cast.episode_number,
        order=cast.order,
    )


async def add_episode_cast(
    series_id: int,
    episode_number: int,
    data: EpisodeCastPersonCreate,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        data_ = {**data, 'series_id': series_id, 'episode_number': episode_number}
        await session.execute(
            sa.dialects.mysql.insert(MEpisodeCast.__table__)  # type: ignore
            .values(data_)
            .on_duplicate_key_update(data_)
        )


async def delete_episode_cast(
    series_id: int,
    episode_number: int,
    person_id: int,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.delete(MEpisodeCast.__table__).where(  # type: ignore
                MEpisodeCast.series_id == series_id,
                MEpisodeCast.episode_number == episode_number,
                MEpisodeCast.person_id == person_id,
            )
        )


async def get_episode_cast(
    series_id: int,
    episode_number: int,
    page_query: PageCursorQuery,
    session: AsyncSession | None = None,
) -> PageCursor[EpisodeCastPerson]:
    query = (
        sa.select(MEpisodeCast)
        .where(
            MEpisodeCast.series_id == series_id,
            MEpisodeCast.episode_number == episode_number,
        )
        .order_by(sa.func.coalesce(MEpisodeCast.order, 0))
    )
    return await page_cursor(
        session=session,
        query=query,
        page_query=page_query,
        count_total=False,
        record_mapper=episode_cast_person_mapper,
    )
