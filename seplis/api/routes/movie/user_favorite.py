import sqlalchemy as sa
from fastapi import Depends, Security

from ... import models, schemas
from ...dependencies import AsyncSession, UserAuthenticated, authenticated, get_session
from .router import router


@router.get(
    '/{movie_id}/favorite',
    response_model=schemas.Movie_favorite,
    description="""
            **Scope required:** `user:view_lists`
            """,
)
async def get_favorite(
    movie_id: int,
    session: AsyncSession = Depends(get_session),
    user: UserAuthenticated = Security(authenticated, scopes=['user:view_lists']),
):
    w = await session.scalar(
        sa.select(models.MMovieFavorite.created_at).where(
            models.MMovieFavorite.user_id == user.id,
            models.MMovieFavorite.movie_id == movie_id,
        )
    )
    if not w:
        return schemas.Movie_favorite()
    return schemas.Movie_favorite(
        favorite=True,
        created_at=w,
    )


@router.put(
    '/{movie_id}/favorite',
    status_code=204,
    description="""
            **Scope required:** `user:manage_lists`
            """,
)
async def add_to_favorite(
    movie_id: int,
    user: UserAuthenticated = Security(authenticated, scopes=['user:manage_lists']),
) -> None:
    await models.MMovieFavorite.add(user_id=user.id, movie_id=movie_id)


@router.delete(
    '/{movie_id}/favorite',
    status_code=204,
    description="""
            **Scope required:** `user:manage_lists`
            """,
)
async def remove_from_favorite(
    movie_id: int,
    user: UserAuthenticated = Security(authenticated, scopes=['user:manage_lists']),
) -> None:
    await models.MMovieFavorite.remove(user_id=user.id, movie_id=movie_id)
