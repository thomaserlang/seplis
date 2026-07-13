from typing import Annotated

from fastapi import APIRouter, Depends, Form, Security, UploadFile

from seplis.api.image import IMAGE_TYPES, Image
from seplis.api.page_cursor import PageCursor, PageCursorQuery

from ...dependencies import authenticated
from ...user import UserAuthenticated
from ..actions.series_image_actions import (
    create_series_image,
    delete_series_image,
    get_series_images,
)

router = APIRouter()


@router.post(
    '/{series_id}/images',
    status_code=201,
    description="""
            **Scope required:** `series:manage_images`
            """,
)
async def create_image_route(
    series_id: int,
    image: UploadFile,
    type: Annotated[IMAGE_TYPES, Form()],
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['series:manage_images'])
    ],
    external_name: Annotated[str | None, Form(min_length=1, max_length=50)] = None,
    external_id: Annotated[str | None, Form(min_length=1, max_length=50)] = None,
) -> Image:
    return await create_series_image(
        series_id=series_id,
        image=image,
        external_name=external_name,
        external_id=external_id,
        image_type=type,
    )


@router.delete(
    '/{series_id}/images/{image_id}',
    status_code=204,
    description="""
            **Scope required:** `series:manage_images`
            """,
)
async def delete_image_route(
    series_id: int,
    image_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['series:manage_images'])
    ],
) -> None:
    await delete_series_image(series_id=series_id, image_id=image_id)


@router.get('/{series_id}/images')
async def get_images_route(
    series_id: int,
    page_query: Annotated[PageCursorQuery, Depends()],
    type: IMAGE_TYPES | None = None,
) -> PageCursor[Image]:
    return await get_series_images(
        series_id=series_id, image_type=type, page_query=page_query
    )
