from typing import Any, Literal, cast

import sqlalchemy as sa
from sqlalchemy.engine import RowMapping

from seplis.api.contexts import AsyncSession, get_session

from ..models.genre_model import MGenre
from ..schemas.genre_schemas import Genre


def genre_mapper(genre: RowMapping | MGenre) -> Genre:
    if isinstance(genre, MGenre):
        return Genre(
            id=genre.id,
            name=genre.name or '',
            number_of=genre.number_of or 0,
        )
    return Genre(
        id=genre['id'],
        name=genre['name'] or '',
        number_of=genre['number_of'] or 0,
    )


async def get_genres(
    *, type: Literal['series', 'movie'], session: AsyncSession | None = None
) -> list[Genre]:
    async with get_session(session) as session:
        rows = (
            await session.execute(
                sa.select(MGenre.__table__)
                .where(
                    MGenre.type == type,
                    MGenre.number_of > 0,
                )
                .order_by(MGenre.name)
            )
        ).mappings()
        return [genre_mapper(row) for row in rows]


async def get_or_create_genre(
    genre: str,
    type_: str,
    session: AsyncSession | None = None,
) -> int:
    async with get_session(session) as session:
        genre_id = await session.scalar(
            sa.select(MGenre.id).where(
                MGenre.name == genre,
                MGenre.type == type_,
            )
        )
        if not genre_id:
            result = cast(
                Any,
                await session.execute(
                    sa.insert(cast(sa.Table, MGenre.__table__)).values(
                        name=genre, type=type_
                    )
                ),
            )
            genre_id = result.lastrowid
        return genre_id


async def get_or_create_genres(
    genres: list[int | str],
    type_: str,
    session: AsyncSession | None = None,
) -> set[int]:
    genre_ids = [genre_id for genre_id in genres if isinstance(genre_id, int)]
    async with get_session(session) as session:
        for genre in genres:
            if isinstance(genre, str):
                genre_ids.append(
                    await get_or_create_genre(genre, type_=type_, session=session)
                )
    return set(genre_ids)
