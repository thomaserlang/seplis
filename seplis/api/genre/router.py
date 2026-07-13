from typing import Literal

from fastapi import APIRouter

from .actions.genre_actions import get_genres
from .schemas.genre_schemas import Genre

router = APIRouter(prefix='/genres', tags=['Genres'])


@router.get('')
async def get_genres_route(
    type: Literal['series', 'movie'],
) -> list[Genre]:
    return await get_genres(type=type)
