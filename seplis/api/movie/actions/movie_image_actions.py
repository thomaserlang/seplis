from typing import cast

import sqlalchemy as sa
from fastapi import UploadFile
from sqlalchemy.engine import RowMapping

from seplis.api.contexts import AsyncSession, get_session
from seplis.api.image import (
    IMAGE_TYPES,
    Image,
    ImageImport,
    MImage,
    image_mapper,
    save_image,
)
from seplis.api.page_cursor import PageCursor, PageCursorQuery, page_cursor

from ..models.movie_model import MMovie


def movie_image_mapper(row: RowMapping) -> Image:
    return image_mapper(row)


async def create_movie_image(
    *,
    movie_id: int,
    image: UploadFile,
    type: IMAGE_TYPES,
    external_name: str | None,
    external_id: str | None,
) -> Image:
    image_data = ImageImport(
        external_name=external_name or '',
        external_id=external_id or '',
        file=image,
        type=type,
    )
    return await save_image(
        relation_type='movie',
        relation_id=movie_id,
        image_data=image_data,
    )


async def delete_movie_image(
    *, movie_id: int, image_id: int, session: AsyncSession | None = None
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.update(cast(sa.Table, MMovie.__table__))
            .values(poster_image_id=None)
            .where(
                MMovie.id == movie_id,
                MMovie.poster_image_id == image_id,
            )
        )
        await session.execute(
            sa.delete(cast(sa.Table, MImage.__table__)).where(
                MImage.relation_type == 'movie',
                MImage.relation_id == movie_id,
                MImage.id == image_id,
            )
        )
        await session.commit()


async def get_movie_images(
    *,
    movie_id: int,
    type: IMAGE_TYPES | None,
    page_query: PageCursorQuery,
    session: AsyncSession | None = None,
) -> PageCursor[Image]:
    query = sa.select(MImage.__table__).where(
        MImage.relation_type == 'movie',
        MImage.relation_id == movie_id,
    )
    if type:
        query = query.where(MImage.type == type)
    return await page_cursor(
        session=session,
        query=query,
        page_query=page_query,
        record_mapper=movie_image_mapper,
    )
