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

from ..models.series_model import MSeries


def series_image_mapper(row: RowMapping) -> Image:
    return image_mapper(row['MImage'])


async def create_series_image(
    series_id: int,
    image: UploadFile,
    external_name: str | None,
    external_id: str | None,
    image_type: IMAGE_TYPES,
) -> Image:
    return await save_image(
        relation_type='series',
        relation_id=series_id,
        image_data=ImageImport(
            external_name=external_name or '',
            external_id=external_id or '',
            file=image,
            type=image_type,
        ),
    )


async def delete_series_image(
    series_id: int,
    image_id: int,
    session: AsyncSession | None = None,
) -> None:
    async with get_session(session) as session:
        await session.execute(
            sa.update(MSeries.__table__)  # type: ignore
            .values(poster_image_id=None)
            .where(
                MSeries.id == series_id,
                MSeries.poster_image_id == image_id,
            )
        )
        await session.execute(
            sa.delete(MImage.__table__).where(  # type: ignore
                MImage.relation_type == 'series',
                MImage.relation_id == series_id,
                MImage.id == image_id,
            )
        )
        await session.commit()


async def get_series_images(
    series_id: int,
    image_type: IMAGE_TYPES | None,
    page_query: PageCursorQuery,
    session: AsyncSession | None = None,
) -> PageCursor[Image]:
    query = sa.select(MImage).where(
        MImage.relation_type == 'series',
        MImage.relation_id == series_id,
    )
    if image_type:
        query = query.where(MImage.type == image_type)
    return await page_cursor(
        session=session,
        query=query,
        page_query=page_query,
        record_mapper=series_image_mapper,
    )
