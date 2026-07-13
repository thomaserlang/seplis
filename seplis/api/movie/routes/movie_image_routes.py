from typing import Annotated

from fastapi import APIRouter, Depends, Form, Security, UploadFile

from seplis.api.dependencies import authenticated
from seplis.api.image import IMAGE_TYPES, Image
from seplis.api.page_cursor import PageCursor, PageCursorQuery
from seplis.api.user import UserAuthenticated

from ..actions.movie_image_actions import (
    create_movie_image,
    delete_movie_image,
    get_movie_images,
)

router = APIRouter()


@router.post('/{movie_id}/images', status_code=201)
async def create_image_route(
    movie_id: int,
    image: UploadFile,
    type: Annotated[IMAGE_TYPES, Form()],
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['movie:manage_images'])
    ],
    external_name: Annotated[str | None, Form(min_length=1, max_length=50)] = None,
    external_id: Annotated[str | None, Form(min_length=1, max_length=50)] = None,
) -> Image:
    return await create_movie_image(
        movie_id=movie_id,
        image=image,
        type=type,
        external_name=external_name,
        external_id=external_id,
    )


@router.delete('/{movie_id}/images/{image_id}', status_code=204)
async def delete_image_route(
    movie_id: int,
    image_id: int,
    user: Annotated[
        UserAuthenticated, Security(authenticated, scopes=['movie:manage_images'])
    ],
) -> None:
    await delete_movie_image(movie_id=movie_id, image_id=image_id)


@router.get('/{movie_id}/images')
async def get_images_route(
    movie_id: int,
    page_query: Annotated[PageCursorQuery, Depends()],
    type: IMAGE_TYPES | None = None,
) -> PageCursor[Image]:
    return await get_movie_images(movie_id=movie_id, type=type, page_query=page_query)
