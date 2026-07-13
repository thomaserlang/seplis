from dataclasses import asdict

import sqlalchemy as sa
from sqlalchemy.engine import RowMapping

from seplis.api.contexts import AsyncSession, get_session
from seplis.api.page_cursor import PageCursor, PageCursorQuery, page_cursor
from seplis.api.person import person_mapper

from ..models.series_cast_model import MSeriesCast
from ..schemas.series_cast_schemas import (
    SeriesCastPerson,
    SeriesCastPersonCreate,
    SeriesCastRole,
)


def series_cast_person_model_mapper(cast: MSeriesCast) -> SeriesCastPerson:
    return SeriesCastPerson(
        series_id=cast.series_id,
        person=person_mapper(cast.person),
        roles=[
            role
            if isinstance(role, SeriesCastRole)
            else SeriesCastRole(
                character=role.get('character'),
                total_episodes=role.get('total_episodes', 0),
            )
            for role in cast.roles or []
        ],
        order=cast.order,
        total_episodes=cast.total_episodes,
    )


def series_cast_person_mapper(row: RowMapping) -> SeriesCastPerson:
    return series_cast_person_model_mapper(row['MSeriesCast'])


async def add_series_cast(
    series_id: int,
    data: SeriesCastPersonCreate,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        data_ = {**data, 'series_id': series_id}
        data_['roles'] = [
            asdict(role) if isinstance(role, SeriesCastRole) else role
            for role in data_.get('roles') or []
        ]
        await session.execute(
            sa.dialects.mysql.insert(MSeriesCast.__table__)  # type: ignore
            .values(data_)
            .on_duplicate_key_update(data_)
        )


async def delete_series_cast(
    series_id: int, person_id: int, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.delete(MSeriesCast.__table__).where(  # type: ignore
                MSeriesCast.series_id == series_id,
                MSeriesCast.person_id == person_id,
            )
        )


async def get_series_cast(
    series_id: int,
    order_le: int | None,
    order_ge: int | None,
    page_query: PageCursorQuery,
    session: AsyncSession | None = None,
) -> PageCursor[SeriesCastPerson]:
    query = (
        sa.select(MSeriesCast)
        .where(MSeriesCast.series_id == series_id)
        .order_by(sa.asc(sa.func.coalesce(MSeriesCast.order, 0)))
    )

    if order_le is not None:
        query = query.where(MSeriesCast.order <= order_le)
    if order_ge is not None:
        query = query.where(MSeriesCast.order >= order_ge)

    return await page_cursor(
        session=session,
        query=query,
        page_query=page_query,
        count_total=False,
        record_mapper=series_cast_person_mapper,
    )
