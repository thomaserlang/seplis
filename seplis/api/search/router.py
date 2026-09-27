from typing import Annotated, Literal

from fastapi import APIRouter, Query

from .actions.search_actions import search_titles
from .schemas.search_schemas import SearchTitleDocument

router = APIRouter(prefix='/search', tags=['Search'])
SearchText = Annotated[str, Query(min_length=1, max_length=200)]


@router.get('', response_model=None)
async def search_route(
    query: SearchText | None = None,
    title: SearchText | None = None,
    title_type: Annotated[Literal['series', 'movie'] | None, Query(alias='type')] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[SearchTitleDocument]:
    return await search_titles(
        query=query, title=title, title_type=title_type, limit=limit
    )
