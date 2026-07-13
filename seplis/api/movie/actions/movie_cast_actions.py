import sqlalchemy as sa
from sqlalchemy.engine import RowMapping

from seplis.api.contexts import AsyncSession, get_session
from seplis.api.page_cursor import PageCursor, PageCursorQuery, page_cursor
from seplis.api.person import person_mapper

from ..models.movie_cast_model import MMovieCast
from ..schemas.movie_cast_schemas import MovieCastPerson, MovieCastPersonCreate


def movie_cast_person_model_mapper(cast: MMovieCast) -> MovieCastPerson:
    return MovieCastPerson(
        movie_id=cast.movie_id,
        person=person_mapper(cast.person),
        character=cast.character,
        order=cast.order,
    )


def movie_cast_person_mapper(row: RowMapping) -> MovieCastPerson:
    return movie_cast_person_model_mapper(row['MMovieCast'])


async def save_movie_cast(
    *, movie_id: int, data: MovieCastPersonCreate, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        data_ = {**dict(data), 'movie_id': movie_id}
        await session.execute(
            sa.dialects.mysql.insert(MMovieCast.__table__)  # type: ignore
            .values(data_)
            .on_duplicate_key_update(data_)
        )


async def delete_movie_cast(
    *, movie_id: int, person_id: int, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.delete(MMovieCast.__table__).where(  # type: ignore
                MMovieCast.movie_id == movie_id,
                MMovieCast.person_id == person_id,
            )
        )


async def get_movie_cast(
    *,
    movie_id: int,
    page_query: PageCursorQuery,
    session: AsyncSession | None = None,
    order_le: int | None = None,
    order_ge: int | None = None,
) -> PageCursor[MovieCastPerson]:
    query = (
        sa.select(MMovieCast)
        .where(MMovieCast.movie_id == movie_id)
        .order_by(sa.asc(sa.func.coalesce(MMovieCast.order, 0)))
    )

    if order_le is not None:
        query = query.where(MMovieCast.order <= order_le)
    if order_ge is not None:
        query = query.where(MMovieCast.order >= order_ge)

    return await page_cursor(
        session=session,
        query=query,
        page_query=page_query,
        count_total=False,
        record_mapper=movie_cast_person_mapper,
    )
